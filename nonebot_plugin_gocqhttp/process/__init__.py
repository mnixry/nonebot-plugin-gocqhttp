import asyncio
import subprocess
import threading
from time import sleep
from typing import Optional

import psutil
from nonebot.utils import run_sync
from pydantic import BaseModel

from ..plugin_config import AccountConfig
from ..log import logger
from .config import ACCOUNTS_DATA_PATH, generate_config, generate_device
from .download import BINARY_PATH


class ProcessInfo(BaseModel):
    memory_used: int
    swap_used: int
    cpu_percent: float
    start_time: float


class GoCQProcess:
    process: Optional[subprocess.Popen] = None

    def __init__(
        self,
        account: AccountConfig,
        kill_timeout: float = 5,
        stop_timeout: float = 6,
        wait_interval: float = 0.1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.account = account
        self.cwd = ACCOUNTS_DATA_PATH / str(account.uin)

        self.stop_timeout, self.kill_timeout = stop_timeout, kill_timeout
        self.wait_interval = wait_interval
        self.loop = loop or asyncio.get_running_loop()
        self.stdout_queue = asyncio.Queue[str]()
        self.stderr_queue = asyncio.Queue[str]()

        self.daemon_thread = threading.Thread(
            target=(
                logger.catch(
                    onerror=lambda e: self.process.kill()
                    if self.process and self.process.returncode
                    else None,
                    message=f"Fatal error occurred for {self.daemon_thread.name!r}",
                )(self._daemon_thread_runner)
            ),
            name=f"{self.account.uin}-Daemon",
            daemon=True,
        )

    def _daemon_thread_runner(self):
        self.process = subprocess.Popen(
            [str(BINARY_PATH.absolute()), "faststart"],
            encoding="utf-8",
            cwd=self.cwd.absolute(),
        )
        assert self.process.stdout and self.process.stderr
        while self.daemon_thread_running:
            stdout, stderr = (
                self.process.stderr.readline(1),
                self.process.stderr.readline(1),
            )
            if stdout and stdout.endswith("\n"):
                asyncio.run_coroutine_threadsafe(
                    self.stdout_queue.put(stdout), loop=self.loop
                )
            if stderr and stderr.endswith("\n"):
                asyncio.run_coroutine_threadsafe(
                    self.stderr_queue.put(stderr), loop=self.loop
                )
            sleep(self.wait_interval)
        self.process.terminate()

        try:
            self.process.wait(self.kill_timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            logger.error(
                f"go-cqhttp process {self.process.pid} for account "
                f"{self.account.uin} terminate failed, killed."
            )
        if self.process.returncode != 0:
            logger.error(
                f"go-cqhttp process {self.process.pid} for account "
                f"{self.account.uin} exited with code {self.process.returncode}."
            )

        return self.process.returncode

    @run_sync
    def start(self):
        generate_config(self.account)
        generate_device(self.account)

        self.daemon_thread_running = True
        self.daemon_thread.start()

    @run_sync
    def stop(self):
        self.daemon_thread_running = False
        self.daemon_thread.join(self.stop_timeout)

    @run_sync
    def status(self):
        if self.process is None:
            raise ValueError("Process not started yet.")
        process_status = psutil.Process(self.process.pid)
        with process_status.oneshot():
            cpu = process_status.cpu_percent()
            memory = process_status.memory_info()
            create_time = process_status.create_time()
        return ProcessInfo(
            memory_used=memory.rss,
            swap_used=memory.vms,
            cpu_percent=cpu,
            start_time=create_time,
        )

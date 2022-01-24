import asyncio
import re
import subprocess
import threading
from itertools import count
from typing import Optional

import psutil
from nonebot.utils import escape_tag, run_sync
from pydantic import BaseModel

from ..log import logger
from ..plugin_config import AccountConfig
from .config import ACCOUNTS_DATA_PATH, generate_config, generate_device
from .download import BINARY_PATH

LOG_REGEX = re.compile(
    r"^"
    r"\[(?P<time>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] "
    r"\[(?P<level>[A-Z]+?)\]: "
    r"(?P<message>.*)"
    r"$"
)


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
        max_restarts: int = -1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.account = account
        self.cwd = ACCOUNTS_DATA_PATH / str(account.uin)

        self.stop_timeout, self.kill_timeout = stop_timeout, kill_timeout
        self.max_restarts = max_restarts

        self.loop = loop or asyncio.get_running_loop()
        self.output_queue = asyncio.Queue[str]()

        def daemon_thread_runner():
            for restarted in count():
                if not self.daemon_thread_running:
                    break
                if self.max_restarts >= 0 and restarted >= self.max_restarts:
                    break
                code = 0
                try:
                    self._daemon_thread_runner()
                except Exception:
                    logger.exception(
                        f"Thread {self.daemon_thread.name!r} raised unknown exception:"
                    )
                logger.warning(
                    f"<b>Process for <e>{self.account.uin}</e> exited</b> with code "
                    f"<r>{code}</r>, retrying to restart... "
                    f"<y>({restarted}/{self.max_restarts})</y>"
                )
            return

        self.daemon_thread = threading.Thread(
            target=daemon_thread_runner,
            name=f"{self.account.uin}-Daemon",
            daemon=True,
        )

    def _daemon_thread_runner(self):
        self.process = subprocess.Popen(
            [BINARY_PATH.absolute(), "faststart"],
            cwd=self.cwd.absolute(),
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert self.process.stdout is not None
        for output in iter(self.process.stdout.readline, ""):
            output = output.strip()
            if "アトリは、高性能ですから!" in output:
                logger.info(
                    "go-cqhttp for "
                    f"<e>{self.account.uin}</e> has successfully started."
                )

            log_matched = LOG_REGEX.match(output)
            if log_matched is not None:
                logger.log(
                    log_matched.group("level"),
                    f"<d>[{self.account.uin}]</d> "
                    + escape_tag(log_matched.group("message")),
                )
            else:
                logger.info(f"<d>[{self.account.uin}]</d> " + escape_tag(output))

        if self.process.returncode is None:
            self.process.terminate()
            self.process.wait(timeout=self.kill_timeout)

        return self.process.returncode

    @run_sync
    def start(self):
        generate_config(self.account)
        generate_device(self.account)

        self.daemon_thread_running = True
        self.daemon_thread.start()

    @run_sync
    def stop(self):
        if self.process is None:
            raise RuntimeError("Process is not running.")
        self.daemon_thread_running = False
        self.process.terminate()
        self.daemon_thread.join(self.stop_timeout)

    @run_sync
    def status(self):
        if self.process is None or self.process.returncode is not None:
            raise RuntimeError("Process not started yet.")

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

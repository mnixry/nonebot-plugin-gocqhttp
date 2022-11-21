import asyncio
import mimetypes
import re
import subprocess
import threading
import time
from base64 import b64encode
from itertools import count
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional, TypeVar

import psutil
from nonebot.utils import escape_tag, run_sync

from nonebot_plugin_gocqhttp.exceptions import ProcessAlreadyStarted
from nonebot_plugin_gocqhttp.log import LogStorage as BaseLogStorage
from nonebot_plugin_gocqhttp.log import logger
from nonebot_plugin_gocqhttp.plugin_config import AccountConfig
from nonebot_plugin_gocqhttp.process.config import (
    AccountConfigHelper,
    AccountDeviceHelper,
)
from nonebot_plugin_gocqhttp.process.download import ACCOUNTS_DATA_PATH, BINARY_PATH
from nonebot_plugin_gocqhttp.process.models import (
    ProcessInfo,
    ProcessLog,
    ProcessStatus,
    RunningProcessDetail,
    StoppedProcessDetail,
)

LOG_REGEX = re.compile(
    r"^"
    r"\[(?P<time>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] "
    r"\[(?P<level>[A-Z]+?)\]: "
    r"(?P<message>.*)"
    r"$"
)
STARTUP_FINISH_PROMPT = "アトリは、高性能ですから!"


LogListener = Callable[[ProcessLog], Awaitable[Any]]
LogListener_T = TypeVar("LogListener_T", bound=LogListener)


class LogStorage(BaseLogStorage[ProcessLog]):
    pass


class GoCQProcess:
    process: Optional[subprocess.Popen] = None
    worker_thread: Optional[threading.Thread] = None
    worker_thread_running = False

    def __init__(
        self,
        account: AccountConfig,
        predefined: bool = False,
        /,
        kill_timeout: float = 5,
        stop_timeout: float = 6,
        max_restarts: int = -1,
        restart_interval: float = 3,
        print_process_log: bool = True,
        log_rotation: float = 5 * 60,
        post_delay: float = 3,
    ):
        from .manager import ProcessesManager

        ProcessesManager.add(self, account.uin)

        self.cwd = (ACCOUNTS_DATA_PATH / str(account.uin)).absolute()
        self.cwd.mkdir(parents=True, exist_ok=True)

        self.config = AccountConfigHelper(account)
        if not self.config.exists:
            self.config.generate()
        self.device = AccountDeviceHelper(account)
        if not self.device.exists:
            self.device.generate()
        self.account, self.predefined = account, predefined

        self.loop = asyncio.get_running_loop()

        self.stop_timeout, self.kill_timeout = stop_timeout, kill_timeout
        self.max_restarts, self.restart_interval = max_restarts, restart_interval
        self.post_delay = post_delay

        self.logs, self.restart_count = LogStorage(log_rotation), 0

        async def process_log(log: ProcessLog):
            logger.log(
                log.level.name,
                f"<d>[{self.account.uin}]</d> {escape_tag(log.message)}",
            )

        if print_process_log:
            self.logs.listeners.add(process_log)

    def __repr__(self):
        return f"<{type(self).__name__} {self.account} process={self.process}>"

    @staticmethod
    def _terminate_process(process: subprocess.Popen, *, timeout: float):
        process.terminate()
        try:
            return process.wait(timeout)
        except subprocess.TimeoutExpired:
            process.kill()

    def _process_executor(self) -> int:
        self.process = subprocess.Popen(
            [BINARY_PATH.absolute(), "-faststart"],
            cwd=self.cwd.absolute(),
            text=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert self.process.stdout and self.process.stdin

        for output in iter(self.process.stdout.readline, b""):
            output = output.strip().decode("utf-8", "replace")
            if STARTUP_FINISH_PROMPT in output:
                logger.info(
                    "go-cqhttp for "
                    f"<e>{self.account.uin}</e> has successfully started."
                )

            log_matched = LOG_REGEX.match(output)
            log_model = (
                ProcessLog(**log_matched.groupdict())
                if log_matched
                else ProcessLog(message=output)
            )
            asyncio.run_coroutine_threadsafe(self.logs.add(log_model), loop=self.loop)

        if self.process.poll() is None:
            self._terminate_process(self.process, timeout=self.post_delay)

        return self.process.returncode

    def _process_worker(self):
        for restarted in count():
            if not self.worker_thread_running:
                break
            if self.max_restarts >= 0 and restarted >= self.max_restarts:
                break

            code = None
            try:
                code = self._process_executor()
            except Exception:
                logger.exception(
                    f"Thread {self.worker_thread!r} raised unknown exception:"
                )
            logger.warning(
                f"<b>Process for <e>{self.account.uin}</e> exited</b> "
                f"with code <r>{code}</r>, retrying to restart... "
                f"<y>({restarted}/{self.max_restarts})</y>"
            )
            self.restart_count += 1
            time.sleep(self.restart_interval)

    async def _find_duplicate_process(self):
        for process in psutil.process_iter():
            try:
                with process.oneshot():
                    pid = process.pid
                    cwd = Path(process.cwd()).absolute()
                    exe = Path(process.exe()).absolute()
            except psutil.Error:
                continue

            if Path(exe).is_file() and (
                BINARY_PATH.absolute().samefile(exe)
                or self.cwd.absolute().samefile(cwd)
            ):
                process.terminate()
                return pid
        return

    async def start(self):
        if self.worker_thread_running:
            raise ProcessAlreadyStarted

        if duplicate_pid := await self._find_duplicate_process():
            logger.warning(f"Possible {duplicate_pid=} found, terminated.")

        if not self.config.exists:
            self.config.generate()
        self.config.before_run()

        if not self.device.exists:
            self.device.generate()
        self.device.before_run()

        self.worker_thread_running = True
        self.worker_thread = threading.Thread(target=self._process_worker, daemon=True)
        self.worker_thread.name = f"daemon-thread-{self.account.uin}"
        self.worker_thread.start()

        await asyncio.sleep(self.post_delay)

    @run_sync
    def stop(self):
        self.worker_thread_running = False
        if self.process is not None:
            self._terminate_process(self.process, timeout=self.post_delay)
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(self.stop_timeout)
            self.worker_thread = None

    @run_sync
    def status(self) -> ProcessInfo:
        qr_path = self.cwd / "qrcode.png"
        if qr_path.exists():
            mimetype, _ = mimetypes.guess_type(qr_path)
            qr_data = qr_path.read_bytes()
            qr_uri = f"data:{mimetype};base64,{b64encode(qr_data).decode()}"
        else:
            qr_uri = None

        if not self.process or self.process.returncode is not None:
            return ProcessInfo(
                status=ProcessStatus.stopped,
                total_logs=self.logs.count,
                restarts=self.restart_count,
                details=(
                    StoppedProcessDetail(code=self.process.returncode)
                    if self.process
                    else None
                ),
            )

        with (ps := psutil.Process(self.process.pid)).oneshot():
            cpu = ps.cpu_percent()
            status = ps.status()
            memory = ps.memory_info()
            create_time = ps.create_time()

        return ProcessInfo(
            status=ProcessStatus.running,
            total_logs=self.logs.count,
            restarts=self.restart_count,
            qr_uri=qr_uri,
            details=RunningProcessDetail(
                pid=self.process.pid,
                status=status,
                memory_used=memory.rss,
                cpu_percent=cpu,
                start_time=create_time,
            ),
        )

import asyncio
import mimetypes
import re
import subprocess
import threading
from base64 import b64encode
from itertools import count
from time import sleep
from typing import Any, Awaitable, Callable, Optional, TypeVar

import psutil
from nonebot.utils import escape_tag, run_sync

from ..exceptions import ProcessAlreadyStarted, ProcessNotStarted
from ..log import LogStorage as BaseLogStorage
from ..log import logger
from ..plugin_config import AccountConfig
from .config import AccountConfigHelper, AccountDeviceHelper
from .download import ACCOUNTS_DATA_PATH, BINARY_PATH
from .models import (
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
    daemon_thread: Optional[threading.Thread] = None
    daemon_thread_running = False

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
    ):
        from .manager import ProcessesManager

        ProcessesManager.add(self, account.uin)

        self.cwd = ACCOUNTS_DATA_PATH / str(account.uin)
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

    def _daemon_thread_runner(self):
        self.process = subprocess.Popen(
            [BINARY_PATH.absolute(), "-faststart"],
            cwd=self.cwd.absolute(),
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert self.process.stdout is not None
        for output in iter(self.process.stdout.readline, ""):
            output = output.strip()
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

        if self.process.returncode is None:
            self.process.terminate()
            self.process.wait(timeout=self.kill_timeout)

        return self.process.returncode

    @run_sync
    def start(self):
        if self.daemon_thread_running:
            raise ProcessAlreadyStarted

        if not self.config.exists:
            self.config.generate()
        self.config.before_run()

        if not self.device.exists:
            self.device.generate()
        self.device.before_run()

        def runner():
            for restarted in count():
                if not self.daemon_thread_running:
                    break
                if self.max_restarts >= 0 and restarted >= self.max_restarts:
                    break
                code = 0
                try:
                    code = self._daemon_thread_runner()
                except Exception:
                    logger.exception(
                        f"Thread {self.daemon_thread!r} raised unknown exception:"
                    )
                logger.warning(
                    f"<b>Process for <e>{self.account.uin}</e> exited</b> with code "
                    f"<r>{code}</r>, retrying to restart... "
                    f"<y>({restarted}/{self.max_restarts})</y>"
                )
                self.restart_count += 1
                sleep(self.restart_interval)
            return

        self.daemon_thread_running = True
        self.daemon_thread = threading.Thread(target=runner, daemon=True)
        self.daemon_thread.name = f"daemon-thread-{self.account.uin}"
        self.daemon_thread.start()

        sleep(self.restart_interval)
        return

    @run_sync
    def stop(self):
        self.daemon_thread_running = False
        if self.process is not None:
            self.process.terminate()
        if self.daemon_thread and self.daemon_thread.is_alive():
            self.daemon_thread.join(self.stop_timeout)
        return

    @run_sync
    def status(self) -> ProcessInfo:
        if self.process is None:
            raise ProcessNotStarted

        qr_path = self.cwd / "qrcode.png"
        if qr_path.exists():
            mimetype, _ = mimetypes.guess_type(qr_path)
            qr_data = qr_path.read_bytes()
            qr_uri = f"data:{mimetype};base64,{b64encode(qr_data).decode()}"
        else:
            qr_uri = None

        if self.process.returncode is None:
            process = psutil.Process(self.process.pid)
            with process.oneshot():
                cpu = process.cpu_percent()
                status = process.status()
                memory = process.memory_info()
                create_time = process.create_time()
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
        else:
            return ProcessInfo(
                status=ProcessStatus.stopped,
                total_logs=self.logs.count,
                restarts=self.restart_count,
                details=StoppedProcessDetail(code=self.process.returncode),
            )
        return

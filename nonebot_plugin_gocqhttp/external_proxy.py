import os
import subprocess
import sys
from threading import Thread
from typing import Optional

import proxy  # type: ignore # noqa: F401
from nonebot.utils import escape_tag, run_sync

from nonebot_plugin_gocqhttp.log import logger


class ProxyServiceManager:
    stop_signal: bool = False
    thread: Optional[Thread] = None

    process: Optional[subprocess.Popen] = None

    @classmethod
    def _start(cls, port: int):
        cls.process = subprocess.Popen(
            [sys.executable, "-m", "proxy", f"--port={port}", "--hostname=0.0.0.0"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
        assert cls.process.stdout

        for line in iter(cls.process.stdout.readline, ""):
            logger.opt(colors=True).trace(
                f"Tunnel proxy log: <e>{escape_tag(line.strip())}</e>"
            )

    @classmethod
    async def start(cls, port: int):
        cls.thread = Thread(
            target=lambda: cls._start(port), name="ProxyService", daemon=True
        )
        cls.thread.start()

        tid = cls.thread.ident
        logger.debug(f"HTTP tunnel server started at {port=}, {tid=}")

    @classmethod
    @run_sync
    def stop(cls, timeout: float = 6):
        assert (
            cls.thread
            and cls.thread.is_alive()
            and cls.process
            and cls.process.poll() is None
        )
        cls.process.terminate()

        cls.stop_signal = True
        cls.thread.join(timeout)

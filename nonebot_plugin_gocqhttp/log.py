import asyncio
import logging
import re
from typing import Awaitable, Callable, ClassVar, Dict, Generic, List, Set, TypeVar
from urllib.parse import urlparse

from nonebot.log import logger as _logger

from .plugin_config import config as plugin_config

_T = TypeVar("_T")
LogListener = Callable[[_T], Awaitable[None]]


class LogStorage(Generic[_T]):
    def __init__(self, rotation: float = 5 * 60):
        self.count, self.rotation = 0, rotation
        self.logs: Dict[int, _T] = {}
        self.listeners: Set[LogListener[_T]] = set()

    async def add(self, log: _T):
        seq = self.count = self.count + 1
        self.logs[seq] = log
        asyncio.get_running_loop().call_later(self.rotation, self.remove, seq)
        await asyncio.gather(
            *map(lambda listener: listener(log), self.listeners),
            return_exceptions=True,
        )
        return seq

    def remove(self, seq: int):
        del self.logs[seq]
        return

    def list(self, reverse: bool = False) -> List[_T]:
        return [self.logs[seq] for seq in sorted(self.logs, reverse=reverse)]


class AccessLogFilter(logging.Filter):
    log_match_re = re.compile(
        r"\"(?P<method>\w+)\s+(?P<path>/\S+)\s(?P<protocol>\S+)\""
    )
    filterable_paths: ClassVar[Set[str]] = set()

    def filter(self, record: logging.LogRecord) -> bool:
        if plugin_config.MUTE_ACCESS_LOG is False:
            return True

        match = self.log_match_re.search(record.getMessage())
        if not match:
            return True

        if urlparse(match.group("path")).path in self.filterable_paths:
            record.levelno = 0
            record.levelname = "TRACE"
        return True


logging.getLogger("uvicorn.access").addFilter(AccessLogFilter())


STDOUT = _logger.level("STDOUT", no=logging.INFO)
FATAL = _logger.level("FATAL", no=logging.FATAL)

LOG_STORAGE = LogStorage[str]()

logger = _logger.opt(colors=True)

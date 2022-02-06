import asyncio
import logging
from typing import Awaitable, Callable, Dict, Generic, List, Set, TypeVar

from nonebot.log import logger as _logger

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


STDOUT = _logger.level("STDOUT", no=logging.INFO)
FATAL = _logger.level("FATAL", no=logging.FATAL)

LOG_STORAGE = LogStorage[str]()

logger = _logger.opt(colors=True)

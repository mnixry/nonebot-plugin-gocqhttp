import pickle
import pickletools
import zlib
from pathlib import Path
from typing import Dict, List, Optional

from ..plugin_config import config as plugin_config
from .models import ProcessAccount
from .process import GoCQProcess


class ProcessesManager:
    _processes: Dict[int, GoCQProcess] = {}

    get = _processes.get

    @classmethod
    def add(cls, process: GoCQProcess, uin: Optional[int] = None):
        uin = uin or process.account.uin
        if uin in cls._processes:
            raise ValueError(f"Account {process.account.uin} is already initialized.")
        cls._processes[uin] = process

    @classmethod
    def create(cls, account: ProcessAccount):
        return GoCQProcess(account, **plugin_config.PROCESS_KWARGS)

    @classmethod
    def all(cls) -> List[GoCQProcess]:
        return [*cls._processes.copy().values()]

    @classmethod
    def save(cls, save_path: Path) -> int:
        accounts = [process.account for process in cls.all()]
        dumped = pickle.dumps(accounts)
        dumped = pickletools.optimize(dumped)
        compressed = zlib.compress(dumped, level=zlib.Z_BEST_COMPRESSION)
        with open(save_path, "wb") as f:
            size = f.write(compressed)
        return size

    @classmethod
    def load_config(cls, *, ignore_loaded: bool = False) -> List[GoCQProcess]:
        return [
            GoCQProcess(account, **plugin_config.PROCESS_KWARGS)
            for account in plugin_config.ACCOUNTS
            if not ignore_loaded or account.uin not in cls._processes
        ]

    @classmethod
    def load_saved(
        cls, save_path: Path, *, ignore_loaded: bool = False
    ) -> List[GoCQProcess]:
        with open(save_path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed)
        accounts: List[ProcessAccount] = pickle.loads(decompressed)
        return [
            GoCQProcess(account, **plugin_config.PROCESS_KWARGS)
            for account in accounts
            if not ignore_loaded or account.uin not in cls._processes
        ]

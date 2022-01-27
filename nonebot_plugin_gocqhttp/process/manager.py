import pickle
import pickletools
import zlib
from pathlib import Path
from typing import Dict, List

from ..plugin_config import config as plugin_config
from .models import ProcessAccount
from .process import GoCQProcess


class ProcessesManager:
    _processes: Dict[int, GoCQProcess] = {}

    @classmethod
    def add(cls, process: GoCQProcess):
        if process.account.uin in cls._processes:
            raise ValueError(f"Account {process.account.uin} is already initialized.")
        cls._processes[process.account.uin] = process

    @classmethod
    def get(cls, uin: int) -> GoCQProcess:
        return cls._processes[uin]

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
    def load_config(cls) -> List[GoCQProcess]:
        return [
            GoCQProcess(account, **plugin_config.PROCESS_KWARGS)
            for account in plugin_config.ACCOUNTS
        ]

    @classmethod
    def load_saved(cls, save_path: Path) -> List[GoCQProcess]:
        with open(save_path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed)
        accounts: List[ProcessAccount] = pickle.loads(decompressed)
        return [
            GoCQProcess(account, **plugin_config.PROCESS_KWARGS) for account in accounts
        ]

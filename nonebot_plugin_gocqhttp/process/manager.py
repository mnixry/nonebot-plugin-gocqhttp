import pickle
import pickletools
import zlib
from pathlib import Path
from typing import Dict, List, Optional

from anyio import open_file
from loguru import logger
from nonebot_plugin_gocqhttp.exceptions import AccountAlreadyExists
from nonebot_plugin_gocqhttp.plugin_config import AccountConfig
from nonebot_plugin_gocqhttp.plugin_config import config as plugin_config
from nonebot_plugin_gocqhttp.process.download import BINARY_DIR
from nonebot_plugin_gocqhttp.process.models import ProcessAccountsStore
from nonebot_plugin_gocqhttp.process.process import GoCQProcess
from pydantic import parse_obj_as

ACCOUNTS_SAVE_PATH = BINARY_DIR / "accounts.pkl"


class ProcessesManager:
    _processes: Dict[int, GoCQProcess] = {}

    get = _processes.get

    @classmethod
    def add(cls, process: GoCQProcess, uin: Optional[int] = None):
        uin = uin or process.account.uin
        if uin in cls._processes:
            raise AccountAlreadyExists
        cls._processes[uin] = process

    @classmethod
    def create_instance(cls, account: AccountConfig, *, predefined: bool = False):
        return GoCQProcess(account, predefined, **plugin_config.PROCESS_KWARGS)

    @classmethod
    def remove(cls, uin: int):
        process = cls._processes.pop(uin)
        process.logs.listeners.clear()
        return

    @classmethod
    def all(cls, include_predefined: bool = True):
        return [
            process
            for process in cls._processes.values()
            if include_predefined or not process.predefined
        ]

    @classmethod
    async def save(cls, save_path: Path = ACCOUNTS_SAVE_PATH) -> int:
        store = ProcessAccountsStore(
            accounts=[
                parse_obj_as(AccountConfig, process.account)
                for process in cls.all(include_predefined=False)
            ]
        )
        dumped = pickle.dumps(store)
        dumped = pickletools.optimize(dumped)
        compressed = zlib.compress(dumped, level=zlib.Z_BEST_COMPRESSION)
        async with await open_file(save_path, "wb") as f:
            size = await f.write(compressed)
        logger.debug(f"Accounts data has been saved: {save_path=} {size=}")
        return size

    @classmethod
    def load_config(cls, *, ignore_loaded: bool = False) -> List[GoCQProcess]:
        return [
            cls.create_instance(account, predefined=True)
            for account in plugin_config.ACCOUNTS
            if not ignore_loaded or account.uin not in cls._processes
        ]

    @classmethod
    async def load_saved(
        cls,
        save_path: Path = ACCOUNTS_SAVE_PATH,
        ignore_loaded: bool = False,
    ) -> List[GoCQProcess]:
        try:
            async with await open_file(save_path, "rb") as f:
                compressed = await f.read()
            decompressed = zlib.decompress(compressed)
            store = parse_obj_as(ProcessAccountsStore, pickle.loads(decompressed))
        except Exception as e:
            raise RuntimeError(
                f"Failed to load saved accounts from {save_path!r}"
            ) from e
        return [
            cls.create_instance(account)
            for account in store.accounts
            if not ignore_loaded or account.uin not in cls._processes
        ]

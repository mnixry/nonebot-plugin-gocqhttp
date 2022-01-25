from typing import Dict

from nonebot import get_driver

import nonebot_plugin_gocqhttp.plugin  # noqa:F401

from .log import logger
from .plugin_config import config
from .process import GoCQProcess
from .process.download import BINARY_PATH, download_gocq

PROCESSES: Dict[int, GoCQProcess] = {}

driver = get_driver()


@driver.on_startup
async def startup():
    if config.FORCE_DOWNLOAD or not BINARY_PATH.is_file():
        await download_gocq()

    for account in config.ACCOUNTS:
        logger.info(f"Starting GoCQ process for <e>{account.uin}</e>")
        process = GoCQProcess(account)
        PROCESSES[account.uin] = process
        await process.start()

    return


@driver.on_shutdown
async def shutdown():
    for uin, process in PROCESSES.items():
        try:
            await process.stop()
        except RuntimeError:
            pass
    return

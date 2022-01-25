import asyncio

from fastapi import FastAPI
from nonebot import get_driver
from nonebot.drivers import ReverseDriver

from .log import logger
from .plugin_config import config
from .process import REGISTERED_PROCESSES, GoCQProcess
from .process.download import BINARY_PATH, download_gocq
from .web.routes import app

driver = get_driver()

if isinstance(driver, ReverseDriver) and isinstance(driver.asgi, FastAPI):
    driver.asgi.mount("/go-cqhttp", app)
else:
    raise NotImplementedError("Support for FastAPI is only available.")


@driver.on_startup
async def startup():
    if config.FORCE_DOWNLOAD or not BINARY_PATH.is_file():
        await download_gocq()

    for account in config.ACCOUNTS:
        logger.info(f"Starting GoCQ process for <e>{account.uin}</e>")
        process = GoCQProcess(account)
        await process.start()

    return


@driver.on_shutdown
async def shutdown():
    await asyncio.gather(
        *map(lambda process: process.stop(), REGISTERED_PROCESSES.values()),
        return_exceptions=True,
    )
    return


from . import plugin  # noqa: F401,E402

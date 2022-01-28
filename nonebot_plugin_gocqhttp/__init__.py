import asyncio

from fastapi import FastAPI
from nonebot import get_driver
from nonebot.drivers import ReverseDriver

from . import plugin  # noqa: F401
from .plugin_config import config
from .process import BINARY_DIR, BINARY_PATH, ProcessesManager, download_gocq
from .web import app

driver = get_driver()

if isinstance(driver, ReverseDriver) and isinstance(driver.asgi, FastAPI):
    driver.asgi.mount("/go-cqhttp", app)
else:
    raise NotImplementedError("Support for FastAPI is only available.")

ACCOUNTS_DATA = BINARY_DIR / "accounts.pkl"


@driver.on_startup
async def startup():
    if config.FORCE_DOWNLOAD or not BINARY_PATH.is_file():
        await download_gocq()

    ProcessesManager.load_config()
    if ACCOUNTS_DATA.is_file():
        await ProcessesManager.load_saved(ACCOUNTS_DATA, ignore_loaded=True)

    await asyncio.gather(
        *map(lambda process: process.start(), ProcessesManager.all()),
        return_exceptions=True,
    )
    return


@driver.on_shutdown
async def shutdown():
    await ProcessesManager.save(ACCOUNTS_DATA)

    await asyncio.gather(
        *map(lambda process: process.stop(), ProcessesManager.all()),
        return_exceptions=True,
    )
    return

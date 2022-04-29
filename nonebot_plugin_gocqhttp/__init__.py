import asyncio

from fastapi import FastAPI
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter
from nonebot.drivers import ReverseDriver
from nonebot.log import default_filter, default_format

from . import plugin, web  # noqa: F401
from .log import LOG_STORAGE, logger
from .plugin_config import config
from .process import (
    ACCOUNTS_SAVE_PATH,
    BINARY_PATH,
    ProcessesManager,
    download_gocq,
    kill_duplicated_processes,
)

driver = get_driver()

if (adapter_name := Adapter.get_name()) not in driver._adapters:
    raise ValueError(f"Adapter {adapter_name!r} is not registered yet.")
if not isinstance(driver, ReverseDriver) or not isinstance(driver.server_app, FastAPI):
    raise NotImplementedError("Only FastAPI reverse driver is supported.")

driver.server_app.mount("/go-cqhttp", web.app, name="go-cqhttp plugin")


@driver.on_startup
async def startup():
    loop = asyncio.get_running_loop()

    def log_sink(message: str):
        asyncio.run_coroutine_threadsafe(
            LOG_STORAGE.add(message.rstrip("\n")), loop=loop
        )

    logger.add(log_sink, colorize=True, filter=default_filter, format=default_format)

    if config.FORCE_DOWNLOAD or not BINARY_PATH.is_file():
        await download_gocq()

    await kill_duplicated_processes()

    ProcessesManager.load_config()
    if ACCOUNTS_SAVE_PATH.is_file():
        await ProcessesManager.load_saved(ignore_loaded=True)

    await asyncio.gather(
        *map(lambda process: process.start(), ProcessesManager.all()),
        return_exceptions=True,
    )

    if web.DIST_PATH.is_dir():
        logger.info(
            "Startup complete, Web UI has served to "
            f"<u><e>http://127.0.0.1:{driver.config.port}/go-cqhttp/</e></u>"
        )

    return


@driver.on_shutdown
async def shutdown():
    await ProcessesManager.save()

    await asyncio.gather(
        *map(lambda process: process.stop(), ProcessesManager.all()),
        return_exceptions=True,
    )
    return

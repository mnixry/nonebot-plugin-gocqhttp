import asyncio

from fastapi import FastAPI
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Adapter
from nonebot.drivers import ReverseDriver
from nonebot.log import default_filter, default_format

import nonebot_plugin_gocqhttp.plugin  # noqa: F401
from nonebot_plugin_gocqhttp import web
from nonebot_plugin_gocqhttp.log import LOG_STORAGE, logger
from nonebot_plugin_gocqhttp.plugin_config import config
from nonebot_plugin_gocqhttp.process import (
    ACCOUNTS_LEGACY_SAVE_PATH,
    ACCOUNTS_SAVE_PATH,
    BINARY_PATH,
    ProcessesManager,
    download_gocq,
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
        loop.create_task(LOG_STORAGE.add(message.rstrip("\n")))

    logger.add(log_sink, colorize=True, filter=default_filter, format=default_format)

    if config.FORCE_DOWNLOAD or not BINARY_PATH.is_file():
        await download_gocq()

    ProcessesManager.load_config()

    if ACCOUNTS_SAVE_PATH.is_file():
        await ProcessesManager.load_saved(
            ACCOUNTS_SAVE_PATH, is_dumps=False, ignore_loaded=True
        )
    elif ACCOUNTS_LEGACY_SAVE_PATH.is_file():
        logger.warning("Legacy accounts data detected, converting...")
        await ProcessesManager.load_saved(
            ACCOUNTS_LEGACY_SAVE_PATH, is_dumps=True, ignore_loaded=True
        )
        await ProcessesManager.save()  # update to new format

    await asyncio.gather(
        *map(lambda process: process.start(), ProcessesManager.all()),
        return_exceptions=True,
    )

    if tunnel_port := config.TUNNEL_PORT:
        try:
            from .external_proxy import ProxyServiceManager

            await ProxyServiceManager.start(tunnel_port)
        except ImportError as e:
            logger.opt(colors=True).error(
                "Tunnel configured but required dependencies missing: "
                f"<r><b>{e}</b></r>"
            )

    logger.info(
        "Startup complete, Web UI has served to "
        f"<u><e>http://{driver.config.host}:{driver.config.port}/go-cqhttp/</e></u>"
    )


@driver.on_shutdown
async def shutdown():
    await asyncio.gather(
        *map(lambda process: process.stop(), ProcessesManager.all()),
        return_exceptions=True,
    )

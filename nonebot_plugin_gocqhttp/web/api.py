import os
import shutil
from typing import Any, Dict, List, Optional, cast

import psutil
from fastapi import APIRouter, Depends
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import ActionFailed, Bot
from nonebot.utils import escape_tag, run_sync
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from ..exceptions import BotNotFound, ProcessNotFound, RemovePredefinedAccount
from ..log import LOG_STORAGE, logger
from ..plugin_config import AccountConfig
from ..process import GoCQProcess, ProcessesManager, ProcessInfo, ProcessLog
from ..process.device.models import DeviceInfo
from . import models

router = APIRouter(tags=["api"])


def RunningProcess():
    async def dependency(uin: int):
        process = ProcessesManager.get(uin)
        if not process:
            raise ProcessNotFound
        return process

    return Depends(dependency)


@router.get("/accounts", response_model=List[models.AccountListItem])
async def all_accounts():
    return [
        models.AccountListItem(
            uin=process.account.uin,
            predefined=process.predefined,
            process_created=not not process.process,
        )
        for process in ProcessesManager.all()
    ]


@router.get("/status", response_model=models.SystemStatus)
def system_status():
    virtual_memory = psutil.virtual_memory()._asdict()
    disk_usage = psutil.disk_usage(path=os.getcwd())._asdict()
    process = psutil.Process()
    with process.oneshot():
        cpu_percent = process.cpu_percent()
        process_memory = process.memory_info()
        process_start_time = process.create_time()
        status = process.status()
    return models.SystemStatus(
        cpu_percent=psutil.cpu_percent(),
        memory=models.SystemMemoryDetail(**virtual_memory),
        disk=models.SystemDiskDetail(**disk_usage),
        boot_time=psutil.boot_time(),
        process=models.RunningProcessDetail(
            pid=process.pid,
            cpu_percent=cpu_percent,
            status=status,
            memory_used=process_memory.rss,
            start_time=process_start_time,
        ),
    )


@router.get("/logs", response_model=List[str])
async def system_logs_history(reverse: bool = False):
    return LOG_STORAGE.list(reverse=reverse)


@router.websocket("/logs")
async def system_logs_realtime(websocket: WebSocket):
    await websocket.accept()

    async def log_listener(log: str):
        await websocket.send_text(log)

    LOG_STORAGE.listeners.add(log_listener)
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            recv = await websocket.receive()
            logger.trace(
                f"{system_logs_realtime.__name__!r} received "
                f"<e>{escape_tag(repr(recv))}</e>"
            )
    except WebSocketDisconnect:
        pass
    finally:
        LOG_STORAGE.listeners.remove(log_listener)
    return


@router.put(
    "/{uin}",
    response_model=AccountConfig,
    response_model_exclude={"config"},
    status_code=201,
)
async def create_account(uin: int, account: Optional[models.AccountCreation] = None):
    process = ProcessesManager.create_instance(
        account=AccountConfig(uin=uin, **account.dict() if account else {})
    )
    await ProcessesManager.save()
    return process.account


@router.delete("/{uin}", status_code=204)
async def delete_account(
    with_file: bool = False, process: GoCQProcess = RunningProcess()
):
    if process.predefined:
        raise RemovePredefinedAccount

    await process.stop()
    if with_file:
        await run_sync(shutil.rmtree)(process.cwd)
    ProcessesManager.remove(process.account.uin)

    await ProcessesManager.save()


@router.get("/{uin}/config", response_model=models.AccountConfigFile)
def account_config_read(process: GoCQProcess = RunningProcess()):
    return models.AccountConfigFile(content=process.config.read())


@router.patch("/{uin}/config", response_model=models.AccountConfigFile)
def account_config_write(
    data: models.AccountConfigFile, process: GoCQProcess = RunningProcess()
):
    process.config.write(data.content)
    return models.AccountConfigFile(content=process.config.read())


@router.delete("/{uin}/config", status_code=204)
def account_config_delete(process: GoCQProcess = RunningProcess()):
    process.config.generate()


@router.get("/{uin}/device", response_model=DeviceInfo)
def account_device_read(process: GoCQProcess = RunningProcess()):
    return process.device.read()


@router.patch("/{uin}/device", response_model=DeviceInfo)
def account_device_write(data: DeviceInfo, process: GoCQProcess = RunningProcess()):
    process.device.write(data)
    return process.device.read()


@router.delete("/{uin}/device", status_code=204)
def account_device_delete(process: GoCQProcess = RunningProcess()):
    process.device.generate()


@router.post("/{uin}/api")
async def account_api(
    name: str, params: Dict[str, Any], process: GoCQProcess = RunningProcess()
):
    bot = next(
        (
            bot
            for bot in get_bots().values()
            if isinstance(bot, Bot) and bot.self_id.endswith(f"{process.account.uin}")
        ),
        None,
    )
    if not bot:
        raise BotNotFound
    try:
        result = await cast(Bot, bot).call_api(name, **params)
    except ActionFailed as e:
        result = e.info
    return result


@router.put("/{uin}/process", response_model=ProcessInfo, status_code=201)
async def process_start(process: GoCQProcess = RunningProcess()):
    await process.start()
    return await process.status()


@router.delete("/{uin}/process", status_code=204)
async def process_stop(process: GoCQProcess = RunningProcess()):
    await process.stop()


@router.get("/{uin}/process/status", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()):
    return await process.status()


@router.get("/{uin}/process/logs", response_model=List[ProcessLog])
async def process_logs_history(
    reverse: bool = False,
    process: GoCQProcess = RunningProcess(),
):
    return process.logs.list(reverse=reverse)


@router.post("/{uin}/process/logs", status_code=204)
async def process_input_line(
    content: models.StdinInputContent,
    process: GoCQProcess = RunningProcess(),
):
    assert process.process and process.process.stdin
    input_ = (content.input + os.linesep) if content.linesep else content.input
    process.process.stdin.write(input_)


@router.websocket("/{uin}/process/logs")
async def process_logs_realtime(
    websocket: WebSocket,
    process: GoCQProcess = RunningProcess(),
):
    await websocket.accept()

    async def log_listener(log: ProcessLog):
        await websocket.send_text(log.json())

    process.logs.listeners.add(log_listener)
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            recv = await websocket.receive()
            logger.trace(
                f"{process_logs_realtime.__name__!r} received "
                f"<e>{escape_tag(repr(recv))}</e>"
            )
    except WebSocketDisconnect:
        pass
    finally:
        process.logs.listeners.remove(log_listener)
    return

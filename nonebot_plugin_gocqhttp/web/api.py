from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import ActionFailed, Bot
from nonebot.utils import escape_tag
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from ..log import logger
from ..plugin_config import AccountConfig, AccountProtocol
from ..process import (
    GoCQProcess,
    ProcessAccount,
    ProcessesManager,
    ProcessInfo,
    ProcessLog,
)

router = APIRouter(tags=["api"])


class AccountCreation(BaseModel):
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.iPad
    config_extra: Optional[Dict[str, Any]] = None
    device_extra: Optional[Dict[str, Any]] = None


def RunningProcess():
    async def dependency(uin: int):
        process = ProcessesManager.get(uin)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    return Depends(dependency)


@router.get("/", response_model=List[int])
async def all_accounts():
    return [process.account.uin for process in ProcessesManager.all()]


@router.put(
    "/{uin}",
    response_model=ProcessAccount,
    response_model_exclude={"config"},
    status_code=201,
)
async def create_account(uin: int, account: Optional[AccountCreation] = None):
    process = ProcessesManager.create(
        account=AccountConfig(uin=uin, **account.dict() if account else {})
    )
    return process.account


@router.delete("/{uin}", status_code=204)
async def delete_account(process: GoCQProcess = RunningProcess()):
    await ProcessesManager.remove(process.account.uin)
    return


@router.get("/{uin}/device")
async def account_device(process: GoCQProcess = RunningProcess()):
    return process.account.device


@router.post("/{uin}/api")
async def account_api(
    name: str, params: Dict[str, Any], process: GoCQProcess = RunningProcess()
):
    bot = next(
        (
            bot
            for bot in get_bots().values()
            if bot.self_id.endswith(f"{process.account.uin}")
        ),
        None,
    )
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
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
    return


@router.get("/{uin}/process/status", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()):
    return await process.status()


@router.get("/{uin}/process/logs", response_model=List[ProcessLog])
async def process_logs_history(
    reverse: bool = False,
    process: GoCQProcess = RunningProcess(),
):
    return process.logs.list(reverse=reverse)


@router.websocket("/{uin}/process/logs")
async def process_logs_realtime(
    websocket: WebSocket,
    process: GoCQProcess = RunningProcess(),
):
    await websocket.accept()

    async def log_listener(log: ProcessLog):
        await websocket.send_text(log.json())

    process.log_listeners.add(log_listener)
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            recv = await websocket.receive()
            logger.trace(f"Websocket received <e>{escape_tag(repr(recv))}</e>")
    except WebSocketDisconnect:
        pass
    finally:
        process.log_listeners.remove(log_listener)
    return

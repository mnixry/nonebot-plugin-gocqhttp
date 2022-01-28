from typing import List

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from nonebot_plugin_gocqhttp.process.models import ProcessAccount

from ..process import GoCQProcess, ProcessesManager, ProcessInfo, ProcessLog

app = FastAPI()


def RunningProcess():
    async def dependency(uin: int):
        process = ProcessesManager.get(uin)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    return Depends(dependency)


@app.get("/", response_model=List[int])
async def all_processes():
    return [process.account.uin for process in ProcessesManager.all()]


@app.put("/{uin}", response_model=ProcessAccount)
async def create_process(account: ProcessAccount):
    process = ProcessesManager.create(account)
    return process.account


@app.get("/{uin}/status", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()):
    return await process.status()


@app.get("/{uin}/device")
async def process_device(process: GoCQProcess = RunningProcess()):
    return process.account.device


@app.get("/{uin}/logs/history", response_model=List[ProcessLog])
async def process_logs_history(
    reverse: bool = False,
    process: GoCQProcess = RunningProcess(),
):
    return process.logs.list(reverse=reverse)


@app.websocket("/{uin}/logs/realtime")
async def process_logs_realtime(
    websocket: WebSocket,
    process: GoCQProcess = RunningProcess(),
):
    await websocket.accept()

    async def log_listener(log: ProcessLog):
        await websocket.send_text(log.json())

    process.log_listeners.add(log_listener)
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        await websocket.close()
    finally:
        process.log_listeners.remove(log_listener)
    return


@app.delete("/{uin}/process", status_code=204)
async def process_stop(process: GoCQProcess = RunningProcess()):
    await process.stop()
    return


@app.put("/{uin}/process", status_code=201)
async def process_start(process: GoCQProcess = RunningProcess()):
    await process.start()
    return

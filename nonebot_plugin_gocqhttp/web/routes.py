from typing import List

from fastapi import Depends, FastAPI, HTTPException

from ..process import REGISTERED_PROCESSES, GoCQProcess
from ..process.models import ProcessInfo
from ..process.device.models import ShortDeviceInfo

app = FastAPI()


def RunningProcess():
    async def dependency(uin: int):
        process = REGISTERED_PROCESSES.get(uin)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    return Depends(dependency)


@app.get("/", response_model=list)
async def all_processes():
    return [*REGISTERED_PROCESSES.keys()]


@app.get("/{uin}/status", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    return await process.status()


@app.get("/{uin}/device")
async def process_device(process: GoCQProcess = RunningProcess()):
    return process.account.device_extra


@app.delete("/{uin}/", response_model=ProcessInfo)
async def process_stop(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    await process.stop()
    return await process.status()

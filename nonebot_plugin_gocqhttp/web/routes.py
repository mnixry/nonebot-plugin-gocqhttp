from typing import List

from fastapi import Depends, FastAPI, HTTPException

from ..process import GoCQProcess, ProcessesManager, ProcessInfo

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


@app.get("/{uin}/status", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    return await process.status()


@app.get("/{uin}/device")
async def process_device(process: GoCQProcess = RunningProcess()):
    return process.account.device


@app.delete("/{uin}/", response_model=ProcessInfo)
async def process_stop(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    await process.stop()
    return await process.status()

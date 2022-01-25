from fastapi import Depends, FastAPI, HTTPException

from ..process import REGISTERED_PROCESSES, GoCQProcess
from ..process.models import ProcessInfo

app = FastAPI()


def RunningProcess():
    async def dependency(uin: int):
        process = REGISTERED_PROCESSES.get(uin)
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")
        return process

    return Depends(dependency)


@app.get("/")
async def all_processes():
    return [*REGISTERED_PROCESSES.keys()]


@app.get("/{uin}/", response_model=ProcessInfo)
async def process_status(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    return await process.status()


@app.delete("/{uin}/", response_model=ProcessInfo)
async def process_stop(process: GoCQProcess = RunningProcess()) -> ProcessInfo:
    await process.stop()
    return await process.status()

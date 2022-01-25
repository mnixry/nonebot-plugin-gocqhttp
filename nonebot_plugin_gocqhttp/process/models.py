from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class ProcessLog(BaseModel):
    raw: str
    time: datetime = Field(default_factory=datetime.now)
    level: Optional[str] = None
    message: Optional[str] = None


class ProcessStatus(str, Enum):
    running = "running"
    stopped = "stopped"


class RunningProcessDetail(BaseModel):
    pid: int
    status: str
    memory_used: int
    swap_used: int
    cpu_percent: float
    start_time: float


class StoppedProcessDetail(BaseModel):
    code: int


class ProcessInfo(BaseModel):
    status: ProcessStatus
    total_logs: int
    restarts: int
    details: Union[RunningProcessDetail, StoppedProcessDetail]

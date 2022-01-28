from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, SecretStr

from ..log import STDOUT


class ProcessAccount(BaseModel):
    uin: int
    password: Optional[SecretStr] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    device: Dict[str, Any] = Field(default_factory=dict)


class ProcessLogLevel(str, Enum):
    STDOUT = STDOUT.name

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class ProcessLog(BaseModel):
    time: datetime = Field(default_factory=datetime.now)
    level: ProcessLogLevel = ProcessLogLevel.STDOUT
    message: str


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

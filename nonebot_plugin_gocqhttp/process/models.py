from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, SecretStr

from ..log import STDOUT
from ..plugin_config import AccountConfig


class ProcessAccount(BaseModel):
    source: AccountConfig
    uin: int
    password: Optional[SecretStr] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    device: Dict[str, Any] = Field(default_factory=dict)


class ProcessAccountsStore(BaseModel):
    accounts: List[AccountConfig]
    created_at: datetime = Field(default_factory=datetime.now)


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
    cpu_percent: float
    start_time: float


class StoppedProcessDetail(BaseModel):
    code: int


class ProcessInfo(BaseModel):
    status: ProcessStatus
    total_logs: int
    restarts: int
    qr_uri: Optional[str] = None
    details: Union[RunningProcessDetail, StoppedProcessDetail]

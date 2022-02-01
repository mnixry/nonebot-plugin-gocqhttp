from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..plugin_config import AccountProtocol
from ..process import RunningProcessDetail


class AccountListItem(BaseModel):
    uin: int
    predefined: bool = False
    process_created: bool = False


class AccountCreation(BaseModel):
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.iPad
    config_extra: Optional[Dict[str, Any]] = None
    device_extra: Optional[Dict[str, Any]] = None


class SystemMemoryDetail(BaseModel):
    total: int
    available: int
    percent: float


class SystemDiskDetail(BaseModel):
    total: int
    free: int
    percent: float


class SystemStatus(BaseModel):
    cpu_percent: float
    memory: SystemMemoryDetail
    disk: SystemDiskDetail
    boot_time: float
    process: RunningProcessDetail

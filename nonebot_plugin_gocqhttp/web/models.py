from typing import Optional

from pydantic import BaseModel

from ..plugin_config import AccountProtocol
from ..process import RunningProcessDetail


class AccountListItem(BaseModel):
    uin: int
    predefined: bool
    process_created: bool
    process_running: bool
    process_connected: bool
    nickname: Optional[str] = None


class AccountCreation(BaseModel):
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.iPad


class AccountConfigFile(BaseModel):
    content: str


class SessionTokenFile(BaseModel):
    base64_content: str


class StdinInputContent(BaseModel):
    input: str
    linesep: bool = True


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

from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from nonebot import get_driver
from nonebot.adapters.onebot.v11.config import Config as OnebotConfig
from nonebot.config import Config as BaseConfig
from pydantic import BaseModel, Field

driver = get_driver()

DEFAULT_DOWNLOAD_URL = (
    "https://download.fastgit.org/"
    "{repo}/releases/{version}/download/go-cqhttp_{goos}_{goarch}{ext}"
)


class AccountProtocol(IntEnum):
    iPad = 0
    AndroidPhone = 1
    AndroidWatch = 2
    MacOS = 3
    QiDian = 4


ExtraConfigType = Union[Dict[str, Any], str]


class AccountConfig(BaseModel):
    uin: int
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.iPad
    config_extra: Optional[ExtraConfigType] = None
    device_extra: Optional[ExtraConfigType] = None


class PluginConfig(BaseConfig):
    ACCOUNTS: List[AccountConfig] = Field(default_factory=list, alias="gocq_accounts")
    DOWNLOAD_REPO: str = Field("Mrs4s/go-cqhttp", alias="gocq_repo")
    DOWNLOAD_VERSION: str = Field("latest", alias="gocq_version")
    DOWNLOAD_URL: str = Field(DEFAULT_DOWNLOAD_URL, alias="gocq_url")

    FORCE_DOWNLOAD: bool = Field(False, alias="gocq_force_download")
    PROCESS_RESTARTS: int = Field(-1, alias="gocq_process_restarts")


driver_config = driver.config
onebot_config = OnebotConfig.parse_obj(driver_config.dict())
config = PluginConfig.parse_obj(driver_config.dict())

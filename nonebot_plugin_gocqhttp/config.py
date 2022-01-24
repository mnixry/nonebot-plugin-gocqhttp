from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

from nonebot import get_driver
from nonebot.config import Config
from pydantic import Field

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


class AccountConfig(Config):
    uin: int
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.iPad
    config_extra: Optional[ExtraConfigType] = None
    device_extra: Optional[ExtraConfigType] = None


class PluginConfig(Config):
    ACCOUNTS: List[AccountConfig] = Field(default_factory=list, env="gocq_accounts")
    DOWNLOAD_REPO: str = Field("Mrs4s/go-cqhttp", env="gocq_repo")
    DOWNLOAD_VERSION: str = Field("latest", env="gocq_version")
    DOWNLOAD_URL: str = Field(DEFAULT_DOWNLOAD_URL, env="gocq_url")
    FORCE_DOWNLOAD: bool = Field(False, env="gocq_force_download")


driver_config = driver.config
config = PluginConfig.parse_obj(driver_config.dict())

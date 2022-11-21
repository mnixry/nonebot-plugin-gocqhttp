from enum import IntEnum
from typing import Any, Dict, List, Optional

from nonebot import get_driver
from nonebot.adapters.onebot.v11.config import Config as OnebotConfig
from pydantic import BaseModel, Field, HttpUrl

driver = get_driver()


class AccountProtocol(IntEnum):
    Default = 0
    AndroidPhone = 1
    AndroidWatch = 2
    MacOS = 3
    QiDian = 4
    iPad = 5


class AccountConfig(BaseModel):
    uin: int
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.Default


class PluginConfig(BaseModel):
    ACCOUNTS: List[AccountConfig] = Field(default_factory=list, alias="gocq_accounts")

    DOWNLOAD_DOMAINS: List[str] = Field(
        [
            "ghdown.obfs.dev",  # Download mirror over Cloudflare worker
            "download.fgit.ml",  # Download mirror provided by FastGit
            "github.com",  # Official GitHub download
        ],
        alias="gocq_download_domains",
    )

    DOWNLOAD_REPO: str = Field("Mrs4s/go-cqhttp", alias="gocq_repo")
    DOWNLOAD_VERSION: Optional[str] = Field(None, alias="gocq_version")
    DOWNLOAD_URL: Optional[HttpUrl] = Field(None, alias="gocq_url")
    FORCE_DOWNLOAD: bool = Field(False, alias="gocq_force_download")

    PROCESS_KWARGS: Dict[str, Any] = Field(
        default_factory=dict, alias="gocq_process_kwargs"
    )

    WEBUI_USERNAME: Optional[str] = Field(None, alias="gocq_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="gocq_webui_password")

    TUNNEL_PORT: Optional[int] = Field(None, alias="gocq_tunnel_port")


driver_config = driver.config
onebot_config = OnebotConfig.parse_obj(driver_config.dict())
config = PluginConfig.parse_obj(driver_config.dict())

from enum import IntEnum
from typing import Any, Dict, List, Literal, Optional, Union

from nonebot import get_driver
from nonebot.adapters.onebot.v11.config import Config as OnebotConfig
from pydantic import BaseModel, Field, FilePath, HttpUrl

driver = get_driver()


class AccountProtocol(IntEnum):
    Default = 0
    AndroidPhone = 1
    AndroidWatch = 2
    MacOS = 3
    QiDian = 4
    iPad = 5
    aPad = 6


class AccountConfig(BaseModel):
    uin: int
    password: Optional[str] = None
    protocol: AccountProtocol = AccountProtocol.Default


class PluginConfig(BaseModel):
    ACCOUNTS: List[AccountConfig] = Field(default_factory=list, alias="gocq_accounts")

    DOWNLOAD_DOMAINS: List[str] = Field(
        [
            "ghdown.obfs.dev",  # Download mirror over Cloudflare worker
            "download.fgit.ml",
            "download.fgit.gq",  # Download mirror provided by FastGit
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
    PROCESS_EXECUTABLE: Optional[Union[Literal["@PATH"], FilePath]] = Field(
        None, alias="gocq_process_executable"
    )

    WEBUI_USERNAME: Optional[str] = Field(None, alias="gocq_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="gocq_webui_password")

    CONFIG_TEMPLATE_PATH: Optional[str] = Field(None, alias="gocq_config_template_path")

    TUNNEL_PORT: Optional[int] = Field(None, alias="gocq_tunnel_port")

    MUTE_ACCESS_LOG: bool = Field(True, alias="gocq_mute_access_log")


driver_config = driver.config
onebot_config = OnebotConfig.parse_obj(driver_config.dict())
config = PluginConfig.parse_obj(driver_config.dict())

import json
from pathlib import Path

import chevron
from nonebot_plugin_gocqhttp.exceptions import BadConfigFormat

from ..plugin_config import AccountConfig, driver_config, onebot_config
from .device import DeviceInfo, random_device
from .download import ACCOUNTS_DATA_PATH


class AccountConfigHelper:
    CONFIG_TEMPLATE_PATH = Path(__file__).parent / "config-template.yml"

    TEMPLATE_FILE_NAME = "config-template.yml"
    CONFIG_FILE_NAME = "config.yml"

    def __init__(self, account: AccountConfig):
        self.account = account
        self.account_path = ACCOUNTS_DATA_PATH / str(account.uin)
        self.account_path.mkdir(parents=True, exist_ok=True)

        self.template_path = self.account_path / self.TEMPLATE_FILE_NAME
        self.config_path = self.account_path / self.CONFIG_FILE_NAME

    @property
    def exists(self):
        return self.config_path.is_file() and self.template_path.is_file()

    def read(self) -> str:
        return self.template_path.read_text(encoding="utf-8")

    def write(self, content: str) -> int:
        return self.template_path.write_text(content, encoding="utf-8")

    def generate(self):
        return self.template_path.write_text(
            self.CONFIG_TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def before_run(self):
        template_string = self.read()
        rendered_string = chevron.render(
            template_string,
            data={
                "account": self.account,
                "server_address": f"ws://127.0.0.1:{driver_config.port}/onebot/v11/ws",
                "access_token": onebot_config.onebot_access_token or "",
            },
        )
        return self.config_path.write_text(rendered_string, encoding="utf-8")


class AccountDeviceHelper:
    DEVICE_FILE_NAME = "device.json"

    def __init__(self, account: AccountConfig):
        self.account = account
        self.account_path = ACCOUNTS_DATA_PATH / str(account.uin)
        self.account_path.mkdir(parents=True, exist_ok=True)

        self.device_path = self.account_path / self.DEVICE_FILE_NAME

    @property
    def exists(self):
        return self.device_path.is_file()

    def read(self) -> DeviceInfo:
        with self.device_path.open("rt", encoding="utf-8") as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError as e:
                raise BadConfigFormat(BadConfigFormat.message + str(e)) from None
        return DeviceInfo.parse_obj(content)

    def write(self, content: DeviceInfo) -> int:
        return self.device_path.write_text(
            content.json(indent=4, ensure_ascii=False), encoding="utf-8"
        )

    def generate(self):
        generated_device = random_device(self.account.uin, self.account.protocol)
        return self.write(generated_device)

    def before_run(self):
        device_content = self.read()
        device_content.protocol = self.account.protocol
        return self.write(device_content)

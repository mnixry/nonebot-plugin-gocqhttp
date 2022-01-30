import json
from pathlib import Path
from typing import Any, Callable, Dict

import yaml

from ..log import logger
from ..plugin_config import AccountConfig, ExtraConfigType, driver_config, onebot_config
from .device import random_device

CONFIG_TEMPLATE_PATH = Path(__file__).parent / "config-template.yml"
CONFIG_REF_PREFIX, CONFIG_OVERRIDE_PREFIX = "ref:", "override:"


def merge_config(
    template: Dict[str, Any], extra_config: Dict[str, Any]
) -> Dict[str, Any]:
    template = template.copy()
    for key, value in extra_config.items():
        if isinstance(template.get(key), dict) and isinstance(value, dict):
            template[key] = merge_config(template[key], value)
        elif isinstance(template.get(key), list) and isinstance(value, list):
            template[key] = (template[key] + value).copy()
        else:
            template[key] = value
    return template


def load_extra_config(
    template: Dict[str, Any],
    extra_config: ExtraConfigType,
    loader: Callable[[str], Any],
) -> Dict[str, Any]:
    if isinstance(extra_config, dict):
        return merge_config(template, extra_config)
    elif isinstance(extra_config, str):
        if extra_config.startswith(CONFIG_REF_PREFIX):
            path, override = extra_config[len(CONFIG_REF_PREFIX) :], False
        elif extra_config.startswith(CONFIG_OVERRIDE_PREFIX):
            path, override = extra_config[len(CONFIG_OVERRIDE_PREFIX) :], True
        else:
            raise ValueError(f"Invalid extra config setting: {extra_config!r}")
        if not Path(path).is_file():
            raise ValueError(f"Extra config file not found: {path!r}")

        with open(path, "rt", encoding="utf-8") as f:
            loaded_config = loader(f.read())
        return loaded_config if override else merge_config(template, loaded_config)

    raise TypeError(f"Invalid extra config type: {extra_config.__class__!r}")


def generate_config(account: AccountConfig, account_path: Path):
    config_path = account_path / "config.yml"
    with CONFIG_TEMPLATE_PATH.open("rt", encoding="utf-8") as f:
        config_template = yaml.safe_load(f)

    config_template["account"]["uin"] = account.uin
    config_template["account"]["password"] = account.password
    config_template["servers"][0]["ws-reverse"].update(
        {
            "universal": f"ws://127.0.0.1:{driver_config.port}/onebot/v11/ws",
            "api": None,
            "event": None,
            "middlewares": {"access-token": onebot_config.onebot_access_token or ""},
        },
    )

    loaded_config = (
        load_extra_config(config_template, account.config_extra, yaml.safe_load)
        if account.config_extra is not None
        else config_template
    )

    with config_path.open("wt", encoding="utf-8") as f:
        yaml.safe_dump(loaded_config, f, default_flow_style=False)
    logger.debug(f"Config file for account {account.uin} generated.")

    return loaded_config


def generate_device(account: AccountConfig, account_path: Path):
    device_path = account_path / "device.json"
    device_template = random_device(account.uin, account.protocol).dict()

    loaded_device = (
        load_extra_config(device_template, account.device_extra, json.loads)
        if account.device_extra is not None
        else device_template
    )

    with device_path.open("wt", encoding="utf-8") as f:
        json.dump(loaded_device, f, indent=4, ensure_ascii=False)
    logger.debug(f"Device file for account {account.uin} generated.")

    return loaded_device

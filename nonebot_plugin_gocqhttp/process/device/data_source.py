from csv import DictReader
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

BUILDS_DIR = Path(__file__).parent / "android_builds.csv"
DEVICES_DIR = Path(__file__).parent / "android_devices.csv"


class AndroidDevice(BaseModel):
    branding: str
    name: str
    device: str
    model: str


class AndroidBuild(BaseModel):
    android_id: str
    version: str


@lru_cache
def load_devices_list(path: Path = DEVICES_DIR):
    with path.open("rt", encoding="utf-8") as f:
        reader = DictReader(f)
        devices = [AndroidDevice(**row) for row in reader]
    return [
        device
        for device in devices
        if (device.branding and device.name and device.device and device.model)
    ]


@lru_cache
def load_builds_list(path: Path = BUILDS_DIR):
    with path.open("rt", encoding="utf-8") as f:
        reader = DictReader(f)
        builds = [AndroidBuild(**row) for row in reader]
    return builds

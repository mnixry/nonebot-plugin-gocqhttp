import hashlib
from typing import List

from pydantic import BaseModel, Field

from ...plugin_config import AccountProtocol


class VersionInfo(BaseModel):
    incremental: str
    release: str = "10"
    codename: str = "REL"
    sdk: int = 29


class ShortDeviceInfo(BaseModel):
    product: str
    device: str
    board: str
    brand: str
    model: str
    wifi_ssid: str
    android_id: str
    boot_id: str
    proc_version: str
    mac_address: str
    ip_address: List[int] = Field(max_items=4, min_items=4)
    imei: str
    incremental: str = ""

    protocol: AccountProtocol


class DeviceInfo(ShortDeviceInfo):
    display: str
    finger_print: str
    proc_version: str
    baseband: str = ""
    sim: str = "T-Mobile"
    sim_info: str = "T-Mobile"
    os_type: str = "android"
    bootloader: str = "U-boot"
    wifi_bssid: str
    wifi_ssid: str
    apn: str = "wifi"
    version: VersionInfo
    imsi_md5: str
    vendor_name: str
    vendor_os_name: str = "android"

    @classmethod
    def from_short(cls, short: ShortDeviceInfo, **extra):
        extra.update(short.dict())
        return cls(
            display=short.android_id,
            finger_print=(
                f"{short.brand}/{short.product}/{short.device}:10/"
                f"{short.android_id}/{short.incremental}:user/release-keys"
            ),
            wifi_bssid=short.mac_address,
            version=VersionInfo(incremental=short.incremental),
            imsi_md5=hashlib.md5(short.imei.encode()).hexdigest(),
            vendor_name=short.brand,
            **extra,
        )

from ...plugin_config import AccountProtocol
from .generator import RandomDeviceInfoGenerator
from .models import DeviceInfo, ShortDeviceInfo


def random_device(uin: int, protocol: AccountProtocol) -> DeviceInfo:
    randomer = RandomDeviceInfoGenerator(uin)

    imei, ssid = randomer.imei(), randomer.ssid()
    android_id, device = randomer.android_device()
    boot_id, proc_version = randomer.boot_id(), randomer.proc_version()
    mac_address, ip_address = randomer.mac_address(), randomer.ip_address()
    incremental = randomer.incremental()

    short = ShortDeviceInfo(
        product=device.name,
        device=device.device,
        board=device.device,
        brand=device.branding,
        model=device.model,
        wifi_ssid=ssid,
        android_id=android_id,
        boot_id=boot_id,
        proc_version=proc_version,
        mac_address=mac_address,
        ip_address=ip_address,
        imei=imei,
        incremental=incremental,
        protocol=protocol,
    )

    return DeviceInfo.from_short(short)

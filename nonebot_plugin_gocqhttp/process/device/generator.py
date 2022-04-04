from ipaddress import IPv4Address, IPv4Network
from random import Random
from string import ascii_letters, ascii_uppercase, digits, hexdigits
from uuid import UUID

from .data_source import load_builds_list, load_devices_list


class RandomDeviceInfoGenerator:
    def __init__(self, uin: int) -> None:
        self.seed = uin

    @staticmethod
    def rand_str(random: Random, charset: str, length: int):
        return "".join(random.choice(charset) for _ in range(length))

    def imei(self) -> str:
        random = Random(self.seed)
        pre = self.rand_str(random, digits, 14)

        def checksum(number: str):
            n = len(digits)
            numbers = tuple(digits.index(i) for i in reversed(str(number)))
            return str(
                (sum(numbers[::2]) + sum(i * 2 // n + i % n for i in numbers[1::2])) % n
            )

        return f"{pre}{checksum(pre)}"

    def ssid(self, prefix: str = "TP-LINK_") -> str:
        random = Random(self.seed)
        return prefix + self.rand_str(random, ascii_uppercase + digits, 6)

    def android_device(self):
        random = Random(self.seed)
        return (
            random.choice(load_builds_list()).android_id,
            random.choice(load_devices_list()),
        )

    def boot_id(self) -> str:
        random = Random(self.seed)
        uuid = UUID(self.rand_str(random, hexdigits, 32))
        return str(uuid)

    def proc_version(self) -> str:
        random = Random(self.seed)

        major_version = random.randint(3, 5)
        minor_version = random.randint(0, 19)
        patch_version = random.randint(0, 99)
        build_id = self.rand_str(random, ascii_letters + digits, 8)
        version = f"{major_version}.{minor_version}.{patch_version}-{build_id}"

        mail_domain = (
            self.rand_str(random, hexdigits, 12).lower() + ".source.android.com"
        )

        return f"Linux version {version} (android-build@{mail_domain})"

    def mac_address(self) -> str:
        random = Random(self.seed)
        return ":".join(self.rand_str(random, hexdigits, 2) for _ in range(6)).upper()

    def ip_address(self, network: IPv4Network = IPv4Network("188.0.0.0/8")):
        random = Random(self.seed)

        address = IPv4Address(
            random.randint(
                int(network.network_address),
                int(network.broadcast_address),
            )
        )
        return [int(i) for i in str(address).split(".")]

    def incremental(self):
        random = Random(self.seed)
        return str(random.randint(0, 2**32))

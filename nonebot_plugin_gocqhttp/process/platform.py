import platform

import psutil
from cpuinfo import get_cpu_info

_SYSTEM_MAP = {
    "Windows": "windows",
    "Linux": "linux",
    "Darwin": "darwin",
}

_ARCHITECTURE_MAP = {
    "X86_32": "386",
    "X86_64": "amd64",
    "ARM_7": "armv7",
    "ARM_8": "arm64",
}


def _get_platform():
    try:
        system = _SYSTEM_MAP[platform.system()]
        architecture = _ARCHITECTURE_MAP[get_cpu_info()["arch"]]
    except KeyError:
        raise RuntimeError(f"Unsupported platform: {platform.uname()!r}") from None
    return system, architecture


GOOS, GOARCH = _get_platform()

ARCHIVE_EXT = ".zip" if psutil.WINDOWS else ".tar.gz"
EXECUTABLE_EXT = ".exe" if psutil.WINDOWS else ""

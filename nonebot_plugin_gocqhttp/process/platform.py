import platform

_ARCHITECTURE_MAP = {
    # For Windows, it uses PROCESSOR_ARCHITECTURE environment variable. Reference:
    # https://docs.microsoft.com/en-us/windows/win32/winprog64/wow64-implementation-details#environment-variables
    # https://github.com/python/cpython/blob/main/Lib/platform.py#L717-L727
    "Windows": {
        "AMD64": "amd64",
        "X86": "386",
        "ARM64": "arm64",
    },
    # For Unix-like system, it follows os.uname result. Reference:
    # https://en.wikipedia.org/wiki/Uname
    "Linux": {
        "x86_64": "amd64",
        "i686": "386",
        "i386": "386",
        "aarch64": "arm64",
        "armv7l": "armv7",
    },
    "Darwin": {
        "x86_64": "amd64",
        "arm64": "arm64",
    },
}

_SYSTEM_MAP = {
    "Windows": "windows",
    "Linux": "linux",
    "Darwin": "darwin",
}


def _get_platform():
    uname = platform.uname()
    try:
        system = _SYSTEM_MAP[uname.system]
        architecture = _ARCHITECTURE_MAP[uname.system][uname.machine]
    except KeyError:
        raise RuntimeError(
            f"Unsupported platform: {uname.system} {uname.machine}"
        ) from None
    return system, architecture


GOOS, GOARCH = _get_platform()

ARCHIVE_EXT = ".zip" if GOOS == "windows" else ".tar.gz"
EXECUTABLE_EXT = ".exe" if GOOS == "windows" else ""

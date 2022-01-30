import hashlib
import shutil
from base64 import b64decode
from contextlib import AsyncExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

from anyio import open_file
from httpx import AsyncClient
from nonebot.utils import run_sync

from ..log import logger
from ..plugin_config import config
from .platform import ARCHIVE_EXT, EXECUTABLE_EXT, GOARCH, GOOS

DOWNLOAD_URL = config.DOWNLOAD_URL.format(
    repo=config.DOWNLOAD_REPO,
    version=config.DOWNLOAD_VERSION,
    goos=GOOS,
    goarch=GOARCH,
    ext=ARCHIVE_EXT,
)

ACCOUNTS_DATA_PATH = Path(".") / "accounts"
BINARY_DIR = ACCOUNTS_DATA_PATH / "binary"
BINARY_PATH = BINARY_DIR / ("go-cqhttp" + EXECUTABLE_EXT)


@run_sync
def unarchive_file(path: Path):
    try:
        shutil.unpack_archive(path, extract_dir=BINARY_DIR)
    except:  # noqa: E722
        shutil.rmtree(BINARY_DIR)
        raise
    assert BINARY_PATH.exists(), "go-cqhttp binary not found"


@logger.catch(reraise=True)
async def download_gocq():
    async with AsyncExitStack() as stack:
        tmpdir = stack.enter_context(TemporaryDirectory())
        download_path = Path(tmpdir) / ("temp" + ARCHIVE_EXT)
        BINARY_DIR.mkdir(parents=True, exist_ok=True)

        logger.info(f"Begin to Download binary from <u>{DOWNLOAD_URL}</u>")

        client = await stack.enter_async_context(AsyncClient(follow_redirects=True))
        response = await stack.enter_async_context(client.stream("GET", DOWNLOAD_URL))
        response.raise_for_status()

        total_size, size = int(response.headers["Content-Length"]), 0
        content_md5 = b64decode(response.headers["Content-MD5"]).hex()
        hasher = hashlib.md5()

        file = await stack.enter_async_context(await open_file(download_path, "wb"))
        async for chunk in response.aiter_bytes():
            size += await file.write(chunk)
            hasher.update(chunk)
            logger.trace(
                "Download progress: "
                f"{size/total_size:.2%} ({size}/{total_size} bytes)"
            )

        if size != total_size:
            raise RuntimeError(f"Download size mismatch: {size}/{total_size} bytes")
        elif hasher.hexdigest().casefold() != content_md5.casefold():
            raise RuntimeError("Download content MD5 validation failed!")

        logger.debug(f"Unarchive binary file to <e>{BINARY_PATH!r}</e>")
        await unarchive_file(download_path)
    return

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


def construct_download_url() -> str:
    return config.DOWNLOAD_URL or (
        f"https://{config.DOWNLOAD_DOMAIN}/"
        + f"{config.DOWNLOAD_REPO}/releases/"
        + (
            f"download/{config.DOWNLOAD_VERSION}/"
            if config.DOWNLOAD_VERSION
            else "latest/download/"
        )
        + f"go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}"
    )


@logger.catch(reraise=True)
async def download_gocq():
    async with AsyncExitStack() as stack:
        tmpdir = stack.enter_context(TemporaryDirectory())
        download_path = Path(tmpdir) / ("temp" + ARCHIVE_EXT)
        BINARY_DIR.mkdir(parents=True, exist_ok=True)

        client = await stack.enter_async_context(AsyncClient(follow_redirects=True))

        url = construct_download_url()
        logger.info(f"Begin to Download binary from <u>{url}</u>")
        response = await stack.enter_async_context(client.stream("GET", url))
        response.raise_for_status()

        total_size, downloaded_size = int(response.headers["Content-Length"]), 0
        content_md5 = b64decode(response.headers["Content-MD5"]).hex().casefold()
        hasher = hashlib.md5()

        async with await open_file(download_path, "wb") as file:
            async for chunk in response.aiter_bytes():
                downloaded_size += await file.write(chunk)
                hasher.update(chunk)
                logger.trace(
                    f"Download progress: {downloaded_size/total_size:.2%} "
                    f"({downloaded_size}/{total_size} bytes)"
                )

        if downloaded_size != total_size:
            raise RuntimeError(
                f"Downloaded size mismatch: {downloaded_size}/{total_size} bytes"
            )
        elif (file_size := download_path.stat().st_size) != total_size:
            raise RuntimeError(
                f"Downloaded file size mismatch: {file_size}/{total_size} bytes"
            )
        elif (actual_md5 := hasher.hexdigest().casefold()) != content_md5:
            raise RuntimeError(
                f"Content MD5 validation failed! "
                f"Expected: {content_md5} "
                f"Actual: {actual_md5}"
            )

        logger.debug(f"Unarchive binary file to <e>{BINARY_PATH}</e>")
        await unarchive_file(download_path)
    return

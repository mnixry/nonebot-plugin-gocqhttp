import asyncio
import hashlib
import shutil
import time
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


def construct_download_url(domain: str) -> str:
    return config.DOWNLOAD_URL or (
        f"https://{domain}/{config.DOWNLOAD_REPO}/releases/"
        + (
            f"download/{config.DOWNLOAD_VERSION}/"
            if config.DOWNLOAD_VERSION
            else "latest/download/"
        )
        + f"go-cqhttp_{GOOS}_{GOARCH}{ARCHIVE_EXT}"
    )


async def get_fastest_mirror(client: AsyncClient):
    if config.DOWNLOAD_URL:
        logger.debug("Download URL has been overridden, skip speed checking.")
        return config.DOWNLOAD_URL

    assert config.DOWNLOAD_DOMAINS, "No download domain specified."

    async def head_mirror(client: AsyncClient, domain: str):
        begin_time = time.time()

        response = await client.head(url := construct_download_url(domain), timeout=6)
        response.raise_for_status()

        elapsed_time = (time.time() - begin_time) * 1000
        content_length = int(response.headers["content-length"])
        content_md5 = b64decode(response.headers["content-md5"]).hex().casefold()

        return url, elapsed_time, content_length, content_md5

    results = zip(
        config.DOWNLOAD_DOMAINS,
        await asyncio.gather(
            *(head_mirror(client, domain) for domain in config.DOWNLOAD_DOMAINS),
            return_exceptions=True,
        ),
    )

    lowest_latency, fastest_url = None, None

    for domain, result in results:
        if isinstance(result, BaseException):
            logger.opt(colors=True).debug(
                f"<r>Failed to check</r> speed of {domain!r}: {result!r}"
            )
            continue

        url, elapsed_time, content_length, content_md5 = result
        logger.debug(
            f"Checked latency of {url} in {elapsed_time:.2f}ms, "
            f"content length: {content_length}, content md5: {content_md5}"
        )

        if lowest_latency is None or elapsed_time < lowest_latency:
            fastest_url = url
            lowest_latency = elapsed_time

    assert lowest_latency and fastest_url, "No download domain available."

    return fastest_url


@logger.catch(reraise=True)
async def download_gocq():
    async with AsyncExitStack() as stack:
        tmpdir = stack.enter_context(TemporaryDirectory())
        download_path = Path(tmpdir) / ("temp" + ARCHIVE_EXT)
        BINARY_DIR.mkdir(parents=True, exist_ok=True)

        client: AsyncClient = await stack.enter_async_context(
            AsyncClient(follow_redirects=True)  # type:ignore
        )  # NOTE: see https://github.com/encode/httpx/pull/2096

        url = await get_fastest_mirror(client)

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
                f"Downloaded file md5 mismatch: {actual_md5=} {content_md5=}"
            )

        logger.debug(f"Unarchive binary file to <e>{BINARY_PATH}</e>")
        await unarchive_file(download_path)
    return

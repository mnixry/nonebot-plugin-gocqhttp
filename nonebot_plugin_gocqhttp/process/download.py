import asyncio
import hashlib
import shutil
import time
from base64 import b64decode
from pathlib import Path
from tempfile import mktemp
from typing import List

from anyio import open_file
from httpx import AsyncClient
from nonebot.utils import run_sync

from nonebot_plugin_gocqhttp.log import logger
from nonebot_plugin_gocqhttp.plugin_config import config
from nonebot_plugin_gocqhttp.process.platform import (
    ARCHIVE_EXT,
    EXECUTABLE_EXT,
    GOARCH,
    GOOS,
)

ACCOUNTS_DATA_PATH = Path(".") / "accounts"
BINARY_DIR = ACCOUNTS_DATA_PATH / "binary"
BINARY_PATH = BINARY_DIR / f"go-cqhttp{EXECUTABLE_EXT}"


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


async def get_fastest_mirror(client: AsyncClient) -> List[str]:
    assert config.DOWNLOAD_DOMAINS, "No download domain specified."

    async def head_mirror(client: AsyncClient, domain: str):
        begin_time = time.time()

        response = await client.head(url := construct_download_url(domain), timeout=6)
        response.raise_for_status()

        elapsed_time = (time.time() - begin_time) * 1000
        content_length = int(response.headers["content-length"])
        content_md5 = b64decode(response.headers["content-md5"]).hex().casefold()

        return {
            "domain": domain,
            "url": url,
            "elapsed_time": elapsed_time,
            "content_length": content_length,
            "content_md5": content_md5,
        }

    results = await asyncio.gather(
        *(head_mirror(client, domain) for domain in config.DOWNLOAD_DOMAINS),
        return_exceptions=True,
    )
    results = sorted(
        (result for result in results if not isinstance(result, Exception)),
        key=lambda r: r["elapsed_time"],
    )
    return [result["url"] for result in results]


async def download_and_extract_binary(client: AsyncClient, url: str):
    async with await open_file(
        download_path := Path(mktemp(suffix=ARCHIVE_EXT)), "wb"
    ) as file, client.stream("GET", url) as response:
        response.raise_for_status()

        total_size, transfer_size = int(response.headers["Content-Length"]), 0
        content_md5 = b64decode(response.headers["Content-MD5"]).hex().casefold()
        hasher = hashlib.md5()

        async for chunk in response.aiter_bytes():
            transfer_size += await file.write(chunk)
            hasher.update(chunk)
            logger.trace(
                f"Download progress: {transfer_size/total_size:.2%} "
                f"({transfer_size}/{total_size} bytes)"
            )

    if transfer_size != total_size:
        raise RuntimeError(f"Transferred size mismatch: {transfer_size}/{total_size}")
    elif (file_size := download_path.stat().st_size) != total_size:
        raise RuntimeError(f"Downloaded size mismatch: {file_size}/{total_size}")
    elif (actual_md5 := hasher.hexdigest()) != content_md5:
        raise RuntimeError(f"Downloaded md5 mismatch: {actual_md5=} {content_md5=}")

    logger.debug(f"Extracting binary file to <e>{BINARY_PATH}</e>")
    await unarchive_file(download_path)


async def download_gocq():
    BINARY_DIR.mkdir(parents=True, exist_ok=True)
    async with AsyncClient(follow_redirects=True) as client:
        available_urls = (
            [config.DOWNLOAD_URL]
            if config.DOWNLOAD_URL
            else await get_fastest_mirror(client)
        )
        if not available_urls:
            raise RuntimeError("No available download mirror found.")
        for index, url in enumerate(available_urls):
            logger.info(f"Begin to Download binary from <u>{url}</u>")
            try:
                await download_and_extract_binary(client, url)
                break
            except Exception as e:
                logger.opt(exception=e).warning(
                    f"Failed to download from <u>{url}</u>, trying next mirror:"
                )
                if index == len(available_urls) - 1:
                    raise RuntimeError("No available download mirror found.") from None
    return

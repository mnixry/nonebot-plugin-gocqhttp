import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from anyio import open_file
from httpx import AsyncClient
from nonebot.utils import run_sync
from tqdm import tqdm

from ..log import logger
from ..plugin_config import config
from .config import ACCOUNTS_DATA_PATH
from .platform import ARCHIVE_EXT, EXECUTABLE_EXT, GOARCH, GOOS

DOWNLOAD_URL = config.DOWNLOAD_URL.format(
    repo=config.DOWNLOAD_REPO,
    version=config.DOWNLOAD_VERSION,
    goos=GOOS,
    goarch=GOARCH,
    ext=ARCHIVE_EXT,
)

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
    with tqdm(leave=False) as progress, TemporaryDirectory() as tmpdir:
        logger.debug(f"Begin to Download go-cqhttp from <u>{DOWNLOAD_URL}</u>")
        download_path = Path(tmpdir) / ("temp" + ARCHIVE_EXT)
        BINARY_DIR.mkdir(parents=True, exist_ok=True)
        async with (
            AsyncClient(follow_redirects=True, http2=True) as client,
            client.stream("GET", DOWNLOAD_URL) as response,
            await open_file(download_path, "wb") as file,
        ):
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            progress.total = total_size
            progress.clear()
            progress.update()
            async for chunk in response.aiter_bytes():
                size = await file.write(chunk)
                progress.update(size)
        logger.debug(f"Unarchive go-cqhttp binary file to <e>{BINARY_PATH!r}</e>")
        await unarchive_file(download_path)
    return

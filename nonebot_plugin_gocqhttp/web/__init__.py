import secrets
from importlib.metadata import version
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from ..exceptions import PluginGoCQException
from ..plugin_config import config as plugin_config
from .api import router as api_router

DIST_PATH = Path(__file__).parent / "dist"

if not DIST_PATH.is_dir():
    raise FileNotFoundError("WebUI dist directory not found")


async def security_dependency(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
):
    assert plugin_config.WEBUI_USERNAME and plugin_config.WEBUI_PASSWORD
    if not (
        secrets.compare_digest(credentials.username, plugin_config.WEBUI_USERNAME)
        and secrets.compare_digest(credentials.password, plugin_config.WEBUI_PASSWORD)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


app = FastAPI(
    title="nonebot-plugin-gocqhttp",
    description="go-cqhttp process manager API",
    dependencies=(
        [Depends(security_dependency)]
        if plugin_config.WEBUI_PASSWORD and plugin_config.WEBUI_USERNAME
        else []
    ),
    version=version("nonebot-plugin-gocqhttp"),
)


@app.exception_handler(PluginGoCQException)
async def handle_plugin_exception(request: Request, exc: PluginGoCQException):
    return JSONResponse(content={"detail": exc.message}, status_code=exc.code)


app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(api_router, prefix="/api")


app.mount("/", StaticFiles(directory=DIST_PATH, html=True), name="frontend")

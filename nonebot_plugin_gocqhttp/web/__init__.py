from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..exceptions import PluginGoCQException
from .api import router as api_router

DIST_PATH = Path(__file__).parent / "dist"

app = FastAPI(
    title="nonebot-plugin-gocqhttp",
    description="go-cqhttp process manager API",
)


@app.exception_handler(PluginGoCQException)
async def handle_plugin_exception(request: Request, exc: PluginGoCQException):
    return JSONResponse(content={"detail": exc.message}, status_code=exc.code)


app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(api_router, prefix="/api")

app.mount("/", StaticFiles(directory=DIST_PATH, html=True), name="frontend")

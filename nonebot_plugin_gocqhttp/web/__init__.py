from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router as api_router

DIST_PATH = Path(__file__).parent / "dist"

app = FastAPI(
    title="nonebot-plugin-gocqhttp",
    description="go-cqhttp process manager API",
)

app.include_router(api_router, prefix="/api")

app.mount("/", StaticFiles(directory=DIST_PATH, html=True), name="frontend")

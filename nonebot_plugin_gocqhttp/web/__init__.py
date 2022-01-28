from fastapi import FastAPI

from .api import router as api_router

app = FastAPI(
    title="nonebot-plugin-gocqhttp",
    description="go-cqhttp process manager API",
)
app.include_router(api_router, prefix="/api")

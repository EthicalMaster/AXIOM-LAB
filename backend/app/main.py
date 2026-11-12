"""AXIOM LAB ASGI application — Phase 01A dataset import."""
from fastapi import FastAPI

from app.api.datasets import router as dataset_router
from app.api.health import router as health_router

app = FastAPI(
    title="AXIOM LAB API",
    description="Scientific computing API. Phase 01B: dataset import and conservative column profiling.",
    version="0.1.0",
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(dataset_router, prefix="/api/v1")

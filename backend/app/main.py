"""AXIOM LAB ASGI application — foundation only."""
from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="AXIOM LAB API",
    description="Scientific computing API. Phase 0 exposes only a health check.",
    version="0.0.1",
)
app.include_router(health_router, prefix="/api/v1")

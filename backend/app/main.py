"""AXIOM LAB ASGI application — through Phase 02B distribution analysis."""
from fastapi import FastAPI

from app.api.datasets import router as dataset_router
from app.api.health import router as health_router
from app.api.statistics import router as statistics_router
from app.api.experiments import router as experiment_router
from app.api.quality import router as quality_router
from app.api.distributions import router as distribution_router

from app.api.hypothesis import router as hypothesis_router

from app.api.diagnostics import router as diagnostics_router

from app.api.mathematics import router as mathematics_router

app = FastAPI(
    title="AXIOM LAB API",
    description="Scientific computing API: import, column profiling, descriptive statistics, persisted chart runs, source quality and distributions.",
    version="0.1.0",
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(dataset_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(experiment_router, prefix="/api/v1")
app.include_router(quality_router, prefix="/api/v1")
app.include_router(distribution_router, prefix="/api/v1")

app.include_router(hypothesis_router, prefix="/api/v1")

app.include_router(diagnostics_router, prefix="/api/v1")

app.include_router(mathematics_router, prefix="/api/v1")

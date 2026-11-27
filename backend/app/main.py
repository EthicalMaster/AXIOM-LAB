"""AXIOM LAB ASGI application — bounded local-first scientific engine through 05A."""
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
from app.api.ml import router as ml_router

app = FastAPI(title='AXIOM LAB API',
              description='Bounded scientific computation, data inspection and local experiment records.',
              version='0.1.0')

for router in (health_router, dataset_router, statistics_router, experiment_router,
               quality_router, distribution_router, hypothesis_router, diagnostics_router,
               mathematics_router, ml_router):
    app.include_router(router, prefix='/api/v1')

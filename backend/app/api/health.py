"""Operational health is not a scientific correctness check."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    phase: str
    scientific_engine: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", phase="01A", scientific_engine="not_implemented")

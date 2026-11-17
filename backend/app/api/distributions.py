"""Scientific dataset distribution endpoint, read-only and bounded."""
from __future__ import annotations
import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset
from app.services.dataset_validation import DatasetValidationError
from app.services.distributions import distribution

router = APIRouter(prefix='/datasets', tags=['distributions'])

class HistogramBin(BaseModel):
    lower: float
    upper: float
    count: int
    percent: float

class DistributionResponse(BaseModel):
    dataset_id: str
    column: str
    method: str
    count: int
    missing_count: int
    minimum: float
    maximum: float
    median: float
    q1: float
    q3: float
    bin_count: int
    bins: list[HistogramBin]
    outlier_count: int | None
    outlier_method: str
    warnings: list[str]
    note: str

@router.get('/{dataset_id}/distribution', response_model=DistributionResponse)
def get_distribution(dataset_id: str, column: str = Query(min_length=1, max_length=200)) -> DistributionResponse:
    if not re.fullmatch(r'[0-9a-f]{32}', dataset_id):
        raise HTTPException(404, detail='Dataset not found')
    metadata = find_dataset(dataset_id)
    if metadata is None:
        raise HTTPException(404, detail='Dataset not found')
    try:
        raw = read_original_dataset(dataset_id, metadata)
        return DistributionResponse(dataset_id=dataset_id, **distribution(raw, '.'+metadata['format'], column))
    except DatasetStorageError as exc:
        raise HTTPException(409, detail={'code':'dataset_integrity_error','message':str(exc)}) from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code':exc.code,'message':exc.message}) from exc

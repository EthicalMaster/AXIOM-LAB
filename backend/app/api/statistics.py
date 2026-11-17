"""Read-only descriptive statistics for stored, integrity-checked datasets."""
from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset
from app.services.dataset_validation import DatasetValidationError
from app.services.descriptive_statistics import dataset_statistics

router = APIRouter(prefix='/datasets', tags=['statistics'])


class ColumnStatistics(BaseModel):
    column: str
    count: int
    missing_count: int
    mean: float
    median: float
    minimum: float
    maximum: float
    q1: float
    q3: float
    iqr: float
    population_variance: float
    population_stddev: float
    sample_variance: float | None
    sample_stddev: float | None
    notes: list[str]


class StatisticsResponse(BaseModel):
    dataset_id: str
    method: str
    row_count: int
    columns: list[ColumnStatistics]
    note: str


@router.get('/{dataset_id}/statistics', response_model=StatisticsResponse)
def get_statistics(dataset_id: str) -> StatisticsResponse:
    if not re.fullmatch(r'[0-9a-f]{32}', dataset_id):
        raise HTTPException(404, detail='Dataset not found')
    metadata = find_dataset(dataset_id)
    if metadata is None:
        raise HTTPException(404, detail='Dataset not found')
    try:
        raw = read_original_dataset(dataset_id, metadata)
        return StatisticsResponse(dataset_id=dataset_id, **dataset_statistics(raw, '.' + metadata['format']))
    except DatasetStorageError as exc:
        raise HTTPException(409, detail={'code': 'dataset_integrity_error', 'message': str(exc)}) from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

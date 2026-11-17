"""Read-only quality summary computed from verified immutable source data."""
from __future__ import annotations
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset
from app.services.data_quality import data_quality
from app.services.dataset_validation import DatasetValidationError

router = APIRouter(prefix='/datasets', tags=['quality'])

class ColumnQuality(BaseModel):
    column: str
    inferred_type: str
    missing_count: int
    present_count: int
    missing_percent: float
    warnings: list[str]

class QualityReport(BaseModel):
    dataset_id: str
    method: str
    row_count: int
    column_count: int
    missing_cells: int
    total_cells: int
    completeness_percent: float
    duplicate_rows: int
    duplicate_count_exact: bool
    unique_rows_tracked: int
    columns: list[ColumnQuality]
    warnings: list[str]
    note: str

@router.get('/{dataset_id}/quality', response_model=QualityReport)
def get_quality(dataset_id: str) -> QualityReport:
    if not re.fullmatch(r'[0-9a-f]{32}', dataset_id):
        raise HTTPException(404, detail='Dataset not found')
    metadata = find_dataset(dataset_id)
    if metadata is None:
        raise HTTPException(404, detail='Dataset not found')
    try:
        raw = read_original_dataset(dataset_id, metadata)
        return QualityReport(dataset_id=dataset_id, **data_quality(raw, '.' + metadata['format']))
    except DatasetStorageError as exc:
        raise HTTPException(409, detail={'code':'dataset_integrity_error','message':str(exc)}) from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code':exc.code,'message':exc.message}) from exc

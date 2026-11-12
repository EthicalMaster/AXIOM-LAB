"""Phase 01A dataset import and metadata lookup API."""
from __future__ import annotations

import logging
import re

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.persistence.dataset_store import find_dataset, save_dataset
from app.services.dataset_validation import (
    MAX_FILE_BYTES, DatasetValidationError, safe_filename, validate_dataset,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])


class DatasetMetadata(BaseModel):
    id: str
    original_name: str
    format: str
    sha256: str
    size_bytes: int
    uploaded_at: str
    row_count: int
    column_count: int
    headers: list[str]
    worksheet: str | None
    sheet_names: list[str]
    warnings: list[str]


class ImportedDataset(DatasetMetadata):
    preview: list[list[str | None]]


@router.post("/import", response_model=ImportedDataset, status_code=201)
async def import_dataset(file: UploadFile = File(...)) -> ImportedDataset:
    try:
        filename, suffix = safe_filename(file.filename)
        # Read only one byte beyond the configured upper bound.
        raw = await file.read(MAX_FILE_BYTES + 1)
        profile = validate_dataset(raw, suffix)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={"code": exc.code, "message": exc.message}) from exc
    finally:
        await file.close()
    metadata = save_dataset(raw, filename, suffix, profile)
    logger.info("dataset_imported id=%s format=%s rows=%s", metadata["id"], profile.file_format, profile.row_count)
    return ImportedDataset(**metadata, preview=profile.preview)


@router.get("/{dataset_id}", response_model=DatasetMetadata)
def get_dataset(dataset_id: str) -> DatasetMetadata:
    if not re.fullmatch(r"[0-9a-f]{32}", dataset_id):
        raise HTTPException(404, detail="Dataset not found")
    record = find_dataset(dataset_id)
    if record is None:
        raise HTTPException(404, detail="Dataset not found")
    return DatasetMetadata(**record)

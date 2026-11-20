"""Shared resolution of immutable dataset bytes for read-only computational routes."""
from __future__ import annotations

import re
from fastapi import HTTPException
from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset


def load_dataset(dataset_id: str) -> tuple[bytes, str, dict]:
    if not re.fullmatch(r'[0-9a-f]{32}', dataset_id):
        raise HTTPException(404, detail='Dataset not found')
    metadata = find_dataset(dataset_id)
    if metadata is None:
        raise HTTPException(404, detail='Dataset not found')
    try:
        return read_original_dataset(dataset_id, metadata), '.' + metadata['format'], metadata
    except DatasetStorageError as exc:
        raise HTTPException(409, detail={'code': 'dataset_integrity_error', 'message': str(exc)}) from exc

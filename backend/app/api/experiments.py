"""Controlled, recorded chart experiment from immutable source bytes."""
from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset
from app.persistence.experiment_store import create_experiment, read_experiment
from app.services.dataset_validation import DatasetValidationError
from app.services.experiment_visualization import sequence_chart

router = APIRouter(prefix='/experiments', tags=['experiments'])


class CreateExperiment(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    dataset_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    column: str = Field(min_length=1, max_length=200)


class Point(BaseModel):
    x: int
    y: float


class Chart(BaseModel):
    method: str
    column: str
    x_label: str
    y_label: str
    original_point_count: int
    shown_point_count: int
    sampled: bool
    missing_count: int
    points: list[Point]
    note: str


class RunRecord(BaseModel):
    id: str
    created_at: str
    status: str
    method: str
    configuration: dict[str, str]
    result: Chart
    environment: dict[str, str]


class ExperimentRecord(BaseModel):
    id: str
    name: str
    dataset_id: str
    dataset_sha256: str
    created_at: str
    run: RunRecord


@router.post('', response_model=ExperimentRecord, status_code=201)
def create_new_experiment(payload: CreateExperiment) -> ExperimentRecord:
    if not payload.name.strip():
        raise HTTPException(422, detail={'code': 'invalid_name', 'message': 'An experiment requires a name.'})
    dataset = find_dataset(payload.dataset_id)
    if dataset is None:
        raise HTTPException(404, detail='Dataset not found')
    try:
        raw = read_original_dataset(payload.dataset_id, dataset)
        chart = sequence_chart(raw, '.' + dataset['format'], payload.column)
    except DatasetStorageError as exc:
        raise HTTPException(409, detail={'code': 'dataset_integrity_error', 'message': str(exc)}) from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc
    saved = create_experiment(name=payload.name.strip(), dataset_id=payload.dataset_id,
                              dataset_sha256=dataset['sha256'],
                              configuration={'column': payload.column, 'chart_kind': 'observation_sequence'},
                              result=chart)
    return ExperimentRecord(**saved)


@router.get('/{experiment_id}', response_model=ExperimentRecord)
def get_experiment(experiment_id: str) -> ExperimentRecord:
    if not re.fullmatch(r'[0-9a-f]{32}', experiment_id):
        raise HTTPException(404, detail='Experiment not found')
    result = read_experiment(experiment_id)
    if result is None:
        raise HTTPException(404, detail='Experiment not found')
    return ExperimentRecord(**result)

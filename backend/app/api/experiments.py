"""Controlled, recorded chart experiment from immutable source bytes."""
from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.persistence.dataset_store import DatasetStorageError, find_dataset, read_original_dataset
from app.persistence.experiment_store import create_experiment, read_experiment, list_experiments, list_experiment_runs, append_experiment_run, get_run
from app.services.dataset_validation import DatasetValidationError
from app.services.experiment_visualization import sequence_chart
from app.services.run_comparison import compare_runs

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
    revision: int = 1
    source_run_id: str | None = None


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


@router.get('')
def experiment_history(limit: int = Query(default=20,ge=1,le=50), offset:int=Query(default=0,ge=0,le=100000)) -> dict:
    return list_experiments(limit, offset)

@router.get('/{experiment_id}/runs')
def experiment_runs(experiment_id: str, limit:int=Query(default=20,ge=1,le=50), offset:int=Query(default=0,ge=0,le=100000)) -> dict:
    if not re.fullmatch(r'[0-9a-f]{32}', experiment_id):
        raise HTTPException(404,detail='Experiment not found')
    result=list_experiment_runs(experiment_id,limit,offset)
    if result is None:
        raise HTTPException(404,detail='Experiment not found')
    return result


class NewRun(BaseModel):
    column: str = Field(min_length=1, max_length=200)


@router.post('/{experiment_id}/runs', response_model=RunRecord, status_code=201)
def append_run(experiment_id: str, payload: NewRun) -> RunRecord:
    if not re.fullmatch(r'[0-9a-f]{32}', experiment_id):
        raise HTTPException(404, detail='Experiment not found')
    experiment = read_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(404, detail='Experiment not found')
    metadata = find_dataset(experiment['dataset_id'])
    if metadata is None or metadata['sha256'] != experiment['dataset_sha256']:
        raise HTTPException(409, detail='Experiment dataset metadata changed or vanished')
    try:
        raw = read_original_dataset(experiment['dataset_id'], metadata)
        chart = sequence_chart(raw, '.' + metadata['format'], payload.column)
    except DatasetStorageError as exc:
        raise HTTPException(409, detail='Dataset integrity failure') from exc
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code':exc.code, 'message':exc.message}) from exc
    record = append_experiment_run(experiment_id, {'column':payload.column,'chart_kind':'observation_sequence'}, chart)
    if record is None:
        raise HTTPException(404, detail='Experiment not found')
    return RunRecord(**record)


@router.get('/{experiment_id}/compare')
def compare_experiment_runs(experiment_id: str, left: str, right: str) -> dict:
    if not all(re.fullmatch(r'[0-9a-f]{32}', value) for value in (experiment_id, left, right)):
        raise HTTPException(404, detail='Run not found')
    a = get_run(experiment_id, left)
    b = get_run(experiment_id, right)
    if a is None or b is None:
        raise HTTPException(404, detail='Run not found in this experiment')
    return compare_runs(a, b)


@router.post('/{experiment_id}/runs/{run_id}/reproduce', status_code=201)
def reproduce_saved_run(experiment_id: str, run_id: str) -> dict:
    if not all(re.fullmatch(r'[0-9a-f]{32}', value) for value in (experiment_id,run_id)):
        raise HTTPException(404, detail='Run not found')
    experiment = read_experiment(experiment_id)
    saved = get_run(experiment_id,run_id)
    if experiment is None or saved is None:
        raise HTTPException(404, detail='Run not found')
    if saved['method'] != 'observation-sequence-v1' or saved['configuration'].get('chart_kind') != 'observation_sequence':
        raise HTTPException(422, detail='This run method cannot be replayed by the current engine')
    dataset = find_dataset(experiment['dataset_id'])
    if not dataset or dataset['sha256'] != experiment['dataset_sha256']:
        raise HTTPException(409, detail='Recorded dataset fingerprint no longer matches')
    try:
        raw = read_original_dataset(dataset['id'], dataset)
        computed = sequence_chart(raw, '.'+dataset['format'], saved['configuration']['column'])
    except DatasetStorageError as exc:
        raise HTTPException(409,detail='Stored dataset failed its integrity check') from exc
    except (DatasetValidationError, KeyError) as exc:
        raise HTTPException(422,detail='Saved configuration cannot be replayed') from exc
    matched = computed == saved['result']
    added = append_experiment_run(experiment_id,saved['configuration'],computed,source_run_id=run_id)
    if added is None:
        raise HTTPException(404,detail='Experiment not found')
    return {'source_run_id':run_id,'reproduced_run':added,'exact_result_match':matched,
            'note':'Exact JSON-equivalent chart result with the current code; cross-platform floating-point stability and external scientific validity are not guaranteed.'}

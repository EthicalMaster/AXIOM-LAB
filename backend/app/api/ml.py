"""Bounded model endpoints. Explicit task choice; no arbitrary estimator execution."""
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api._dataset import load_dataset
from app.services.dataset_validation import DatasetValidationError
from app.services.ml_common import preview
from app.services.ml_regression import regression
from app.services.ml_classification import classification
from app.services.ml_clustering import cluster
from app.services.ml_evaluation import compare_models

router = APIRouter(prefix='/datasets', tags=['machine-learning'])


class SupervisedRequest(BaseModel):
    task: Literal['regression', 'classification']
    features: list[str] = Field(min_length=1, max_length=8)
    target: str = Field(min_length=1, max_length=200)
    time_dependent: bool = False


class ClusterRequest(BaseModel):
    features: list[str] = Field(min_length=1, max_length=8)
    n_clusters: int = Field(default=2, ge=2, le=8)


def _run(method, raw, suffix, *args):
    try:
        return method(raw, suffix, *args)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc


def _source(dataset_id: str, request: SupervisedRequest):
    if request.time_dependent:
        raise HTTPException(422, detail={'code': 'time_aware_split_required',
                                         'message': 'Time-dependent datasets require time-aware splitting.'})
    return load_dataset(dataset_id)


@router.post('/{dataset_id}/ml/preview')
def preview_ml(dataset_id: str, request: SupervisedRequest) -> dict:
    raw, suffix, _ = _source(dataset_id, request)
    return _run(preview, raw, suffix, request.features, request.target, request.task)


@router.post('/{dataset_id}/ml/regression')
def fit_regression(dataset_id: str, request: SupervisedRequest) -> dict:
    if request.task != 'regression':
        raise HTTPException(422, detail='Choose task=regression.')
    raw, suffix, _ = _source(dataset_id, request)
    return _run(regression, raw, suffix, request.features, request.target)


@router.post('/{dataset_id}/ml/classification')
def fit_classifier(dataset_id: str, request: SupervisedRequest) -> dict:
    if request.task != 'classification':
        raise HTTPException(422, detail='Choose task=classification.')
    raw, suffix, _ = _source(dataset_id, request)
    return _run(classification, raw, suffix, request.features, request.target)


@router.post('/{dataset_id}/ml/clustering')
def fit_clustering(dataset_id: str, request: ClusterRequest) -> dict:
    raw, suffix, _ = load_dataset(dataset_id)
    return _run(cluster, raw, suffix, request.features, request.n_clusters)


@router.post('/{dataset_id}/ml/compare')
def compare_algorithms(dataset_id: str, request: SupervisedRequest) -> dict:
    raw, suffix, _ = _source(dataset_id, request)
    return _run(compare_models, raw, suffix, request.features, request.target, request.task)

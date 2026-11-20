"""Bounded supervised learning endpoints; explicit task selection and typed inputs."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from app.api._dataset import load_dataset
from app.services.dataset_validation import DatasetValidationError
from app.services.ml_common import preview

router=APIRouter(prefix='/datasets',tags=['machine-learning'])

class SupervisedRequest(BaseModel):
    task: Literal['regression','classification']
    features: list[str] = Field(min_length=1,max_length=8)
    target: str = Field(min_length=1,max_length=200)
    time_dependent: bool = False


def source(dataset_id: str, request: SupervisedRequest):
    if request.time_dependent:
        raise HTTPException(422,detail={'code':'time_aware_split_required','message':'Time-dependent data need time-aware splitting; this slice supports independent rows only.'})
    return load_dataset(dataset_id)

@router.post('/{dataset_id}/ml/preview')
def preview_ml(dataset_id:str,request:SupervisedRequest)->dict:
    raw,suffix,_=source(dataset_id,request)
    try:return preview(raw,suffix,request.features,request.target,request.task)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code,detail={'code':exc.code,'message':exc.message}) from exc

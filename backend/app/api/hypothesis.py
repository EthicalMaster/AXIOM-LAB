"""Bounded one-sample inferential test over source-verified numeric values."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.api._dataset import load_dataset
from app.services.hypothesis import one_sample_t
from app.services.dataset_validation import DatasetValidationError

router = APIRouter(prefix='/datasets', tags=['inference'])

class TestRequest(BaseModel):
    column: str = Field(min_length=1, max_length=200)
    null_mean: float = Field(allow_inf_nan=False)
    alpha: float = Field(default=0.05, ge=0.001, le=0.2)

@router.post('/{dataset_id}/hypothesis')
def hypothesis_test(dataset_id: str, request: TestRequest) -> dict:
    raw, suffix, _ = load_dataset(dataset_id)
    try:
        return one_sample_t(raw, suffix, request.column, request.null_mean, request.alpha)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

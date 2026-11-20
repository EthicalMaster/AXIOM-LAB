from fastapi import APIRouter, HTTPException, Query
from app.api._dataset import load_dataset
from app.services.diagnostics import normality_diagnostic
from app.services.dataset_validation import DatasetValidationError

router = APIRouter(prefix='/datasets', tags=['diagnostics'])

@router.get('/{dataset_id}/diagnostics')
def get_diagnostics(dataset_id: str, column: str = Query(min_length=1, max_length=200)) -> dict:
    raw, suffix, _ = load_dataset(dataset_id)
    try:
        return normality_diagnostic(raw, suffix, column)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

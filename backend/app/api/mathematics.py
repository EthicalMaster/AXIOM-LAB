"""Small controlled mathematical operations with validated typed inputs."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.safe_math import evaluate
from app.services.dataset_validation import DatasetValidationError

router = APIRouter(prefix='/math', tags=['mathematics'])

class ExpressionInput(BaseModel):
    expression: str = Field(min_length=1, max_length=120)

@router.post('/evaluate')
def evaluate_expression(request: ExpressionInput) -> dict:
    try:
        return evaluate(request.expression)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

from app.services.polynomial import polynomial_calculus

class PolynomialInput(BaseModel):
    coefficients: list[float] = Field(min_length=2, max_length=7)

@router.post('/polynomial')
def polynomial(request: PolynomialInput) -> dict:
    try:
        return polynomial_calculus(request.coefficients)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

from app.services.linear_algebra import analyse_matrix

class MatrixInput(BaseModel):
    matrix: list[list[float]] = Field(min_length=1, max_length=8)
    vector: list[float] | None = None

@router.post('/matrix')
def matrix_operations(request: MatrixInput) -> dict:
    try:
        return analyse_matrix(request.matrix, request.vector)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc

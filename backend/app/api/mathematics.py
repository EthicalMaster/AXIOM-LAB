"""Controlled mathematical endpoints. All methods accept bounded typed inputs."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.dataset_validation import DatasetValidationError
from app.services.safe_math import evaluate
from app.services.polynomial import polynomial_calculus
from app.services.linear_algebra import analyse_matrix
from app.services.numerical_methods import analyse_interval

router = APIRouter(prefix='/math', tags=['mathematics'])


def _invoke(function, *args):
    try:
        return function(*args)
    except DatasetValidationError as exc:
        raise HTTPException(exc.status_code, detail={'code': exc.code, 'message': exc.message}) from exc


class ExpressionInput(BaseModel):
    expression: str = Field(min_length=1, max_length=120)


class PolynomialInput(BaseModel):
    coefficients: list[float] = Field(min_length=2, max_length=7)


class MatrixInput(BaseModel):
    matrix: list[list[float]] = Field(min_length=1, max_length=8)
    vector: list[float] | None = None


class IntervalInput(PolynomialInput):
    lower: float = Field(allow_inf_nan=False)
    upper: float = Field(allow_inf_nan=False)


@router.post('/evaluate')
def evaluate_expression(request: ExpressionInput) -> dict:
    return _invoke(evaluate, request.expression)


@router.post('/polynomial')
def polynomial(request: PolynomialInput) -> dict:
    return _invoke(polynomial_calculus, request.coefficients)


@router.post('/matrix')
def matrix_operations(request: MatrixInput) -> dict:
    return _invoke(analyse_matrix, request.matrix, request.vector)


@router.post('/numerical')
def numerical_methods(request: IntervalInput) -> dict:
    return _invoke(analyse_interval, request.coefficients, request.lower, request.upper)

"""Bounded univariate polynomial calculus; coefficients, never arbitrary source code."""
from __future__ import annotations

import math
import numpy as np
from sympy import Poly, Symbol, Float
from app.services.dataset_validation import DatasetValidationError

X = Symbol('x')


def validate_coefficients(coefficients: list[float]) -> list[float]:
    if not 2 <= len(coefficients) <= 7 or not all(math.isfinite(v) and abs(v) <= 1e6 for v in coefficients):
        raise DatasetValidationError('invalid_polynomial', 'Use 2–7 finite coefficients within ±1,000,000, highest degree first.')
    if coefficients[0] == 0:
        raise DatasetValidationError('invalid_polynomial', 'The highest-degree coefficient must be nonzero.')
    return coefficients


def polynomial_calculus(coefficients: list[float]) -> dict:
    coeffs = validate_coefficients(coefficients)
    # Numeric coefficient arrays are converted directly; no SymPy string parser.
    polynomial = Poly.from_list([Float(v) for v in coeffs], gens=X)
    derivative = polynomial.diff()
    antiderivative = polynomial.integrate()
    roots = np.roots(np.asarray(coeffs, dtype=float))
    if not np.all(np.isfinite(roots)):
        raise DatasetValidationError('unstable_polynomial', 'Root calculation produced non-finite values.')
    return {
        'method': 'bounded-polynomial-v1', 'degree': len(coeffs) - 1,
        'polynomial': str(polynomial.as_expr()),
        'derivative': str(derivative.as_expr()),
        'antiderivative_c0': str(antiderivative.as_expr()),
        'derivative_coefficients': [float(v) for v in derivative.all_coeffs()],
        'antiderivative_coefficients': [float(v) for v in antiderivative.all_coeffs()],
        'roots_approx': [{'real': float(v.real), 'imag': float(v.imag)} for v in roots],
        'warnings': ['Roots are floating-point approximations. Multiple or poorly conditioned roots may be inaccurate.',
                     'Antiderivative uses integration constant C=0; add any constant C for the full family.'],
    }

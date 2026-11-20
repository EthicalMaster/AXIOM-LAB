"""Bounded 1D polynomial root finding and numerical quadrature."""
from __future__ import annotations

import math
from scipy.integrate import quad
from scipy.optimize import brentq
from app.services.polynomial import validate_coefficients
from app.services.dataset_validation import DatasetValidationError


def analyse_interval(coefficients: list[float], lower: float, upper: float) -> dict:
    coeff = validate_coefficients(coefficients)
    if not math.isfinite(lower) or not math.isfinite(upper) or not -100 <= lower < upper <= 100:
        raise DatasetValidationError('invalid_interval', 'Require finite increasing bounds between -100 and 100.')

    def f(x: float) -> float:
        y = 0.0
        for c in coeff:
            y = y * x + c
        if not math.isfinite(y) or abs(y) > 1e12:
            raise ValueError('Numerical range limit')
        return y

    try:
        at_lower, at_upper = f(lower), f(upper)
        root = None
        if at_lower == 0:
            root = lower
        elif at_upper == 0:
            root = upper
        elif at_lower * at_upper < 0:
            root = float(brentq(f, lower, upper, xtol=1e-10, maxiter=100))
        integral, absolute_error = quad(f, lower, upper, epsabs=1e-9, epsrel=1e-9, limit=100)
        if not all(map(math.isfinite, (integral, absolute_error))):
            raise ValueError('Integration result not finite')
        residual = abs(f(root)) if root is not None else None
        return {'method': 'brentq-and-quad-v1', 'bounds': [lower, upper],
                'root': root, 'root_residual': residual, 'integral': float(integral),
                'estimated_absolute_error': float(absolute_error),
                'warnings': [] if root is not None else ['No sign-changing bracket or endpoint zero: a root was not established; even-multiplicity roots may be missed.'],
                'note': 'Real-valued polynomial only. Integration error is a numerical estimate, not a proof.'}
    except (ValueError, OverflowError, RuntimeError) as exc:
        raise DatasetValidationError('unstable_numerical_method', 'Computation failed under interval or precision limits.') from exc

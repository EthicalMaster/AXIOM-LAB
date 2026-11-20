"""Small real square-matrix operations with explicit conditioning diagnostics."""
from __future__ import annotations

import numpy as np
from app.services.dataset_validation import DatasetValidationError


def analyse_matrix(matrix: list[list[float]], vector: list[float] | None = None) -> dict:
    if not 1 <= len(matrix) <= 8 or any(len(row) != len(matrix) for row in matrix):
        raise DatasetValidationError('invalid_matrix', 'A square real matrix of size 1–8 is required.')
    try:
        a = np.asarray(matrix, dtype=np.float64)
        if not np.all(np.isfinite(a)) or np.max(np.abs(a)) > 1e6:
            raise ValueError('Numerical limit')
        condition = float(np.linalg.cond(a))
        determinant = float(np.linalg.det(a))
        eigenvalues = np.linalg.eigvals(a)
        if not np.isfinite(determinant) or not np.all(np.isfinite(eigenvalues)):
            raise ValueError('Numerical limit')
        ill_conditioned = not np.isfinite(condition) or condition > 1e12
        inverse = None if ill_conditioned else np.linalg.inv(a).tolist()
        solution = None
        if vector is not None:
            b = np.asarray(vector, dtype=np.float64)
            if b.shape != (len(matrix),) or not np.all(np.isfinite(b)) or np.max(np.abs(b)) > 1e6:
                raise ValueError('Invalid RHS vector')
            if not ill_conditioned:
                solution = np.linalg.solve(a, b).tolist()
        return {'method': 'numpy-linear-algebra-v1', 'size': len(matrix),
                'determinant': determinant, 'rank': int(np.linalg.matrix_rank(a)),
                'condition_number': condition if np.isfinite(condition) else None,
                'inverse': inverse, 'solution': solution,
                'eigenvalues': [{'real':float(z.real),'imag':float(z.imag)} for z in eigenvalues],
                'warnings': ['Ill-conditioned or singular matrix: inverse and solution withheld.'] if ill_conditioned else [],
                'note': 'Floating-point calculations; conditioning controls whether inverse/solve results are reliable.'}
    except (ValueError, TypeError, np.linalg.LinAlgError, OverflowError) as exc:
        raise DatasetValidationError('invalid_matrix', 'Matrix shape, entries, or numerical conditioning are unsupported.') from exc

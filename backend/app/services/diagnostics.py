"""Normality diagnostic; neither independence nor a valid sampling design can be inferred."""
from __future__ import annotations

import math
import statistics
from scipy.stats import shapiro
from app.services.descriptive_statistics import numeric_series
from app.services.dataset_validation import DatasetValidationError


def normality_diagnostic(raw: bytes, suffix: str, column: str) -> dict:
    values, missing = numeric_series(raw, suffix, column)
    n = len(values)
    if n < 3:
        return {'column': column, 'method': 'shapiro-wilk-v1', 'n': n, 'missing_count': missing,
                'statistic': None, 'p_value': None, 'status': 'insufficient_sample',
                'warnings': ['Shapiro-Wilk requires at least 3 observations.'],
                'note': 'A normality check cannot verify independence or sampling validity.'}
    if n > 5000:
        return {'column': column, 'method': 'shapiro-wilk-v1', 'n': n, 'missing_count': missing,
                'statistic': None, 'p_value': None, 'status': 'unsupported_sample_size',
                'warnings': ['Shapiro-Wilk is withheld for samples above 5000: p-value calibration is uncertain.'],
                'note': 'A normality check cannot verify independence or sampling validity.'}
    if min(values) == max(values):
        return {'column': column, 'method': 'shapiro-wilk-v1', 'n': n, 'missing_count': missing,
                'statistic': None, 'p_value': None, 'status': 'constant_sample',
                'warnings': ['Constant observations provide no meaningful normality test.'],
                'note': 'A normality check cannot verify independence or sampling validity.'}
    test = shapiro(values)
    statistic, p_value = float(test.statistic), float(test.pvalue)
    if not all(map(math.isfinite, [statistic, p_value])):
        raise DatasetValidationError('numerical_overflow', 'Normality diagnostic produced a non-finite result.')
    notes = ['Failure to reject normality does not demonstrate that the distribution is normal.',
             'This test does not check independence, selection bias, or outlier relevance.']
    if missing:
        notes.append('Empty cells were excluded; assess potential missingness bias.')
    return {'column': column, 'method': 'shapiro-wilk-v1', 'n': n, 'missing_count': missing,
            'statistic': statistic, 'p_value': p_value, 'status': 'computed',
            'warnings': notes, 'note': 'Low p-values provide evidence against a normal distribution, not a proof of any alternative.'}

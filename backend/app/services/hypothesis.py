"""Explicit, two-sided one-sample Student t-test; never automates test selection."""
from __future__ import annotations

import math
import statistics
from scipy.stats import t as student_t
from app.services.descriptive_statistics import numeric_series
from app.services.dataset_validation import DatasetValidationError

METHOD = 'one-sample-student-t-v1'


def one_sample_t(raw: bytes, suffix: str, column: str, null_mean: float, alpha: float) -> dict:
    if not math.isfinite(null_mean) or not 0.001 <= alpha <= 0.2:
        raise DatasetValidationError('invalid_test_configuration', 'Null mean must be finite and alpha between 0.001 and 0.2.')
    values, missing = numeric_series(raw, suffix, column)
    n = len(values)
    if n < 2:
        raise DatasetValidationError('insufficient_sample', 'A one-sample t-test requires at least two observations.')
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    if sd == 0 or not math.isfinite(sd):
        raise DatasetValidationError('zero_variance', 'The sample has zero or non-finite variance; a t-statistic is undefined.')
    se = sd / math.sqrt(n)
    statistic = (mean - null_mean) / se
    df = n - 1
    p_value = float(2 * student_t.sf(abs(statistic), df))
    margin = float(student_t.ppf(1 - alpha / 2, df)) * se
    if not all(map(math.isfinite, [statistic, p_value, margin])):
        raise DatasetValidationError('numerical_overflow', 'Statistical result exceeded numerical precision limits.')
    notes = ['Two-sided test of H0: population mean equals the specified null mean; observations must be independent.']
    if n < 30:
        notes.append('Small sample: check approximate normality; the t-test may be unreliable with strong skew or outliers.')
    if missing:
        notes.append('Empty cells were excluded; missingness may bias conclusions.')
    return {
        'method': METHOD, 'column': column, 'n': n, 'missing_count': missing,
        'null_mean': null_mean, 'sample_mean': mean, 'sample_sd': sd,
        't_statistic': statistic, 'degrees_of_freedom': df, 'p_value': p_value,
        'alpha': alpha, 'confidence_interval': [mean - margin, mean + margin],
        'cohens_d': (mean - null_mean) / sd,
        'reject_null': p_value < alpha, 'warnings': notes,
        'note': 'p-value is the probability of results at least as extreme under H0, NOT the probability H0 is true. Noncausal inference only.',
    }

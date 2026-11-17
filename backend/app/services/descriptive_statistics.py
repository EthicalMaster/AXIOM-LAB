"""Phase 01C: explicitly defined descriptive statistics over immutable inputs.

Population variance divides by n; unbiased sample variance divides by n-1.
Quartiles follow linear interpolation at index (n-1)*p (Hyndman-Fan type 7).
Missing means empty/whitespace-only, not tokens such as NA.
"""
from __future__ import annotations

import math
import statistics
from typing import Any

from app.services.column_profiling import _source_rows, profile_columns
from app.services.dataset_validation import DatasetValidationError

METHOD_VERSION = "descriptive-v1/type7"


def quantile_type7(sorted_values: list[float], probability: float) -> float:
    """Linear interpolated quantile, p in [0,1], matching common plotting tools."""
    if not sorted_values or not 0 <= probability <= 1:
        raise ValueError("Quantile requires data and a probability within [0,1]")
    index = (len(sorted_values) - 1) * probability
    low = math.floor(index)
    high = math.ceil(index)
    weight = index - low
    return sorted_values[low] * (1 - weight) + sorted_values[high] * weight


def numeric_series(raw: bytes, suffix: str, column: str) -> tuple[list[float], int]:
    """Only allow columns whose *entire* nonempty content was inferred numeric."""
    profile = profile_columns(raw, suffix)
    matching = next((i for i, col in enumerate(profile['columns']) if col['name'] == column), None)
    if matching is None:
        raise DatasetValidationError('unknown_column', 'Select a column in this dataset.')
    if profile['columns'][matching]['inferred_type'] != 'numeric':
        raise DatasetValidationError('non_numeric_column', 'This column is not consistently numeric; no values were silently converted.')
    values: list[float] = []
    first = True
    with _source_rows(raw, suffix) as rows:
        for row in rows:
            cells = list(row)
            if not cells or all(v is None or not str(v).strip() for v in cells):
                continue
            if first:
                first = False
                continue
            value = cells[matching] if matching < len(cells) else None
            if value is None or not str(value).strip():
                continue
            number = float(value)
            if not math.isfinite(number):
                raise DatasetValidationError('non_finite', 'Non-finite numerical values cannot be analysed.')
            values.append(number)
    return values, profile['columns'][matching]['missing_count']


def describe_values(values: list[float], missing: int) -> dict[str, Any]:
    if not values:
        raise DatasetValidationError('empty_numeric_column', 'No numeric observations available.')
    ordered = sorted(values)
    n = len(values)
    try:
        mean = statistics.fmean(values)
        median = statistics.median(values)
        q1 = quantile_type7(ordered, 0.25)
        q3 = quantile_type7(ordered, 0.75)
        population_variance = statistics.pvariance(values)
        sample_variance = statistics.variance(values) if n >= 2 else None
        results = [mean, median, q1, q3, q3-q1, population_variance, min(values), max(values)]
        if sample_variance is not None:
            results.append(sample_variance)
        if not all(math.isfinite(result) for result in results):
            raise OverflowError('Non-finite statistics')
    except (OverflowError, ValueError) as exc:
        raise DatasetValidationError('numerical_overflow', 'Numerical range is too large for reliable floating-point statistics.') from exc
    notes: list[str] = []
    if n < 2:
        notes.append('Sample variance and standard deviation require at least two observations.')
    if missing:
        notes.append('Only nonempty numerical observations are included; missing values were not imputed.')
    if ordered[0] == ordered[-1]:
        notes.append('All observations have the same value; dispersion is zero.')
    return {
        'count': n, 'missing_count': missing, 'mean': mean, 'median': median,
        'minimum': ordered[0], 'maximum': ordered[-1], 'q1': q1, 'q3': q3, 'iqr': q3-q1,
        'population_variance': population_variance,
        'population_stddev': math.sqrt(population_variance),
        'sample_variance': sample_variance,
        'sample_stddev': math.sqrt(sample_variance) if sample_variance is not None else None,
        'notes': notes,
    }


def dataset_statistics(raw: bytes, suffix: str) -> dict[str, Any]:
    profile = profile_columns(raw, suffix)
    output = []
    for col in profile['columns']:
        if col['inferred_type'] == 'numeric':
            values, missing = numeric_series(raw, suffix, col['name'])
            output.append({'column': col['name'], **describe_values(values, missing)})
    return {'method': METHOD_VERSION, 'row_count': profile['row_count'], 'columns': output,
            'note': 'Descriptive measures only; no inferential claims, units or cleaning implied.'}

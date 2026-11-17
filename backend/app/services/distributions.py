"""Phase 02B: transparent bounded histogram and Tukey-style outlier indicators.

Histogram widths are uniform in source units (no probability-density claim).
The last bin includes the upper bound. Quartiles use the Phase 01C type-7 definition.
"""
from __future__ import annotations

import math

from app.services.dataset_validation import DatasetValidationError
from app.services.descriptive_statistics import describe_values, numeric_series

DISTRIBUTION_METHOD = 'histogram-sturges-v1/type7-tukey'
MAX_HISTOGRAM_BINS = 20


def histogram(values: list[float]) -> list[dict]:
    """Equal-width count bins using Sturges' heuristic capped at 20."""
    if not values:
        raise ValueError('Histogram requires at least one numeric value')
    low = min(values)
    high = max(values)
    if low == high:
        return [{'lower': low, 'upper': high, 'count': len(values), 'percent': 100.0}]
    k = min(MAX_HISTOGRAM_BINS, max(1, math.ceil(1 + math.log2(len(values)))))
    width = (high - low) / k
    if not math.isfinite(width) or width <= 0:
        raise DatasetValidationError('numerical_overflow', 'Numerical range is too wide for a reliable histogram.')
    counts = [0] * k
    for value in values:
        # Interior bins: [lower, upper); final bin: [lower, upper].
        index = min(k - 1, max(0, int((value - low) / width)))
        counts[index] += 1
    result = []
    for i, count in enumerate(counts):
        lower = low + i * width
        upper = high if i == k - 1 else low + (i+1) * width
        if not (math.isfinite(lower) and math.isfinite(upper)):
            raise DatasetValidationError('numerical_overflow', 'Histogram boundaries are not representable.')
        result.append({'lower': lower, 'upper': upper, 'count': count, 'percent': 100 * count / len(values)})
    assert sum(item['count'] for item in result) == len(values)
    return result


def distribution(raw: bytes, suffix: str, column: str) -> dict:
    values, missing = numeric_series(raw, suffix, column)
    stat = describe_values(values, missing)
    bins = histogram(values)
    warnings = []
    outliers: int | None = None
    if len(values) < 4:
        warnings.append('Fewer than four observations: outlier indicator is withheld.')
    else:
        iqr = stat['iqr']
        if iqr == 0:
            warnings.append('IQR is zero; a Tukey-fence outlier indicator can be unstable for tied/discrete values.')
        lower_fence = stat['q1'] - 1.5 * iqr
        upper_fence = stat['q3'] + 1.5 * iqr
        if not all(map(math.isfinite, (lower_fence, upper_fence))):
            raise DatasetValidationError('numerical_overflow', 'Outlier bounds are not representable.')
        outliers = sum(v < lower_fence or v > upper_fence for v in values)
    if missing:
        warnings.append('Missing cells were excluded from counts, and no imputation occurred.')
    if stat['minimum'] == stat['maximum']:
        warnings.append('Constant column: histogram has one zero-width category at the observed value.')
    return {
        'column': column, 'method': DISTRIBUTION_METHOD,
        'count': len(values), 'missing_count': missing,
        'minimum': stat['minimum'], 'maximum': stat['maximum'],
        'median': stat['median'], 'q1': stat['q1'], 'q3': stat['q3'],
        'bin_count': len(bins), 'bins': bins,
        'outlier_count': outliers, 'outlier_method': 'Tukey fences: < Q1-1.5*IQR or > Q3+1.5*IQR; withheld for n<4',
        'warnings': warnings,
        'note': 'Histogram counts, not modelled probabilities. Equal-width bins use Sturges heuristic capped at 20. Boundary and outlier conventions are explicit; no values have been changed.',
    }

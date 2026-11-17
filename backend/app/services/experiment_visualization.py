"""Produces a bounded, inspectable numerical sequence chart from a validated dataset."""
from __future__ import annotations

import math

from app.services.descriptive_statistics import numeric_series

CHART_METHOD = 'observation-sequence-v1'
MAX_CHART_POINTS = 250


def sequence_chart(raw: bytes, suffix: str, column: str) -> dict:
    values, missing = numeric_series(raw, suffix, column)
    n = len(values)
    if n <= MAX_CHART_POINTS:
        indices = list(range(n))
    else:
        # Inclusive endpoints and uniformly spaced indices, no interpolation or synthetic values.
        indices = [round(i * (n - 1) / (MAX_CHART_POINTS - 1)) for i in range(MAX_CHART_POINTS)]
    return {
        'method': CHART_METHOD, 'column': column, 'x_label': 'Valid observation index (1-based)',
        'y_label': f'{column} (units not declared)', 'original_point_count': n,
        'shown_point_count': len(indices), 'sampled': n > MAX_CHART_POINTS,
        'missing_count': missing,
        'points': [{'x': i + 1, 'y': values[i]} for i in indices],
        'note': 'This is observation order, not elapsed time. Points are real observations; for >250 observations, the display uses deterministic subsampling. All data remain in the original upload.',
    }

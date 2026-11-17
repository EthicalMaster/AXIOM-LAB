"""Phase 02A: transparent quality diagnostics; original file is never changed."""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from app.services.column_profiling import _source_rows, profile_columns

MAX_TRACKED_ROWS = 10000


def _text(value: object) -> str | None:
    if value is None:
        return None
    return value.isoformat() if isinstance(value, (date, datetime)) else str(value)


def data_quality(raw: bytes, suffix: str) -> dict:
    structural = profile_columns(raw, suffix)
    columns = structural['columns']
    seen: set[str] = set()
    duplicate_rows = 0
    overflow = False
    row_count = 0
    first = True
    with _source_rows(raw, suffix) as rows:
        for row in rows:
            cells = list(row)
            if not cells or all(v is None or not str(v).strip() for v in cells):
                continue
            if first:
                first = False
                continue
            row_count += 1
            padded = (cells + [None] * len(columns))[:len(columns)]
            # Exact lexical row values, preserving strings, leading zeros and whitespace.
            # SHA-256 bounds memory per row; SHA collision risk is negligible, not zero.
            digest = hashlib.sha256(json.dumps([_text(v) for v in padded], ensure_ascii=False).encode('utf-8')).hexdigest()
            if digest in seen:
                duplicate_rows += 1
            elif len(seen) < MAX_TRACKED_ROWS:
                seen.add(digest)
            else:
                overflow = True
    assert row_count == structural['row_count']
    missing = sum(col['missing_count'] for col in columns)
    total = row_count * len(columns)
    column_quality = []
    for col in columns:
        fraction = 100 * col['missing_count'] / row_count if row_count else 0
        warnings: list[str] = []
        if fraction > 50:
            warnings.append('More than half the observations are missing in this column.')
        elif fraction > 20:
            warnings.append('Over 20% of observations are missing; check whether analysis remains representative.')
        if col['inferred_type'] == 'mixed':
            warnings.append('Mixed values can prevent numerical analysis without an explicit cleaning decision.')
        column_quality.append({'column': col['name'], 'inferred_type': col['inferred_type'],
                               'missing_count': col['missing_count'], 'present_count': col['non_missing_count'],
                               'missing_percent': fraction, 'warnings': warnings})
    warnings = []
    if missing:
        warnings.append('Missing means empty or whitespace-only; tokens like NA are not automatically missing.')
    if duplicate_rows:
        warnings.append('Repeated raw rows may be valid measurements; no rows have been removed.')
    if overflow:
        warnings.append('Duplicate tracking reached its 10,000-distinct-row cap; reported duplicate count is a lower bound.')
    return {
        'row_count': row_count, 'column_count': len(columns), 'missing_cells': missing,
        'total_cells': total, 'completeness_percent': 100 * (total - missing) / total if total else 100,
        'duplicate_rows': duplicate_rows, 'duplicate_count_exact': not overflow,
        'unique_rows_tracked': len(seen), 'columns': column_quality, 'warnings': warnings,
        'method': 'quality-audit-v1',
        'note': 'Exact lexical row duplicates, excluding fully blank rows. Results describe raw data; no cleaning or statistical inference.',
    }

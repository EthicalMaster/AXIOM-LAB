"""Conservative, bounded column-type inference for already validated datasets.

This is structural profiling, NOT statistical inference or cleaning. No coercion is
written back to the original bytes. Type labels are provisional observations.
"""
from __future__ import annotations

import csv
import io
import math
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterator

from app.services.dataset_validation import validate_dataset

MAX_DISTINCT_TRACKED = 1000
MAX_EXAMPLES = 3
MAX_EXAMPLE_CHARS = 80


@dataclass
class ColumnAccumulator:
    name: str
    non_missing: int = 0
    missing: int = 0
    seen: set[str] = field(default_factory=set)
    overflow: bool = False
    examples: list[str] = field(default_factory=list)
    observed_kinds: set[str] = field(default_factory=set)
    has_leading_zero_identifier: bool = False

    def add(self, value: object) -> None:
        if value is None or (isinstance(value, str) and not value.strip()):
            self.missing += 1
            return
        raw = value.isoformat() if isinstance(value, (date, datetime)) else str(value)
        self.non_missing += 1
        if raw not in self.seen:
            if len(self.seen) < MAX_DISTINCT_TRACKED:
                self.seen.add(raw)
            else:
                self.overflow = True
        if len(self.examples) < MAX_EXAMPLES and raw[:MAX_EXAMPLE_CHARS] not in self.examples:
            self.examples.append(raw[:MAX_EXAMPLE_CHARS] + ('…' if len(raw) > MAX_EXAMPLE_CHARS else ''))
        normalized = raw.strip()
        if re.fullmatch(r'[+-]?0\d+(?:\.\d*)?(?:[eE][+-]?\d+)?', normalized):
            self.has_leading_zero_identifier = True
            self.observed_kinds.add('text')
        else:
            self.observed_kinds.add(_value_kind(normalized))

    def finish(self) -> dict:
        if not self.non_missing:
            inferred = 'empty'
        elif self.observed_kinds == {'numeric'}:
            inferred = 'numeric'
        elif self.observed_kinds == {'boolean'}:
            inferred = 'boolean'
        elif self.observed_kinds == {'datetime'}:
            inferred = 'datetime'
        elif self.observed_kinds == {'text'}:
            inferred = 'categorical'
        else:
            inferred = 'mixed'
        warnings: list[str] = []
        if self.has_leading_zero_identifier:
            warnings.append('Leading-zero identifiers are treated as text to preserve their meaning.')
        if inferred == 'mixed':
            warnings.append('Mixed value patterns detected. Inspect before numerical analysis.')
        if self.missing:
            warnings.append('Missing means an empty or whitespace-only cell; tokens such as NA are not automatically missing.')
        if self.overflow:
            warnings.append('Distinct-count tracking is capped to limit memory use.')
        return {
            'name': self.name, 'inferred_type': inferred,
            'non_missing_count': self.non_missing, 'missing_count': self.missing,
            'distinct_count': len(self.seen), 'distinct_count_exact': not self.overflow,
            'examples': self.examples, 'warnings': warnings,
        }


def _value_kind(value: str) -> str:
    if value.casefold() in {'true', 'false'}:
        return 'boolean'
    # Recognize only ISO dates/datetimes; reject ambiguous locale-specific strings.
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        try:
            date.fromisoformat(value)
            return 'datetime'
        except ValueError:
            pass
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?', value):
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return 'datetime'
        except ValueError:
            pass
    try:
        number = float(value)
        if math.isfinite(number):
            return 'numeric'
    except (ValueError, OverflowError):
        pass
    return 'text'


@contextmanager
def _source_rows(raw: bytes, suffix: str) -> Iterator[Iterator]:
    if suffix == '.csv':
        text = raw.decode('utf-8-sig')
        yield csv.reader(io.StringIO(text, newline=''), strict=True)
    elif suffix == '.xlsx':
        from openpyxl import load_workbook
        book = load_workbook(io.BytesIO(raw), read_only=True, data_only=False, keep_links=False)
        try:
            yield iter(book.worksheets[0].iter_rows(values_only=True))
        finally:
            book.close()
    elif suffix == '.xls':
        import xlrd
        book = xlrd.open_workbook(file_contents=raw, on_demand=True)
        try:
            sheet = book.sheet_by_index(0)
            yield (sheet.row_values(i) for i in range(sheet.nrows))
        finally:
            book.release_resources()
    else:
        raise ValueError('Unsupported data format')


def profile_columns(raw: bytes, suffix: str) -> dict:
    """Return provisional per-column metadata for the first worksheet only.

    Reuse Phase 01A validation before a second bounded read. The two-pass trade-off
    avoids changing the existing import contract and keeps profiling on demand.
    """
    structural = validate_dataset(raw, suffix)
    accumulators = [ColumnAccumulator(name) for name in structural.headers]
    found_header = False
    with _source_rows(raw, suffix) as rows:
        for record in rows:
            cells = list(record)
            if not cells or all(value is None or not str(value).strip() for value in cells):
                continue
            if not found_header:
                found_header = True
                continue
            padded = (cells + [None] * len(accumulators))[:len(accumulators)]
            for accumulator, value in zip(accumulators, padded):
                accumulator.add(value)
    columns = [acc.finish() for acc in accumulators]
    assert all(c['missing_count'] + c['non_missing_count'] == structural.row_count for c in columns)
    return {
        'row_count': structural.row_count,
        'column_count': structural.column_count,
        'worksheet': structural.worksheet,
        'columns': columns,
        'method_note': 'Conservative structural inference; no cleaning, type conversion, or statistical computation was performed.',
    }

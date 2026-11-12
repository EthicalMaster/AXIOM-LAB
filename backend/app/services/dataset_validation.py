"""Bounded, non-executing dataset structure validation for Phase 01A.

Preserves original bytes; no cleaning, type inference, or statistics are performed.
"""
from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import PurePosixPath

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000
MAX_COLUMNS = 150
PREVIEW_ROWS = 8
MAX_UNCOMPRESSED_XLSX_BYTES = 30 * 1024 * 1024
MAX_XLSX_ENTRIES = 500
MAX_PREVIEW_CELL_CHARS = 180
ALLOWED_FORMATS = {".csv": "csv", ".xlsx": "xlsx", ".xls": "xls"}


class DatasetValidationError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 422):
        self.code, self.message, self.status_code = code, message, status_code
        super().__init__(message)


@dataclass(frozen=True)
class DatasetProfile:
    file_format: str
    headers: list[str]
    row_count: int
    column_count: int
    preview: list[list[str | None]]
    worksheet: str | None
    sheet_names: list[str]
    warnings: list[str]


def safe_filename(filename: str | None) -> tuple[str, str]:
    if not filename:
        raise DatasetValidationError("missing_filename", "Choose a named CSV, XLSX, or XLS file.")
    basename = PurePosixPath(filename.replace("\\", "/")).name
    if not basename or len(basename) > 160 or any(ord(c) < 32 for c in basename):
        raise DatasetValidationError("invalid_filename", "The file name is empty, too long, or contains control characters.")
    suffix = ("." + basename.rsplit(".", 1)[-1]).lower() if "." in basename else ""
    if suffix not in ALLOWED_FORMATS:
        raise DatasetValidationError("unsupported_format", "Only .csv, .xlsx and .xls files are supported.", 415)
    return basename, suffix


def _display_cell(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        representation = value.isoformat()
    else:
        representation = str(value)
    return representation[:MAX_PREVIEW_CELL_CHARS] + ("…" if len(representation) > MAX_PREVIEW_CELL_CHARS else "")


def _profile_rows(rows, *, file_format: str, worksheet: str | None = None, sheet_names: list[str] | None = None) -> DatasetProfile:
    header: list[str] | None = None
    row_count = 0
    preview: list[list[str | None]] = []
    blank_rows = 0
    formula_found = False
    for physical_row, record in enumerate(rows, start=1):
        values = list(record)
        if len(values) > MAX_COLUMNS:
            raise DatasetValidationError("too_many_columns", f"This file exceeds the {MAX_COLUMNS}-column limit.", 413)
        if not values or all(v is None or str(v).strip() == "" for v in values):
            blank_rows += 1
            continue
        if header is None:
            header = [str(v).strip() if v is not None else "" for v in values]
            if not header or any(not h for h in header):
                raise DatasetValidationError("invalid_header", "The first nonblank row must contain a name for every column.")
            if len(set(h.casefold() for h in header)) != len(header):
                raise DatasetValidationError("duplicate_headers", "Column names must be unique (ignoring case).")
            continue
        # CSV may have a different number of cells. In Excel, trailing blank cells are normal.
        if len(values) > len(header) and any(v is not None and str(v).strip() for v in values[len(header):]):
            raise DatasetValidationError("row_width_mismatch", f"Data row {physical_row} contains values beyond the {len(header)} declared columns.")
        if file_format == "csv" and len(values) != len(header):
            raise DatasetValidationError("row_width_mismatch", f"CSV row {physical_row} contains {len(values)} cells; expected {len(header)}.")
        values = (values + [None] * len(header))[:len(header)]
        if any(isinstance(v, str) and v.startswith("=") for v in values):
            formula_found = True
        row_count += 1
        if row_count > MAX_ROWS:
            raise DatasetValidationError("too_many_rows", f"This file exceeds the {MAX_ROWS:,}-data-row limit.", 413)
        if len(preview) < PREVIEW_ROWS:
            preview.append([_display_cell(v) for v in values])
    if header is None:
        raise DatasetValidationError("empty_dataset", "No header row was found in this file.")
    if row_count == 0:
        raise DatasetValidationError("no_data_rows", "Add at least one nonblank data row below the column headers.")
    warnings: list[str] = []
    if blank_rows:
        warnings.append(f"{blank_rows} blank row(s) were ignored in the preview/count; the original file is unchanged.")
    if formula_found:
        warnings.append("Formula-like cells detected. AXIOM LAB does not execute formulas; values are not evaluated.")
    if sheet_names and len(sheet_names) > 1:
        warnings.append(f"Workbook has {len(sheet_names)} sheets. Only the first sheet ({worksheet}) is inspected in this phase.")
    return DatasetProfile(file_format, header, row_count, len(header), preview, worksheet, sheet_names or [], warnings)


def _validate_csv(raw: bytes) -> DatasetProfile:
    if b"\x00" in raw:
        raise DatasetValidationError("invalid_csv", "This CSV contains null bytes or binary data.")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DatasetValidationError("invalid_encoding", "This CSV is not UTF-8. Export it as UTF-8 CSV and try again.") from exc
    try:
        reader = csv.reader(io.StringIO(content, newline=""), strict=True)
        return _profile_rows(reader, file_format="csv")
    except csv.Error as exc:
        raise DatasetValidationError("invalid_csv", f"CSV could not be parsed: {exc}") from exc


def _validate_xlsx(raw: bytes) -> DatasetProfile:
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise DatasetValidationError("invalid_xlsx", "This XLSX file is not a valid Excel workbook.")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if (len(entries) > MAX_XLSX_ENTRIES or
                sum(e.file_size for e in entries) > MAX_UNCOMPRESSED_XLSX_BYTES or
                any(e.file_size > MAX_UNCOMPRESSED_XLSX_BYTES for e in entries)):
            raise DatasetValidationError("xlsx_too_complex", "Workbook exceeds safe uncompressed-size or entry-count limits.", 413)
        if any(e.flag_bits & 1 for e in entries):
            raise DatasetValidationError("encrypted_file", "Encrypted spreadsheets are not supported.")
    from openpyxl import load_workbook
    try:
        book = load_workbook(io.BytesIO(raw), read_only=True, data_only=False, keep_links=False)
        try:
            names = book.sheetnames
            if not names:
                raise DatasetValidationError("empty_workbook", "The workbook contains no worksheets.")
            sheet = book.worksheets[0]
            if sheet.max_row is not None and sheet.max_row > MAX_ROWS + 1:
                raise DatasetValidationError("too_many_rows", f"Worksheet exceeds the {MAX_ROWS:,}-data-row limit.", 413)
            if sheet.max_column is not None and sheet.max_column > MAX_COLUMNS:
                raise DatasetValidationError("too_many_columns", f"Worksheet exceeds the {MAX_COLUMNS}-column limit.", 413)
            return _profile_rows(sheet.iter_rows(values_only=True), file_format="xlsx", worksheet=names[0], sheet_names=names)
        finally:
            book.close()
    except DatasetValidationError:
        raise
    except Exception as exc:
        raise DatasetValidationError("invalid_xlsx", "This XLSX workbook could not be safely opened or parsed.") from exc


def _validate_xls(raw: bytes) -> DatasetProfile:
    if not raw.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        raise DatasetValidationError("invalid_xls", "This XLS file is not a recognised legacy Excel workbook.")
    import xlrd
    try:
        book = xlrd.open_workbook(file_contents=raw, on_demand=True)
        try:
            names = book.sheet_names()
            if not names:
                raise DatasetValidationError("empty_workbook", "The workbook contains no worksheets.")
            sheet = book.sheet_by_index(0)
            if sheet.nrows > MAX_ROWS + 1:
                raise DatasetValidationError("too_many_rows", f"Worksheet exceeds the {MAX_ROWS:,}-data-row limit.", 413)
            if sheet.ncols > MAX_COLUMNS:
                raise DatasetValidationError("too_many_columns", f"Worksheet exceeds the {MAX_COLUMNS}-column limit.", 413)
            result = _profile_rows((sheet.row_values(i) for i in range(sheet.nrows)), file_format="xls", worksheet=names[0], sheet_names=names)
            return result
        finally:
            book.release_resources()
    except DatasetValidationError:
        raise
    except Exception as exc:
        raise DatasetValidationError("invalid_xls", "This XLS workbook could not be safely opened or parsed.") from exc


def validate_dataset(raw: bytes, suffix: str) -> DatasetProfile:
    if not raw:
        raise DatasetValidationError("empty_file", "The selected file is empty.")
    if len(raw) > MAX_FILE_BYTES:
        raise DatasetValidationError("file_too_large", "Maximum upload size is 5 MiB.", 413)
    if suffix == ".csv":
        return _validate_csv(raw)
    if suffix == ".xlsx":
        return _validate_xlsx(raw)
    if suffix == ".xls":
        return _validate_xls(raw)
    raise DatasetValidationError("unsupported_format", "Only .csv, .xlsx and .xls files are supported.", 415)

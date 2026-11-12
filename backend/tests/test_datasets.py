"""Phase 01A API, validation, immutability and metadata lookup tests."""
from __future__ import annotations

import hashlib
import io
import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app
from app.services.dataset_validation import MAX_FILE_BYTES

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AXIOM_DATA_DIR", str(tmp_path))


def upload(name: str, payload: bytes):
    return client.post("/api/v1/datasets/import", files={"file": (name, io.BytesIO(payload), "application/octet-stream")})


def workbook_bytes(*, extra_sheet: bool = False, formula: bool = False) -> bytes:
    book = Workbook()
    ws = book.active
    ws.title = "Measurements"
    ws.append(["Day", "Temperature"])
    ws.append(["Mon", "24.5"])
    ws.append(["Tue", "=1+2" if formula else 27])
    if extra_sheet:
        book.create_sheet("Extra")
    stream = io.BytesIO()
    book.save(stream)
    return stream.getvalue()


def test_valid_csv_import_persists_original_bytes(tmp_path: Path):
    raw = b"subject,score\nA,10\nB,15\n"
    response = upload("experiment.csv", raw)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["format"] == "csv"
    assert data["headers"] == ["subject", "score"]
    assert data["row_count"] == 2 and data["column_count"] == 2
    assert data["preview"] == [["A", "10"], ["B", "15"]]
    assert data["sha256"] == hashlib.sha256(raw).hexdigest()
    expected_path = tmp_path / "datasets" / data["id"] / "original.csv"
    assert expected_path.read_bytes() == raw
    metadata = client.get(f"/api/v1/datasets/{data['id']}")
    assert metadata.status_code == 200
    assert metadata.json()["sha256"] == data["sha256"]
    assert "preview" not in metadata.json()
    # No raw dataset content should appear in persisted metadata.
    with sqlite3.connect(tmp_path / "axiom.sqlite3") as conn:
        stored = conn.execute("SELECT sha256 FROM datasets WHERE id = ?", (data["id"],)).fetchone()
    assert stored == (data["sha256"],)


def test_multiple_imports_do_not_overwrite_raw_dataset(tmp_path: Path):
    original = b"x,y\n1,2\n"
    first = upload("input.csv", original).json()
    second = upload("input.csv", b"x,y\n5,6\n").json()
    assert first["id"] != second["id"]
    assert (tmp_path / "datasets" / first["id"] / "original.csv").read_bytes() == original


def test_accepts_utf8_bom_and_quoted_commas():
    response = upload("test.csv", b"\xef\xbb\xbfname,note\nA,\"a,b\"\n")
    assert response.status_code == 201
    assert response.json()["preview"] == [["A", "a,b"]]


def test_rejects_duplicate_headers_and_inconsistent_rows():
    duplicate = upload("dupes.csv", b"a,A\n1,2\n")
    assert duplicate.status_code == 422
    assert duplicate.json()["detail"]["code"] == "duplicate_headers"
    inconsistent = upload("bad.csv", b"a,b\n1\n")
    assert inconsistent.status_code == 422
    assert inconsistent.json()["detail"]["code"] == "row_width_mismatch"


def test_rejects_non_utf8_csv_and_unsupported_format():
    assert upload("latin1.csv", b"name\n\xff\n").json()["detail"]["code"] == "invalid_encoding"
    unsupported = upload("dataset.json", b"{}")
    assert unsupported.status_code == 415
    assert unsupported.json()["detail"]["code"] == "unsupported_format"


def test_rejects_empty_or_oversized_upload():
    assert upload("empty.csv", b"").json()["detail"]["code"] == "empty_file"
    too_big = upload("huge.csv", b"x\n" + b"a" * MAX_FILE_BYTES)
    assert too_big.status_code == 413
    assert too_big.json()["detail"]["code"] == "file_too_large"


def test_rejects_path_like_bad_filename_but_never_uses_it_for_storage(tmp_path: Path):
    response = upload(r"C:\\Users\\someone\\docs\\measurement.csv", b"a\n1\n")
    assert response.status_code == 201
    assert response.json()["original_name"] == "measurement.csv"
    assert (tmp_path / "datasets" / response.json()["id"] / "original.csv").exists()


def test_xlsx_import_reports_sheet_selection_and_formula_warnings(tmp_path: Path):
    raw = workbook_bytes(extra_sheet=True, formula=True)
    response = upload("readings.xlsx", raw)
    assert response.status_code == 201, response.text
    record = response.json()
    assert record["row_count"] == 2
    assert record["worksheet"] == "Measurements"
    assert record["sheet_names"] == ["Measurements", "Extra"]
    assert any("first sheet" in warning for warning in record["warnings"])
    assert any("Formula-like" in warning for warning in record["warnings"])
    assert (tmp_path / "datasets" / record["id"] / "original.xlsx").read_bytes() == raw


def test_rejects_fake_excel_files():
    assert upload("fake.xlsx", b"not-excel").json()["detail"]["code"] == "invalid_xlsx"
    assert upload("fake.xls", b"not-excel").json()["detail"]["code"] == "invalid_xls"


def test_metadata_lookup_rejects_invalid_id():
    assert client.get("/api/v1/datasets/not-a-dataset-id").status_code == 404


def test_invalid_import_does_not_persist_upload(tmp_path: Path):
    failed = upload("bad.csv", b"x,x\n1,2\n")
    assert failed.status_code == 422
    assert not (tmp_path / "datasets").exists()

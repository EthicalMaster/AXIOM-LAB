"""Phase 01B independent API and inference verification."""
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app
from app.services.column_profiling import profile_columns

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))


def upload_csv(raw: bytes):
    return client.post('/api/v1/datasets/import', files={'file': ('table.csv', io.BytesIO(raw), 'text/csv')})


def get_profile(raw: bytes):
    uploaded = upload_csv(raw)
    assert uploaded.status_code == 201, uploaded.text
    response = client.get(f"/api/v1/datasets/{uploaded.json()['id']}/profile")
    assert response.status_code == 200, response.text
    return response.json()


def test_infer_numerics_and_categorical_and_missing_counts():
    data = get_profile(b'id,temperature,note\nA,22.5,ok\nB,24.0,\nC,23.5,ok\n')
    assert data['row_count'] == 3 and data['column_count'] == 3
    assert [col['inferred_type'] for col in data['columns']] == ['categorical', 'numeric', 'categorical']
    numeric = data['columns'][1]
    assert numeric['missing_count'] == 0 and numeric['non_missing_count'] == 3
    assert numeric['distinct_count'] == 3 and numeric['distinct_count_exact'] is True
    assert numeric['examples'] == ['22.5', '24.0', '23.5']
    note = data['columns'][2]
    assert note['missing_count'] == 1 and note['non_missing_count'] == 2
    assert note['distinct_count'] == 1


def test_ambiguous_tokens_not_silently_converted_to_null():
    data = get_profile(b'values\n1\nNA\n3\n')
    col = data['columns'][0]
    assert col['inferred_type'] == 'mixed'
    assert col['missing_count'] == 0
    assert col['non_missing_count'] == 3
    assert any('Mixed' in warning for warning in col['warnings'])


def test_leading_zeros_are_identifier_preserving_and_boolean_datetime_detected():
    data = get_profile(b'code,flag,when\n001,TRUE,2026-11-12\n002,false,2026-11-13\n')
    assert [c['inferred_type'] for c in data['columns']] == ['categorical', 'boolean', 'datetime']
    assert any('Leading-zero' in warning for warning in data['columns'][0]['warnings'])


def test_empty_and_whitespace_only_cells_are_missing():
    data = get_profile(b'blank,reading\n,1\n  ,2\n,3\n')
    assert data['columns'][0]['inferred_type'] == 'empty'
    assert data['columns'][0]['missing_count'] == 3
    assert data['columns'][0]['distinct_count'] == 0


def test_nonfinite_numeric_literals_are_not_numeric():
    data = get_profile(b'value\n1\nnan\ninf\n')
    assert data['columns'][0]['inferred_type'] == 'mixed'


def test_distinct_counts_are_memory_bounded():
    raw = ('item\n' + ''.join(f'v{i}\n' for i in range(1004))).encode()
    profile = get_profile(raw)
    col = profile['columns'][0]
    assert col['distinct_count'] == 1000
    assert col['distinct_count_exact'] is False
    assert len(col['examples']) == 3


def test_dataset_profile_remains_retrievable_from_storage_after_import(tmp_path: Path):
    imported = upload_csv(b'x,y\n1,2\n3,4\n').json()
    response = client.get(f"/api/v1/datasets/{imported['id']}/profile")
    assert response.status_code == 200
    assert response.json()['dataset_id'] == imported['id']
    assert (tmp_path / 'datasets' / imported['id'] / 'original.csv').read_bytes() == b'x,y\n1,2\n3,4\n'


def test_profile_refuses_tampered_original(tmp_path: Path):
    imported = upload_csv(b'x\n1\n').json()
    original = tmp_path / 'datasets' / imported['id'] / 'original.csv'
    original.write_bytes(b'x\n2\n')
    response = client.get(f"/api/v1/datasets/{imported['id']}/profile")
    assert response.status_code == 409
    assert response.json()['detail']['code'] == 'dataset_integrity_error'


def test_profile_rejects_invalid_and_nonexistent_dataset_ids():
    assert client.get('/api/v1/datasets/hello/profile').status_code == 404
    assert client.get('/api/v1/datasets/' + 'a' * 32 + '/profile').status_code == 404


def test_xlsx_uses_first_worksheet_and_does_not_evaluate_formula():
    book = Workbook()
    sheet = book.active
    sheet.title = 'Readings'
    sheet.append(['value', 'day'])
    sheet.append([10, '2026-11-12'])
    sheet.append(['=1+2', '2026-11-13'])
    book.create_sheet('Other').append(['ignored'])
    buffer = io.BytesIO()
    book.save(buffer)
    imported = client.post('/api/v1/datasets/import', files={'file': ('table.xlsx', buffer.getvalue())})
    assert imported.status_code == 201, imported.text
    response = client.get(f"/api/v1/datasets/{imported.json()['id']}/profile")
    assert response.status_code == 200, response.text
    profile = response.json()
    assert profile['worksheet'] == 'Readings'
    assert profile['columns'][0]['inferred_type'] == 'mixed'
    assert profile['columns'][0]['examples'] == ['10', '=1+2']
    assert profile['columns'][1]['inferred_type'] == 'datetime'


def test_blanks_are_excluded_consistently_with_original_import():
    data = get_profile(b'a,b\n1,2\n\n3,4\n')
    assert data['row_count'] == 2
    assert all(c['non_missing_count'] == 2 for c in data['columns'])


def test_conservative_inferrence_can_be_called_separately():
    p = profile_columns(b'c\n1\n2\n', '.csv')
    assert p['columns'][0]['inferred_type'] == 'numeric'
    assert 'no cleaning' in p['method_note']

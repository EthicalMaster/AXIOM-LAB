"""Independently known reference values and endpoint boundary tests."""
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.descriptive_statistics import quantile_type7, describe_values

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))

def stats(raw: bytes):
    res = client.post('/api/v1/datasets/import', files={'file': ('data.csv', io.BytesIO(raw), 'text/csv')})
    assert res.status_code == 201, res.text
    return client.get(f"/api/v1/datasets/{res.json()['id']}/statistics")

def test_known_reference_statistics():
    col = stats(b'v,category\n1,A\n2,A\n3,B\n4,B\n5,C\n').json()['columns'][0]
    assert col['column'] == 'v'
    assert col['mean'] == 3 and col['median'] == 3
    assert col['sample_variance'] == 2.5
    assert col['population_variance'] == 2
    assert col['sample_stddev'] == pytest.approx(2.5**.5)
    assert col['q1'] == 2 and col['q3'] == 4 and col['iqr'] == 2

def test_missing_and_single_value():
    col = stats(b'value,label\n7,A\n,B\n').json()['columns'][0]
    assert col['count'] == 1 and col['missing_count'] == 1
    assert col['sample_stddev'] is None and col['sample_variance'] is None

def test_non_numeric_is_excluded_and_na_not_imputed():
    result = stats(b'id,score\n001,1\n002,NA\n003,3\n').json()
    assert result['columns'] == []

def test_constant_and_finite():
    col = stats(b'v\n2\n2\n2\n').json()['columns'][0]
    assert col['iqr'] == 0 and col['population_stddev'] == 0
    assert any('same value' in n for n in col['notes'])

def test_quantile_is_interpolated():
    assert quantile_type7([1, 2, 4, 8], .25) == 1.75
    assert quantile_type7([1, 2, 4, 8], .75) == 5

def test_invalid_id_and_integrity(tmp_path):
    assert client.get('/api/v1/datasets/nope/statistics').status_code == 404
    uploaded = client.post('/api/v1/datasets/import', files={'file':('d.csv', b'v\n1\n2\n')}).json()
    (tmp_path/'datasets'/uploaded['id']/'original.csv').write_bytes(b'v\n8\n9\n')
    res = client.get(f"/api/v1/datasets/{uploaded['id']}/statistics")
    assert res.status_code == 409

def test_numerical_overflow_rejected():
    from app.services.dataset_validation import DatasetValidationError
    with pytest.raises(DatasetValidationError):
        describe_values([1e308, -1e308], 0)

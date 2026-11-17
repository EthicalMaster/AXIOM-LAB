import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.distributions import distribution, histogram

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(tmp_path:Path,monkeypatch:pytest.MonkeyPatch):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def report(raw:bytes, column='v'):
    uploaded=client.post('/api/v1/datasets/import',files={'file':('d.csv',io.BytesIO(raw))})
    assert uploaded.status_code==201,uploaded.text
    return client.get('/api/v1/datasets/'+uploaded.json()['id']+'/distribution',params={'column':column})

def test_histogram_counts_known_values():
    d=report(b'v\n1\n2\n3\n4\n5\n').json()
    assert d['count']==5 and d['bin_count']==4
    assert sum(b['count'] for b in d['bins'])==5
    assert sum(b['percent'] for b in d['bins'])==pytest.approx(100)
    assert d['q1']==2 and d['median']==3 and d['q3']==4
    assert d['outlier_count']==0

def test_outlier_indicator_reference():
    d=report(b'v\n1\n2\n2\n3\n100\n').json()
    assert d['outlier_count']==1
    assert d['method'].startswith('histogram-sturges')

def test_fewer_than_four_withholds_outlier():
    d=report(b'v\n1\n2\n3\n').json()
    assert d['outlier_count'] is None
    assert any('Fewer than four' in w for w in d['warnings'])

def test_constant_single_bin_and_warning():
    d=report(b'v\n5\n5\n5\n5\n').json()
    assert d['bin_count']==1 and d['bins'][0]['count']==4
    assert d['bins'][0]['lower']==d['bins'][0]['upper']==5
    assert any('IQR is zero' in w for w in d['warnings'])

def test_missing_values_excluded_not_filled():
    d=report(b'v,label\n1,A\n,B\n3,C\n4,D\n5,E\n').json()
    assert d['count']==4 and d['missing_count']==1
    assert sum(b['count'] for b in d['bins'])==4

def test_mixed_rejected_and_dataset_integrity(tmp_path):
    assert report(b'v\n1\nNA\n3\n').status_code==422
    upload=client.post('/api/v1/datasets/import',files={'file':('d.csv',b'v\n1\n2\n')}).json()
    (tmp_path/'datasets'/upload['id']/'original.csv').write_bytes(b'v\n2\n3\n')
    assert client.get('/api/v1/datasets/'+upload['id']+'/distribution',params={'column':'v'}).status_code==409

def test_extreme_range_rejected():
    from app.services.dataset_validation import DatasetValidationError
    with pytest.raises(DatasetValidationError): histogram([-1e308,1e308])

def test_histogram_does_not_exceed_cap():
    bins=histogram([float(i) for i in range(1000)])
    assert len(bins) <= 20
    assert sum(b['count'] for b in bins)==1000

def test_invalid_column_and_query():
    assert report(b'v\n1\n2\n',column='absent').status_code==422
    assert client.get('/api/v1/datasets/nope/distribution',params={'column':'v'}).status_code==404

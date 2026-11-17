import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.data_quality import data_quality

client=TestClient(app)

@pytest.fixture(autouse=True)
def isolate(tmp_path:Path,monkeypatch:pytest.MonkeyPatch):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def load(raw:bytes):
    response=client.post('/api/v1/datasets/import',files={'file':('data.csv',io.BytesIO(raw))})
    assert response.status_code == 201, response.text
    ident=response.json()['id']
    result=client.get(f'/api/v1/datasets/{ident}/quality')
    assert result.status_code == 200, result.text
    return result.json()

def test_missingness_and_duplicate_rows():
    q=load(b'code,value\n001,1\n002,\n002,\n003,3\n')
    assert q['row_count']==4 and q['total_cells']==8
    assert q['missing_cells']==2 and q['completeness_percent']==75
    assert q['duplicate_rows']==1 and q['duplicate_count_exact']
    assert q['columns'][1]['missing_percent']==50

def test_raw_whitespace_affects_duplicate_identity_but_missingness_is_same():
    q=load(b'a,b\nA, \nA,\n')
    assert q['missing_cells']==2 and q['duplicate_rows']==0

def test_duplicate_does_not_delete_data():
    q=load(b'value\n5\n5\n5\n')
    assert q['duplicate_rows']==2 and q['row_count']==3

def test_more_than_10000_unique_rows_bounds_memory():
    raw=('code\n' + ''.join(f'id-{i}\n' for i in range(10003))).encode()
    q=data_quality(raw,'.csv')
    assert q['unique_rows_tracked']==10000
    assert not q['duplicate_count_exact']
    assert q['duplicate_rows']==0

def test_unknown_dataset_and_integrity(tmp_path):
    assert client.get('/api/v1/datasets/incorrect/quality').status_code==404
    r=client.post('/api/v1/datasets/import',files={'file':('d.csv',b'v\n1\n')}).json()
    (tmp_path/'datasets'/r['id']/'original.csv').write_bytes(b'v\n2\n')
    assert client.get('/api/v1/datasets/'+r['id']+'/quality').status_code==409

def test_critical_missingness_warning():
    q=load(b'a,b\n1,\n2,\n3,7\n4,\n')
    assert any('More than half' in w for w in q['columns'][1]['warnings'])

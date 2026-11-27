import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))

def test_append_is_immutable_and_revisioned():
    upload = client.post('/api/v1/datasets/import', files={'file': ('numbers.csv', b'a,b\n1,5\n2,6\n3,7\n')}).json()
    exp = client.post('/api/v1/experiments', json={'name':'Run history','dataset_id':upload['id'],'column':'a'}).json()
    before = exp['run']['result']
    r = client.post('/api/v1/experiments/'+exp['id']+'/runs', json={'column':'b'})
    assert r.status_code == 201, r.text
    assert r.json()['revision'] == 2
    runs = client.get('/api/v1/experiments/'+exp['id']+'/runs').json()['items']
    assert [x['revision'] for x in runs] == [2,1]
    assert runs[1]['result'] == before
    assert client.get('/api/v1/experiments/'+exp['id']).json()['run']['revision'] == 2


def test_append_invalid_and_missing():
    assert client.post('/api/v1/experiments/'+'f'*32+'/runs',json={'column':'a'}).status_code == 404
    upload = client.post('/api/v1/datasets/import', files={'file': ('x.csv', b'a\n1\n2\n')}).json()
    exp = client.post('/api/v1/experiments', json={'name':'X','dataset_id':upload['id'],'column':'a'}).json()
    assert client.post('/api/v1/experiments/'+exp['id']+'/runs',json={'column':'unknown'}).status_code == 422

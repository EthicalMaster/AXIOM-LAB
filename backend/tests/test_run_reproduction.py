import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(tmp_path,monkeypatch):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_reproduce_preserves_source_and_records_lineage():
    dataset=client.post('/api/v1/datasets/import',files={'file':('a.csv',b'x\n10\n20\n30\n')}).json()
    exp=client.post('/api/v1/experiments',json={'name':'Replay','dataset_id':dataset['id'],'column':'x'}).json()
    url=f"/api/v1/experiments/{exp['id']}/runs/{exp['run']['id']}/reproduce"
    res=client.post(url)
    assert res.status_code==201,res.text
    j=res.json()
    assert j['exact_result_match'] is True
    assert j['reproduced_run']['source_run_id']==exp['run']['id']
    assert j['reproduced_run']['revision']==2
    assert client.get('/api/v1/experiments/'+exp['id']+'/runs').json()['total']==2


def test_replay_rejects_changed_raw_bytes(tmp_path):
    d=client.post('/api/v1/datasets/import',files={'file':('a.csv',b'x\n1\n2\n')}).json()
    exp=client.post('/api/v1/experiments',json={'name':'Replay','dataset_id':d['id'],'column':'x'}).json()
    (tmp_path/'datasets'/d['id']/'original.csv').write_text('x\n99\n')
    assert client.post(f"/api/v1/experiments/{exp['id']}/runs/{exp['run']['id']}/reproduce").status_code==409

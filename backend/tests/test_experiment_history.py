import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_empty_history_and_pagination():
    assert client.get('/api/v1/experiments').json()['total']==0
    imported=client.post('/api/v1/datasets/import',files={'file':('x.csv',b'x\n1\n2\n3\n')}).json()
    ids=[]
    for name in ['First','Second','Third']:
        res=client.post('/api/v1/experiments',json={'name':name,'dataset_id':imported['id'],'column':'x'})
        assert res.status_code==201,res.text
        ids.append(res.json()['id'])
    page=client.get('/api/v1/experiments',params={'limit':2,'offset':0}).json()
    assert page['total']==3 and len(page['items'])==2
    assert all(item['run_count']==1 for item in page['items'])
    nextpage=client.get('/api/v1/experiments',params={'limit':2,'offset':2}).json()
    assert len(nextpage['items'])==1
    assert not set(x['id'] for x in page['items']) & set(x['id'] for x in nextpage['items'])
    for experiment_id in ids:
        runs=client.get(f'/api/v1/experiments/{experiment_id}/runs').json()
        assert runs['total']==1 and runs['items'][0]['status']=='completed'
        assert runs['items'][0]['result']['points']

def test_invalid_history_queries():
    assert client.get('/api/v1/experiments',params={'limit':500}).status_code==422
    assert client.get('/api/v1/experiments/missing/runs').status_code==404

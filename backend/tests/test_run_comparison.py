import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(tmp_path,monkeypatch): monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_comparison_avoids_apples_to_oranges():
    dataset=client.post('/api/v1/datasets/import',files={'file':('x.csv', b'a,b\n1,3\n2,6\n3,9\n')}).json()
    e=client.post('/api/v1/experiments',json={'dataset_id':dataset['id'],'name':'Compare','column':'a'}).json()
    identical=client.post(f"/api/v1/experiments/{e['id']}/runs",json={'column':'a'}).json()
    params={'left':e['run']['id'],'right':identical['id']}
    result=client.get(f"/api/v1/experiments/{e['id']}/compare",params=params).json()
    assert result['comparable'] and result['comparison']['identical_values']
    different=client.post(f"/api/v1/experiments/{e['id']}/runs",json={'column':'b'}).json()
    result=client.get(f"/api/v1/experiments/{e['id']}/compare",params={'left':identical['id'],'right':different['id']}).json()
    assert not result['comparable'] and result['comparison'] is None
    assert client.get(f"/api/v1/experiments/{e['id']}/compare",params={'left':'f'*32,'right':identical['id']}).status_code==404

import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def setup(tmp_path,monkeypatch):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))
    for name in ('AXIOM_AI_BASE_URL','AXIOM_AI_MODEL','AXIOM_AI_API_KEY'):
        monkeypatch.delenv(name,raising=False)

def test_offline_guidance_no_hallucinated_statistics():
    d=client.post('/api/v1/datasets/import',files={'file':('x.csv',b'x,c\n1,A\n2,B\n3,A\n')}).json()
    r=client.post('/api/v1/ai/guidance',json={'dataset_id':d['id'],'goal':'distribution'})
    assert r.status_code==200,r.text
    j=r.json()
    assert j['source']=='deterministic-rules-v1'
    assert j['suggestions'][0]['method']=='histogram-and-quartiles'
    assert j['ai_commentary'] is None
    assert 'values' not in j

def test_guidance_rejects_missing_id():
    assert client.post('/api/v1/ai/guidance',json={'dataset_id':'f'*32,'goal':'prediction'}).status_code==404
    assert client.post('/api/v1/ai/guidance',json={'dataset_id':'f'*32,'goal':'make stuff up'}).status_code==422

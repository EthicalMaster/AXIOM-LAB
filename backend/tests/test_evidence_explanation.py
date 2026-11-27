import pytest
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
@pytest.fixture(autouse=True)
def setup(tmp_path,monkeypatch):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))
    for x in ('AXIOM_AI_MODEL','AXIOM_AI_API_KEY','AXIOM_AI_BASE_URL'):monkeypatch.delenv(x,raising=False)

def test_grounded_evidence_and_offline_mode():
    d=client.post('/api/v1/datasets/import',files={'file':('x.csv',b'x\n1\n2\n3\n')}).json()
    e=client.post('/api/v1/experiments',json={'name':'Explain','dataset_id':d['id'],'column':'x'}).json()
    result=client.post('/api/v1/ai/explain',json={'experiment_id':e['id'],'run_id':e['run']['id']})
    assert result.status_code==200,result.text
    j=result.json()
    assert j['evidence']['observations_total']==3
    assert j['evidence']['dataset_sha256']==d['sha256']
    assert len(j['evidence_sha256'])==64
    assert j['source']=='deterministic-evidence-template'
    assert 'causal' in j['explanation']


def test_unknown_run_cannot_be_explained():
    result=client.post('/api/v1/ai/explain',json={'experiment_id':'f'*32,'run_id':'f'*32})
    assert result.status_code==404

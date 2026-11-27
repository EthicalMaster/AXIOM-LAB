"""Cross-phase contract: recorded evidence survives the full local workflow."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def local(tmp_path, monkeypatch):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '0')
    for key in ('AXIOM_AI_MODEL', 'AXIOM_AI_BASE_URL', 'AXIOM_AI_API_KEY'):
        monkeypatch.delenv(key, raising=False)


def test_full_research_evidence_journey():
    data = client.post('/api/v1/datasets/import',
                       files={'file': ('measurements.csv', b'sample,value\nA,10\nB,20\nC,30\n')})
    assert data.status_code == 201
    dataset = data.json()
    dataset_id = dataset['id']
    summary = client.get(f'/api/v1/datasets/{dataset_id}/statistics').json()
    assert summary['columns'][0]['mean'] == 20
    advice = client.post('/api/v1/ai/guidance', json={'dataset_id':dataset_id,'goal':'describe'}).json()
    assert advice['suggestions'] and advice['ai_commentary'] is None
    experiment = client.post('/api/v1/experiments',
                             json={'name':'Local study', 'dataset_id':dataset_id, 'column':'value'}).json()
    experiment_id=experiment['id']
    first=experiment['run']['id']
    repeat=client.post(f'/api/v1/experiments/{experiment_id}/runs',json={'column':'value'}).json()
    comparison=client.get(f'/api/v1/experiments/{experiment_id}/compare',
                          params={'left':first,'right':repeat['id']}).json()
    assert comparison['comparison']['identical_values']
    reproduction=client.post(f'/api/v1/experiments/{experiment_id}/runs/{first}/reproduce').json()
    assert reproduction['exact_result_match']
    explanation=client.post('/api/v1/ai/explain',json={'experiment_id':experiment_id,'run_id':first}).json()
    assert explanation['evidence']['dataset_sha256']==dataset['sha256']
    url=f'/api/v1/experiments/{experiment_id}/runs/{first}/report'
    assert client.get(url,params={'format':'pdf'}).content.startswith(b'%PDF')
    assert client.get(url,params={'format':'json'}).json()['run']['result']==experiment['run']['result']
    assert client.get(url,params={'format':'csv'}).status_code==200
    assert client.get(f'/api/v1/experiments/{experiment_id}/runs').json()['total']==3

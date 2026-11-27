from fastapi.testclient import TestClient
from app.main import app


def test_guide_works_without_provider(monkeypatch, tmp_path):
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    for name in ('AXIOM_AI_API_KEY','AXIOM_AI_MODEL','AXIOM_AI_BASE_URL'):
        monkeypatch.delenv(name, raising=False)
    with TestClient(app) as client:
        uploaded = client.post('/api/v1/datasets/import', files={'file':('test.csv', b'x\n1\n2\n3\n')}).json()
        data = client.post('/api/v1/ai/guide', json={'question':'What is the mean?', 'page':'Statistics','dataset_id':uploaded['id'],'column':'x','use_provider':True}).json()
        assert data['evidence']['column_statistics']['mean'] == 2
        assert data['source'].startswith('Built-in')
        assert 'provider unavailable' in data['answer']
        assert client.post('/api/v1/ai/guide',json={'question':'x'*501,'page':'Statistics'}).status_code == 422

import json
from fastapi.testclient import TestClient
from app.main import app
from app.services import guide


def test_lens_offline_never_calls_provider(monkeypatch):
    def unexpected(_):
        raise AssertionError('provider must not be called without consent')
    monkeypatch.setattr(guide, 'chat_from_evidence', unexpected)
    result = guide.explain('Explain this', 'Machine Learning', None, False, selection={'kind':'metric','label':'R²','excerpt':'R²: 0.984'})
    assert 'baseline' in result['answer']
    assert 'client-supplied' in result['answer']
    assert result['source'].startswith('Built-in')


def test_lens_provider_receives_separate_selection(monkeypatch):
    def provider(payload):
        data = json.loads(payload)
        assert data['client_selection']['excerpt'] == 'R²: 0.984'
        assert data['verified_summary'] is None
        return 'Advisory interpretation'
    monkeypatch.setattr(guide, 'chat_from_evidence', provider)
    result = guide.explain('Explain this', 'Machine Learning', None, True, selection={'kind':'metric','label':'R²','excerpt':'R²: 0.984'})
    assert result['answer'] == 'Advisory interpretation'
    assert 'advisory' in result['source']


def test_lens_request_validation(monkeypatch):
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    with TestClient(app) as client:
        payload={'question':'Explain this','page':'Statistics','selection':{'kind':'text','label':'Mean','excerpt':'Mean: 2'}}
        assert client.post('/api/v1/ai/guide',json=payload).status_code == 200
        payload['selection']['excerpt']='x'*321
        assert client.post('/api/v1/ai/guide',json=payload).status_code == 422
        payload['selection']['excerpt']='x'
        payload['selection']['kind']='invalid'
        assert client.post('/api/v1/ai/guide',json=payload).status_code == 422

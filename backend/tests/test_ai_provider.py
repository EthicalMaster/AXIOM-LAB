import httpx
import pytest
from app.services.ai_provider import configuration, chat_from_evidence, AIUnavailable
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_disabled_by_default(monkeypatch):
    for k in ('AXIOM_AI_MODEL','AXIOM_AI_BASE_URL','AXIOM_AI_API_KEY'):
        monkeypatch.delenv(k,raising=False)
    assert client.get('/api/v1/ai/status').json()['enabled'] is False
    with pytest.raises(AIUnavailable):chat_from_evidence('count=4')

def test_config_rejects_unprotected_remote(monkeypatch):
    monkeypatch.setenv('AXIOM_AI_MODEL','test')
    monkeypatch.setenv('AXIOM_AI_BASE_URL','http://example.com/v1')
    monkeypatch.setenv('AXIOM_AI_API_KEY','test')
    with pytest.raises(AIUnavailable): configuration()

def test_mock_provider_sends_only_summary(monkeypatch):
    monkeypatch.setenv('AXIOM_AI_MODEL','test')
    monkeypatch.setenv('AXIOM_AI_BASE_URL','https://example.org/v1')
    monkeypatch.setenv('AXIOM_AI_API_KEY','secret-test-key')
    def respond(request):
        assert request.url.path=='/v1/chat/completions'
        assert request.headers['authorization']=='Bearer secret-test-key'
        assert b'count=4' in request.content
        return httpx.Response(200,json={'choices':[{'message':{'content':'The verified summary contains four observations.'}}]})
    with httpx.Client(transport=httpx.MockTransport(respond)) as mocked:
        assert 'four' in chat_from_evidence('count=4',client=mocked)

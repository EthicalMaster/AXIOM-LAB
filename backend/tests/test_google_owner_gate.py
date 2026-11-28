from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

OWNER='12345678-1234-4234-8234-123456789abc'
OTHER='12345678-1234-4234-8234-123456789abd'

def test_managed_gate_blocks_non_owner_and_allows_bootstrap(monkeypatch):
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','1')
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    monkeypatch.delenv('AXIOM_GOOGLE_OWNER_ID',raising=False)
    with TestClient(app) as client, patch('app.main.verify_google',new_callable=AsyncMock) as verify:
        verify.return_value=OTHER
        response=client.get('/api/v1/auth/google/verify')
        assert response.status_code==200
        assert response.json()=={'user_id':OTHER,'workspace_allowed':False}
        assert client.get('/api/v1/auth/status').status_code==403
        assert client.get('/api/v1/datasets').status_code==403
        monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',OWNER)
        assert client.get('/api/v1/auth/status').status_code==403
        verify.return_value=OWNER
        assert client.get('/api/v1/auth/status').status_code==200
        verify.side_effect=HTTPException(401,'Invalid session')
        assert client.get('/api/v1/auth/status').status_code==401
        assert client.get('/api/v1/health').status_code==200

def test_disabled_mode_preserved(monkeypatch):
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','0')
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    with TestClient(app) as client:
        assert client.get('/api/v1/auth/status').status_code==200
        assert client.get('/api/v1/auth/google/verify').status_code==503

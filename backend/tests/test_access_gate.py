import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(autouse=True)
def configured(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','1')
    monkeypatch.setenv('AXIOM_ACCESS_TOKEN','long-local-integration-test-secret-1234567890')

def test_public_protected_session():
    with TestClient(app,base_url='https://testserver') as user:
        assert user.get('/api/v1/ai/status').status_code==401
        assert user.get('/api/v1/auth/status').json()['required'] is True
        assert user.post('/api/v1/auth/login',json={'token':'incorrect'}).status_code==401
        login=user.post('/api/v1/auth/login',json={'token':'long-local-integration-test-secret-1234567890'})
        assert login.status_code==200
        assert 'httponly' in login.headers['set-cookie'].lower()
        assert 'secure' in login.headers['set-cookie'].lower()
        assert user.get('/api/v1/ai/status').status_code==200
        bad=user.post('/api/v1/datasets/import',files={'file':('x.csv',b'x\n1\n')},headers={'Origin':'https://evil.example'})
        assert bad.status_code==403
        good=user.post('/api/v1/datasets/import',files={'file':('x.csv',b'x\n1\n')},headers={'Origin':'https://testserver'})
        assert good.status_code==201,good.text
        assert user.post('/api/v1/auth/logout',headers={'Origin':'https://testserver'}).status_code==200
        assert user.get('/api/v1/ai/status').status_code==401

def test_fail_closed_for_missing_public_secret(monkeypatch):
    monkeypatch.delenv('AXIOM_ACCESS_TOKEN')
    with TestClient(app,base_url='https://testserver') as user:
        assert user.get('/api/v1/ai/status').status_code==503

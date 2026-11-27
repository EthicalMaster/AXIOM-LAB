"""Defensive regression checks; isolated synthetic records, no network targets."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.access import verify_session, new_session
from app.persistence.dataset_store import read_original_dataset, DatasetStorageError

TOKEN = 'synthetic-release-fixture-' + 'x'*32

@pytest.fixture
def protected(monkeypatch, tmp_path):
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '1')
    monkeypatch.setenv('AXIOM_ACCESS_TOKEN', TOKEN)
    monkeypatch.setenv('AXIOM_PUBLIC_ORIGIN', 'https://studio.example')
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))
    with TestClient(app, base_url='https://studio.example') as c:
        yield c


def test_private_endpoints_and_headers(protected):
    for path in ('/api/v1/experiments', '/api/v1/ai/status', '/api/v1/datasets/'+'a'*32):
        r=protected.get(path)
        assert r.status_code == 401
        assert r.headers['cache-control']=='no-store'
        assert r.headers['x-content-type-options']=='nosniff'
        assert "frame-ancestors 'none'" in r.headers['content-security-policy']
    assert protected.get('/openapi.json').status_code==404


def test_origin_and_cookie_contract(protected):
    r=protected.post('/api/v1/auth/login',json={'token':TOKEN},headers={'Origin':'https://other.example'})
    assert r.status_code==403 and 'set-cookie' not in r.headers
    r=protected.post('/api/v1/auth/login',json={'token':TOKEN},headers={'Origin':'https://studio.example'})
    assert r.status_code==200
    cookie=r.headers['set-cookie'].lower()
    assert all(x in cookie for x in ('httponly','secure','samesite=strict'))
    assert protected.post('/api/v1/math/evaluate',json={'expression':'2+2'},headers={'Origin':'https://other.example'}).status_code==403
    assert protected.post('/api/v1/math/evaluate',json={'expression':'2+2'},headers={'Origin':'https://studio.example'}).status_code==200


def test_session_expiry_and_rotation(protected, monkeypatch):
    import app.core.access as access
    monkeypatch.setattr(access.time,'time',lambda:100000.0)
    session=new_session(); assert verify_session(session)
    monkeypatch.setattr(access.time,'time',lambda:100000.0+access.TTL_SECONDS+1)
    assert not verify_session(session)
    monkeypatch.setattr(access.time,'time',lambda:100000.0)
    monkeypatch.setenv('AXIOM_ACCESS_TOKEN','different-fixture-'+'z'*32)
    assert not verify_session(session)


def test_invalid_origin_without_config(protected,monkeypatch):
    monkeypatch.delenv('AXIOM_PUBLIC_ORIGIN')
    r=protected.post('/api/v1/auth/login',json={'token':TOKEN},headers={'Origin':'https://[invalid'})
    assert r.status_code==403


def test_storage_rejects_invalid_identifier():
    with pytest.raises(DatasetStorageError):
        read_original_dataset('not-an-opaque-id',{'format':'csv'})

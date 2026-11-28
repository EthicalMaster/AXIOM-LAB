from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import asyncio
import httpx
import pytest
from fastapi import HTTPException
from app.core.google_auth import verify_google, workspace_allowed

ID='12345678-1234-4234-8234-123456789abc'
@pytest.fixture(autouse=True)
def config(monkeypatch):
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','1')
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','sb_publishable_test')
    monkeypatch.delenv('AXIOM_GOOGLE_OWNER_ID',raising=False)

def req(token='Bearer example-token'):
    return SimpleNamespace(headers={'authorization':token})

def check(response):
    with patch('app.core.google_auth.httpx.AsyncClient') as cls:
        get=AsyncMock(return_value=response)
        cls.return_value.__aenter__.return_value.get=get
        identity=asyncio.run(verify_google(req()))
        get.assert_awaited_once_with('https://example.supabase.co/auth/v1/user',headers={'apikey':'sb_publishable_test','Authorization':'Bearer example-token'})
        return identity

def test_verified_owner_only(monkeypatch):
    assert check(httpx.Response(200,json={'id':ID}))==ID
    assert not workspace_allowed(ID)
    monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',ID)
    assert workspace_allowed(ID)
    assert not workspace_allowed('12345678-1234-4234-8234-123456789abd')

@pytest.mark.parametrize('status,body,expected',[(401,{},401),(403,{},401),(429,{},503),(500,{},503),(200,{'id':'bad'},401),(200,{'id':ID,'is_anonymous':True},401)])
def test_rejects_invalid_or_unavailable(status,body,expected):
    with pytest.raises(HTTPException) as e:check(httpx.Response(status,json=body))
    assert e.value.status_code==expected

def test_missing_token():
    with pytest.raises(HTTPException) as e:asyncio.run(verify_google(req('')))
    assert e.value.status_code==401

def test_disabled(monkeypatch):
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','0')
    with pytest.raises(HTTPException) as e:asyncio.run(verify_google(req()))
    assert e.value.status_code==503

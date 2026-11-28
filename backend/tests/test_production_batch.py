import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from fastapi import HTTPException
from app.core import production as p, tenant, google_auth

A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'

@pytest.fixture(autouse=True)
def settings(monkeypatch):
    for key in ('AXIOM_OPEN_REGISTRATION','AXIOM_DISTRIBUTED_RPM','AXIOM_CLOUD_STORAGE','AXIOM_BLOCKED_USER_IDS','AXIOM_MULTI_USER_IDS'):
        monkeypatch.delenv(key,raising=False)
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','1');monkeypatch.setenv('AXIOM_MULTI_USER','1');monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',A)
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co');monkeypatch.setenv('SUPABASE_SECRET_KEY','sb_secret_fixture');monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','sb_publishable_fixture')

def open_mode(monkeypatch):
    for k in ('AXIOM_OPEN_REGISTRATION','AXIOM_CLOUD_STORAGE','AXIOM_DISTRIBUTED_RPM'):monkeypatch.setenv(k,'1')

def test_default_invited_only():
    assert tenant.admitted(A) and not tenant.admitted(B)

def test_open_requires_all_controls(monkeypatch):
    open_mode(monkeypatch)
    assert p.registration_ready() and tenant.admitted(B)
    monkeypatch.setenv('AXIOM_DISTRIBUTED_RPM','0')
    assert not p.registration_ready() and not tenant.admitted(B)

def test_blocked_even_if_owner_or_open(monkeypatch):
    open_mode(monkeypatch);monkeypatch.setenv('AXIOM_BLOCKED_USER_IDS',A)
    assert not tenant.admitted(A) and tenant.admitted(B) and not tenant.admitted('../escape')

def test_distributed_disabled():
    with patch.object(p,'rpc',new_callable=AsyncMock) as rpc:
        assert asyncio.run(p.take_distributed(A));rpc.assert_not_awaited()

def test_distributed_scoped(monkeypatch):
    monkeypatch.setenv('AXIOM_DISTRIBUTED_RPM','1');monkeypatch.setenv('AXIOM_USER_RPM','60')
    with patch.object(p,'rpc',new_callable=AsyncMock,return_value=False) as rpc:
        assert asyncio.run(p.take_distributed(A)) is False
        rpc.assert_awaited_once_with('axiom_take_request',{'p_owner':A,'p_limit':60})

def test_distributed_fails_closed(monkeypatch):
    monkeypatch.setenv('AXIOM_DISTRIBUTED_RPM','1')
    with patch.object(p,'rpc',new_callable=AsyncMock,return_value={'unexpected':True}):
        with pytest.raises(HTTPException) as exc:asyncio.run(p.take_distributed(A))
        assert exc.value.status_code==503

def test_cloud_usage(monkeypatch):
    monkeypatch.setenv('AXIOM_CLOUD_STORAGE','1')
    with patch.object(p,'rpc',new_callable=AsyncMock,return_value={'datasets':2,'bytes':500,'pending':1}) as rpc:
        assert asyncio.run(p.storage_usage(B))=={'datasets':2,'bytes':500,'pending':1,'mode':'cloud'}
        rpc.assert_awaited_once_with('axiom_workspace_usage',{'p_owner':B})

def test_cloud_invalid_usage(monkeypatch):
    monkeypatch.setenv('AXIOM_CLOUD_STORAGE','1')
    with patch.object(p,'rpc',new_callable=AsyncMock,return_value={'datasets':-1,'bytes':500,'pending':1}):
        with pytest.raises(HTTPException):asyncio.run(p.storage_usage(B))

def test_verified_google_required_for_public(monkeypatch):
    open_mode(monkeypatch)
    request=SimpleNamespace(headers={'authorization':'Bearer token'})
    with patch.object(google_auth.httpx,'AsyncClient') as factory:
        get=AsyncMock(return_value=httpx.Response(200,json={'id':B,'email_confirmed_at':'2026-01-01','identities':[{'provider':'google'}]}))
        factory.return_value.__aenter__.return_value.get=get
        assert asyncio.run(google_auth.verify_google(request))==B
        get.return_value=httpx.Response(200,json={'id':B,'email_confirmed_at':'2026-01-01','identities':[{'provider':'email'}],'user_metadata':{'provider':'google'}})
        with pytest.raises(HTTPException) as exc:asyncio.run(google_auth.verify_google(request))
        assert exc.value.status_code==403

def test_rpc_failure_has_no_secrets():
    with patch.object(p.httpx,'AsyncClient') as factory:
        post=AsyncMock(return_value=httpx.Response(500,text='private diagnostic'))
        factory.return_value.__aenter__.return_value.post=post
        with pytest.raises(HTTPException) as exc:asyncio.run(p.rpc('axiom_take_request',{'p_owner':A}))
        assert exc.value.status_code==503 and 'private diagnostic' not in str(exc.value)

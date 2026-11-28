import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from fastapi import FastAPI, Request, HTTPException
from starlette.concurrency import run_in_threadpool
from app.core.tenant import admitted, storage_root, tenant_scope
from app.core.tenant_access import tenant_request

A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'
C='12345678-1234-4234-8234-123456789abe'

@pytest.fixture(autouse=True)
def config(monkeypatch):
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','1')
    monkeypatch.setenv('AXIOM_MULTI_USER','1')
    monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',A)
    monkeypatch.setenv('AXIOM_MULTI_USER_IDS',B)


def test_explicit_admission():
    assert admitted(A) and admitted(B)
    assert not admitted(C) and not admitted('../outside')


def test_no_context_or_legacy_fallback(tmp_path):
    with pytest.raises(PermissionError): storage_root(tmp_path)
    with pytest.raises(PermissionError):
        with tenant_scope(C): pass
    with tenant_scope(A):
        assert storage_root(tmp_path)==tmp_path/'tenants'/A
    with pytest.raises(PermissionError): storage_root(tmp_path)


def test_local_mode_unchanged(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_MULTI_USER','0')
    assert storage_root(tmp_path)==tmp_path


def test_threadpool_and_concurrent_contexts(tmp_path):
    async def run(user):
        with tenant_scope(user):
            await asyncio.sleep(0)
            root=await run_in_threadpool(storage_root,tmp_path)
            await asyncio.sleep(0)
            assert storage_root(tmp_path)==root
            return root
    async def both(): return await asyncio.gather(run(A),run(B))
    assert asyncio.run(both())==[tmp_path/'tenants'/A,tmp_path/'tenants'/B]


def test_symlink_namespace_denied(tmp_path):
    other=tmp_path/'other';other.mkdir()
    try: (tmp_path/'tenants').symlink_to(other,target_is_directory=True)
    except OSError: pytest.skip('OS does not allow test symlinks')
    with tenant_scope(A), pytest.raises(PermissionError): storage_root(tmp_path)


def test_middleware_contract(tmp_path,monkeypatch):
    app=FastAPI()
    app.middleware('http')(tenant_request)
    @app.get('/api/v1/data')
    def data(): return {'root':str(storage_root(tmp_path))}
    @app.get('/api/v1/health')
    def health(): return {'status':'ok'}
    async def fake_verify(request):
        value=request.headers.get('authorization','')
        if value not in {A,B,C}: raise HTTPException(401,'Invalid session')
        return value
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
            assert (await client.get('/api/v1/data')).status_code==401
            assert (await client.get('/api/v1/data',headers={'authorization':C})).status_code==403
            denied=await client.get('/api/v1/auth/google/verify',headers={'authorization':C})
            assert denied.json()['workspace_allowed'] is False
            a,b=await asyncio.gather(*(client.get('/api/v1/data',headers={'authorization':i,'x-user-id':C}) for i in (A,B)))
            assert a.json()['root']==str(tmp_path/'tenants'/A)
            assert b.json()['root']==str(tmp_path/'tenants'/B)
            assert (await client.get('/api/v1/auth/me',headers={'authorization':A})).json()['user_id']==A
            assert (await client.post('/api/v1/auth/login',headers={'authorization':A})).status_code==404
            assert (await client.get('/api/v1/health')).status_code==200
            monkeypatch.setenv('AXIOM_GOOGLE_AUTH','0')
            assert (await client.get('/api/v1/data',headers={'authorization':A})).status_code==503
    with patch('app.core.tenant_access.verify_google',side_effect=fake_verify): asyncio.run(run())

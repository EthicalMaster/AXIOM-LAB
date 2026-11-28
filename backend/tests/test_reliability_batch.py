import asyncio
import hashlib
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
import httpx
import pytest
from app.core import upstream

ROOT=Path(__file__).resolve().parents[2]
recovery=runpy.run_path(str(ROOT/'scripts/axiom_pending_recovery.py'))
verify_pending=recovery['verify_pending']
D='a'*32
A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'
RAW=b'x\n1\n2\n'


def test_bound_clients_reused_and_reset():
    async def run():
        app=SimpleNamespace(state=SimpleNamespace())
        async with upstream.lifespan(app):
            pools=app.state.axiom_upstream
            with upstream.bind_clients(pools):
                async with upstream.async_client('auth') as first, upstream.async_client('auth') as second:
                    assert first is second and first is pools['auth']
                async with upstream.async_client('rpc') as rpc:
                    assert rpc is not first
                with upstream.cloud_client() as cloud:
                    assert cloud is pools['cloud']
                assert await asyncio.to_thread(lambda: upstream._clients.get()) is pools
            assert upstream._clients.get() is None
        assert app.state.axiom_upstream is None and first.is_closed and rpc.is_closed and cloud.is_closed
    asyncio.run(run())


def test_cookie_isolation_and_per_request_bearer():
    async def run():
        observed=[]
        def respond(req):
            observed.append((req.headers.get('cookie'),req.headers.get('authorization')))
            return httpx.Response(200,headers={'Set-Cookie':'session=private; Path=/; Secure'})
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond),**upstream.options(5)) as client:
            await client.get('https://example.supabase.co/auth/v1/user',headers={'Authorization':'Bearer A'})
            await client.get('https://example.supabase.co/auth/v1/user',headers={'Authorization':'Bearer B'})
            assert len(client.cookies)==0
        assert observed==[(None,'Bearer A'),(None,'Bearer B')]
    asyncio.run(run())


def test_metrics_bounded_and_sanitized():
    for _ in range(300):
        with upstream.measure('auth') as s:s['ok']=True
    with pytest.raises(ValueError):
        with upstream.measure('auth'):raise ValueError('never expose token')
    result=upstream.snapshot()['upstream']['auth']
    assert result['calls']>=301 and result['failures']>=1 and result['sample_count']==256
    assert 'token' not in str(result) and result['p95_ms']>=0


def fake_cloud(raw=RAW):
    c=Mock(); c.owner.return_value=A
    c.one.return_value={'id':D,'ready':False,'size_bytes':len(RAW),'metadata':{'id':D,'format':'csv','size_bytes':len(RAW),'sha256':hashlib.sha256(RAW).hexdigest()}}
    c.object_path.return_value='axiom-originals/'+A+'/'+D+'/original.csv'
    def req(method,path,**kw):
        if method=='GET':return SimpleNamespace(content=raw)
        return SimpleNamespace(json=lambda:[{'id':D,'ready':True}])
    c.request.side_effect=req
    return c


def test_pending_audit_never_writes():
    c=fake_cloud();assert verify_pending(c,D)=='verified_pending'
    assert [call.args[0] for call in c.request.call_args_list]==['GET']


def test_pending_recovery_rejects_corruption():
    c=fake_cloud(b'bad');assert verify_pending(c,D,finalize=True)=='integrity_mismatch'
    assert c.request.call_count==1


def test_pending_recovery_binds_owner_and_fingerprint():
    c=fake_cloud();assert verify_pending(c,D,finalize=True)=='finalized'
    call=c.request.call_args
    assert call.args[0]=='PATCH' and call.kwargs['params']['owner_id']=='eq.'+A
    assert call.kwargs['params']['ready']=='eq.false' and call.kwargs['params']['metadata->>sha256']=='eq.'+hashlib.sha256(RAW).hexdigest()
    assert call.kwargs['json']=={'ready':True}


def test_pending_missing_never_calls_storage():
    c=fake_cloud();c.one.return_value=None
    assert verify_pending(c,D)=='not_pending';c.request.assert_not_called()


def test_pending_bad_identifier_or_metadata():
    c=fake_cloud()
    with pytest.raises(ValueError):verify_pending(c,'../escape')
    c.one.assert_not_called();c.one.return_value['metadata']['id']='b'*32
    with pytest.raises(ValueError):verify_pending(c,D)
    c.request.assert_not_called()


def test_operator_diagnostics_not_granted_by_open_registration(monkeypatch):
    from app.core import tenant_access as t
    for k in ('AXIOM_GOOGLE_AUTH','AXIOM_MULTI_USER','AXIOM_CLOUD_STORAGE','AXIOM_DISTRIBUTED_RPM','AXIOM_OPEN_REGISTRATION'):
        monkeypatch.setenv(k,'1')
    monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',A)
    monkeypatch.delenv('AXIOM_BLOCKED_USER_IDS',raising=False)
    request=SimpleNamespace(url=SimpleNamespace(path='/api/v1/auth/ops'),method='GET')
    call=AsyncMock()
    with patch.object(t,'verify_google',new_callable=AsyncMock,return_value=B):
        assert asyncio.run(t.tenant_request(request,call)).status_code==403
    with patch.object(t,'verify_google',new_callable=AsyncMock,return_value=A):
        assert asyncio.run(t.tenant_request(request,call)).status_code==200
    call.assert_not_awaited()

import asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.core.request_guard import RequestGuard, WindowBudget


def make_app():
    app = FastAPI()
    @app.get('/api/v1/health')
    def health():
        return {'ok': True}
    @app.get('/api/v1/work')
    def work():
        return {'ok': True}
    @app.post('/api/v1/work')
    async def body(request: Request):
        return {'length': len(await request.body())}
    @app.post('/api/v1/math/calculate')
    def compute():
        return {'ok': True}
    app.add_middleware(RequestGuard)
    return app


def test_public_request_budget(monkeypatch):
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '1')
    monkeypatch.setenv('AXIOM_API_RPM', '2')
    with TestClient(make_app()) as client:
        for _ in range(2):
            response = client.get('/api/v1/work')
            assert response.status_code == 200
            assert response.headers['x-request-id']
            assert response.headers['cache-control'] == 'no-store'
        response = client.get('/api/v1/work')
        assert response.status_code == 429
        assert response.headers['retry-after'] == '60'
        assert response.json()['request_id'] == response.headers['x-request-id']
        assert client.get('/api/v1/health').status_code == 200
        assert client.get('/docs').status_code == 404


def test_compute_budget_and_body_limits(monkeypatch):
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '1')
    monkeypatch.setenv('AXIOM_COMPUTE_RPM', '1')
    with TestClient(make_app()) as client:
        assert client.post('/api/v1/math/calculate').status_code == 200
        assert client.post('/api/v1/math/calculate').status_code == 429
        assert client.post('/api/v1/work', content=b'x'*65537).status_code == 413
        assert client.post('/api/v1/work', content=b'abc').json() == {'length': 3}
        assert client.get('/api/v1/work?q='+'x'*4097).status_code == 414


def test_window_expires(monkeypatch):
    import app.core.request_guard as guard
    now = [0.0]
    monkeypatch.setattr(guard, 'monotonic', lambda: now[0])
    budget = WindowBudget(1, 60)
    assert budget.take()
    assert not budget.take()
    now[0] = 60.0
    assert budget.take()


def test_concurrency_backpressure(monkeypatch):
    monkeypatch.setenv('AXIOM_MAX_INFLIGHT', '1')
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '0')
    import httpx
    async def exercise():
        ready, release = asyncio.Event(), asyncio.Event()
        app = FastAPI()
        @app.get('/api/v1/work')
        async def work():
            ready.set()
            await release.wait()
            return {'ok': True}
        app.add_middleware(RequestGuard)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            pending = asyncio.create_task(client.get('/api/v1/work'))
            await ready.wait()
            try:
                rejected = await client.get('/api/v1/work')
                assert rejected.status_code == 503
                assert rejected.headers['retry-after'] == '3'
            finally:
                release.set()
                assert (await pending).status_code == 200
            assert (await client.get('/api/v1/work')).status_code == 200
    asyncio.run(exercise())


def test_dataset_quota_returns_clear_error(monkeypatch, tmp_path):
    from app.main import app
    monkeypatch.setenv('AXIOM_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('AXIOM_PUBLIC_MODE', '0')
    monkeypatch.setenv('AXIOM_DATASET_MAX_COUNT', '1')
    with TestClient(app) as client:
        upload = {'file': ('small.csv', b'x\n1\n2\n')}
        assert client.post('/api/v1/datasets/import', files=upload).status_code == 201
        denied = client.post('/api/v1/datasets/import', files=upload)
        assert denied.status_code == 507
        assert denied.json()['detail']['code'] == 'storage_quota'
        assert len(list((tmp_path/'datasets').glob('*/original.csv'))) == 1


def test_unicode_access_token_does_not_raise(monkeypatch):
    from app.core.access import authorized_token
    monkeypatch.setenv('AXIOM_ACCESS_TOKEN', 'x'*32)
    assert not authorized_token('é')

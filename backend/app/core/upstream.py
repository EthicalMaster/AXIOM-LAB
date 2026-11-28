"""Lifespan-owned HTTP pools, no ambient cookies and no identity caching."""
from collections import deque
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from http.cookiejar import CookieJar, DefaultCookiePolicy
from threading import Lock
from time import perf_counter
import math
import httpx


class NoCookies(DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        return False

    def return_ok(self, cookie, request):
        return False


def options(timeout):
    return dict(timeout=timeout, follow_redirects=False, trust_env=False,
                limits=httpx.Limits(max_connections=12, max_keepalive_connections=6, keepalive_expiry=20),
                cookies=CookieJar(policy=NoCookies()))


_clients = ContextVar('axiom_upstream_clients', default=None)


@asynccontextmanager
async def lifespan(app):
    # Separate transports for user bearer tokens, service-role RPCs and storage.
    async with httpx.AsyncClient(**options(5)) as auth, httpx.AsyncClient(**options(5)) as rpc:
        with httpx.Client(**options(15)) as cloud:
            app.state.axiom_upstream = {'auth': auth, 'rpc': rpc, 'cloud': cloud}
            try:
                yield
            finally:
                app.state.axiom_upstream = None


@contextmanager
def bind_clients(clients):
    token = _clients.set(clients)
    try:
        yield
    finally:
        _clients.reset(token)


@asynccontextmanager
async def async_client(kind):
    if kind not in ('auth', 'rpc'):
        raise ValueError('Unknown upstream class')
    clients = _clients.get()
    if clients is not None:
        yield clients[kind]
    else:
        # Direct function tests and standalone scripts do not run ASGI lifespan.
        async with httpx.AsyncClient(**options(5)) as client:
            yield client


@contextmanager
def cloud_client():
    clients = _clients.get()
    if clients is not None:
        yield clients['cloud']
    else:
        with httpx.Client(**options(15)) as client:
            yield client


_lock = Lock()
_metrics = {name: {'calls': 0, 'failures': 0, 'samples': deque(maxlen=256)}
            for name in ('auth', 'rpc', 'cloud')}


@contextmanager
def measure(kind):
    # Only fixed categories, elapsed milliseconds and success/failure. No URLs,
    # credentials, IDs, headers, bodies, or exception strings.
    state = {'ok': False}
    start = perf_counter()
    try:
        yield state
    finally:
        with _lock:
            entry = _metrics[kind]
            entry['calls'] += 1
            entry['failures'] += int(not state['ok'])
            entry['samples'].append((perf_counter()-start)*1000)


def snapshot():
    with _lock:
        result = {}
        for name, value in _metrics.items():
            samples = sorted(value['samples'])
            result[name] = {'calls': value['calls'], 'failures': value['failures'],
                            'sample_count': len(samples),
                            'p95_ms': round(samples[math.ceil(.95*len(samples))-1], 2) if samples else None}
    return {'scope': 'current backend process', 'upstream': result}

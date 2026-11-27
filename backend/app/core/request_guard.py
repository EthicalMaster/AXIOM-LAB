"""Bounded single-process request admission and uniform response metadata.
Not a distributed rate limiter, TLS terminator, or multi-tenant boundary.
"""
from collections import deque
from threading import Lock
from time import monotonic, perf_counter
from uuid import uuid4
import logging
import asyncio
import os
from starlette.responses import JSONResponse
from app.core.access import public_mode

log = logging.getLogger(__name__)

class WindowBudget:
    def __init__(self, limit: int, seconds: float):
        self.limit, self.seconds = limit, seconds
        self.events = deque()
        self.lock = Lock()

    def take(self) -> bool:
        now = monotonic()
        with self.lock:
            while self.events and self.events[0] <= now - self.seconds:
                self.events.popleft()
            if len(self.events) >= self.limit:
                return False
            self.events.append(now)
            return True


def setting(name: str, default: int, maximum: int) -> int:
    try:
        return max(1, min(maximum, int(os.getenv(name, str(default)))))
    except ValueError:
        return default


def max_inflight() -> int:
    return setting('AXIOM_MAX_INFLIGHT', 4, 16)


class RequestGuard:
    def __init__(self, app):
        self.app = app
        self.active = 0
        self.lock = Lock()
        # Fixed, bounded process-wide buckets: no untrusted identity/IP keys.
        self.login_budget = WindowBudget(setting('AXIOM_LOGIN_RPM', 12, 120), 60)
        self.api_budget = WindowBudget(setting('AXIOM_API_RPM', 120, 1200), 60)
        self.upload_budget = WindowBudget(setting('AXIOM_UPLOAD_RPM', 6, 60), 60)
        self.compute_budget = WindowBudget(setting('AXIOM_COMPUTE_RPM', 30, 300), 60)
        self.guide_budget = WindowBudget(setting('AXIOM_GUIDE_RPM', 20, 120), 60)

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        path, method = scope['path'], scope['method']
        request_id, started = uuid4().hex[:12], perf_counter()
        response_started = False
        status = 0

        async def send_checked(message):
            nonlocal response_started, status
            if message['type'] == 'http.response.start':
                response_started = True
                status = message['status']
                headers = dict(message.get('headers', []))
                headers.update({b'x-request-id': request_id.encode(),
                                b'server-timing': f'app;dur={(perf_counter()-started)*1000:.2f}'.encode(),
                                b'cache-control': b'no-store', b'x-content-type-options': b'nosniff',
                                b'x-frame-options': b'DENY', b'referrer-policy': b'no-referrer',
                                b'permissions-policy': b'camera=(), microphone=(), geolocation=()'})
                # Preserve duplicate headers (e.g. Set-Cookie) from downstream.
                existing = message.get('headers', [])
                managed = {b'x-request-id', b'server-timing', b'cache-control', b'x-content-type-options', b'x-frame-options', b'referrer-policy', b'permissions-policy'}
                message['headers'] = [(k,v) for k,v in existing if k not in managed] + [(k,headers[k]) for k in managed]
            await send(message)

        async def reject(code, message, retry=None):
            headers = {'Retry-After': str(retry)} if retry else None
            await JSONResponse({'detail': {'code': 'request_rejected', 'message': message}, 'request_id': request_id}, status_code=code, headers=headers)(scope, receive, send_checked)

        if public_mode() and path in ('/docs', '/redoc', '/openapi.json', '/docs/oauth2-redirect'):
            return await reject(404, 'Not found')
        if not path.startswith('/api/v1/'):
            return await self.app(scope, receive, send_checked)
        if len(scope.get('query_string', b'')) > 4096:
            return await reject(414, 'Query is too long.')
        if public_mode():
            budget = None
            if path == '/api/v1/auth/login' and method == 'POST':
                budget = self.login_budget
            elif path == '/api/v1/datasets/import' and method == 'POST':
                budget = self.upload_budget
            elif path.startswith('/api/v1/ai/') and method == 'POST':
                budget = self.guide_budget
            elif '/ml/' in path or path.startswith('/api/v1/math'):
                budget = self.compute_budget
            if budget is not None and not budget.take():
                return await reject(429, 'This operation has reached its request allowance.', 60)
            if path not in ('/api/v1/health', '/api/v1/auth/status') and not self.api_budget.take():
                return await reject(429, 'API request allowance reached. Retry later.', 60)
        # Leave health/status responsive, even when computation is full.
        admitted = path not in ('/api/v1/health', '/api/v1/auth/status')
        if admitted:
            with self.lock:
                accepted = self.active < max_inflight()
                if accepted:
                    self.active += 1
            if not accepted:
                return await reject(503, 'Computational capacity reached; retry later.', 3)
        try:
            if method in ('POST','PUT','PATCH','DELETE'):
                limit = 6 * 1024 * 1024 if path == '/api/v1/datasets/import' else 64 * 1024
                length = dict(scope['headers']).get(b'content-length')
                if length is not None:
                    try:
                        size = int(length)
                    except ValueError:
                        return await reject(400, 'Invalid request length.')
                    if size < 0 or size > limit:
                        return await reject(413, 'Request exceeds the allowed size.')
                # Enforce actual body size even without a Content-Length header.
                chunks = bytearray()
                try:
                    async with asyncio.timeout(15):
                        while True:
                            event = await receive()
                            if event['type'] == 'http.disconnect':
                                return
                            chunk = event.get('body', b'')
                            if len(chunks) + len(chunk) > limit:
                                return await reject(413, 'Request exceeds the allowed size.')
                            chunks.extend(chunk)
                            if not event.get('more_body', False):
                                break
                except TimeoutError:
                    return await reject(408, 'Request body did not arrive in time.')
                delivered = False
                async def replay():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {'type':'http.request','body':bytes(chunks),'more_body':False}
                    return await receive()
                await self.app(scope, replay, send_checked)
            else:
                await self.app(scope, receive, send_checked)
        except Exception as exc:
            log.error('request_failed id=%s type=%s', request_id, type(exc).__name__)
            if response_started:
                raise
            await reject(500, 'Unexpected server error. Reference the request ID in System checks.')
        finally:
            if admitted:
                with self.lock:
                    self.active -= 1
            log.info('request id=%s method=%s status=%s elapsed_ms=%.2f', request_id, method, status, (perf_counter()-started)*1000)

"""Multi-user beta HTTP authorization, distinct from legacy cookie access."""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.google_auth import google_enabled, verify_google
from app.core.tenant import admitted, tenant_scope
from app.core.tenant_budget import admit_request


def reject(status: int, detail: str):
    return JSONResponse({'detail':detail}, status_code=status, headers={'Cache-Control':'no-store'})


async def tenant_request(request: Request, call_next):
    if not google_enabled():
        return reject(503, 'Multi-user mode requires managed authentication.')
    path = request.url.path
    if path in ('/docs','/redoc','/openapi.json','/docs/oauth2-redirect'):
        return reject(404, 'Not found.')
    if not path.startswith('/api/v1/') or (path == '/api/v1/health' and request.method == 'GET'):
        return await call_next(request)
    try:
        identity = await verify_google(request)
    except HTTPException as exc:
        return reject(exc.status_code, exc.detail)
    allowed = admitted(identity)
    if path == '/api/v1/auth/google/verify' and request.method == 'GET':
        return JSONResponse({'user_id':identity, 'workspace_allowed':allowed, 'mode':'multi-user beta'}, headers={'Cache-Control':'no-store'})
    if not allowed:
        return reject(403, 'Workspace invitation required.')
    if path == '/api/v1/auth/status' and request.method == 'GET':
        # Managed bearer auth is the gate; do not request a shared access cookie.
        return JSONResponse({'required':False,'authenticated':True,'mode':'multi-user beta'}, headers={'Cache-Control':'no-store'})
    if path in ('/api/v1/auth/login','/api/v1/auth/logout'):
        return reject(404, 'Use Google authentication in multi-user mode.')
    if path == '/api/v1/auth/me' and request.method == 'GET':
        return JSONResponse({'user_id':identity,'mode':'multi-user beta','workspace':'private'}, headers={'Cache-Control':'no-store'})
    request.state.user_id = identity
    with admit_request(identity) as allowed:
        if not allowed:
            return JSONResponse({"detail":"Private workspace request allowance reached."},status_code=429,headers={"Retry-After":"3","Cache-Control":"no-store"})
        with tenant_scope(identity):
            return await call_next(request)

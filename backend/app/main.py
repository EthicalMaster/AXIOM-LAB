"""AXIOM LAB ASGI application — bounded local-first scientific engine through Phase 07D release candidate."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.access import public_mode, access_secret, authorized_token, verify_session, same_origin, COOKIE_NAME
from app.api.access import router as auth_router
from fastapi.exceptions import RequestValidationError
from app.core.request_guard import RequestGuard
from app.api.ai import router as ai_router
from app.api.reports import router as reports_router
from app.api.datasets import router as dataset_router
from app.api.health import router as health_router
from app.api.statistics import router as statistics_router
from app.api.experiments import router as experiment_router
from app.api.quality import router as quality_router
from app.api.distributions import router as distribution_router
from app.api.hypothesis import router as hypothesis_router
from app.api.diagnostics import router as diagnostics_router
from app.api.mathematics import router as mathematics_router
from app.api.ml import router as ml_router

app = FastAPI(title='AXIOM LAB API',
              description='Bounded scientific computation, data inspection and local experiment records.',
              version='0.1.0')

for router in (health_router, dataset_router, statistics_router, experiment_router,
               quality_router, distribution_router, hypothesis_router, diagnostics_router,
               mathematics_router, ml_router):
    app.include_router(router, prefix='/api/v1')

app.include_router(ai_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


app.include_router(auth_router, prefix="/api/v1")


@app.middleware('http')
async def protect_public_mode(request: Request, call_next):
    # Fail closed if remote exposure was requested without a strong server token.
    if public_mode() and not access_secret():
        return JSONResponse(status_code=503,content={'detail':'Public access requires a strong configured token.'})
    path=request.url.path
    if public_mode() and path.startswith('/api/v1/') and path not in {
        '/api/v1/health','/api/v1/auth/status','/api/v1/auth/login'}:
        bearer=request.headers.get('authorization','')
        using_bearer=bearer.startswith('Bearer ') and authorized_token(bearer[7:])
        using_cookie=verify_session(request.cookies.get(COOKIE_NAME))
        if not using_bearer and not using_cookie:
            return JSONResponse(status_code=401,content={'detail':'Authentication required.'})
        if not using_bearer and request.method not in ('GET','HEAD','OPTIONS') and not same_origin(request):
            return JSONResponse(status_code=403,content={'detail':'Cross-origin mutation denied.'})
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Never reflect submitted credentials or raw invalid values.
    return JSONResponse(status_code=422, content={'detail': {'code':'invalid_request','message':'Check required fields and input limits.'}})


app.add_middleware(RequestGuard)

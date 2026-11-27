"""Cookie session is HttpOnly, Secure, SameSite=Strict in public mode."""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from app.core.access import public_mode, authorized_token, verify_session, new_session, COOKIE_NAME, TTL_SECONDS, same_origin

router=APIRouter(prefix='/auth',tags=['access'])

class LoginRequest(BaseModel):
    token: str = Field(min_length=1,max_length=4096)

@router.get('/status')
def status(request: Request) -> dict:
    enabled=public_mode()
    authenticated=not enabled or verify_session(request.cookies.get(COOKIE_NAME))
    return {'required':enabled,'authenticated':authenticated,'mode':'single-user local' if not enabled else 'protected single-user'}

@router.post('/login')
def login(payload:LoginRequest,response:Response,request:Request) -> dict:
    if not public_mode():
        return {'authenticated':True}
    if request.headers.get('origin') and not same_origin(request):
        raise HTTPException(403,detail='Cross-origin login denied.')
    if not authorized_token(payload.token):
        raise HTTPException(401,detail='Invalid access token')
    response.set_cookie(key=COOKIE_NAME,value=new_session(),max_age=TTL_SECONDS,
                        secure=True,httponly=True,samesite='strict',path='/')
    return {'authenticated':True}

@router.post('/logout')
def logout(response:Response) -> dict:
    response.delete_cookie(COOKIE_NAME,secure=True,httponly=True,samesite='strict',path='/')
    return {'authenticated':False}

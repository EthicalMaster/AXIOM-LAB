"""Optional single-user access gate for deliberately published instances.

This is NOT multi-tenant user management. For shared/public production, place the
application behind a trusted TLS gateway and replace this with managed identity.
"""
from __future__ import annotations
import hashlib
import hmac
import os
import secrets
import time
from urllib.parse import urlsplit

COOKIE_NAME='axiom_session'
TTL_SECONDS=8*60*60


def public_mode() -> bool:
    return os.getenv('AXIOM_PUBLIC_MODE','').strip().lower() not in ('','0','false','no','off')


def access_secret() -> str | None:
    token=os.getenv('AXIOM_ACCESS_TOKEN','')
    return token if len(token)>=32 else None


def authorized_token(candidate: str) -> bool:
    secret=access_secret()
    return bool(secret and hmac.compare_digest(secret.encode(),candidate.encode()))


def new_session() -> str:
    secret=access_secret()
    if not secret:
        raise ValueError('Access token is not configured')
    payload=f'{int(time.time())}.{secrets.token_hex(16)}'
    digest=hmac.new(secret.encode(),payload.encode(),hashlib.sha256).hexdigest()
    return f'{payload}.{digest}'


def verify_session(value: str | None) -> bool:
    secret=access_secret()
    if not value or not secret or len(value)>256:
        return False
    try:
        timestamp,nonce,signature=value.split('.')
        if not timestamp.isdecimal() or len(nonce)!=32 or len(signature)!=64:
            return False
        created=int(timestamp)
        now=int(time.time())
        if created>now+10 or now-created>TTL_SECONDS:
            return False
        expected=hmac.new(secret.encode(),f'{timestamp}.{nonce}'.encode(),hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,signature)
    except (ValueError,TypeError):
        return False


def same_origin(request) -> bool:
    origin=request.headers.get('origin','')
    if not origin:
        return False
    configured=os.getenv('AXIOM_PUBLIC_ORIGIN','').strip().rstrip('/')
    if configured:
        return configured.startswith('https://') and origin == configured
    url=urlsplit(origin)
    return url.scheme == 'https' and url.netloc.lower()==request.headers.get('host','').lower()

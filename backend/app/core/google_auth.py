"""Owner-only managed identity until dataset and experiment isolation exists."""
import os
import re
from uuid import UUID
import httpx
from fastapi import HTTPException, Request


def google_enabled() -> bool:
    # Invalid non-empty values fail closed instead of silently disabling auth.
    return os.getenv('AXIOM_GOOGLE_AUTH','').strip().lower() not in ('','0','false','no','off')


def canonical_id(value: object) -> str | None:
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        return None


def workspace_allowed(user_id: str) -> bool:
    owner = canonical_id(os.getenv('AXIOM_GOOGLE_OWNER_ID',''))
    return owner is not None and owner == user_id


async def verify_google(request: Request) -> str:
    if not google_enabled():
        raise HTTPException(503, 'Managed authentication is not enabled.')
    url = os.getenv('SUPABASE_URL','').strip().rstrip('/')
    key = os.getenv('SUPABASE_PUBLISHABLE_KEY','').strip()
    if not re.fullmatch(r'https://[a-z0-9]+\.supabase\.co',url) or not key.startswith('sb_publishable_'):
        raise HTTPException(503, 'Managed authentication configuration is incomplete.')
    scheme, _, token = request.headers.get('authorization','').partition(' ')
    if scheme.lower() != 'bearer' or not token or len(token)>8192 or any(c.isspace() for c in token):
        raise HTTPException(401, 'Authentication required.')
    # The Auth service validates the access token; do not trust unverified JWT claims.
    try:
        async with httpx.AsyncClient(timeout=5.0,follow_redirects=False,trust_env=False) as client:
            result=await client.get(url+'/auth/v1/user',headers={'apikey':key,'Authorization':'Bearer '+token})
    except httpx.HTTPError:
        raise HTTPException(503, 'Managed authentication unavailable.') from None
    if result.status_code in (400,401,403):
        raise HTTPException(401, 'Invalid or expired session.')
    if result.status_code!=200:
        raise HTTPException(503, 'Managed authentication unavailable.')
    try:
        user=result.json()
        identity=canonical_id(user.get('id')) if isinstance(user,dict) else None
    except ValueError:
        identity=None
    if not identity or user.get('is_anonymous') is True:
        raise HTTPException(401, 'Invalid user identity.')
    return identity

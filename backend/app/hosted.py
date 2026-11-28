"""Container entry point. Hosted mode fails closed; local Compose opts out explicitly."""
from pathlib import Path
import os
import tempfile
from urllib.parse import urlsplit


def https_origin(value: str) -> str:
    """Canonical HTTPS origin only (no path, query, credentials or local host)."""
    value=value.strip().rstrip('/')
    try:
        url=urlsplit(value)
        host=url.hostname
        if (url.scheme!='https' or not host or '.' not in host or host.endswith('.local')
                or url.username or url.password or url.path or url.query or url.fragment
                or url.port not in (None,443) or any(c.isspace() for c in value)
                or value != 'https://'+host):
            raise ValueError
    except ValueError:
        raise ValueError('Expected a canonical HTTPS origin, without path or credentials.') from None
    return value


def preflight() -> int:
    mode=os.getenv('AXIOM_HOSTED_MODE','1')
    if mode not in ('0','1'):
        raise ValueError('AXIOM_HOSTED_MODE must be 0 or 1.')
    try:
        port=int(os.getenv('PORT','8000'))
        if not 1<=port<=65535: raise ValueError
    except ValueError:
        raise ValueError('PORT must be a valid TCP port.') from None
    if mode=='1':
        if os.getenv('AXIOM_PUBLIC_MODE')!='1':
            raise ValueError('Hosted mode requires public protection.')
        managed = os.getenv('AXIOM_MULTI_USER')=='1' and os.getenv('AXIOM_GOOGLE_AUTH')=='1'
        if not managed and len(os.getenv('AXIOM_ACCESS_TOKEN','').strip())<32:
            raise ValueError('Hosted legacy mode requires a unique strong access token.')
        from app.core.production import registration_ready, cloud_configuration, open_registration
        if open_registration() and not registration_ready():
            raise ValueError('Open registration requires managed cloud mode and distributed quotas.')
        if managed:
            import re
            if not re.fullmatch(r'https://[a-z0-9]+\.supabase\.co',os.getenv('SUPABASE_URL','')) or not os.getenv('SUPABASE_PUBLISHABLE_KEY','').startswith('sb_publishable_'):
                raise ValueError('Managed authentication configuration incomplete.')
        if os.getenv('AXIOM_CLOUD_STORAGE')=='1' or os.getenv('AXIOM_DISTRIBUTED_RPM')=='1':
            if not managed:
                raise ValueError('Cloud services require managed multi-user mode.')
            try: cloud_configuration()
            except Exception: raise ValueError('Cloud credentials incomplete.') from None
        origin=os.getenv('AXIOM_PUBLIC_ORIGIN','')
        if https_origin(origin)!=origin:
            raise ValueError('AXIOM_PUBLIC_ORIGIN must exactly match the browser origin.')
        if managed and os.getenv('AXIOM_CLOUD_STORAGE')=='1':
            return port
        path=os.getenv('AXIOM_DATA_DIR','')
        if not path or not Path(path).is_absolute() or not Path(path).is_dir():
            raise ValueError('Hosted mode requires an existing absolute data directory on a persistent volume.')
        # A writable directory is necessary, not proof of persistent storage.
        try:
            with tempfile.TemporaryFile(dir=path) as handle:
                handle.write(b'axiom'); handle.flush()
        except OSError:
            raise ValueError('Configured data directory is not writable.') from None
    return port


def main():
    try:
        port=preflight()
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    import uvicorn
    uvicorn.run('app.main:app',host='0.0.0.0',port=port,workers=1,proxy_headers=False,access_log=False)


if __name__=='__main__': main()

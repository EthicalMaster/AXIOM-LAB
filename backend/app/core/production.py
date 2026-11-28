"""Opt-in production controls; verified identities only, no JWT or secret logging."""
import os
import re
import httpx
from app.core.upstream import async_client, measure
from fastapi import HTTPException


def open_registration():
    return os.getenv('AXIOM_OPEN_REGISTRATION') == '1'


def distributed_enabled():
    return os.getenv('AXIOM_DISTRIBUTED_RPM') == '1'


def registration_ready():
    return all(os.getenv(k) == '1' for k in ('AXIOM_GOOGLE_AUTH','AXIOM_MULTI_USER','AXIOM_CLOUD_STORAGE','AXIOM_DISTRIBUTED_RPM'))


def cloud_configuration():
    url=os.getenv('SUPABASE_URL','').strip().rstrip('/')
    key=os.getenv('SUPABASE_SECRET_KEY','').strip()
    if not re.fullmatch(r'https://[a-z0-9]+\.supabase\.co',url) or not key.startswith('sb_secret_'):
        raise HTTPException(503,'Production storage configuration incomplete.')
    return url,key


async def rpc(name, payload):
    url,key=cloud_configuration()
    try:
        with measure('rpc') as timing:
            async with async_client('rpc') as client:
                response=await client.post(url+'/rest/v1/rpc/'+name,headers={'apikey':key},json=payload)
                timing['ok']=response.status_code==200
        if response.status_code!=200: raise ValueError('RPC unavailable')
        return response.json()
    except (httpx.HTTPError,ValueError):
        raise HTTPException(503,'Production service unavailable; retry later.') from None


async def take_distributed(identity):
    if not distributed_enabled(): return True
    from app.core.request_guard import setting
    result=await rpc('axiom_take_request',{'p_owner':identity,'p_limit':setting('AXIOM_USER_RPM',60,1200)})
    if type(result) is not bool: raise HTTPException(503,'Invalid quota service response.')
    return result


async def storage_usage(identity):
    if os.getenv('AXIOM_CLOUD_STORAGE')=='1':
        result=await rpc('axiom_workspace_usage',{'p_owner':identity})
        if not isinstance(result,dict) or any(type(result.get(k)) is not int or result[k]<0 for k in ('datasets','bytes','pending')):
            raise HTTPException(503,'Invalid storage usage response.')
        return {**result,'mode':'cloud'}
    from app.persistence.dataset_store import _data_root
    from starlette.concurrency import run_in_threadpool
    import sqlite3
    from contextlib import closing
    def local():
        path=_data_root()/'axiom.sqlite3'
        if not path.is_file(): return {'datasets':0,'bytes':0,'pending':0,'mode':'local'}
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=3)) as conn:
            if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='datasets'").fetchone():
                return {'datasets':0,'bytes':0,'pending':0,'mode':'local'}
            count,size=conn.execute('SELECT COUNT(*),COALESCE(SUM(size_bytes),0) FROM datasets').fetchone()
            return {'datasets':count,'bytes':size,'pending':0,'mode':'local'}
    return await run_in_threadpool(local)

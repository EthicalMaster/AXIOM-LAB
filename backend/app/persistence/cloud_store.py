"""Opt-in server-only Supabase persistence. Every read/write binds verified tenant.
No user credentials or service key may be supplied by API callers.
"""
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from uuid import uuid4
import httpx
from app.core.upstream import cloud_client, measure
from fastapi import HTTPException
from app.core.tenant import multi_user_enabled, admitted, _identity

BUCKET = 'axiom-originals'


def enabled():
    return os.getenv('AXIOM_CLOUD_STORAGE','0') == '1'


def owner():
    value = _identity.get()
    if not multi_user_enabled() or not value or not admitted(value):
        raise HTTPException(403, 'Verified private workspace required.')
    return value


def configuration():
    url = os.getenv('SUPABASE_URL','').rstrip('/')
    key = os.getenv('SUPABASE_SECRET_KEY','')
    if not re.fullmatch(r'https://[a-z0-9]+\.supabase\.co',url) or not key.startswith('sb_secret_'):
        raise HTTPException(503,'Cloud persistence configuration incomplete.')
    return url, key


def request(method,path,**kwargs):
    url,key=configuration()
    headers={'apikey':key, **kwargs.pop('headers',{})}
    try:
        with measure('cloud') as timing:
            with cloud_client() as client:
                res=client.request(method,url+path,headers=headers,**kwargs)
                timing['ok']=200<=res.status_code<300
    except httpx.HTTPError:
        raise HTTPException(503,'Cloud persistence unavailable; verify saved state before retrying.') from None
    if not 200<=res.status_code<300:
        raise HTTPException(503,'Cloud persistence rejected the operation; check configuration and saved state.')
    return res


def rpc(name,**args):
    return request('POST','/rest/v1/rpc/'+name,json={**args,'p_owner':owner()}).json()


def rows(table,**params):
    return request('GET','/rest/v1/axiom_'+table,params={**params,'owner_id':'eq.'+owner()}).json()


def one(table,**params):
    result=rows(table,limit=1,**params)
    return result[0] if result else None


def page(table,limit,offset,**params):
    result=request('GET','/rest/v1/axiom_'+table,params={**params,'owner_id':'eq.'+owner(),'limit':limit,'offset':offset},headers={'Prefer':'count=exact'})
    total=result.headers.get('content-range','').rsplit('/',1)[-1]
    if not total.isdecimal(): raise HTTPException(503,'Cloud history count unavailable.')
    return int(total),result.json()


def object_path(dataset_id,extension):
    if not re.fullmatch('[0-9a-f]{32}',dataset_id) or extension not in ('.csv','.xls','.xlsx'):
        raise HTTPException(404,'Dataset not found.')
    return f'{BUCKET}/{owner()}/{dataset_id}/original{extension}'


def save_dataset(raw,original_name,extension,profile):
    from app.core.request_guard import setting
    from app.persistence.dataset_store import DatasetStorageQuotaError
    meta={'id':uuid4().hex,'original_name':original_name,'format':profile.file_format,'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'uploaded_at':datetime.now(timezone.utc).isoformat(),'row_count':profile.row_count,'column_count':profile.column_count,'headers':profile.headers,'worksheet':profile.worksheet,'sheet_names':profile.sheet_names,'warnings':profile.warnings}
    persist_original(meta,raw,extension)
    return meta


def persist_original(meta,raw,extension):
    from app.core.request_guard import setting
    from app.persistence.dataset_store import DatasetStorageQuotaError
    path=object_path(meta['id'],extension)
    if not 0<len(raw)<=5242880 or meta['format'] != extension[1:] or len(raw)!=meta['size_bytes'] or hashlib.sha256(raw).hexdigest()!=meta['sha256']:
        raise ValueError('Original integrity mismatch.')
    if not rpc('axiom_reserve',p_metadata=meta,p_max_count=setting('AXIOM_DATASET_MAX_COUNT',500,10000),p_max_bytes=setting('AXIOM_DATASET_QUOTA_MIB',256,10240)*1048576,p_global_bytes=setting('AXIOM_CLOUD_GLOBAL_MIB',512,10240)*1048576):
        raise DatasetStorageQuotaError('Cloud dataset allowance reached.')
    request('POST','/storage/v1/object/'+path,content=raw,headers={'Content-Type':'application/octet-stream','x-upsert':'false'})
    # A pending row is never exposed. Read-back verification before visibility.
    check=request('GET','/storage/v1/object/authenticated/'+path).content
    if len(check)!=len(raw) or hashlib.sha256(check).hexdigest()!=meta['sha256']:
        raise HTTPException(503,'Cloud original integrity verification failed.')
    result=request('PATCH','/rest/v1/axiom_datasets',params={'owner_id':'eq.'+owner(),'id':'eq.'+meta['id'],'ready':'eq.false'},json={'ready':True},headers={'Prefer':'return=representation'}).json()
    if len(result)!=1: raise HTTPException(503,'Cloud dataset finalization not confirmed.')


def find_dataset(dataset_id):
    row=one('datasets',id='eq.'+dataset_id,ready='eq.true',select='metadata')
    return row['metadata'] if row else None


def read_original_dataset(dataset_id,metadata):
    from app.persistence.dataset_store import DatasetStorageError
    # Do not trust a passed metadata record without checking tenant ownership.
    actual=find_dataset(dataset_id)
    if actual is None or actual!=metadata: raise DatasetStorageError('Dataset metadata unavailable.')
    raw=request('GET','/storage/v1/object/authenticated/'+object_path(dataset_id,'.'+actual['format'])).content
    if len(raw)!=actual['size_bytes'] or hashlib.sha256(raw).hexdigest()!=actual['sha256']:
        raise DatasetStorageError('Cloud original failed its integrity check.')
    return raw


def new_run(configuration,result,source_run_id=None):
    return {'id':uuid4().hex,'created_at':datetime.now(timezone.utc).isoformat(),'status':'completed','method':result['method'],'configuration':configuration,'result':result,'environment':{'python':'.'.join(map(str,sys.version_info[:3])),'algorithm':result['method']},'revision':1,'source_run_id':source_run_id}


def create_experiment(*,name,dataset_id,dataset_sha256,configuration,result):
    run=new_run(configuration,result)
    record={'id':uuid4().hex,'name':name,'dataset_id':dataset_id,'dataset_sha256':dataset_sha256,'created_at':run['created_at']}
    saved=rpc('axiom_create_experiment',p_record=record,p_run=run)
    if saved is None: raise HTTPException(404,'Dataset not found.')
    return saved


def read_experiment(experiment_id):
    row=one('experiments',id='eq.'+experiment_id,select='record')
    if not row: return None
    run=one('runs',experiment_id='eq.'+experiment_id,order='revision.desc',select='record')
    return {**row['record'],'run':run['record']} if run else None


def list_experiments(limit=20,offset=0):
    total, items=page('experiments',limit,offset,order='created_at.desc,id.desc',select='record,axiom_runs(count)')
    return {'total':total,'limit':limit,'offset':offset,'items':[{**r['record'],'run_count':r['axiom_runs'][0]['count']} for r in items]}


def list_experiment_runs(experiment_id,limit=20,offset=0):
    if not one('experiments',id='eq.'+experiment_id,select='id'): return None
    total,items=page('runs',limit,offset,experiment_id='eq.'+experiment_id,order='revision.desc',select='record')
    return {'experiment_id':experiment_id,'total':total,'limit':limit,'offset':offset,'items':[r['record'] for r in items]}


def append_experiment_run(experiment_id,configuration,result,*,source_run_id=None):
    return rpc('axiom_append_run',p_experiment=experiment_id,p_run=new_run(configuration,result,source_run_id))


def get_run(experiment_id,run_id):
    row=one('runs',experiment_id='eq.'+experiment_id,id='eq.'+run_id,select='record')
    return row['record'] if row else None

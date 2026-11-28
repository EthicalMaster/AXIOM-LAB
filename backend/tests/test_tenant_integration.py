"""Actual app regression: datasets, runs, reports, AI evidence and legacy separation."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'
C='12345678-1234-4234-8234-123456789abe'


def headers(user): return {'Authorization':'Bearer '+user}


def test_real_store_cross_tenant_and_legacy(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    monkeypatch.setenv('AXIOM_GOOGLE_AUTH','0')
    monkeypatch.setenv('AXIOM_MULTI_USER','0')
    monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',A)
    monkeypatch.setenv('AXIOM_MULTI_USER_IDS',B)
    # Use isolated test configuration with generous limits for repeated requests.
    monkeypatch.setenv('AXIOM_API_RPM','1200')
    monkeypatch.setenv('AXIOM_UPLOAD_RPM','60')
    monkeypatch.setattr(app,'middleware_stack',None)
    async def fake_verify(request):
        token=request.headers.get('authorization','')
        for uid in (A,B,C):
            if token=='Bearer '+uid: return uid
        raise HTTPException(401,'Invalid session')
    with TestClient(app) as client, patch('app.core.tenant_access.verify_google',side_effect=fake_verify):
        def upload(h):
            r=client.post('/api/v1/datasets/import',headers=h,files={'file':('x.csv',b'x\n1\n2\n3\n')})
            assert r.status_code==201,r.text
            return r.json()['id']
        legacy=upload({})
        monkeypatch.setenv('AXIOM_GOOGLE_AUTH','1')
        monkeypatch.setenv('AXIOM_MULTI_USER','1')
        a,b=upload(headers(A)),upload(headers(B))
        for owner,other,dataset in ((A,B,a),(B,A,b)):
            assert client.get('/api/v1/datasets/'+dataset,headers=headers(owner)).status_code==200
            assert client.get('/api/v1/datasets/'+dataset,headers=headers(other)).status_code==404
            assert client.get('/api/v1/datasets/'+dataset+'/profile',headers=headers(other)).status_code==404
            assert client.get('/api/v1/datasets/'+legacy,headers=headers(owner)).status_code==404
        assert client.post('/api/v1/experiments',headers=headers(B),json={'name':'Cross-user','dataset_id':a,'column':'x'}).status_code==404
        exp=client.post('/api/v1/experiments',headers=headers(A),json={'name':'Private research','dataset_id':a,'column':'x'})
        assert exp.status_code==201,exp.text
        record=exp.json(); eid=record['id']; rid=record['run']['id']
        assert client.get('/api/v1/experiments',headers=headers(A)).json()['total']==1
        assert client.get('/api/v1/experiments',headers=headers(B)).json()['total']==0
        path=f'/api/v1/experiments/{eid}'
        for route in (path,path+'/runs',path+f'/runs/{rid}/report?format=json'):
            assert client.get(route,headers=headers(A)).status_code==200
            assert client.get(route,headers=headers(B)).status_code==404
        assert client.post(path+'/runs',headers=headers(B),json={'column':'x'}).status_code==404
        assert client.post('/api/v1/ai/explain',headers=headers(B),json={'experiment_id':eid,'run_id':rid}).status_code==404
        assert client.get('/api/v1/datasets/'+a,headers=headers(C)).status_code==403
        assert client.get('/api/v1/datasets/'+a).status_code==401
        assert (tmp_path/'tenants'/A/'axiom.sqlite3').is_file()
        assert (tmp_path/'tenants'/B/'axiom.sqlite3').is_file()
        # Legacy files remain untouched and cannot see tenant files.
        monkeypatch.setenv('AXIOM_MULTI_USER','0');monkeypatch.setenv('AXIOM_GOOGLE_AUTH','0')
        assert client.get('/api/v1/datasets/'+legacy).status_code==200
        assert client.get('/api/v1/datasets/'+a).status_code==404

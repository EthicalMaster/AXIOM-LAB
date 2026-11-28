import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.api import workspace as w
from app.core.tenant import tenant_scope

A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'
D='a'*32
P='b'*32

@pytest.fixture(autouse=True)
def env(monkeypatch):
    for k,v in {'AXIOM_GOOGLE_AUTH':'1','AXIOM_MULTI_USER':'1','AXIOM_CLOUD_STORAGE':'1','AXIOM_OPEN_REGISTRATION':'0','AXIOM_GOOGLE_OWNER_ID':A,'AXIOM_MULTI_USER_IDS':B,'AXIOM_BLOCKED_USER_IDS':''}.items():monkeypatch.setenv(k,v)

def test_no_context():
    with pytest.raises(HTTPException) as e:w.library('',20,0)
    assert e.value.status_code==403

def test_local_mode(monkeypatch):
    monkeypatch.setenv('AXIOM_CLOUD_STORAGE','0')
    with tenant_scope(A),pytest.raises(HTTPException) as e:w.library('',20,0)
    assert e.value.status_code==409

def test_library_binds_owner(monkeypatch):
    calls=[]
    class Result:
        def json(self):return {'total':0,'items':[]}
    def request(method,path,**kwargs):calls.append(kwargs['json']);return Result()
    monkeypatch.setattr(w.cloud,'request',request)
    for who in [A,B]:
        with tenant_scope(who):assert w.library('sample',20,0)['total']==0
    assert [c['p_owner'] for c in calls]==[A,B]

def test_project_link_rejects_foreign_record(monkeypatch):
    monkeypatch.setattr(w.cloud,'rpc',lambda *a,**kw:'missing')
    with tenant_scope(B),pytest.raises(HTTPException) as e:w.attach(P,w.Link(kind='dataset',id=D))
    assert e.value.status_code==404

def test_project_link_limit(monkeypatch):
    monkeypatch.setattr(w.cloud,'rpc',lambda *a,**kw:'limit')
    with tenant_scope(A),pytest.raises(HTTPException) as e:w.attach(P,w.Link(kind='experiment',id=D))
    assert e.value.status_code==409

def test_rename_owner_filter(monkeypatch):
    class Result:
        def json(self):return []
    def request(method,path,**kwargs):
        assert kwargs['params']=={'owner_id':'eq.'+B,'id':'eq.'+P}
        return Result()
    monkeypatch.setattr(w.cloud,'request',request)
    with tenant_scope(B),pytest.raises(HTTPException) as e:w.rename_project(P,w.Name(name='private'))
    assert e.value.status_code==404

def test_reopen_foreign_no_download(monkeypatch):
    monkeypatch.setattr(w.cloud,'find_dataset',lambda _:None)
    monkeypatch.setattr(w.cloud,'read_original_dataset',lambda *_:pytest.fail('must not download'))
    with tenant_scope(B),pytest.raises(HTTPException) as e:w.reopen(D)
    assert e.value.status_code==404

def test_invalid_input():
    with pytest.raises(ValidationError):w.Link(kind='dataset',id='../secret')
    with pytest.raises(ValidationError):w.Name(name=' ',owner_id=A)

def test_deletion_requires_confirmation(monkeypatch):
    monkeypatch.setattr(w.cloud,'rpc',lambda *a,**kw:pytest.fail('no mutation'))
    with tenant_scope(A),pytest.raises(HTTPException) as e:w.deletion(w.Deletion(action='request',confirmation='wrong'))
    assert e.value.status_code==422

def test_admin_denied_for_invited_account(monkeypatch):
    monkeypatch.setattr(w.cloud,'rpc',lambda *a,**kw:pytest.fail('no admin query'))
    with tenant_scope(B),pytest.raises(HTTPException) as e:w.admin()
    assert e.value.status_code==403

def test_admin_owner(monkeypatch):
    monkeypatch.setattr(w.cloud,'rpc',lambda name:{'datasets':2} if name=='axiom_admin_summary' else None)
    with tenant_scope(A):assert w.admin()=={'datasets':2}

def test_label_preserves_original_metadata(monkeypatch):
    class Result:
        def json(self):return [{'display_label':'Renamed'}]
    def request(method,path,**kwargs):
        assert kwargs['params']=={'owner_id':'eq.'+B,'id':'eq.'+D,'ready':'eq.true'}
        assert kwargs['json']=={'display_label':'Renamed'}
        return Result()
    monkeypatch.setattr(w.cloud,'request',request)
    with tenant_scope(B):assert w.label_dataset(D,w.Label(label='Renamed'))=={'label':'Renamed'}

def test_reopen_returns_preview(monkeypatch):
    from types import SimpleNamespace
    meta={'id':D,'format':'csv','original_name':'sample.csv'}
    monkeypatch.setattr(w.cloud,'find_dataset',lambda _:meta)
    monkeypatch.setattr(w.cloud,'read_original_dataset',lambda *args:b'x\n1\n')
    monkeypatch.setattr(w,'validate_dataset',lambda raw,ext:SimpleNamespace(preview=[['1']]))
    with tenant_scope(A):assert w.reopen(D)=={**meta,'preview':[['1']]}

def test_deletion_cancel_is_non_destructive(monkeypatch):
    def rpc(name,**args):
        assert name=='axiom_deletion_request' and args=={'p_request':False}
        return {'display_name':'Researcher','deletion_requested_at':None}
    monkeypatch.setattr(w.cloud,'rpc',rpc)
    with tenant_scope(A):assert w.deletion(w.Deletion(action='cancel',confirmation='CANCEL'))['deletion_requested_at'] is None

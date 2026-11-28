import hashlib
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.core.tenant import tenant_scope
from app.core.tenant_budget import admit_request,_states
from app.persistence import cloud_store as c

A='12345678-1234-4234-8234-123456789abc'
B='12345678-1234-4234-8234-123456789abd'
D='a'*32

@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv('AXIOM_MULTI_USER','1');monkeypatch.setenv('AXIOM_GOOGLE_OWNER_ID',A);monkeypatch.setenv('AXIOM_MULTI_USER_IDS',B)
    _states.clear()
    yield
    _states.clear()

def test_owner_required():
    with pytest.raises(HTTPException) as exc: c.owner()
    assert exc.value.status_code==403

def test_owner_filters_override_supplied_filter():
    with tenant_scope(A),patch.object(c,'request') as call:
        call.return_value.json.return_value=[]
        c.rows('datasets',owner_id='eq.'+B)
        assert call.call_args.kwargs['params']['owner_id']=='eq.'+A

def test_private_paths():
    with tenant_scope(A):
        assert c.object_path(D,'.csv')==f'axiom-originals/{A}/{D}/original.csv'
        with pytest.raises(HTTPException): c.object_path('../escape','.csv')
        with pytest.raises(HTTPException): c.object_path(D,'/../x')
    with tenant_scope(B): assert c.object_path(D,'.csv').split('/')[1]==B

def test_read_checks_tenant_metadata():
    with tenant_scope(B),patch.object(c,'find_dataset',return_value=None),patch.object(c,'request') as call:
        from app.persistence.dataset_store import DatasetStorageError
        with pytest.raises(DatasetStorageError): c.read_original_dataset(D,{'id':D})
        call.assert_not_called()

def test_rpc_binds_owner():
    with tenant_scope(A),patch.object(c,'request') as call:
        c.rpc('axiom_append_run',p_experiment=D,p_run={})
        assert call.call_args.kwargs['json']['p_owner']==A

def test_quota_concurrency(monkeypatch):
    monkeypatch.setenv('AXIOM_USER_INFLIGHT','1');monkeypatch.setenv('AXIOM_USER_RPM','2')
    with admit_request(A) as a:
        assert a
        with admit_request(A) as blocked: assert not blocked
        with admit_request(B) as b: assert b
    with admit_request(A) as a: assert a
    with admit_request(A) as blocked: assert not blocked

def test_bad_configuration(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL','https://malicious.example');monkeypatch.setenv('SUPABASE_SECRET_KEY','sb_secret_dummy')
    with pytest.raises(HTTPException): c.configuration()

def test_cloud_disabled_default(monkeypatch):
    monkeypatch.delenv('AXIOM_CLOUD_STORAGE',raising=False)
    assert not c.enabled()

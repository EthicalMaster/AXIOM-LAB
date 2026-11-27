from pathlib import Path
import runpy
import pytest
from fastapi.testclient import TestClient
from app.main import app

storage=runpy.run_path(str(Path(__file__).resolve().parents[2]/'scripts/storage_backup.py'))
verify=storage['verify']; snapshot=storage['snapshot']


def test_backup_restore_saved_evidence(tmp_path,monkeypatch):
    live=tmp_path/'live'; backup=tmp_path/'backup'; restored=tmp_path/'restored'
    monkeypatch.setenv('AXIOM_DATA_DIR',str(live)); monkeypatch.setenv('AXIOM_PUBLIC_MODE','0')
    with TestClient(app) as client:
        d=client.post('/api/v1/datasets/import',files={'file':('local.csv',b'x\n1\n2\n3\n')}).json()
        e=client.post('/api/v1/experiments',json={'name':'Snapshot fixture','dataset_id':d['id'],'column':'x'}).json()
    assert snapshot(live,backup)==(1,8)
    assert snapshot(backup,restored)==(1,8)
    monkeypatch.setenv('AXIOM_DATA_DIR',str(restored))
    with TestClient(app) as client:
        assert client.get(f"/api/v1/datasets/{d['id']}/statistics").json()['columns'][0]['mean']==2
        url=f"/api/v1/experiments/{e['id']}/runs/{e['run']['id']}/report?format=json"
        assert client.get(url).json()['run']['result']==e['run']['result']
    with pytest.raises(ValueError): snapshot(live,backup)
    with pytest.raises(ValueError): snapshot(live,live/'nested')
    next(restored.glob('datasets/*/original.csv')).write_bytes(b'x\n0\n0\n0\n')
    with pytest.raises(ValueError): verify(restored)

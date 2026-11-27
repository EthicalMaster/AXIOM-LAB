import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_clustering import cluster
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def samples():
    return ('x\n'+'\n'.join(map(str,list(range(20))+list(range(100,120))))+'\n').encode()

def test_two_clusters_are_separated():
    r=cluster(samples(),'.csv',['x'],2)
    assert r['found_clusters']==2 and sum(r['cluster_counts'].values())==40
    assert r['silhouette']>0.75
    assert len(r['example_assignments'])==25

def test_invalid_configuration():
    with pytest.raises(DatasetValidationError):cluster(samples(),'.csv',['x'],9)
    with pytest.raises(DatasetValidationError):cluster(samples(),'.csv',['missing'],2)

def test_api_and_source_preservation(tmp_path):
    raw=samples()
    up=client.post('/api/v1/datasets/import',files={'file':('x.csv',raw)}).json()
    response=client.post(f"/api/v1/datasets/{up['id']}/ml/clustering",json={'features':['x'],'n_clusters':2})
    assert response.status_code==200
    assert (tmp_path/'datasets'/up['id']/'original.csv').read_bytes()==raw

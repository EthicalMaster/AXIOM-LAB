import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_regression import regression
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def linear():return ('x,y\n'+'\n'.join(f'{i},{3*i+2}' for i in range(1,81))+'\n').encode()

def test_perfect_linear_reference():
    r=regression(linear(),'.csv',['x'],'y')
    assert r['r2']==pytest.approx(1,abs=1e-12)
    assert r['mae']<1e-10 and r['rmse']<1e-10
    assert r['train_rows']==60 and r['test_rows']==20

def test_bad_features_target():
    with pytest.raises(DatasetValidationError):regression(linear(),'.csv',['y'],'y')

def test_api_preserves_source(tmp_path):
    file=linear()
    up=client.post('/api/v1/datasets/import',files={'file':('values.csv',file)}).json()
    url=f"/api/v1/datasets/{up['id']}/ml/regression"
    request={'task':'regression','features':['x'],'target':'y'}
    assert client.post(url,json=request).status_code==200
    assert client.post(url,json={**request,'task':'classification'}).status_code==422
    assert (tmp_path/'datasets'/up['id']/'original.csv').read_bytes()==file

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_common import preview,read_supervised,holdout,preprocessing
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def sample():
    return ('x,y\n'+'\n'.join(f'{i},{3*i+2}' for i in range(1,41))+'\n').encode()

def test_split_first_and_impute_training_only():
    result=preview(sample(),'.csv',['x'],'y','regression')
    data=read_supervised(sample(),'.csv',['x'],'y','regression')
    Xtr,Xte,_,_=holdout(data)
    assert result['train_rows']==30 and result['test_rows']==10
    assert result['training_medians'][0]==pytest.approx(__import__('numpy').median(Xtr[:,0]))
    assert result['training_scaler_means'][0]==pytest.approx(Xtr[:,0].mean())
    assert result['seed']==42

def test_invalid_target_leakage_and_rows():
    for features,target in [(['x'],'x'),(['not_here'],'y'),(['x','x'],'y')]:
        with pytest.raises(DatasetValidationError):preview(sample(),'.csv',features,target,'regression')
    with pytest.raises(DatasetValidationError):preview(b'x,y\n1,2\n','.csv',['x'],'y','regression')

def test_endpoint_rejects_time_series():
    uploaded=client.post('/api/v1/datasets/import',files={'file':('f.csv',sample())}).json()
    url=f"/api/v1/datasets/{uploaded['id']}/ml/preview"
    valid={'task':'regression','features':['x'],'target':'y'}
    assert client.post(url,json=valid).status_code==200
    assert client.post(url,json={**valid,'time_dependent':True}).status_code==422

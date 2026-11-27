import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_classification import classification
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def sample():
    return ('x,class\n'+'\n'.join(f'{i},{"A" if i<50 else "B"}' for i in range(100))+'\n').encode()

def test_high_separation_binary_reference():
    r=classification(sample(),'.csv',['x'],'class')
    assert r['labels']==['A','B']
    assert r['test_rows']==25 and r['train_rows']==75
    assert r['accuracy']>=0.9 and r['macro_f1']>=0.9
    assert r['roc_auc']==pytest.approx(1,abs=1e-10)
    assert sum(sum(row) for row in r['confusion_matrix'])==25

def test_invalid_class_counts():
    raw=b'x,class\n'+b'1,A\n'*20+b'2,B\n'*2
    with pytest.raises(DatasetValidationError):classification(raw,'.csv',['x'],'class')

def test_api_and_no_modification(tmp_path):
    raw=sample()
    up=client.post('/api/v1/datasets/import',files={'file':('labels.csv',raw)}).json()
    url=f"/api/v1/datasets/{up['id']}/ml/classification"
    assert client.post(url,json={'task':'classification','features':['x'],'target':'class'}).status_code==200
    assert client.post(url,json={'task':'regression','features':['x'],'target':'class'}).status_code==422
    assert (tmp_path/'datasets'/up['id']/'original.csv').read_bytes()==raw

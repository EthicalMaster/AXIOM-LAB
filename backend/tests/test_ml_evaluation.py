import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_evaluation import compare_models

client=TestClient(app)
@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def regression_sample():
    return ('x,y\n'+'\n'.join(f'{i},{4*i+1}' for i in range(1,81))+'\n').encode()

def classification_sample():
    return ('x,label\n'+'\n'.join(f'{i},{"A" if i<40 else "B"}' for i in range(80))+'\n').encode()

def test_cv_and_holdout_regression():
    r=compare_models(regression_sample(),'.csv',['x'],'y','regression')
    assert r['chosen_by_training_cv']=='linear'
    assert r['train_rows']==60 and r['test_rows']==20
    assert r['heldout_metric_name']=='mae' and r['heldout_metric']<1e-8
    assert len(r['models'])==2 and all(len(x['cv_scores'])==3 for x in r['models'])

def test_classification_cv_comparison():
    r=compare_models(classification_sample(),'.csv',['x'],'label','classification')
    assert r['heldout_metric_name']=='macro_f1'
    assert 0<=r['heldout_metric']<=1
    assert r['chosen_by_training_cv'] in ('logistic','decision_tree')

def test_api_reject_time_and_preserves_raw(tmp_path):
    raw=regression_sample()
    upload=client.post('/api/v1/datasets/import',files={'file':('x.csv',raw)}).json()
    url=f"/api/v1/datasets/{upload['id']}/ml/compare"
    request={'task':'regression','features':['x'],'target':'y'}
    assert client.post(url,json=request).status_code==200
    assert client.post(url,json={**request,'time_dependent':True}).status_code==422
    assert (tmp_path/'datasets'/upload['id']/'original.csv').read_bytes()==raw

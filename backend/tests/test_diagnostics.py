import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.diagnostics import normality_diagnostic

client=TestClient(app)

@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_reference_shapiro_against_scipy():
    from scipy.stats import shapiro
    values=[-1,0,0.2,0.7,1,1.2,2,3]
    raw=('v\n'+'\n'.join(map(str,values))+'\n').encode()
    result=normality_diagnostic(raw,'.csv','v')
    assert result['statistic']==pytest.approx(shapiro(values).statistic)
    assert result['p_value']==pytest.approx(shapiro(values).pvalue)
    assert result['status']=='computed'

def test_withheld_for_tiny_and_constant():
    assert normality_diagnostic(b'v\n1\n2\n','.csv','v')['status']=='insufficient_sample'
    assert normality_diagnostic(b'v\n1\n1\n1\n','.csv','v')['status']=='constant_sample'

def test_withheld_above_size():
    raw=b'v\n'+b'1\n'*5000+b'2\n'
    assert normality_diagnostic(raw,'.csv','v')['status']=='unsupported_sample_size'

def test_endpoint():
    uploaded=client.post('/api/v1/datasets/import',files={'file':('v.csv',b'v\n1\n2\n3\n4\n5\n')}).json()
    response=client.get(f"/api/v1/datasets/{uploaded['id']}/diagnostics",params={'column':'v'})
    assert response.status_code==200
    assert response.json()['status']=='computed'
    assert client.get('/api/v1/datasets/invalid/diagnostics',params={'column':'v'}).status_code==404

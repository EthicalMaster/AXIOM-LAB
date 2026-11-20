import math
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.hypothesis import one_sample_t
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

@pytest.fixture(autouse=True)
def isolate(monkeypatch,tmp_path):
    monkeypatch.setenv('AXIOM_DATA_DIR',str(tmp_path))

def test_reference_t_test():
    result=one_sample_t(b'v\n1\n2\n3\n4\n5\n','.csv','v',0,0.05)
    assert result['t_statistic']==pytest.approx(4.242640687)
    assert result['degrees_of_freedom']==4
    assert result['p_value']==pytest.approx(0.01323559956)
    assert result['confidence_interval']==pytest.approx([1.03675684,4.96324316])

def test_exact_null_never_rejected():
    result=one_sample_t(b'v\n1\n2\n3\n4\n5\n','.csv','v',3,0.05)
    assert result['t_statistic']==0 and result['p_value']==1 and not result['reject_null']

def test_invalid_inputs():
    for raw in (b'v\n1\n',b'v\n1\n1\n',b'v\n1\nNA\n2\n'):
        with pytest.raises(DatasetValidationError): one_sample_t(raw,'.csv','v',0,0.05)
    with pytest.raises(DatasetValidationError): one_sample_t(b'v\n1\n2\n','.csv','v',math.inf,0.05)

def test_api_contract_and_integrity(tmp_path):
    imported=client.post('/api/v1/datasets/import',files={'file':('test.csv',b'v\n1\n2\n3\n4\n5\n')}).json()
    url=f"/api/v1/datasets/{imported['id']}/hypothesis"
    assert client.post(url,json={'column':'v','null_mean':0}).status_code==200
    assert client.post(url,json={'column':'v','null_mean':'Infinity'}).status_code==422
    (tmp_path/'datasets'/imported['id']/'original.csv').write_bytes(b'v\n9\n9\n')
    assert client.post(url,json={'column':'v','null_mean':0}).status_code==409

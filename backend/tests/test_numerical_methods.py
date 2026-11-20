import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.numerical_methods import analyse_interval
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

def test_known_root_and_integral():
    r=analyse_interval([1,0,-4],0,3)
    assert r['root']==pytest.approx(2,abs=1e-9)
    assert r['root_residual']<1e-8
    assert r['integral']==pytest.approx(-3,abs=1e-8)

def test_no_bracket_and_endpoint_root():
    assert analyse_interval([1,0,1],-1,1)['root'] is None
    assert analyse_interval([1,-2],0,2)['root']==pytest.approx(2)

def test_invalid_intervals():
    for a,b in [(1,1),(2,1),(-101,0),(0,101)]:
        with pytest.raises(DatasetValidationError):analyse_interval([1,1],a,b)

def test_api():
    assert client.post('/api/v1/math/numerical',json={'coefficients':[1,0,-4],'lower':0,'upper':3}).status_code==200
    assert client.post('/api/v1/math/numerical',json={'coefficients':[1,0,-4],'lower':3,'upper':0}).status_code==422

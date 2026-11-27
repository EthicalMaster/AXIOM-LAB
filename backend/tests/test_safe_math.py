import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.safe_math import evaluate
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

def test_reference_values():
    assert evaluate('2 + 3*4')['value']==14
    assert evaluate('sin(pi/2) + sqrt(9)')['value']==pytest.approx(4)
    assert evaluate('log(e)')['value']==pytest.approx(1)
    assert evaluate('2**3**1')['value']==8

def test_rejects_unsafe_or_unbounded_expressions():
    samples=['__import__("os").system("whoami")','(1).__class__','[1,2,3]',
             'x', 'True', '2**200','2**3**2','1/0','sqrt(-4)','1e309', '2'+'*2'*60]
    for expr in samples:
        with pytest.raises(DatasetValidationError):evaluate(expr)

def test_api_handles_input():
    assert client.post('/api/v1/math/evaluate',json={'expression':'2*(3+4)'}).json()['value']==14
    assert client.post('/api/v1/math/evaluate',json={'expression':'__import__("os")'}).status_code==422

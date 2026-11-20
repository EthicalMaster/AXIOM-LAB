import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.polynomial import polynomial_calculus
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

def test_quadratic_reference():
    d=polynomial_calculus([1,0,-4])
    assert d['degree']==2
    assert d['derivative_coefficients']==pytest.approx([2,0])
    assert sorted(round(r['real'],5) for r in d['roots_approx'])==[-2,2]
    assert all(abs(r['imag'])<1e-10 for r in d['roots_approx'])
    assert d['antiderivative_coefficients']==pytest.approx([1/3,0,-4,0])

def test_cubic_three_roots():
    d=polynomial_calculus([1,-6,11,-6]);assert sorted(round(r['real']) for r in d['roots_approx'])==[1,2,3]

def test_rejects_extreme_invalid_inputs():
    for coeff in [[0,2],[1], [1]*8, [1,float('inf')]]:
        with pytest.raises(DatasetValidationError):polynomial_calculus(coeff)

def test_endpoint():
    assert client.post('/api/v1/math/polynomial',json={'coefficients':[1,0,-4]}).status_code==200
    assert client.post('/api/v1/math/polynomial',json={'coefficients':[0,0]}).status_code==422

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.linear_algebra import analyse_matrix
from app.services.dataset_validation import DatasetValidationError

client=TestClient(app)

def test_two_by_two_reference():
    r=analyse_matrix([[2,0],[0,4]],[2,8])
    assert r['determinant']==pytest.approx(8)
    assert r['inverse'][0]==pytest.approx([0.5,0])
    assert r['inverse'][1]==pytest.approx([0,0.25])
    assert r['solution']==pytest.approx([1,2])
    assert sorted(round(z['real']) for z in r['eigenvalues'])==[2,4]

def test_singular_matrix_withholds_inverse():
    r=analyse_matrix([[1,2],[2,4]],[1,2])
    assert r['inverse'] is None and r['solution'] is None and r['rank']==1

def test_invalid_dimensions():
    for matrix in [[[1,2]],[[1,2],[3]],[[float('nan')]]]:
        with pytest.raises(DatasetValidationError):analyse_matrix(matrix)

def test_api():
    assert client.post('/api/v1/math/matrix',json={'matrix':[[2,0],[0,3]]}).status_code==200
    assert client.post('/api/v1/math/matrix',json={'matrix':[[1,2],[3]]}).status_code==422

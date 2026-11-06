"""Foundation checks: honest phase status and stable API contract."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_phase_zero():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "phase": "0",
        "scientific_engine": "not_implemented",
    }


def test_unknown_science_route_is_not_implemented():
    response = client.get("/api/v1/statistics")
    assert response.status_code == 404


def test_openapi_contract_includes_health():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]

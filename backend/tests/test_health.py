"""Operational health remains truthful after the first data import feature."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_phase_02c():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "phase": "03D",
        "scientific_engine": "descriptive_statistics",
    }


def test_unknown_science_route_is_not_implemented():
    response = client.get("/api/v1/statistics")
    assert response.status_code == 404


def test_openapi_contract_includes_health_and_import():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]
    assert "/api/v1/datasets/import" in response.json()["paths"]
    assert "/api/v1/datasets/{dataset_id}/profile" in response.json()["paths"]
    assert "/api/v1/datasets/{dataset_id}/statistics" in response.json()["paths"]
    assert "/api/v1/experiments" in response.json()["paths"]
    assert "/api/v1/datasets/{dataset_id}/quality" in response.json()["paths"]
    assert "/api/v1/datasets/{dataset_id}/distribution" in response.json()["paths"]

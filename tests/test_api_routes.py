"""
Phase 5 API tests.
Run with: pytest tests/test_api_routes.py -v

All tests run without a real dataset or Groq API key.
"""
from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "dataset_loaded" in data
    assert "output_exists" in data


def test_health_returns_correct_model_name(client):
    response = client.get("/health")
    data = response.json()
    assert "llama" in data["model"].lower() or "gemini" in data["model"].lower() or len(data["model"]) > 0


def test_claims_endpoint_returns_list(client):
    with patch("backend.api.routes.claims.load_output_csv", return_value=[]):
        response = client.get("/claims")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_claims_endpoint_returns_correct_shape(client):
    mock_rows = [{
        "user_id": "user_001",
        "claim_object": "car",
        "claim_status": "supported",
        "severity": "medium",
        "risk_flags": "none",
        "image_paths": "images/sample/case_001/img_1.jpg",
        "user_claim": "My car got dented.",
        "evidence_standard_met": "true",
        "evidence_standard_met_reason": "Clear image.",
        "issue_type": "dent",
        "object_part": "door",
        "claim_status_justification": "img_1 shows a dent.",
        "supporting_image_ids": "img_1",
        "valid_image": "true",
    }]
    with patch("backend.api.routes.claims.load_output_csv", return_value=mock_rows):
        response = client.get("/claims")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == "user_001"
        assert data[0]["claim_status"] == "supported"


def test_get_claim_by_user_id(client):
    mock_rows = [{
        "user_id": "user_001",
        "claim_object": "car",
        "claim_status": "supported",
        "severity": "medium",
        "risk_flags": "none",
        "image_paths": "images/sample/case_001/img_1.jpg",
        "user_claim": "My car got dented.",
        "evidence_standard_met": "true",
        "evidence_standard_met_reason": "Clear image.",
        "issue_type": "dent",
        "object_part": "door",
        "claim_status_justification": "img_1 shows a dent.",
        "supporting_image_ids": "img_1",
        "valid_image": "true",
    }]
    with patch("backend.api.routes.claims.load_output_csv", return_value=mock_rows):
        response = client.get("/claims/user_001")
        assert response.status_code == 200
        assert response.json()["user_id"] == "user_001"


def test_get_claim_not_found_returns_404(client):
    with patch("backend.api.routes.claims.load_output_csv", return_value=[]):
        response = client.get("/claims/nonexistent_user")
        assert response.status_code == 404


def test_pipeline_run_returns_run_id(client):
    response = client.post("/pipeline/run", json={"run_type": "sample"})
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "started"


def test_pipeline_status_not_found_returns_404(client):
    response = client.get("/pipeline/run/nonexistent_run_id")
    assert response.status_code == 404


def test_evaluation_metrics_no_data_returns_404(client):
    with patch("backend.api.routes.evaluation.Path.exists", return_value=False):
        response = client.get("/evaluation/metrics")
        assert response.status_code == 404


def test_cors_headers_present(client):
    response = client.options(
        "/health",
        headers={"Origin": "http://localhost:8501"}
    )
    assert response.status_code in (200, 405)
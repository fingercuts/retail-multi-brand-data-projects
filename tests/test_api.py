from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch

client = TestClient(app)

def test_read_root_branding():
    """Verify API root message reflects the OmniRetail branding"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "OmniRetail" in data["message"]
    assert data["docs"] == "/docs"

@patch("api.main.engine.connect")
def test_health_check_operational(mock_connect):
    """Verify health check monitoring logic"""
    mock_connect.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_invalid_endpoint():
    """Verify standard 404 behavior for non-existent resources"""
    response = client.get("/v1/non_existent")
    assert response.status_code == 404

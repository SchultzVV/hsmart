import pytest
from services.ingestion_service.main import app

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_ingestion_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# just to create
import requests

BASE_URL = "http://127.0.0.1:5003"

def test_ingestion():
    response = requests.post(f"{BASE_URL}/ingest")
    assert response.status_code == 200
    assert "Texto processado e armazenado com sucesso" in response.text
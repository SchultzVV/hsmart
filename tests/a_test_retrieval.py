# just to create
import requests

BASE_URL = "http://127.0.0.1:5004"

def test_retrieval():
    payload = {"question": "O que é a Hotmart?"}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()
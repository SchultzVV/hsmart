import requests
import time

def wait_for_service(url, timeout=30):
    """Aguarda um serviço ficar disponível antes de testar."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)  # Espera 2 segundos antes de tentar de novo
    raise Exception(f"Serviço {url} não está respondendo após {timeout} segundos.")

def test_ingestion_to_retrieval():
    # Esperar os serviços subirem
    wait_for_service("http://localhost:5003")
    wait_for_service("http://localhost:5004")

    # Simulando uma ingestão de dados
    ingest_response = requests.post("http://localhost:5003/ingest", json={"url": "https://example.com"})
    assert ingest_response.status_code == 200

    # Verificando se o dado foi armazenado e pode ser recuperado
    retrieval_response = requests.post("http://localhost:5004/query", json={"question": "O que foi ingerido?"})
    assert retrieval_response.status_code == 200
    assert "resposta" in retrieval_response.json()

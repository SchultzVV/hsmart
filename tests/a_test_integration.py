# import requests

# def test_ingestion_to_retrieval():
#     # Simulando uma ingestão de dados
#     ingest_response = requests.post("http://localhost:5003/ingest", json={"url": "https://example.com"})
#     assert ingest_response.status_code == 200

#     # Verificando se o dado foi armazenado e pode ser recuperado
#     retrieval_response = requests.post("http://localhost:5004/query", json={"question": "O que foi ingerido?"})
#     assert retrieval_response.status_code == 200
#     assert "resposta" in retrieval_response.json()
import requests
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def wait_for_service(url, timeout=30):
    """Tenta conectar ao serviço até o timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    return False

def test_ingestion_to_retrieval():
    # Esperar os serviços subirem antes de rodar os testes
    # assert wait_for_service("http://localhost:5003"), "Ingestion Service não subiu!"
    # assert wait_for_service("http://localhost:5004"), "Retrieval Service não subiu!"

    # Frase de teste
    test_text = "MLOps é a prática de gerenciar modelos de machine learning em produção."

    # Simulando uma ingestão de dados
    ingest_response = requests.post("http://localhost:5003/ingest", json={"text": test_text})
    assert ingest_response.status_code == 200, f"Falha ao ingerir dado: {ingest_response.text}"

    # Tempo para garantir que a ingestão foi processada
    time.sleep(5)

    # Verificando se o dado foi armazenado e pode ser recuperado
    retrieval_response = requests.post("http://localhost:5004/query", json={"question": "O que é MLOps?"})
    assert retrieval_response.status_code == 200, f"Falha na recuperação: {retrieval_response.text}"

    # Garantindo que a resposta contenha a frase original
    retrieved_text = retrieval_response.json().get("resposta", "")
    print(retrieved_text)
    logging.info(f"Texto recuperado: {retrieved_text}")
    assert test_text in retrieved_text, f"Texto esperado não encontrado! Obtido: {retrieved_text}"

import requests
import time
import logging

# Configurar logging para depuração
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def wait_for_service(url, timeout=30):
    """Espera até que um serviço esteja disponível"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    return False

def test_retrieval():
    """Testa se o retrieval_service consegue encontrar um texto ingerido"""

    # Esperar os serviços subirem antes de rodar os testes
    # assert wait_for_service("http://localhost:5003/get_all_documents"), "Ingestion Service não subiu!"
    # assert wait_for_service("http://localhost:5004/query"), "Retrieval Service não subiu!"
    
    # Frase de teste
    test_text = "MLOps é essencial para ML em produção."

    # 1️⃣ **Enviar um texto para a ingestão manual**
    ingest_response = requests.post("http://localhost:5003/ingest_manual", json={"text": test_text})
    assert ingest_response.status_code == 200, f"Falha ao ingerir dado: {ingest_response.text}"

    # 2️⃣ **Esperar um pouco para garantir que os dados foram armazenados**
    time.sleep(5)

    # 3️⃣ **Consultar o banco vetorial via retrieval_service**
    query_response = requests.post("http://localhost:5004/query", json={"question": "MLOps é essencial para?"})
    assert query_response.status_code == 200, f"Erro ao consultar retrieval: {query_response.text}"

    # 4️⃣ **Verificar se a resposta contém o texto armazenado**
    retrieved_text = query_response.json().get("resposta", "")
    logging.info(f"Texto recuperado: {retrieved_text}")

    assert test_text in retrieved_text, f"Texto esperado não encontrado na resposta! Obtido: {retrieved_text}"

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

def test_ingestion():
    """Testa se a ingestão de um texto funciona corretamente"""

    # Esperar os serviços subirem antes de rodar os testes
    # assert wait_for_service("http://localhost:5003/get_all_documents"), "Ingestion Service não subiu!"
    
    # Frase de teste
    test_text = "MLOps é essencial para ML em produção."

    # 1️⃣ **Enviar um texto para a ingestão manual**
    ingest_response = requests.post("http://localhost:5003/ingest_manual", json={"text": test_text})
    assert ingest_response.status_code == 200, f"Falha ao ingerir dado: {ingest_response.text}"
    logging.info("Texto ingerido com sucesso.")

    # 2️⃣ **Esperar um pouco para garantir que os dados foram armazenados**
    time.sleep(5)

    # 3️⃣ **Verificar se o dado foi armazenado corretamente**
    retrieval_response = requests.get("http://localhost:5003/get_all_documents")
    assert retrieval_response.status_code == 200, f"Erro ao recuperar documentos: {retrieval_response.text}"

    # 4️⃣ **Obter a lista de documentos armazenados**
    documents = retrieval_response.json().get("documents", [])

    # 5️⃣ **Verificar se o texto esperado está nos documentos armazenados**
    stored_texts = [doc["text"] for doc in documents]  # Extrai apenas os textos armazenados
    logging.info(f"Documentos armazenados: {stored_texts}")

    assert test_text in stored_texts, f"Texto esperado não encontrado! Obtido: {stored_texts}"

    # 6️⃣ **Se chegou aqui, a ingestão está OK**
    logging.info("✅ Teste de ingestão passou com sucesso!")

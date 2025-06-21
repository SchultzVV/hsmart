import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from shared.langchain_container import LangChainContainer
import os

JSON_LOG_PATH = "logs/ufsm/cursos_links_acessados_full.json"
OUTPUT_LOG_PATH = "logs/ufsm/cursos_links_filtrados.json"
COLLECTION_NAME = "ufsm_knowledge"
MAX_WORKERS = 12
DATA_MINIMA = datetime(2023, 1, 1)

container = LangChainContainer()
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

def url_tem_data_antiga(url):
    """
    Retorna True apenas se o URL contiver uma data E essa data for anterior a 2023-01-01.
    Caso não haja data, o link é considerado válido.
    """
    match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", url)
    if match:
        try:
            data = datetime.strptime(match.group(0).strip("/"), "%Y/%m/%d")
            return data < DATA_MINIMA
        except Exception:
            return False
    return False  # Mantém links sem data

def process_url(curso, campus, nivel, url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "Sem título"
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
        content = "\n".join(paragraphs)
        if not content:
            return []

        metadados = [{
            "curso": curso,
            "campus": campus,
            "nivel": nivel,
            "document_title": title,
            "source": url,
            "timestamp": datetime.now().isoformat()
        }]
        return splitter.create_documents([content], metadatas=metadados)

    except Exception as e:
        print(f"[!] Erro em {url}: {e}")
        return []

def reprocess_from_log():
    print(f"📂 Lendo log: {JSON_LOG_PATH}")
    all_chunks = []

    try:
        with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
            curso_logs = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Erro ao ler o log: {e}"}), 500

    total_urls = 0
    filtered_logs = {}

    for curso, info in curso_logs.items():
        campus = info["campus"]
        nivel = info["nivel"]
        urls_validas = [url for url in info["urls_acessadas"] if not url_tem_data_antiga(url)]
        if urls_validas:
            filtered_logs[curso] = {
                "campus": campus,
                "nivel": nivel,
                "urls_acessadas": urls_validas
            }
            total_urls += len(urls_validas)

    if total_urls == 0:
        return jsonify({"message": "Nenhuma URL válida após filtro de data."}), 200

    print(f"✅ {total_urls} URLs válidas encontradas após filtro por data (>= 2023-01-01).")

    # Salva os cursos e URLs válidas
    os.makedirs(os.path.dirname(OUTPUT_LOG_PATH), exist_ok=True)
    with open(OUTPUT_LOG_PATH, "w", encoding="utf-8") as f_out:
        json.dump(filtered_logs, f_out, indent=2, ensure_ascii=False)
    print(f"📝 Log filtrado salvo em {OUTPUT_LOG_PATH}")

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for curso, info in filtered_logs.items():
            campus = info["campus"]
            nivel = info["nivel"]
            for url in info["urls_acessadas"]:
                tasks.append(executor.submit(process_url, curso, campus, nivel, url))

        for idx, future in enumerate(as_completed(tasks), 1):
            chunks = future.result()
            if chunks:
                all_chunks.extend(chunks)
            print(f"📦 Progresso: {idx}/{total_urls} URLs processadas.")

    if not all_chunks:
        return jsonify({"message": "Nenhum conteúdo válido extraído."}), 200

    print(f"💾 Armazenando {len(all_chunks)} chunks na coleção `{COLLECTION_NAME}`...")
    container.set_collection(COLLECTION_NAME)
    container.vectorstore.add_documents(all_chunks)

    print("✅ Ingestão finalizada com sucesso.")
    return jsonify({
        "message": f"{len(all_chunks)} chunks reprocessados e armazenados com sucesso.",
        "log_filtrado": OUTPUT_LOG_PATH
    }), 200

# import json
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from flask import jsonify
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from shared.langchain_container import LangChainContainer


# JSON_LOG_PATH = "logs/ufsm/cursos_links_acessados_full.json"
# COLLECTION_NAME = "ufsm_knowledge"
# MAX_WORKERS = 12

# container = LangChainContainer()
# splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

# def process_url(curso, campus, nivel, url):
#     try:
#         response = requests.get(url, timeout=10)
#         if response.status_code != 200:
#             return []

#         soup = BeautifulSoup(response.text, "html.parser")
#         title = soup.title.string.strip() if soup.title else "Sem título"
#         paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
#         content = "\n".join(paragraphs)
#         if not content:
#             return []

#         metadados = [{
#             "curso": curso,
#             "campus": campus,
#             "nivel": nivel,
#             "document_title": title,
#             "source": url,
#             "timestamp": datetime.now().isoformat()
#         }]
#         return splitter.create_documents([content], metadatas=metadados)

#     except Exception as e:
#         print(f"[!] Erro em {url}: {e}")
#         return []

# def reprocess_from_log():
#     all_chunks = []

#     try:
#         with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
#             curso_logs = json.load(f)
#     except Exception as e:
#         return jsonify({"error": f"Erro ao ler o log: {e}"}), 500

#     tasks = []
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         for curso, info in curso_logs.items():
#             campus = info["campus"]
#             nivel = info["nivel"]
#             for url in info["urls_acessadas"]:
#                 tasks.append(executor.submit(process_url, curso, campus, nivel, url))

#         for future in as_completed(tasks):
#             chunks = future.result()
#             if chunks:
#                 all_chunks.extend(chunks)

#     if not all_chunks:
#         return jsonify({"message": "Nenhum conteúdo válido extraído."}), 200

#     container.set_collection(COLLECTION_NAME)
#     container.vectorstore.add_documents(all_chunks)

#     return jsonify({"message": f"{len(all_chunks)} chunks reprocessados e armazenados com sucesso."}), 200

import os
import json
import logging
from urllib.parse import urljoin, urlparse
import requests
from flask import request, jsonify
from bs4 import BeautifulSoup

from services.ingestion_manager import IngestionManager

logger = logging.getLogger(__name__)


def get_internal_links(base_url, max_links=20):
    """Extração básica de links internos navegáveis a partir de uma URL."""
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        base_domain = urlparse(base_url).netloc

        links = set()
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            parsed = urlparse(href)
            if parsed.netloc == base_domain and href.startswith(base_url):
                links.add(href)
                if len(links) >= max_links:
                    break

        return sorted(links)

    except Exception as e:
        logger.warning(f"❌ Erro ao extrair links de {base_url}: {e}")
        return []


def ingest_from_web_loader(request):
    data = request.get_json()
    url = data.get("url")
    collection = "web_geral_loader"

    if not url:
        return jsonify({"error": "URL obrigatória"}), 400

    ingestion = IngestionManager(collection_name=collection)
    result, status = ingestion.ingest_url(url)
    return jsonify(result), status

# import os
# import json
# import requests
# from urllib.parse import urljoin, urlparse
# from bs4 import BeautifulSoup
# from flask import request, jsonify
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# # from langchain.document_loaders import PlaywrightURLLoader
# from langchain_community.document_loaders import PlaywrightURLLoader, UnstructuredURLLoader

# from shared.langchain_container import LangChainContainer

# # 🔌 LangChain container único e compartilhado
# container = LangChainContainer()
# client = container.qdrant_client
# embedding_model = container.embedding_model

# def get_internal_links(base_url, max_links=20):
#     """Extração básica de links internos navegáveis a partir de uma URL."""
#     try:
#         response = requests.get(base_url, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
#         base_domain = urlparse(base_url).netloc

#         links = set()
#         for a in soup.find_all("a", href=True):
#             href = urljoin(base_url, a["href"])
#             parsed = urlparse(href)
#             if parsed.netloc == base_domain and href.startswith(base_url):
#                 links.add(href)
#                 if len(links) >= max_links:
#                     break

#         return sorted(links)

#     except Exception as e:
#         print(f"❌ Erro ao extrair links de {base_url}: {e}")
#         return []

# def ingest_from_web_loader(request):
#     data = request.get_json()
#     url = data.get("url")
#     collection = "web_geral_loader"

#     if not url:
#         return jsonify({"error": "URL obrigatória"}), 400

#     docs = []
#     try:
#         print(f"🔍 Tentando carregar com UnstructuredURLLoader: {url}")
#         loader = UnstructuredURLLoader(urls=[url])
#         docs = loader.load()
#     except Exception as e1:
#         print(f"⚠️ Unstructured falhou: {e1}")
#         try:
#             print("🔁 Tentando fallback com PlaywrightURLLoader...")
#             loader = PlaywrightURLLoader(urls=[url], remove_selectors=["nav", "footer", "script"])
#             docs = loader.load()
#         except Exception as e2:
#             return jsonify({"error": f"Falha com ambos loaders. Unstructured: {e1}, Playwright: {e2}"}), 500

#     if not docs:
#         return jsonify({"error": "Nenhum conteúdo extraído"}), 204

#     splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
#     chunks = splitter.split_documents(docs)

#     container.set_collection(collection)
#     container.vectorstore.add_documents(chunks)

#     return jsonify({
#         "message": f"{len(chunks)} chunks adicionados à coleção `{collection}`.",
#         "url": url,
#         "loader": "unstructured" if "UnstructuredURLLoader" in str(loader.__class__) else "playwright"
#     }), 200


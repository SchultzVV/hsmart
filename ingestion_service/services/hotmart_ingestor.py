import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from utils.vector_store import recreate_and_upsert
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_url(url):
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
    return "\n".join(paragraphs)


def ingest_hotmart():
    from flask import jsonify  # import local para evitar dependência circular
    url = "https://hotmart.com/pt-br/blog/como-funciona-hotmart"
    text = extract_text_from_url(url)

    if not text:
        return jsonify({"error": "Erro ao baixar a página"}), 500

    sentences = [s.strip() for s in text.split(". ") if len(s.strip()) >= 40]
    embeddings = embedding_model.encode(sentences)
    logging.info(f"📌 {len(sentences)} sentenças extraídas da página da Hotmart.")

    metadata = [{"source": url, "timestamp": datetime.now().isoformat()} for _ in sentences]

    recreate_and_upsert(
        collection_name="hotmart_knowledge",
        sentences=sentences,
        embeddings=embeddings,
        metadata=metadata
    )

    return jsonify({"message": "Texto da Hotmart processado com sucesso"}), 200

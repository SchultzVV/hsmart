import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import jsonify
from shared.langchain_container import LangChainContainer

container = LangChainContainer()
embedding_model = container.embedding_model

def ingest_hotmart():
    url = "https://hotmart.com/pt-br/blog/como-funciona-hotmart"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return jsonify({"error": "Falha ao acessar URL"}), 500

        soup = BeautifulSoup(r.text, "html.parser")
        sentences = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
        embeddings = embedding_model.embed_documents(sentences)
        metadata = [{"source": url, "timestamp": datetime.now().isoformat()} for _ in sentences]

        container.store("hotmart_knowledge", sentences, embeddings, metadata)
        return jsonify({"message": f"Ingestão de {len(sentences)} sentenças da Hotmart concluída."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

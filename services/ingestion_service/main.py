from flask import Flask, jsonify, request
import qdrant_client
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import os
import logging
import sys

# Configura os logs para aparecerem no Docker
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

client = qdrant_client.QdrantClient(host="vector_db", port=6333)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text_from_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    return "\n".join([p.get_text() for p in paragraphs if p.get_text()])


def store_text_in_vector_db(text, collection_name):
    sentences = text.split(". ")
    embeddings = embedding_model.encode(sentences)
    logging.info(f"📌 Total de sentenças extraídas: {len(sentences)}")

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qdrant_client.http.models.VectorParams(
            size=384,
            distance=qdrant_client.http.models.Distance.COSINE
        )
    )

    points = [
        qdrant_client.http.models.PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={"text": sentence}
        )
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)
    logging.info(f"✅ Ingestão concluída na coleção `{collection_name}`!")


@app.route('/ingest_hotmart', methods=['POST'])
def ingest_hotmart():
    url = "https://hotmart.com/pt-br/blog/como-funciona-hotmart"
    text = extract_text_from_url(url)
    if text:
        store_text_in_vector_db(text, "hotmart_knowledge")
        return jsonify({"message": "Texto da Hotmart processado com sucesso"}), 200
    else:
        return jsonify({"error": "Erro ao baixar a página"}), 500


@app.route('/ingest_manual', methods=['POST'])
def ingest_manual():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "O campo 'text' é obrigatório"}), 400

    store_text_in_vector_db(data["text"], "mlops_knowledge")
    return jsonify({"message": "Texto manual processado com sucesso"}), 200


@app.route('/get_all_collections', methods=['GET'])
def get_all_collections():
    """Lista todas as coleções existentes no Qdrant"""
    try:
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        return jsonify({"collections": collection_names}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_all_documents', methods=['GET'])
def get_all_documents():
    """Lista todos os documentos de todas as coleções"""
    try:
        collections = client.get_collections()
        resultado = {}

        for collection in collections.collections:
            collection_name = collection.name
            scroll_result = client.scroll(collection_name=collection_name, limit=100)
            documents = [point.payload for point in scroll_result[0]]
            resultado[collection_name] = documents

        return jsonify({"collections": resultado}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    print("Inicializando serviço de ingestão...")
    app.run(host='0.0.0.0', port=5003, debug=DEBUG_MODE)

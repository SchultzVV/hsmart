import qdrant_client
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from flask import Flask, jsonify
import os

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Inicializando Flask
app = Flask(__name__)

# Conectando ao Qdrant
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

# Nome da coleção
COLLECTION_NAME = "hotmart_knowledge"

# Criar a coleção no Qdrant se não existir
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=qdrant_client.http.models.VectorParams(
        size=384,  # Dimensão dos embeddings do modelo
        distance=qdrant_client.http.models.Distance.COSINE
    )
)

# Carregar modelo de embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_url(url):
    """Baixa e extrai o texto de uma página web."""
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
    return text

def store_text_in_vector_db(text):
    """Divide o texto em sentenças, gera embeddings e armazena no banco vetorial."""
    sentences = text.split(". ")
    embeddings = embedding_model.encode(sentences)

    print(f"Total de sentenças extraídas: {len(sentences)}")  # Debug

    # Adiciona as sentenças ao banco vetorial
    points = []
    for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
        points.append(
            qdrant_client.http.models.PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={"text": sentence}
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("✅ Ingestão de dados concluída com sucesso!")

@app.route('/ingest', methods=['POST'])
def ingest():
    """Endpoint para ingestão manual de textos"""
    url = "https://hotmart.com/pt-br/blog/como-funciona-hotmart"
    text = extract_text_from_url(url)

    if text:
        store_text_in_vector_db(text)
        return jsonify({"message": "Texto processado e armazenado com sucesso"}), 200
    else:
        return jsonify({"error": "Erro ao baixar a página"}), 500

if __name__ == '__main__':
    print("Baixando e armazenando texto da Hotmart...")
    url = "https://hotmart.com/pt-br/blog/como-funciona-hotmart"
    text = extract_text_from_url(url)
    if text:
        store_text_in_vector_db(text)
        print("Texto armazenado no banco vetorial com sucesso!")
    else:
        print("Erro ao baixar o texto da página.")

    # app.run(host='0.0.0.0', port=5003)
    app.run(host='0.0.0.0', port=5003, debug=DEBUG_MODE)

import os
import json
import csv
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
import qdrant_client
from langchain_openai.embeddings import OpenAIEmbeddings

from utils.sitemap_utils import get_all_sitemap_urls, extract_urls_from_sitemap, filter_course_urls, save_urls_to_csv

# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.environ["OPENAI_API_KEY"])
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

def ingest_ufsm(request):
    req = request.get_json(silent=True) or {}
    tipo = req.get("tipo", "curso")
    filtro_nome = req.get("filtro_nome")

    all_urls = get_all_sitemap_urls()
    if tipo == "curso":
        filtered_urls = filter_course_urls(all_urls, curso_especifico=filtro_nome)
    else:
        return {"error": "Atualmente apenas ingestão de cursos está suportada."}, 400

    if not filtered_urls:
        return {"error": "Nenhuma URL encontrada para o filtro aplicado."}, 404

    save_urls_to_csv(filtered_urls)

    sentences, metadata = [], []
    for url, categoria in filtered_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
            full_text = "\n".join(paragraphs)

            for sent in full_text.split(". "):
                if len(sent.strip()) >= 40:
                    sentences.append(sent.strip())
                    metadata.append({"source": url, "categoria": categoria, "timestamp": datetime.now().isoformat()})

        except Exception as e:
            logging.warning(f"Erro ao processar {url}: {e}")
            continue

    if not sentences:
        return {"error": "Nenhum conteúdo válido encontrado."}, 500

    embeddings = embedding_model.encode(sentences)
    collection_name = f"ufsm_{tipo}"

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qdrant_client.http.models.VectorParams(size=384, distance=qdrant_client.http.models.Distance.COSINE)
    )

    points = [
        qdrant_client.http.models.PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={**metadata[i], "text": sentence}
        ) for i, (sentence, embedding) in enumerate(zip(sentences, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)

    return {
        "message": f"{len(sentences)} sentenças ingeridas na coleção `{collection_name}`.",
        "csv": "data/ufsm_urls.csv"
    }, 200
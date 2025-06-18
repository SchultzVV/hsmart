from flask import Flask, jsonify, request
import qdrant_client
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import xml.etree.ElementTree as ET
import os
import logging
import sys
import csv
from datetime import datetime
from unidecode import unidecode


# Configura os logs para aparecerem no Docker
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
# 
client = qdrant_client.QdrantClient(host="vector_db", port=6333)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    urls = []

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(url.text)
    return urls


def get_all_sitemap_urls():
    robots_url = "https://www.ufsm.br/robots.txt"
    response = requests.get(robots_url)
    sitemap_urls = []

    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_urls.append(line.split(": ", 1)[1])

    all_urls = []
    for sitemap in sitemap_urls:
        urls = extract_urls_from_sitemap(sitemap)
        all_urls.extend(urls)

    return all_urls


def filter_course_urls(urls, curso_especifico=None):
    filtered = []
    for url in urls:
        if "/cursos/graduacao/" in url:
            if curso_especifico:
                if curso_especifico.lower() in url.lower():
                    filtered.append((url, "curso"))
            else:
                filtered.append((url, "curso"))
    return filtered


def save_urls_to_csv(data, filename="data/ufsm_urls.csv"):
    os.makedirs("data", exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "categoria"])
        writer.writerows(data)
    logging.info(f"📝 CSV salvo com {len(data)} URLs em {filename}")


@app.route('/ingest_ufsm', methods=['POST'])
def ingest_ufsm():
    base_url = "https://www.ufsm.br"
    req = request.get_json(silent=True) or {}

    tipo = req.get("tipo", "curso")  # default: curso
    filtro_nome = req.get("filtro_nome")  # ex: "ciencia-da-computacao"

    all_urls = get_all_sitemap_urls()

    if tipo == "curso":
        filtered_urls = filter_course_urls(all_urls, curso_especifico=filtro_nome)
    else:
        return jsonify({"error": "Atualmente apenas ingestão de cursos está suportada."}), 400

    if not filtered_urls:
        return jsonify({"error": "Nenhuma URL encontrada para o filtro aplicado."}), 404

    save_urls_to_csv(filtered_urls)

    # Faz crawling e ingestão dos conteúdos filtrados
    sentences = []
    metadata = []

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
                    metadata.append({
                        "source": url,
                        "categoria": categoria,
                        "timestamp": datetime.now().isoformat()
                    })

        except Exception as e:
            logging.warning(f"Erro ao processar {url}: {e}")
            continue

    if not sentences:
        return jsonify({"error": "Nenhum conteúdo válido encontrado nas páginas filtradas."}), 500

    embeddings = embedding_model.encode(sentences)
    logging.info(f"📌 Total de sentenças extraídas: {len(sentences)}")

    collection_name = f"ufsm_{tipo}"

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
            payload={**metadata[i], "text": sentence}
        )
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)
    logging.info(f"✅ Ingestão concluída com sucesso na coleção `{collection_name}`")

    return jsonify({
        "message": f"{len(sentences)} sentenças ingeridas na coleção `{collection_name}`.",
        "csv": "data/ufsm_urls.csv"
    }), 200

@app.route('/get_courses_list', methods=['GET'])
def get_courses_list():
    all_urls = get_all_sitemap_urls()
    course_urls = filter_course_urls(all_urls)

    cursos = set()
    for url, _ in course_urls:
        # Exemplo de URL: https://www.ufsm.br/cursos/graduacao/santa-maria/ciencia-da-computacao/wp-sitemap.xml
        parts = url.split("/cursos/graduacao/")[-1].split("/")
        if len(parts) >= 2:
            curso_slug = parts[-2]  # geralmente o nome do curso
            cursos.add(curso_slug.replace("-", " ").title())

    sorted_courses = sorted(cursos)

    return jsonify({
        "quantidade": len(sorted_courses),
        "cursos": sorted_courses
    }), 200
#---------------------------------------------------------------------------------------
import json

def gerar_dataset_fine_tuning(cursos, frases, path="/app/data/ufsm_geral_dataset.jsonl"):
    prompts_respostas = []
    
    for frase in frases:
        curso_encontrado = None
        for curso in cursos:
            if curso.lower() in frase.lower():
                curso_encontrado = curso
                break

        if curso_encontrado:
            prompt_variacoes = [
                f"A UFSM tem curso de {curso_encontrado}?",
                f"{curso_encontrado} é oferecido pela UFSM?",
                f"Existe {curso_encontrado} na Universidade Federal de Santa Maria?",
                f"UFSM oferece o curso de {curso_encontrado}?",
                f"Há {curso_encontrado} na UFSM?"
            ]
            for prompt in prompt_variacoes:
                prompts_respostas.append({
                    "prompt": prompt,
                    "response": frase
                })

    prompts_respostas.append({
        "prompt": "Quantos cursos a UFSM oferece?",
        "response": f"A UFSM oferece {len(cursos)} cursos diferentes."
    })

    os.makedirs("/app/data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in prompts_respostas:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    logging.info(f"💾 Dataset salvo com {len(prompts_respostas)} exemplos em `{path}`.")


@app.route('/ingest_ufsm_geral', methods=['POST'])
def ingest_ufsm_geral():
    all_urls = get_all_sitemap_urls()
    course_urls = filter_course_urls(all_urls)

    cursos = set()
    for url, _ in course_urls:
        parts = url.split("/cursos/graduacao/")[-1].split("/")
        if len(parts) >= 2:
            curso_slug = parts[-2]
            curso_nome = curso_slug.replace("-", " ").title()
            cursos.add(curso_nome)

    cursos_ordenados = sorted(cursos)
    total_cursos = len(cursos_ordenados)

    frases = []

    for curso in cursos_ordenados:
        frases.extend([
            f"A Universidade Federal de Santa Maria tem curso de {curso}.",
            f"{curso} é ofertado pela UFSM.",
            f"{curso} é um curso oferecido pela Universidade Federal de Santa Maria - UFSM.",
            f"A UFSM tem o curso de {curso}.",
            f"A UFSM ministra o curso de {curso}.",
            f"O curso de {curso} está disponível na UFSM.",
            f"{curso} é uma graduação da Universidade Federal de Santa Maria.",
        ])

    frases.extend([
        f"A quantidade de cursos da UFSM é {total_cursos}.",
        f"A Universidade Federal de Santa Maria ministra {total_cursos} cursos diferentes.",
        f"Atualmente a UFSM oferece {total_cursos} cursos de graduação.",
        f"No total, são {total_cursos} cursos oferecidos pela UFSM.",
    ])

    embeddings = embedding_model.encode(frases)
    logging.info(f"🧠 Ingerindo {len(frases)} frases em ufsm_geral_knowledge...")

    client.recreate_collection(
        collection_name="ufsm_geral_knowledge",
        vectors_config=qdrant_client.http.models.VectorParams(
            size=384,
            distance=qdrant_client.http.models.Distance.COSINE
        )
    )

    points = [
        qdrant_client.http.models.PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                "text": frase,
                "normalized_text": unidecode(frase),
                "categoria": "geral"
            }
        )
        for i, (frase, embedding) in enumerate(zip(frases, embeddings))
    ]

    client.upsert(collection_name="ufsm_geral_knowledge", points=points)
    gerar_dataset_fine_tuning(cursos_ordenados, frases)

    return jsonify({
        "message": f"{len(frases)} frases geradas e armazenadas com sucesso!",
        "colecao": "ufsm_geral_knowledge"
    }), 200
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
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

    text = data["text"]
    collection = data.get("collection", "mlops_knowledge")  # padrão: mlops_knowledge

    try:
        store_text_in_vector_db(text, collection)
        return jsonify({
            "message": f"Texto manual processado com sucesso na coleção `{collection}`"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_collection', methods=['POST'])
def delete_collection():
    """
    Deleta uma coleção inteira do Qdrant (exclui todos os documentos)
    Requer o campo: {"collection": "nome_da_colecao"}
    """
    data = request.get_json()

    if not data or "collection" not in data:
        return jsonify({"error": "O campo 'collection' é obrigatório"}), 400

    collection_name = data["collection"]

    try:
        if client.collection_exists(collection_name):
            client.delete_collection(collection_name=collection_name)
            return jsonify({"message": f"Coleção `{collection_name}` deletada com sucesso."}), 200
        else:
            return jsonify({"error": f"A coleção `{collection_name}` não existe."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from urllib.parse import urljoin, urlparse
from collections import deque

def crawl_ufsm_site(base_url="https://www.ufsm.br", max_pages=50):
    visited = set()
    queue = deque([base_url])
    all_texts = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue

            visited.add(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extrair parágrafos com conteúdo relevante
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
            full_text = "\n".join(paragraphs)
            if full_text:
                all_texts.append({"url": url, "text": full_text})

            # Descobrir novos links internos
            for link_tag in soup.find_all("a", href=True):
                href = link_tag['href']
                full_link = urljoin(url, href)
                if full_link.startswith(base_url) and full_link not in visited:
                    queue.append(full_link)

        except Exception as e:
            logging.warning(f"Erro ao processar {url}: {e}")
            continue

    logging.info(f"🔎 Crawling finalizado: {len(visited)} páginas visitadas.")
    return all_texts

@app.route('/ingest_ufsm2', methods=['POST'])
def ingest_ufsm2():
    base_url = "https://www.ufsm.br"
    pages = crawl_ufsm_site(base_url=base_url, max_pages=50)

    if not pages:
        return jsonify({"error": "Nenhum texto foi encontrado no site da UFSM."}), 500

    sentences = []
    metadata = []

    for i, page in enumerate(pages):
        text = page["text"]
        url = page["url"]
        for sent in text.split(". "):
            if len(sent.strip()) >= 40:  # filtrar sentenças curtas
                sentences.append(sent.strip())
                metadata.append({"source": url})

    embeddings = embedding_model.encode(sentences)
    logging.info(f"📌 Total de sentenças extraídas: {len(sentences)}")

    client.recreate_collection(
        collection_name="ufsm_knowledge",
        vectors_config=qdrant_client.http.models.VectorParams(
            size=384,
            distance=qdrant_client.http.models.Distance.COSINE
        )
    )

    points = [
        qdrant_client.http.models.PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={"text": sentence, "source": metadata[i]["source"]}
        )
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings))
    ]

    client.upsert(collection_name="ufsm_knowledge", points=points)
    logging.info(f"✅ Ingestão concluída com sucesso na coleção `ufsm_knowledge`")

    return jsonify({"message": f"{len(sentences)} sentenças da UFSM foram ingeridas com sucesso!"}), 200

@app.route('/list_collections', methods=['GET'])
def list_collections():
    """Lista os nomes de todas as coleções disponíveis no Qdrant"""
    try:
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        return jsonify({"collections": collection_names}), 200
    except Exception as e:
        logging.error(f"Erro ao listar coleções: {e}")
        return jsonify({"error": str(e)}), 500

# @app.route('/ingest_manual', methods=['POST'])
# def ingest_manual():
#     data = request.get_json()
#     if not data or "text" not in data:
#         return jsonify({"error": "O campo 'text' é obrigatório"}), 400

#     store_text_in_vector_db(data["text"], "mlops_knowledge")
#     return jsonify({"message": "Texto manual processado com sucesso"}), 200


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

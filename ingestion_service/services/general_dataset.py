import os
import json
import logging
from datetime import datetime
from unidecode import unidecode

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# Modelos e client
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

def get_all_sitemap_urls():
    robots_url = "https://www.ufsm.br/robots.txt"
    response = requests.get(robots_url)
    sitemap_urls = []

    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_urls.append(line.split(": ", 1)[1])
    return sitemap_urls


def extract_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    urls = []
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(url.text)
    return urls


def filter_course_urls(urls):
    return [url for url in urls if "/cursos/graduacao/" in url]


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


def ingest_ufsm_geral():
    all_urls = []
    for sitemap in get_all_sitemap_urls():
        all_urls.extend(extract_urls_from_sitemap(sitemap))

    course_urls = filter_course_urls(all_urls)

    cursos = set()
    for url in course_urls:
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
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    points = [
        PointStruct(
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

    return {
        "message": f"{len(frases)} frases geradas e armazenadas com sucesso!",
        "colecao": "ufsm_geral_knowledge"
    }

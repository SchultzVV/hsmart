import logging
import os
import json
from datetime import datetime
from unidecode import unidecode
from sentence_transformers import SentenceTransformer
import qdrant_client

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

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

    logging.info(f"📎 Dataset salvo com {len(prompts_respostas)} exemplos em `{path}`.")

def ingest_ufsm_geral(course_list, collection_name="ufsm_geral_knowledge"):
    frases = []

    for curso in course_list:
        frases.extend([
            f"A Universidade Federal de Santa Maria tem curso de {curso}.",
            f"{curso} é ofertado pela UFSM.",
            f"{curso} é um curso oferecido pela Universidade Federal de Santa Maria - UFSM.",
            f"A UFSM tem o curso de {curso}.",
            f"A UFSM ministra o curso de {curso}.",
            f"O curso de {curso} está disponível na UFSM.",
            f"{curso} é uma graduação da Universidade Federal de Santa Maria."
        ])

    total_cursos = len(course_list)
    frases.extend([
        f"A quantidade de cursos da UFSM é {total_cursos}.",
        f"A Universidade Federal de Santa Maria ministra {total_cursos} cursos diferentes.",
        f"Atualmente a UFSM oferece {total_cursos} cursos de graduação.",
        f"No total, são {total_cursos} cursos oferecidos pela UFSM."
    ])

    embeddings = embedding_model.encode(frases)
    logging.info(f"🧠 Ingerindo {len(frases)} frases em {collection_name}...")

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
            payload={
                "text": frase,
                "normalized_text": unidecode(frase),
                "categoria": "geral",
                "timestamp": datetime.now().isoformat()
            }
        )
        for i, (frase, embedding) in enumerate(zip(frases, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)
    gerar_dataset_fine_tuning(course_list, frases)

    return len(frases), collection_name
import qdrant_client
from qdrant_client.http.models import VectorParams, Distance, PointStruct
import logging

client = qdrant_client.QdrantClient(host="vector_db", port=6333)


def recreate_and_upsert(collection_name, sentences, embeddings, metadata):
    """
    Cria (ou recria) uma coleção no Qdrant e insere os embeddings com metadados.
    """
    logging.info(f"🧹 (Re)criando coleção `{collection_name}` com {len(sentences)} sentenças...")

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=len(embeddings[0]),
            distance=Distance.COSINE
        )
    )

    points = [
        PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={**metadata[i], "text": sentence}
        )
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)
    logging.info(f"✅ Inserção finalizada na coleção `{collection_name}` com {len(points)} pontos.")

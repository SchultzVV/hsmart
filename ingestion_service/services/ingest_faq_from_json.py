import json
from collections import defaultdict
from pathlib import Path
from langchain_core.documents import Document
from qdrant_client.http.models import VectorParams, Distance
from shared.langchain_container import LangChainContainer

def ingest_faq_from_jsonl(file_path: str, collection_name: str = "ufsm_faqs"):
    """
    Ingesta um dataset JSONL com pares {prompt, response} em uma coleção vetorial.
    Os prompts são armazenados como exemplos no metadata do response.

    Args:
        file_path (str): Caminho para o arquivo .jsonl
        collection_name (str): Nome da coleção no Qdrant
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {file_path}")

    print(f"📥 Lendo dataset de {file_path}...")
    response_map = defaultdict(list)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip())
            response_map[data["response"]].append(data["prompt"])

    docs = [
        Document(
            page_content=response,
            metadata={
                "prompt_examples": prompts,
                "type": "faq"
            }
        )
        for response, prompts in response_map.items()
    ]

    if not docs:
        print("⚠️ Nenhum documento encontrado para ingestão.")
        return

    container = LangChainContainer()
    embeddings = container.embedding_model.embed_documents([doc.page_content for doc in docs])
    embedding_dim = len(embeddings[0])

    print(f"🔧 Recriando coleção '{collection_name}' com dimensão {embedding_dim}...")
    container.qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
    )

    container.set_collection(collection_name)
    container.vectorstore.add_documents(docs)

    print(f"✅ {len(docs)} documentos FAQ ingeridos na coleção '{collection_name}'")

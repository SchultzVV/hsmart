import json
from collections import defaultdict
from pathlib import Path
from langchain_core.documents import Document
from qdrant_client.http.models import VectorParams, Distance
from shared.langchain_container import LangChainContainer

# Caminho do arquivo com os pares prompt-response
file_path = Path("ufsm_geral_dataset.jsonl")

# Agrupa os prompts pela mesma resposta
response_map = defaultdict(list)

with file_path.open("r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line.strip())
        response = data["response"]
        prompt = data["prompt"]
        response_map[response].append(prompt)

# Cria documentos com metadados
docs = []
for response, prompts in response_map.items():
    docs.append(Document(
        page_content=response,
        metadata={
            "prompt_examples": prompts,
            "type": "faq"
        }
    ))

# Ingestão no Qdrant com LangChainContainer
container = LangChainContainer()
collection_name = "ufsm_faqs"

# Cria embeddings para detectar a dimensão
embeddings = container.embedding_model.embed_documents([doc.page_content for doc in docs])
embedding_dim = len(embeddings[0])

# Cria ou recria a coleção
container.qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=embedding_dim,
        distance=Distance.COSINE
    )
)

# Configura a collection e insere
container.set_collection(collection_name)
container.vectorstore.add_documents(docs)

print(f"✅ {len(docs)} documentos FAQ ingeridos na coleção '{collection_name}'")

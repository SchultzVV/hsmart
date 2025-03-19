
Dentro do container de ingestão 
```bash
docker exec -it ingestion_service bash
python
```

```python
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

texto_teste = "A Hotmart é uma plataforma global para venda de conteúdos digitais."
embedding = embedding_model.encode([texto_teste])

print("Embedding gerado:", embedding)
print("Dimensão do embedding:", len(embedding[0]))
```

### para deletar as ingestões:

```python
import chromadb

# Conectar ao banco vetorial
chroma_client = chromadb.PersistentClient(path="/app/chroma_db")
collection = chroma_client.get_or_create_collection(name="hotmart_knowledge")

# Apagar todos os dados antigos
collection.delete(ids=collection.get()["ids"])
print("🚨 Banco de vetores resetado. Agora, execute a ingestão novamente.")
```
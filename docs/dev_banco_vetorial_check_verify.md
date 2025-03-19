Para verificar se as informações estão sendo ingeridas pelo banco vetorial ChromaDB, dentro do container
```bash
docker exec -it ingestion_service bash
python
```
Use esse código
```python
import chromadb

# Conectar ao banco vetorial
chroma_client = chromadb.PersistentClient(path="/app/chroma_db")
collection = chroma_client.get_or_create_collection(name="hotmart_knowledge")

# Verificar quantos itens estão armazenados
print("Total de documentos armazenados:", collection.count())

# Exibir um exemplo do que foi armazenado
if collection.count() > 0:
    results = collection.get()
    print("IDs armazenados:", results["ids"])
    print("Metadados armazenados:", results["metadatas"])
else:
    print("Nenhum dado encontrado no banco vetorial.")
```

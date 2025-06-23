from flask import jsonify
from shared.langchain_container import LangChainContainer

container = LangChainContainer()
client = container.qdrant_client
embedding_model = container.embedding_model

def ingest_manual_text(request):
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Texto obrigatório"}), 400

    sentences = [s.strip() for s in data["text"].split(". ") if len(s.strip()) >= 40]
    embeddings = embedding_model.embed_documents(sentences)
    metadata = [{"source": "manual"} for _ in sentences]

    collection = data.get("collection", "mlops_knowledge")
    container.store(collection, sentences, embeddings, metadata)
    return jsonify({"message": f"Ingestão manual em `{collection}` realizada com sucesso"}), 200

def list_collections():
    try:
        collections = client.get_collections()
        collection_infos = []

        for col in collections.collections:
            try:
                info = client.get_collection(collection_name=col.name)
                vectors_cfg = info.config.params.vectors
                count_result = client.count(collection_name=col.name, exact=True)

                collection_infos.append({
                    "name": col.name,
                    "vector_size": vectors_cfg.size,
                    "distance": vectors_cfg.distance,
                    "points_count": count_result.count,
                    "status": info.status,
                    "hints": getattr(info, "hints", None)
                    # 🔁 Removido: "on_disk": info.on_disk
                })
            except Exception as inner_err:
                collection_infos.append({
                    "name": col.name,
                    "error": f"❌ Erro ao buscar detalhes: {inner_err}"
                })

        return jsonify({"collections": collection_infos}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao listar coleções: {e}"}), 500
# def list_collections():
#     try:
#         collections = client.get_collections()
#         return jsonify({"collections": [c.name for c in collections.collections]}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def list_all_documents():
    try:
        resultado = {}
        for col in client.get_collections().collections:
            docs, _ = client.scroll(col.name, limit=100)
            resultado[col.name] = [d.payload for d in docs]
        return jsonify({"collections": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_collection(request):
    data = request.get_json()
    name = data.get("collection")
    if not name:
        return jsonify({"error": "Coleção obrigatória"}), 400
    try:
        client.delete_collection(name)
        return jsonify({"message": f"Coleção `{name}` deletada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

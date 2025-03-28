from flask import request, jsonify
import logging
from datetime import datetime
from sentence_transformers import SentenceTransformer
from utils.vector_store import recreate_and_upsert

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def ingest_manual(flask_request):
    try:
        data = flask_request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "O campo 'text' é obrigatório"}), 400

        text = data["text"]
        collection = data.get("collection", "mlops_knowledge")

        sentences = [s.strip() for s in text.split(". ") if len(s.strip()) >= 40]
        if not sentences:
            return jsonify({"error": "Nenhuma sentença válida encontrada no texto"}), 400

        embeddings = embedding_model.encode(sentences)
        metadata = [{"source": "manual", "timestamp": datetime.now().isoformat()} for _ in sentences]

        recreate_and_upsert(
            collection_name=collection,
            sentences=sentences,
            embeddings=embeddings,
            metadata=metadata
        )

        logging.info(f"✅ Ingestão manual concluída na coleção `{collection}` com {len(sentences)} sentenças.")
        return jsonify({
            "message": f"Texto manual processado com sucesso na coleção `{collection}`",
            "sentencas": len(sentences)
        }), 200

    except Exception as e:
        logging.error(f"Erro na ingestão manual: {e}")
        return jsonify({"error": str(e)}), 500

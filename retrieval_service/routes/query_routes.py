from flask import Blueprint, request, jsonify, current_app
from unidecode import unidecode
import json
import logging
# import qdrant_client
from models.client_loader import get_qdrant_client


from models.model_loader import load_embedding_model, load_generator_model
from services.collection_selector import decide_collection
from services.context_retriever import retrieve_context
from services.answer_generator import generate_answer

query_blueprint = Blueprint("query", __name__)
logger = logging.getLogger(__name__)

# 🔧 Inicialização de modelos e cliente
# client = qdrant_client.QdrantClient(host="vector_db", port=6333)
client = get_qdrant_client()
embedding_model = load_embedding_model()
generator = load_generator_model()


@query_blueprint.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "").strip()
    question = unidecode(question)

    if not question:
        return jsonify({"error": "A pergunta não pode estar vazia."}), 400

    logger.info(f"📥 Pergunta recebida: {question}")

    try:
        context = retrieve_context(question, client, embedding_model)
        response = generate_answer(question, context, generator)
    except Exception as e:
        logger.exception("❌ Erro durante o processamento da pergunta.")
        return jsonify({"error": str(e)}), 500

    # 📝 Salvar a resposta em um arquivo
    try:
        with open("ultima_resposta.txt", "w", encoding="utf-8") as f:
            f.write(f"Pergunta: {question}\n\n")
            f.write(f"Contexto utilizado:\n{context}\n\n")
            f.write(f"Resposta gerada:\n{response}\n")
        logger.info("📝 Resposta salva em 'ultima_resposta.txt'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resposta: {e}")

    return current_app.response_class(
        response=json.dumps({"response": response}, ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

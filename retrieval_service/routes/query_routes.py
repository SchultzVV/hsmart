from flask import Blueprint, request, jsonify, current_app
from unidecode import unidecode
import json
import logging
from services.qa_service import qa_chain
from shared.conversation_memory import get_conversation_memory

query_blueprint = Blueprint("query", __name__)
logger = logging.getLogger(__name__)

@query_blueprint.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = unidecode(data.get("question", "").strip())
    session_id = data.get("session_id", "default")

    if not question:
        return jsonify({"error": "A pergunta não pode estar vazia."}), 400

    logger.info(f"📥 Pergunta recebida: {question}")

    try:
        # result = qa_chain.invoke({"query": question})
        result = qa_chain(question, session_id=session_id)
        answer = result["result"]
        sources = result.get("source_documents", [])
        context = "\n---\n".join([doc.page_content for doc in sources])
    except Exception as e:
        logger.exception("❌ Erro durante o processamento.")
        return jsonify({"error": str(e)}), 500

    # Salva a última resposta
    try:
        with open("ultima_resposta.txt", "w", encoding="utf-8") as f:
            f.write(f"Pergunta: {question}\n\nContexto:\n{context}\n\nResposta:\n{answer}\n")
        logger.info("📝 Resposta salva em 'ultima_resposta.txt'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resposta: {e}")

    return current_app.response_class(
        response=json.dumps({"response": answer}, ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

@query_blueprint.route("/history/<session_id>", methods=["GET"])
def get_history(session_id):
    try:
        memory = get_conversation_memory(session_id)
        messages = memory.chat_memory.messages

        formatted = []
        for msg in messages:
            role = "user" if msg.type == "human" else "ai"
            formatted.append({"role": role, "content": msg.content})

        return jsonify({
            "session_id": session_id,
            "total_messages": len(formatted),
            "history": formatted
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao recuperar histórico: {str(e)}"}), 500
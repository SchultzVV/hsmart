from flask import Blueprint, request, jsonify, current_app
from unidecode import unidecode
import json
import logging
import os

from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain_openai.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient

query_blueprint = Blueprint("query", __name__)
logger = logging.getLogger(__name__)

# 🔧 Inicialização dos componentes
client = QdrantClient(host="vector_db", port=6333)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

vectorstore = Qdrant(
    client=client,
    collection_name="ufsm_geral_knowledge",  # Pode ser dinâmico se desejar
    embeddings=embedding_model
)

retriever = vectorstore.as_retriever()

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)


@query_blueprint.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "").strip()
    question = unidecode(question)

    if not question:
        return jsonify({"error": "A pergunta não pode estar vazia."}), 400

    logger.info(f"📥 Pergunta recebida: {question}")

    try:
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        sources = result.get("source_documents", [])
        context = "\n---\n".join([doc.page_content for doc in sources])
    except Exception as e:
        logger.exception("❌ Erro durante o processamento da pergunta.")
        return jsonify({"error": str(e)}), 500

    # 📝 Salvar resposta e contexto
    try:
        with open("ultima_resposta.txt", "w", encoding="utf-8") as f:
            f.write(f"Pergunta: {question}\n\n")
            f.write(f"Contexto utilizado:\n{context}\n\n")
            f.write(f"Resposta gerada:\n{answer}\n")
        logger.info("📝 Resposta salva em 'ultima_resposta.txt'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resposta: {e}")

    return current_app.response_class(
        response=json.dumps({"response": answer}, ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

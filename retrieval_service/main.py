from flask import Flask
from routes.query_routes import query_blueprint
import os
import logging
import sys

from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient

# Configura logs para o console (útil em Docker)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Inicializa Flask
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Registra rotas
app.register_blueprint(query_blueprint)

# Inicializa embeddings e vetores
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

client = QdrantClient(host="vector_db", port=6333)

vectorstore = Qdrant(
    client=client,
    collection_name="ufsm_geral_knowledge",
    embeddings=embedding
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

# Exemplo (pode ser movido para testes ou logs)
if DEBUG_MODE:
    example = qa_chain.run("A UFSM tem curso de Física?")
    print(f"🧠 Exemplo de resposta: {example}")


if __name__ == "__main__":
    print("🚀 Inicializando serviço de recuperação...")
    app.run(host="0.0.0.0", port=5004, debug=DEBUG_MODE)

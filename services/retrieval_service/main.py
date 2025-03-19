import qdrant_client
from flask import Flask, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import re
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Inicializando Flask
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Conectando ao Qdrant
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

# Nome da coleção no Qdrant
COLLECTION_NAME = "hotmart_knowledge"

# 🔹 Carregar modelo de embeddings para busca no banco vetorial
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cuda" if torch.cuda.is_available() else "cpu")

# 🔥 Configurar a GPU se disponível
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"\n🚀 Usando dispositivo: {device}")

# 🔥 Usando pipeline do Hugging Face com GPU ativada
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    device=0 if torch.cuda.is_available() else -1
)

logging.info("\n✅ Pipeline de geração de texto carregado com FLAN-T5-SMALL!")


def retrieve_context(question):
    """Busca os trechos mais relevantes no banco vetorial"""
    question_embedding = embedding_model.encode(question).tolist()

    logging.info(f"\n🔍 Consulta ao Qdrant para a pergunta: {question}")

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=question_embedding,
        limit=2
    )

    logging.info(f"\n🔹 Resultados retornados pelo Qdrant: {results}")

    if results:
        context = " ".join([hit.payload["text"] for hit in results])
    else:
        context = "Não há informações disponíveis sobre esse assunto."

    logging.info(f"\n✅ Contexto recuperado: {context}")
    return context


def clean_response(response):
    """Remove conteúdos extras indesejados na resposta"""
    # 🔹 Remover textos que começam com palavras irrelevantes
    unwanted_phrases = ["VÍDEO:", "VIDEO:", "Saiba mais",
                        "Leia mais", "Para saber mais"]
    for phrase in unwanted_phrases:
        response = re.split(phrase, response, flags=re.IGNORECASE)[0].strip()

    # 🔹 Remover pontuações e espaços extras no final
    response = re.sub(r"\s+[,.!?]$", "", response)

    return response


def generate_answer(question, context):
    """Gera uma resposta coerente baseada no contexto relevante"""

    if "Não há informações disponíveis" in context:
        return "Não sei a resposta."

    # Melhorando o prompt para garantir respostas mais precisas e em português
    prompt = f"""
    Responda à seguinte pergunta com base no contexto fornecido. 
    Responda **apenas em português** de forma objetiva.

    🔹 **Pergunta:** {question}

    🔹 **Contexto:** {context}

    🔹 **Resposta:**
    """

    response = generator(
        prompt,
        max_length=150,  # Ajustado para evitar repetições longas
        min_length=40,  # Evita respostas curtas e genéricas
        truncation=True,
        do_sample=True,  # Gera variações na resposta
        temperature=0.5,  # Menos aleatoriedade para mais precisão
        top_k=40,  
        top_p=0.85,  
        repetition_penalty=1.2,  
    )[0]["generated_text"]

    response = clean_response(response)
    logging.info(f"\n🤖 Resposta gerada: {response}")
    return response





@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get("question", "")

    # Busca os trechos mais relevantes no Qdrant
    context = retrieve_context(question)

    # Gera resposta usando FLAN-T5-SMALL
    response = generate_answer(question, context)

    # formatted_response = response.encode("utf-8").decode("utf-8")
    # 🔹 Salva a resposta em um arquivo .txt
    with open("ultima_resposta.txt", "w", encoding="utf-8") as file:
        file.write(f"Pergunta: {question}\n\nResposta:\n{response}")

    return jsonify({"response": response}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=DEBUG_MODE)

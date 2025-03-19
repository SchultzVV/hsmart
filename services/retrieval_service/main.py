import qdrant_client
from flask import Flask, request, jsonify
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments, pipeline
from sentence_transformers import SentenceTransformer
import torch
import os
import logging
import sys
from datasets import Dataset

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
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# 🔥 Configurar a GPU se disponível
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"\n🚀 Usando dispositivo: {device}")

# 🔥 Carregar modelo de Geração de Texto (Flan-T5)
MODEL_PATH = "./fine_tuned_flan_t5"
if os.path.exists(MODEL_PATH):
    logging.info("✅ Carregando modelo fine-tuned...")
    tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
else:
    logging.info("⚠️ Nenhum modelo fine-tuned encontrado, carregando Flan-T5 base...")
    tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
    model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)

logging.info("\n✅ Pipeline de geração de texto carregado!")


def retrieve_context(question):
    """Busca os trechos mais relevantes no banco vetorial"""
    question_embedding = embedding_model.encode(question).tolist()
    logging.info(f"\n🔍 Consulta ao Qdrant para a pergunta: {question}")

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=question_embedding,
        limit=5  # Ajustado para buscar mais opções e filtrar
    )

    if results:
        # Filtrar respostas muito curtas ou irrelevantes
        context_candidates = [hit.payload["text"] for hit in results if len(hit.payload["text"]) > 20]

        if not context_candidates:
            context = "Não há informações disponíveis sobre esse assunto."
        else:
            context = " ".join(context_candidates[:3])  # Pegamos no máximo 3 trechos
    else:
        context = "Não há informações disponíveis sobre esse assunto."

    logging.info(f"\n✅ Contexto recuperado: {context}")
    return context


def generate_answer(question, context):
    """Gera uma resposta coerente baseada no contexto relevante"""
    if "Não há informações disponíveis" in context:
        return "Não sei a resposta."

    prompt = f"""
    Responda à seguinte pergunta com base no contexto fornecido.
    Responda **somente em português** e de forma clara e objetiva.

    🔹 **Pergunta:** {question}

    🔹 **Contexto:** {context}

    🔹 **Resposta:** (não use informações fora do contexto fornecido)
    """

    response = generator(
        prompt,
        max_length=150,  
        min_length=40,  
        truncation=True,
        do_sample=False,  # Mudamos para evitar respostas aleatórias
        temperature=0.1,  # Reduzimos para tornar as respostas mais exatas
        top_k=30,  
        top_p=0.85,  
        repetition_penalty=1.3,  
    )[0]["generated_text"]

    logging.info(f"\n🤖 Resposta gerada: {response}")
    return response


@app.route('/fine_tune', methods=['POST'])
def fine_tune():
    """Endpoint para iniciar fine-tuning manualmente"""
    fine_tune_model()
    return jsonify({"message": "Fine-tuning concluído!"}), 200


@app.route('/query', methods=['POST'])
def query():
    """Endpoint para responder perguntas com base no contexto recuperado"""
    data = request.json
    question = data.get("question", "")

    context = retrieve_context(question)
    response = generate_answer(question, context)

    return jsonify({"response": response}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=DEBUG_MODE)

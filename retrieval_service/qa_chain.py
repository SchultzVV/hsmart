import qdrant_client
from flask import Flask, request
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
# from sentence_transformers import SentenceTransformer
import torch
import os
import logging
import sys
from flask import Flask, request
import json
from unidecode import unidecode
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings



logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

client = qdrant_client.QdrantClient(host="vector_db", port=6333)


# embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.environ["OPENAI_API_KEY"])
# embedding_model = SentenceTransformer(
#     "all-MiniLM-L6-v2",
#     device="cuda" if torch.cuda.is_available() else "cpu"
# )

# from openai import OpenAI
from langchain_openai import OpenAIEmbeddings

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
embedding_model = OpenAIEmbeddings()#client=openai_client, model="text-embedding-3-small")


device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"\n🚀 Usando dispositivo: {device}")

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

import random


def decide_collection(question, max_results_per_collection=3):
    question_embedding = embedding_model.encode(question).tolist()

    try:
        collections = client.get_collections()
        available = [col.name for col in collections.collections]

        if not available:
            logging.warning("❌ Nenhuma coleção disponível no Qdrant.")
            return None

        scores = {}
        for col in available:
            try:
                results = client.search(
                    collection_name=col,
                    query_vector=question_embedding,
                    limit=max_results_per_collection
                )
                if results:
                    # Calcula score médio ou máximo
                    avg_score = sum([r.score for r in results if r.score]) / len(results)
                    scores[col] = avg_score
                    logging.info(f"📊 Score médio da coleção `{col}`: {avg_score:.4f}")
            except Exception as e:
                logging.warning(f"Erro ao buscar na coleção `{col}`: {e}")

        if scores:
            # 🔝 Seleciona a coleção com maior score médio
            best_collection = max(scores, key=scores.get)
            logging.info(f"✅ Coleção mais relevante: `{best_collection}`")
            return best_collection
        else:
            logging.warning("⚠️ Nenhuma coleção retornou resultados relevantes.")
            return None

    except Exception as e:
        logging.error(f"Erro ao decidir melhor coleção: {e}")
        return None


# def decide_collection(question):
#     q = question.lower()
#     if "ufsm" in q or "campus" in q or "matrícula" in q or "disciplina" in q:
#         return "ufsm_knowledge"
#     elif "hotmart" in q:
#         return "hotmart_knowledge"
#     elif "mlops" in q or "modelo" in q:
#         return "mlops_knowledge"
#     return None

def retrieve_context(question):
    collection_name = decide_collection(question)
    question_embedding = embedding_model.encode(question).tolist()

    try:
        collections = client.get_collections()
        available = [col.name for col in collections.collections]
        logging.info(f"📚 Coleções disponíveis: {available}")

        # 🔍 Caso a coleção exista normalmente, busca apenas nela
        if collection_name and collection_name in available:
            logging.info(f"🔍 Usando coleção detectada: `{collection_name}`")
            results = client.search(
                collection_name=collection_name,
                query_vector=question_embedding,
                limit=5
            )
            high_score = [hit for hit in results if hit.score and hit.score >= 0.7]
            if high_score:
                return " ".join([hit.payload["text"] for hit in high_score])
            return "Não há informações suficientes no contexto para responder à pergunta."

        # 🔁 Se nenhuma coleção for encontrada ou a escolhida não existir
        logging.warning(f"⚠️ Coleção `{collection_name}` não encontrada. Buscando em todas as coleções.")
        combined_context = []

        for col in available:
            try:
                results = client.search(
                    collection_name=col,
                    query_vector=question_embedding,
                    limit=3
                )
                high_score = [hit for hit in results if hit.score and hit.score >= 0.7]
                combined_context.extend([hit.payload["text"] for hit in high_score])
                logging.info(f"🔹 Resultados da coleção `{col}`: {len(high_score)} trechos")
            except Exception as e:
                logging.warning(f"Erro ao buscar na coleção `{col}`: {e}")

        if combined_context:
            return " ".join(combined_context)
        return "Não há informações suficientes em nenhuma coleção para responder à pergunta."

    except Exception as e:
        return f"Erro ao verificar coleções disponíveis: {e}"


# def retrieve_context(question):
#     """Busca os trechos mais relevantes no Qdrant e ajusta dinamicamente o filtro de score"""
#     if "mlops" in question.lower():
#         collection_name = "mlops_knowledge"
#     else:
#         collection_name = "hotmart_knowledge"

#     question_embedding = embedding_model.encode(question).tolist()
#     logging.info(f"\n🔍 Buscando na coleção `{collection_name}` para a pergunta: {question}")

#     # 🔎 Contar número de pontos na coleção
#     try:
#         scroll_result = client.scroll(collection_name=collection_name, limit=100)
#         total_docs = len(scroll_result[0])
#     except Exception as e:
#         logging.warning(f"Erro ao contar documentos: {e}")
#         total_docs = 0

#     # 📏 Ajustar threshold dinamicamente
#     score_threshold = 0.7 if total_docs > 10 else 0.3
#     logging.info(f"📊 Total de sentenças na coleção: {total_docs} → Usando threshold: {score_threshold}")

#     results = client.search(
#         collection_name=collection_name,
#         query_vector=question_embedding,
#         limit=5
#     )

#     # 🧠 Filtrar por score
#     high_score = [hit for hit in results if hit.score and hit.score >= score_threshold]

#     if high_score:
#         context = " ".join([hit.payload["text"] for hit in high_score])
#     else:
#         context = "Não há informações suficientes no contexto para responder à pergunta."

#     logging.info(f"\n✅ Contexto recuperado: {context}")
#     return context

# def retrieve_context(question):
#     """Decide coleção e aplica filtro de score >= 0.7"""
#     collection = "mlops_knowledge" if "mlops" in question.lower() else "hotmart_knowledge"
#     question_embedding = embedding_model.encode(question).tolist()
#     logging.info(f"\n🔍 Buscando na coleção `{collection}` para a pergunta: {question}")

#     results = client.search(
#         collection_name=collection,
#         query_vector=question_embedding,
#         limit=5
#     )

#     logging.info(f"\n🔹 Resultados brutos do Qdrant: {results}")
#     score_threshold = 0.7 if total_docs > 10 else 0.3

#     high_score = [hit for hit in results if hit.score and hit.score >= 0.7]

#     if high_score:
#         context = " ".join([hit.payload["text"] for hit in high_score])
#     else:
#         context = "Não há informações suficientes no contexto para responder à pergunta."

#     logging.info(f"\n✅ Contexto recuperado: {context}")
    return context

import re

def clean_response(response):
    """Limpa a resposta gerada para evitar palavras incompletas, repetições e truncamentos feios"""

    # Remove repetições tipo: "Hotmart, Hotmart, Hotmart"
    response = re.sub(r"\b(\w+)(, \1)+\b", r"\1", response)

    # Corta se a resposta terminar no meio de uma palavra ou símbolo estranho
    response = re.split(r"[.!?]", response)[0].strip() + "."

    # Remove quebras de linha e espaços duplicados
    response = re.sub(r"\s+", " ", response)

    return response.strip()


# def generate_answer(question, context):
#     if "Não há informações disponíveis" in context or "Não há informações suficientes" in context:
#         return "Não sei a resposta."

#     prompt = f"""
#     Baseando-se apenas no contexto abaixo, responda em portugues.

#     🔹 Pergunta: {question}

#     🔹 Contexto: {context}

#     🔹 Resposta:
#     """

#     response = generator(
#         prompt,
#         max_length=193,
#         min_length=30,
#         truncation=True,
#         do_sample=True,
#         temperature=0.7,
#         top_k=40,
#         top_p=0.8,
#         repetition_penalty=1.3
#     )[0]["generated_text"]

#     logging.info(f"\n🤖 Resposta gerada: {response}")
#     return response.strip()
def generate_answer(question, context):
    if "Não há informações disponíveis" in context or "Não há informações suficientes" in context:
        return "Não sei a resposta."

    prompt = f"""
        Responda à pergunta abaixo de forma clara, objetiva e apenas com base no contexto fornecido.

        Pergunta: {question}
        Contexto: {context}
    """

    response = generator(
        prompt,
        max_length=120,   # 🔹 Evita cortes
        min_length=40,    # 🔹 Garante uma resposta completa
        truncation=True,
        do_sample=True,
        temperature=0.3,
        top_k=40,
        top_p=0.8,
        repetition_penalty=1.2
    )[0]["generated_text"]

    return clean_response(response)



@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get("question", "")
    question = unidecode(question)

    context = retrieve_context(question)
    response = generate_answer(question, context)
    # return jsonify({"response": response}), 200
     # 📝 Salvar resposta em um arquivo TXT
    try:
        with open("ultima_resposta.txt", "w", encoding="utf-8") as f:
            f.write(f"Pergunta: {question}\n\n")
            f.write(f"Contexto utilizado:\n{context}\n\n")
            f.write(f"Resposta gerada:\n{response}\n")
        logging.info("📝 Resposta salva em 'ultima_resposta.txt'")
    except Exception as e:
        logging.warning(f"Erro ao salvar resposta: {e}")
    return app.response_class(
        response=json.dumps({"response": response}, ensure_ascii=False),
        status=200,
        mimetype="application/json"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=DEBUG_MODE)

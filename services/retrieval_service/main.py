import qdrant_client
from flask import Flask, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import re

# Inicializando Flask
app = Flask(__name__)

# Conectando ao Qdrant
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

# Nome da coleção no Qdrant
COLLECTION_NAME = "hotmart_knowledge"

# 🔹 Carregar modelo de embeddings para busca no banco vetorial
embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda" if torch.cuda.is_available() else "cpu")

# 🔥 Configurar a GPU se disponível
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🚀 Usando dispositivo: {device}")

# 🔥 Usando pipeline do Hugging Face com GPU ativada
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    device=0 if torch.cuda.is_available() else -1  # `0` usa GPU, `-1` força uso de CPU
)

print("\n✅ Pipeline de geração de texto carregado com FLAN-T5-SMALL!")

def retrieve_context(question):
    """Busca os trechos mais relevantes no banco vetorial"""
    question_embedding = embedding_model.encode(question).tolist()

    print("\n🔍 Consulta ao Qdrant para a pergunta:", question)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=question_embedding,
        limit=3
    )

    if results:
        context = " ".join([hit.payload["text"] for hit in results])
    else:
        context = "Não há informações disponíveis sobre esse assunto."

    print("\n✅ Contexto recuperado:", context)
    return context

def clean_response(response):
    """Remove conteúdos extras indesejados na resposta"""
    # 🔹 Remover textos que começam com palavras irrelevantes
    unwanted_phrases = ["VÍDEO:", "VIDEO:", "Saiba mais", "Leia mais", "Para saber mais"]
    for phrase in unwanted_phrases:
        response = re.split(phrase, response, flags=re.IGNORECASE)[0].strip()

    # 🔹 Remover pontuações e espaços extras no final
    response = re.sub(r"\s+[,.!?]$", "", response)
    
    return response

def generate_answer(question, context):
    """Gera uma resposta garantindo que seja em português"""

    prompt = f"""Responda a ### **Pergunta**:
    {question} estritamente em **português do Brasil (PT-BR)** com base no seguinte contexto:

    ### **Contexto**:
    {context}"""

    response = generator(
        prompt,
        max_length=194,  # 🔹 Reduzi um pouco para evitar cortes no meio da resposta
        min_length=50,  # 🔹 Mantém respostas bem estruturadas
        truncation=True,
        temperature=0.5,  # 🔹 Mantém equilíbrio entre precisão e criatividade
        top_k=50,  # 🔹 Evita palavras irrelevantes
        top_p=0.85,  # 🔹 Mantém coerência na geração
        repetition_penalty=1.2,  # 🔹 Evita repetições excessivas
    )[0]["generated_text"]

    response = clean_response(response)  # 🔹 Aplica limpeza pós-processamento

    print("\n🤖 Resposta gerada:", response)
    return response

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get("question", "")

    # Busca os trechos mais relevantes no Qdrant
    context = retrieve_context(question)

    # Gera resposta usando FLAN-T5-SMALL
    response = generate_answer(question, context)

    return jsonify({"response": response}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
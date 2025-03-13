import qdrant_client
from flask import Flask, request, jsonify
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# Inicializando Flask
app = Flask(__name__)

# Conectando ao Qdrant
client = qdrant_client.QdrantClient(host="vector_db", port=6333)

# Nome da coleção no Qdrant
COLLECTION_NAME = "hotmart_knowledge"

# 🔹 Carregar modelo de embeddings para busca no banco vetorial
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔥 Usando pipeline do Hugging Face com o modelo MAIS LEVE (`flan-t5-small`)
generator = pipeline("text2text-generation", model="google/flan-t5-small", device=-1)  # `device=-1` força o uso da CPU

print("\n✅ Pipeline de geração de texto carregado com FLAN-T5-SMALL!")

def retrieve_context(question):
    """Busca os trechos mais relevantes no banco vetorial"""
    question_embedding = embedding_model.encode(question).tolist()

    print("\n🔍 Consulta ao Qdrant para a pergunta:", question)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=question_embedding,
        limit=3  # Retorna os 3 trechos mais relevantes
    )

    if results:
        context = " ".join([hit.payload["text"] for hit in results])
    else:
        context = "Não há informações disponíveis sobre esse assunto."

    print("\n✅ Contexto recuperado:", context)
    return context

def generate_answer(question, context):
    """Gera uma resposta usando FLAN-T5-SMALL"""

    prompt = f"Baseado no seguinte contexto, responda de forma clara e objetiva:\n\nContexto:\n{context}\n\nPergunta: {question}\nResposta:"

    response = generator(prompt, max_length=100, truncation=True)[0]["generated_text"]
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

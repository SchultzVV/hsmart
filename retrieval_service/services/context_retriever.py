import logging
# from qdrant_client import QdrantClient
from models.client_loader import get_qdrant_client
client = get_qdrant_client()

logger = logging.getLogger(__name__)
# client = QdrantClient(host="vector_db", port=6333)

def decide_collection(question, embedding_model, max_results_per_collection=3):
    question_embedding = embedding_model.encode(question).tolist()

    try:
        collections = client.get_collections()
        available = [col.name for col in collections.collections]

        if not available:
            logger.warning("❌ Nenhuma coleção disponível no Qdrant.")
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
                    avg_score = sum([r.score for r in results if r.score]) / len(results)
                    scores[col] = avg_score
                    logger.info(f"📊 Score médio da coleção `{col}`: {avg_score:.4f}")
            except Exception as e:
                logger.warning(f"Erro ao buscar na coleção `{col}`: {e}")

        if scores:
            best_collection = max(scores, key=scores.get)
            logger.info(f"✅ Coleção mais relevante: `{best_collection}`")
            return best_collection
        else:
            logger.warning("⚠️ Nenhuma coleção retornou resultados relevantes.")
            return None

    except Exception as e:
        logger.error(f"Erro ao decidir melhor coleção: {e}")
        return None


# def retrieve_context(question, embedding_model):
def retrieve_context(question, client, embedding_model):
    collection_name = decide_collection(question, embedding_model)
    question_embedding = embedding_model.encode(question).tolist()

    try:
        collections = client.get_collections()
        available = [col.name for col in collections.collections]

        if collection_name and collection_name in available:
            logger.info(f"🔍 Usando coleção detectada: `{collection_name}`")
            results = client.search(
                collection_name=collection_name,
                query_vector=question_embedding,
                limit=5
            )
            high_score = [hit for hit in results if hit.score and hit.score >= 0.6]
            if high_score:
                return " ".join([hit.payload["text"] for hit in high_score])
            return "Não há informações suficientes no contexto para responder à pergunta."

        logger.warning(f"⚠️ Coleção `{collection_name}` não encontrada. Buscando em todas.")
        combined_context = []

        for col in available:
            try:
                results = client.search(
                    collection_name=col,
                    query_vector=question_embedding,
                    limit=3
                )
                high_score = [hit for hit in results if hit.score and hit.score >= 0.6]
                combined_context.extend([hit.payload["text"] for hit in high_score])
                logger.info(f"🔹 Resultados da coleção `{col}`: {len(high_score)} trechos")
            except Exception as e:
                logger.warning(f"Erro ao buscar na coleção `{col}`: {e}")

        if combined_context:
            return " ".join(combined_context)
        return "Não há informações suficientes em nenhuma coleção para responder à pergunta."

    except Exception as e:
        return f"Erro ao verificar coleções disponíveis: {e}"

import logging
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


def decide_collection(question: str, client: QdrantClient, embedding_model: SentenceTransformer, max_results_per_collection=3) -> str:
    """
    Decide qual coleção do Qdrant é mais relevante com base na pergunta usando similaridade de embeddings.

    Parameters:
        question (str): A pergunta do usuário.
        client (QdrantClient): Cliente conectado ao Qdrant.
        embedding_model (SentenceTransformer): Modelo de embeddings.
        max_results_per_collection (int): Número de documentos para avaliar por coleção.

    Returns:
        str: Nome da coleção mais relevante, ou None se não encontrado.
    """
    try:
        question_embedding = embedding_model.encode(question).tolist()

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

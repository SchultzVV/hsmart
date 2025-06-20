import logging
from typing import Optional
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class CollectionRouter:
    def __init__(self, client: QdrantClient, embedding_model):
        self.client = client
        self.embedding_model = embedding_model

    def heuristic(self, question: str) -> Optional[str]:
        q = question.lower()

        # 🎯 Regras simples (expanda conforme necessário)
        if "curso" in q or "oferece" in q or "tem curso de" in q or "existe" in q:
            return "ufsm_faqs"
        if "matrícula" in q or "campus" in q or "colegiado" in q:
            return "ufsm_knowledge"
        return None

    def decide(self, question: str, max_results_per_collection: int = 3) -> Optional[str]:
        # 1. Heurística simples
        heuristica = self.heuristic(question)
        if heuristica:
            logger.info(f"🔀 Heurística aplicável → usando coleção `{heuristica}`")
            return heuristica

        # 2. Busca vetorial (fallback)
        # question_embedding = self.embedding_model.encode(question).tolist()
        question_embedding = self.embedding_model.embed_query(question)
        try:
            collections = self.client.get_collections()
            available = [col.name for col in collections.collections]
            if not available:
                logger.warning("❌ Nenhuma coleção disponível.")
                return None

            scores = {}
            for col in available:
                try:
                    results = self.client.search(
                        collection_name=col,
                        query_vector=question_embedding,
                        limit=max_results_per_collection
                    )
                    if results:
                        avg_score = sum([r.score for r in results if r.score]) / len(results)
                        scores[col] = avg_score
                        logger.debug(f"📊 Média de score na `{col}`: {avg_score:.3f}")
                except Exception as e:
                    logger.warning(f"Erro ao buscar na `{col}`: {e}")

            if scores:
                best = max(scores, key=scores.get)
                logger.info(f"✅ Vetorial escolheu coleção `{best}`")
                return best

            logger.warning("⚠️ Nenhuma coleção retornou resultado relevante.")
            return None

        except Exception as e:
            logger.error(f"❌ Erro ao decidir coleção: {e}")
            return None

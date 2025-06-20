from shared.langchain_container import LangChainContainer
from shared.collection_router import CollectionRouter
from models.client_loader import get_qdrant_client

# Instâncias únicas
container = LangChainContainer()
client = get_qdrant_client()
embedding_model = container.embedding_model  # já vem do container
router = CollectionRouter(client=client, embedding_model=embedding_model)


def qa_chain(question: str):
    """
    Executa a cadeia de Pergunta e Resposta com seleção dinâmica de coleção.

    Retorna:
    - dict com 'result' (resposta) e 'sources' (metadados dos documentos).
    """
    collection_name = router.decide(question)
    if not collection_name:
        return {"result": "Não encontrei nenhuma base relevante para essa pergunta.", "sources": []}

    container.set_collection(collection_name)
    result = container.qa_chain(question)

    return {
        "result": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }

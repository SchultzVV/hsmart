from shared.langchain_container import LangChainContainer
from shared.collection_router import CollectionRouter
from models.client_loader import get_qdrant_client
from memory.redis_memory import get_conversation_memory  # vamos criar esse arquivo abaixo

# Instâncias
container = LangChainContainer()
client = get_qdrant_client()
embedding_model = container.embedding_model
router = CollectionRouter(client=client, embedding_model=embedding_model)


def qa_chain(query: str, session_id: str):
    print(f"📥 Pergunta recebida: {query}")
    collection_name = router.decide(query)

    if not collection_name:
        print("⚠️ Nenhuma coleção relevante encontrada.")
        return {
            "result": "Não encontrei nenhuma base relevante para essa pergunta.",
            "sources": []
        }

    print(f"📚 Coleção selecionada: {collection_name}")
    container.set_collection(collection_name)

    # Vincula a memória ao chain
    memory = get_conversation_memory(session_id)
    memory.output_key = "result"  # 👈 ESSENCIAL
    container.qa_chain.memory = memory
    print(f"🔗 Output key da memória: {memory.output_key}")

    result = container.qa_chain.invoke({
            "query": query,
            "chat_history": memory.chat_memory.messages
        })
    try:
        # result = container.qa_chain.invoke({"query": query})
        result = container.qa_chain.invoke({
            "query": query,
            "chat_history": memory.chat_memory.messages
        })
    except Exception as e:
        print(f"❌ Erro durante execução do QA Chain: {e}")
        return {
            "result": "Erro interno ao processar a pergunta.",
            "sources": []
        }

    print("✅ Resposta gerada com sucesso!")
    print(f"🧠 Resposta:\n{result['result']}\n")

    print("🔎 Documentos usados como contexto:")
    for idx, doc in enumerate(result.get("source_documents", []), 1):
        content_preview = doc.page_content[:300].strip().replace("\n", " ")
        print(f"  {idx}. 📄 {content_preview}...")
        print(f"     🔖 Metadados: {doc.metadata}\n")

    return {
        "result": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }


# from shared.langchain_container import LangChainContainer
# from shared.collection_router import CollectionRouter
# from models.client_loader import get_qdrant_client

# # Instâncias únicas
# container = LangChainContainer()
# client = get_qdrant_client()
# embedding_model = container.embedding_model  # já vem do container
# router = CollectionRouter(client=client, embedding_model=embedding_model)


# def qa_chain(query: str, session_id):
#     """
#     Executa a cadeia de Pergunta e Resposta com seleção dinâmica de coleção.

#     Retorna:
#     - dict com 'result' (resposta) e 'sources' (metadados dos documentos).
#     """
#     print(f"📥 Pergunta recebida: {query}")

#     collection_name = router.decide(query)
#     if not collection_name:
#         print("⚠️ Nenhuma coleção relevante encontrada.")
#         return {
#             "result": "Não encontrei nenhuma base relevante para essa pergunta.",
#             "sources": []
#         }

#     print(f"📚 Coleção selecionada: {collection_name}")
#     container.set_collection(collection_name)

#     try:
#         result = container.qa_chain.invoke({"query": query})
#     except Exception as e:
#         print(f"❌ Erro durante execução do QA Chain: {e}")
#         return {
#             "result": "Erro interno ao processar a pergunta.",
#             "sources": []
#         }

#     print("✅ Resposta gerada com sucesso!")
#     print(f"🧠 Resposta:\n{result['result']}\n")

#     print("🔎 Documentos usados como contexto:")
#     for idx, doc in enumerate(result.get("source_documents", []), 1):
#         content_preview = doc.page_content[:300].strip().replace("\n", " ")
#         print(f"  {idx}. 📄 {content_preview}...")
#         print(f"     🔖 Metadados: {doc.metadata}\n")

#     return {
#         "result": result["result"],
#         "sources": [doc.metadata for doc in result["source_documents"]]
#     }

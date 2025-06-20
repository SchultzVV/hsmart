from shared.langchain_container import LangChainContainer

# Instancia o container e configura a collection
container = LangChainContainer()
container.set_collection("ufsm_knowledge")


def qa_chain(question: str):
    """
    Executa a cadeia de Pergunta e Resposta para a collection configurada.
    
    Retorna:
    - dict com 'result' (resposta) e 'source_documents' (documentos usados).
    """
    result = container.qa_chain(question)
    return {
        "result": result['result'],
        "sources": [doc.metadata for doc in result['source_documents']]
    }

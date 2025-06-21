# 🧠 Retrieval Service — UFSM RAG com LangChain

Serviço responsável por responder perguntas com base em documentos previamente ingeridos, utilizando uma arquitetura de Recuperação com Geração (RAG) via LangChain, OpenAI e Qdrant.

---

## 📑 Índice

- [📌 Visão Geral](#-visão-geral)
- [🧠 Arquitetura LangChain](#-arquitetura-langchain)
- [📂 Arquivos Relevantes](#-arquivos-relevantes)
- [⚙️ Como Funciona o Ciclo RAG](#️-como-funciona-o-ciclo-rag)
- [📥 Ingestão de Conteúdo](#-ingestão-de-conteúdo)
- [🧪 Como Testar](#-como-testar)
- [🔍 Debug do Processo](#-debug-do-processo)
- [📎 Links Úteis](#-links-úteis)

---

## 📌 Visão Geral

Este serviço implementa um sistema RAG (Retrieval-Augmented Generation), capaz de:

- Identificar a melhor coleção vetorial para a pergunta.
- Recuperar documentos similares via Qdrant.
- Utilizar `ChatOpenAI` para responder com base nesses contextos.

---

## 🧠 Arquitetura LangChain

| Componente        | Classe                                   | Descrição                                                         |
|------------------|------------------------------------------|-------------------------------------------------------------------|
| Embeddings        | `OpenAIEmbeddings`                       | Gera vetores numéricos para textos                                |
| LLM               | `ChatOpenAI`                             | Modelo de linguagem usado para resposta contextual                |
| Vetor Store       | `Qdrant`                                 | Banco vetorial onde os documentos são armazenados                 |
| Retriever         | `vectorstore.as_retriever()`             | Busca os documentos mais relevantes                               |
| Cadeia QA         | `RetrievalQA.from_chain_type(...)`       | Executa o fluxo de recuperação + geração                          |
| Splitter          | `RecursiveCharacterTextSplitter`         | Divide o texto em chunks para vetorização                         |

📚 Documentação:
- [OpenAIEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/openai)
- [ChatOpenAI](https://python.langchain.com/docs/integrations/llms/openai)
- [Qdrant VectorStore](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
- [RetrievalQA](https://python.langchain.com/docs/modules/chains/popular/retrieval_qa)
- [Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/)

---

## 📂 Arquivos Relevantes

| Arquivo                         | Função                                                            |
|----------------------------------|-------------------------------------------------------------------|
| `langchain_container.py`         | Inicializa embeddings, LLM, vectorstore, retriever, QAChain      |
| `collection_router.py`           | Decide qual coleção usar com heurística + vetorial               |
| `qa_service.py`                  | Executa a cadeia RAG e loga as fontes usadas                      |
| `query_routes.py`                | Expõe o endpoint `/query`                                        |

---

## ⚙️ Como Funciona o Ciclo RAG

```mermaid
graph TD
    A[Usuário envia pergunta] --> B[qa_service.py]
    B --> C[CollectionRouter decide coleção]
    C --> D[set_collection()]
    D --> E[Retriever busca chunks no Qdrant]
    E --> F[ChatOpenAI responde com contexto]
    F --> G[Retorna resposta + fontes]
```

---

## 📥 Ingestão de Conteúdo

- Split por `RecursiveCharacterTextSplitter` com `chunk_size=512`, `overlap=64`.
- Armazena no Qdrant via `vectorstore.add_documents()`.
- Cada chunk contém metadados úteis:
  - `curso`, `campus`, `document_title`, `source`, `timestamp`.

---

## 🧪 Como Testar

### Fazer uma pergunta

```bash
curl -X POST http://localhost:5004/query \
  -H "Content-Type: application/json" \
  -d '{"question": "qual é o roteiro para elaboracao de projeto de ensino de arquitetura ?"}'
```

---

## 🔍 Debug do Processo

- `qa_service.py` faz `print()` dos documentos fontes:
  ```python
  for doc in result["source_documents"]:
      print(doc.page_content[:300])
      print(doc.metadata)
  ```
- Você pode inspecionar coleções com:
  ```python
  container.qdrant_client.scroll(collection_name="ufsm_knowledge", limit=5)
  ```

---

## 📎 Links Úteis

- LangChain docs: https://docs.langchain.com
- LangChain GitHub: https://github.com/langchain-ai/langchain
- Qdrant docs: https://qdrant.tech/documentation
- OpenAI API: https://platform.openai.com/docs

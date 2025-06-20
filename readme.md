# 🧠 UFSM LLM Ingestion & Retrieval API

Sistema modular para ingestão de dados acadêmicos (como cursos da UFSM e conteúdos da Hotmart) e recuperação de conhecimento utilizando LLMs com embeddings e banco vetorial Qdrant. A arquitetura é orientada a serviços com Flask + LangChain + OpenAI.

  ---

## 📑 Índice

- [📦 Estrutura de Serviços](#-estrutura-de-serviços)
- [🚀 Como Rodar (Modo Dev)](#-como-rodar-modo-dev)
- [📚 Requisitos Principais](#-requisitos-principais)
- [🧪 Exemplos de Uso via `curl`](#-exemplos-de-uso-via-curl)
  - [🔍 Perguntar ao sistema](#-1-perguntar-ao-sistema-retrieval_service-porta-5004)
  - [📥 Ingestão RAG da UFSM](#-2-ingestão-rag-automatizada-via-sitemap-da-ufsm)
  - [🔗 Ingestão com filtro de curso](#-3-ingestão-direta-de-páginas-via-sitemap-completo-da-ufsm-com-ou-sem-filtro)
  - [🌐 Crawling manual](#-4-ingestão-via-crawling-manual-da-ufsm-limitado-a-50-páginas)
  - [🌍 URL arbitrária](#-5-ingestão-a-partir-de-uma-url-web-arbitrária)
  - [🧾 Texto manual](#-6-ingestão-manual-de-texto-bruto)
  - [🔥 Hotmart](#-7-ingestão-de-conteúdos-da-hotmart)
  - [📄 Listar cursos](#-8-obter-lista-de-cursos-encontrados-via-sitemap)
  - [📂 Listar coleções](#-9-listar-todas-as-coleções-existentes)
  - [📜 Listar documentos](#-10-listar-todos-os-documentos-por-coleção)
  - [❌ Deletar coleção](#-11-deletar-uma-coleção-específica)
- [🧠 Arquitetura Interna](#-arquitetura-interna)
- [🛠️ Dev/Prod com Docker](#️-devprod-com-docker)
- [✨ Contribuições Futuras](#-contribuições-futuras)
- [📄 Licença](#-licença)

---

## 📦 Estrutura de Serviços

- `ingestion_service` - Responsável por coletar, processar e armazenar documentos vetorizados em coleções Qdrant.
- `retrieval_service` - Fornece respostas a perguntas usando LLM + embeddings de acordo com a coleção mais relevante.
- `vector_db` - Banco vetorial Qdrant para persistência dos embeddings e metadados.

---

## 🚀 Como Rodar (Modo Dev)

```bash
make up
```

---

## 📚 Requisitos Principais

**🚀 Framework Web**
- `Flask 3.0+` 
---
**🧠 LLM + Embeddings**
- `langchain==0.2.1`
- `langchain-community==0.2.3`
- `langchain-openai==0.1.8`
---
   **📦 Banco**
  - `Qdrant 1.8+`
  - `OpenAI API`
  - `.env` com `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, etc.

**🔍 Utilitários**
- `unidecode==1.3.8`
- `certifi==2024.6.2`
- `python-dotenv==1.0.1`

**✅ Testes**
- `pytest==8.2.1`
---

## 🧪 Exemplos de Uso via `curl`

### 🔍 1. Perguntar ao sistema (`retrieval_service`, porta 5004)

```bash
curl -X POST http://localhost:5004/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quais cursos a UFSM oferece no campus de Frederico Westphalen?"}'
```

---

### 📥 2. Ingestão RAG automatizada via sitemap da UFSM

```bash
curl -X POST http://localhost:5003/ingest_ufsm_cursos_rag
```

---

### 🔗 3. Ingestão direta de páginas via sitemap completo da UFSM (com ou sem filtro)

```bash
curl -X POST http://localhost:5003/ingest_ufsm \
  -H "Content-Type: application/json" \
  -d '{"filtro_nome": "ciencia-da-computacao"}'
```

---

### 🌐 4. Ingestão via crawling manual da UFSM (limitado a 50 páginas)

```bash
curl -X POST http://localhost:5003/ingest_ufsm2
```

---

### 🌍 5. Ingestão a partir de uma URL web arbitrária

```bash
curl -X POST http://localhost:5003/ingest_from_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ufsm.br/cursos/graduacao/santa-maria/ciencia-da-computacao/"}'
```

---

### 🧾 6. Ingestão manual de texto bruto

```bash
curl -X POST http://localhost:5003/ingest_manual \
  -H "Content-Type: application/json" \
  -d '{
        "text": "Machine Learning é o estudo de algoritmos que melhoram automaticamente com a experiência.",
        "collection": "mlops_knowledge"
      }'
```

---

### 🔥 7. Ingestão de conteúdos da Hotmart

```bash
curl -X POST http://localhost:5003/ingest_hotmart
```

---

### 📄 8. Obter lista de cursos encontrados via sitemap

```bash
curl http://localhost:5003/get_courses_list
```

---

### 📂 9. Listar todas as coleções existentes

```bash
curl http://localhost:5003/list_collections
```

---

### 📜 10. Listar todos os documentos por coleção

```bash
curl http://localhost:5003/get_all_documents
```

---

### ❌ 11. Deletar uma coleção específica

```bash
curl -X POST http://localhost:5003/delete_collection \
  -H "Content-Type: application/json" \
  -d '{"collection": "ufsm_geral_knowledge"}'
```

---

## 🧠 Arquitetura Interna

- 🔌 **LangChainContainer**: Inicializa Qdrant, embeddings (OpenAI) e LLM.
- 🧭 **CollectionRouter**: Decide dinamicamente a melhor coleção com heurística + vetorial.
- 🧾 **qa_service**: Executa cadeia RetrievalQA com recuperação de contexto e fontes.

---

## 🛠️ Dev/Prod com Docker

- Dev: `docker-compose.dev.yaml` ou `make up`
- Prod: `docker-compose.prod.yaml` com `ghcr.io` e `.env.prd`

---

## ✨ Contribuições Futuras

- [ ] Implementar histórico de interações
- [ ] Dashboard com Streamlit
- [ ] Suporte a múltiplas línguas
- [ ] Cache com Redis

---

## 📄 Licença

MIT © 2025 — UFSM AI Engineering Project

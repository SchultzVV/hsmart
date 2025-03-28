# 🔍 UFSM LLM Ingestion & Retrieval System

Sistema completo de ingestão e recuperação de conhecimento com Qdrant e LLMs.

---

## 📦 Serviços

- `ingestion_service`: Crawling, parsing e ingestão de dados estruturados
- `retrieval_service`: Respostas automáticas com contexto via LLM

---

## 🚀 Executar em modo Dev

```bash
make build
make up
```

---

## 🧪 Testes e Lint

```bash
make test
make lint
```

---

## 📌 Endpoints REST

### 🔽 Ingestion API (`:5003`)

| Rota                   | Método | Descrição                                            |
|------------------------|--------|------------------------------------------------------|
| `/ingest_ufsm`         | POST   | Ingestão de cursos de graduação da UFSM             |
| `/ingest_ufsm_geral`   | POST   | Geração automática de conhecimento geral da UFSM    |
| `/ingest_hotmart`      | POST   | Ingestão de texto da Hotmart                        |
| `/ingest_manual`       | POST   | Ingestão de texto manual em uma coleção             |
| `/get_courses_list`    | GET    | Lista os cursos da UFSM                             |
| `/get_all_collections` | GET    | Lista todas as coleções                             |
| `/get_all_documents`   | GET    | Retorna os documentos por coleção                   |

---

### 🧠 Retrieval API (`:5004`)

| Rota     | Método | Descrição                                     |
|----------|--------|-----------------------------------------------|
| `/query` | POST   | Gera resposta com base em embeddings          |

```json
POST /query
{
  "question": "A UFSM tem curso de Ciência da Computação?"
}
```

---

## 📤 Build e Deploy

Imagens são construídas e publicadas automaticamente via GitHub Actions para o GHCR.

---

## 📚 Dataset para Fine-Tuning

Ao rodar `/ingest_ufsm_geral`, um arquivo JSONL com exemplos `{"prompt": ..., "response": ...}` é salvo em:

```bash
/app/data/ufsm_geral_dataset.jsonl
```

---

## 📂 Estrutura Modular

- `routes/` → define os endpoints
- `services/` → lógica de negócio
- `utils/` → ferramentas comuns
- `data/` → arquivos persistidos

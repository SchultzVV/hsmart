# 📥 Ingestion Service — UFSM RAG com LangChain

Serviço responsável por realizar o crawling, parsing e armazenamento vetorial de conteúdos acadêmicos da UFSM, utilizando LangChain e Qdrant como base para um sistema de Recuperação com Geração (RAG).

---

## 📑 Índice

- [📌 Visão Geral](#-visão-geral)
- [🔧 Fontes e Estratégias de Ingestão](#-fontes-e-estratégias-de-ingestão)
- [🧠 Arquitetura com LangChain](#-arquitetura-com-langchain)
- [📂 Arquivos Relevantes](#-arquivos-relevantes)
- [📊 Metadados por Chunk](#-metadados-por-chunk)
- [🧪 Como Testar](#-como-testar)
- [🔍 Debug do Processo](#-debug-do-processo)
- [📎 Links Úteis](#-links-úteis)

---

## 📌 Visão Geral

Este serviço realiza a ingestão automatizada de conteúdo textual estruturado e semiestruturado de:

- Cursos de graduação e pós da UFSM
- Hotmart (materiais externos)
- URLs arbitrárias

O conteúdo é segmentado em chunks e armazenado com metadados no banco vetorial Qdrant.

---

## 🔧 Fontes e Estratégias de Ingestão

| Endpoint                      | Estratégia                                                                 |
|------------------------------|----------------------------------------------------------------------------|
| `/ingest_ufsm_cursos_rag`    | Sitemap dos cursos via `robots.txt` + sub-subpages com datas recentes     |
| `/ingest_ufsm`               | Sitemap geral com filtro opcional por nome do curso                       |
| `/ingest_ufsm2`              | Crawling em largura limitado a 50 páginas                                 |
| `/ingest_from_url`           | Ingestão de uma URL única com split automático                            |
| `/ingest_hotmart`            | Ingestão de materiais externos da Hotmart                                 |
| `/ingest_manual`             | Texto manual inserido via JSON                                            |

---

## 🧠 Arquitetura com LangChain

| Componente        | Classe                             | Descrição                                                           |
|------------------|------------------------------------|---------------------------------------------------------------------|
| Embeddings        | `OpenAIEmbeddings`                 | Vetorização dos chunks com modelo da OpenAI                        |
| Vector Store      | `Qdrant`                           | Armazenamento vetorial e recuperação posterior                      |
| Splitter          | `RecursiveCharacterTextSplitter`   | Fragmentação inteligente com sobreposição                           |

📚 Documentação:
- [LangChain - Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/)
- [LangChain - Qdrant](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
- [LangChain - Embeddings](https://python.langchain.com/docs/integrations/text_embedding/openai)

---

## 📂 Arquivos Relevantes

| Arquivo                         | Função                                                               |
|----------------------------------|----------------------------------------------------------------------|
| `ufsm_ingestor.py`               | Parsing de sitemaps, crawling, extração de texto e ingestão         |
| `vector_ops.py`                  | Listar coleções, documentos e deletar via Qdrant                    |
| `hotmart_ingestor.py`           | Ingestão de materiais Hotmart com estrutura própria                 |
| `ingest_routes.py`              | Exposição dos endpoints Flask de ingestão                           |
| `reprocess_log.py`              | Reprocessamento paralelo de links já logados                        |

---

## 📊 Metadados por Chunk

Cada documento vetorizado carrega os seguintes metadados:

```json
{
  "curso": "Arquitetura e Urbanismo",
  "campus": "Santa Maria",
  "nivel": "graduacao",
  "document_title": "Roteiro para Elaboração de Projeto de Ensino",
  "source": "https://www.ufsm.br/cursos/.../",
  "timestamp": "2025-06-20T14:30:00"
}
```

Esses metadados são usados para:
- Navegação e filtro posterior
- Transparência da origem
- Auditabilidade de contexto usado em resposta

---

## 🧪 Como Testar

### Enviar URL arbitrária:
```bash
curl -X POST http://localhost:5003/ingest_from_url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ufsm.br/cursos/graduacao/santa-maria/arquitetura-e-urbanismo/roteiro-para-elaboracao-de-projeto-de-ensino"}'
```

### Ingestão completa via sitemap RAG:
```bash
curl -X POST http://localhost:5003/ingest_ufsm_cursos_rag
```

---

## 🔍 Debug do Processo

- Os documentos são divididos com `RecursiveCharacterTextSplitter(chunk_size=512, overlap=64)`
- Você pode inspecionar o conteúdo:

```python
for chunk in splitter.create_documents([texto], metadatas=[metadados]):
    print(chunk.page_content[:300])
```

- Para verificar o conteúdo no Qdrant:

```python
from shared.langchain_container import LangChainContainer

# 🔌 Inicializa o container (com cliente e modelo embutido)
container = LangChainContainer()

# 🧠 Inspeciona 3 documentos da coleção 'ufsm_knowledge'
response = container.qdrant_client.scroll(
    collection_name="ufsm_knowledge",
    limit=3
)

# 📄 Exibe os documentos recuperados
for i, point in enumerate(response[0], 1):
    print(f"--- Documento {i} ---")
    print("ID:", point.id)
    print("Payload:", point.payload)
    print()
```

---

## 📎 Links Úteis

- LangChain docs: https://docs.langchain.com
- Qdrant docs: https://qdrant.tech/documentation
- OpenAI API: https://platform.openai.com/docs

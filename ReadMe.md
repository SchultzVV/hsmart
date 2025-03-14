# 🚀 Projeto de Protótipo de LLM com Base de Conhecimento (Qdrant + FLAN-T5)

Este projeto implementa um **protótipo de microsserviços** que utiliza um **banco vetorial (Qdrant)** e um **modelo de LLM (`FLAN-T5`)** para responder perguntas com base em um conhecimento previamente armazenado.

---

## 📌 **Arquitetura**
O projeto é composto por três serviços principais:
1. **Vector Database (Qdrant)**: Armazena os embeddings dos textos processados.
2. **Ingestion Service** (`ingestion_service`): Extrai texto de uma página, gera embeddings e armazena no Qdrant.
3. **Retrieval Service** (`retrieval_service`): Busca informações relevantes no banco vetorial e usa um modelo de LLM (`FLAN-T5`) para gerar respostas.

---

## 📂 **Estrutura de Diretórios**

```bash
/llm-projeto
│── docker-compose.yaml
│── .env
│── README.md
│── services/
│   ├── ingestion_service/
│   │   ├── main.py  # API: ingestão de documentos
│   │   ├── requirements.txt  
│   │   ├── Dockerfile  
│   ├── retrieval_service/
│   │   ├── main.py  # API: consulta e respostas
│   │   ├── requirements.txt  
│   │   ├── Dockerfile  
│   │   ├── .env  
│── vector_db/
│   ├── aliases/
│   ├── collections/
│   ├── docker-compose.yaml
│   ├── config.py
│── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
```


---

## 🚀 **Como Rodar o Projeto**

### **1️⃣ Instale o Docker e Docker Compose**
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)


### **2️⃣ Configure as Variáveis de Ambiente**
Para rodar o projeto, você precisará de um **Hugging Face Token**.  
Se ainda não tem um, **crie um novo token de acesso aqui**:  
🔗 [Criar Token no Hugging Face](https://huggingface.co/settings/tokens)

Após gerar o token, crie o arquivo `.env` com o seguinte comando:
```bash
echo "HUGGINGFACE_TOKEN=seu_token_aqui" > .env
```
O arquivo `.env` deve estar na pasta raiz do projeto com o seguinte conteúdo:
> 🔹 **Substitua `seu_token_aqui` pelo token da Hugging Face** (necessário para baixar o modelo `FLAN-T5`).

### **3️⃣ Suba os Contêineres**
```bash
docker-compose up --build
```
Após concluir o passo 3 está pronto apra uso. A resposta para a pergunta do PDF foi gerada pelo endpoint e encontra-se no [`ultima_resposta.txt`](services/retrieval_service/ultima_resposta.txt). Para mais detalhes veja o [`README_de_resposta.md`](README_de_resposta.md)
## 🧪 Como Rodar os Testes
Para garantir que os serviços estão funcionando corretamente, você pode rodar os testes automatizados.

#### Instale o `pytest` (se ainda não estiver instalado)
```bash
pip install pytest
```
#### Realize os testes automáticos
Rode o comando abaixo na pasta raiz do projeto
```bash
pytest tests/
```

O retorno esperado é 
```bash
================= test session starts ================
collected 2 items

tests/test_ingestion.py ✅ PASSED
tests/test_retrieval.py ✅ PASSED
```

###### ** OBS: Se quiser ver os logs das imagens use os comandos**
```bash
docker logs ingestion_service --follow
```
ou
```bash
docker logs retrieval_service --follow
```

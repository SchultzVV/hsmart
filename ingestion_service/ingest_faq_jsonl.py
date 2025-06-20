import json
from collections import defaultdict
from pathlib import Path
from langchain_core.documents import Document
from shared.langchain_container import LangChainContainer

# Caminho do arquivo com os pares prompt-response
file_path = Path("faqs_ufsm.jsonl")

# Agrupa os prompts pela mesma resposta
response_map = defaultdict(list)

with file_path.open("r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line.strip())
        response = data["response"]
        prompt = data["prompt"]
        response_map[response].append(prompt)

# Cria documentos com metadados
docs = []
for response, prompts in response_map.items():
    docs.append(Document(
        page_content=response,
        metadata={
            "prompt_examples": prompts,
            "type": "faq"
        }
    ))

# Ingestão no Qdrant com LangChainContainer
container = LangChainContainer()
container.set_collection("ufsm_faqs")
container.vectorstore.add_documents(docs)

print(f"✅ {len(docs)} documentos FAQ ingeridos na coleção 'ufsm_faqs'")

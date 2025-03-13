import os

# Estrutura de diretórios e arquivos
project_structure = {
    "llm-projeto": [
        "docker-compose.yaml",
        "README.md"
    ],
    "llm-projeto/services/ingestion_service": [
        "main.py",
        "requirements.txt",
        "Dockerfile"
    ],
    "llm-projeto/services/retrieval_service": [
        "main.py",
        "requirements.txt",
        "Dockerfile"
    ],
    "llm-projeto/vector_db": [
        "docker-compose.yaml",
        "config.py"
    ],
    "llm-projeto/tests": [
        "test_ingestion.py",
        "test_retrieval.py"
    ]
}

# Criar diretórios e arquivos
for directory, files in project_structure.items():
    os.makedirs(directory, exist_ok=True)
    for file in files:
        file_path = os.path.join(directory, file)
        with open(file_path, "w") as f:
            if file.endswith(".py"):
                f.write("# just to create\n")

print("Projeto configurado com sucesso! 🚀")

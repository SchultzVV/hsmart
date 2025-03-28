# Nome do serviço
SERVICE=retrieval_service
PY_IMAGE=python:3.9-slim
CODE_DIR=/app
GITHUB_USERNAME=schultzvv
IMAGE_INGESTION=ghcr.io/$(GITHUB_USERNAME)/ingestion_service:latest
IMAGE_RETRIEVAL=ghcr.io/$(GITHUB_USERNAME)/retrieval_service:latest

# Utilitário interno
define run_py_container
	docker run --rm -v $$PWD:$(CODE_DIR) -w $(CODE_DIR)/services/$(SERVICE) $(PY_IMAGE) sh -c "$(1)"
endef

# 🧪 Testes com pytest via Docker
test:
	$(call run_py_container, pip install -r requirements.txt && pip install pytest && pytest tests/ --disable-warnings)

# 🧽 Lint com flake8 via Docker
lint:
	$(call run_py_container, pip install flake8 && flake8)

# 🎨 Formatador Black via Docker (modo dry-run)
format-check:
	$(call run_py_container, pip install black && black --check .)

# 🎨 Aplicar Black para formatar tudo
format:
	$(call run_py_container, pip install black && black .)

# 🔨 Build local (com cache limpo)
build:
	docker-compose build --no-cache

# 🐳 Sobe serviços padrão
up:
	docker-compose up -d

# 🐳 Encerra todos
down:
	docker-compose down -v

# ♻️ Reinicia o serviço de retrieval
retrieval-restart:
	docker-compose stop retrieval_service
	docker-compose rm -f retrieval_service
	docker-compose build retrieval_service
	docker-compose up -d retrieval_service

# ♻️ Reinicia o serviço de ingestion
ingestion-restart:
	docker-compose stop ingestion_service
	docker-compose rm -f ingestion_service
	docker-compose build ingestion_service
	docker-compose up -d ingestion_service


# 🧪 Sobe em modo dev
devup:
	docker-compose -f docker-compose.dev.yaml up -d

# 🚀 Sobe em modo prod
prdup:
	docker-compose -f docker-compose.prod.yaml up -d

# 🔍 Logs individuais
logs:
	docker-compose logs -f $(SERVICE)

# 🔍 Todos logs
logs-all:
	docker-compose logs -f

# 🛠️ Build imagens prod
build-prod:
	docker build -t $(IMAGE_INGESTION) ./services/ingestion_service
	docker build -t $(IMAGE_RETRIEVAL) ./services/retrieval_service

# 🚀 Push imagens
push:
	docker push $(IMAGE_INGESTION)
	docker push $(IMAGE_RETRIEVAL)

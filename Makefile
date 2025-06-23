# Nome do serviço
SERVICE=retrieval_service

PY_IMAGE=python:3.10-slim
CODE_DIR=/app
GITHUB_USERNAME=schultzvv
IMAGE_INGESTION=ghcr.io/$(GITHUB_USERNAME)/ingestion_service:latest
IMAGE_RETRIEVAL=ghcr.io/$(GITHUB_USERNAME)/retrieval_service:latest

# Arquivos docker-compose
COMPOSE_DEV=-f docker-compose.dev.yaml --env-file .env
COMPOSE_PRD=-f docker-compose.prd.yaml --env-file .env.prd

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

# 🔨 Build local (modo dev, com cache limpo)
build:
	docker-compose $(COMPOSE_DEV) build --no-cache

# 🐳 Sobe serviços em modo dev
up:
	docker-compose $(COMPOSE_DEV) up

# 🐳 Encerra serviços dev
down:
	docker-compose $(COMPOSE_DEV) down -v

# ♻️ Reinicia o serviço de retrieval no dev
retrieval-restart:
	docker-compose $(COMPOSE_DEV) stop retrieval_service
	docker-compose $(COMPOSE_DEV) rm -f retrieval_service
	docker-compose $(COMPOSE_DEV) build retrieval_service
	docker-compose $(COMPOSE_DEV) up -d retrieval_service

# ♻️ Reinicia o serviço de ingestion no dev
ingestion-restart:
	docker-compose $(COMPOSE_DEV) stop ingestion_service
	docker-compose $(COMPOSE_DEV) rm -f ingestion_service
	docker-compose $(COMPOSE_DEV) build ingestion_service
	docker-compose $(COMPOSE_DEV) up -d ingestion_service

# 🧪 Sobe em modo dev (alias)
devup:
	docker-compose $(COMPOSE_DEV) up -d

# 🚀 Sobe em modo prod
prdup:
	docker-compose $(COMPOSE_PRD) up -d

# 🔍 Logs individuais (dev)
logs:
	docker-compose $(COMPOSE_DEV) logs -f $(SERVICE)

# 🔍 Todos logs (dev)
logs-all:
	docker-compose $(COMPOSE_DEV) logs -f

# 🛠️ Build imagens prod
build-prod:
	docker build -t $(IMAGE_INGESTION) ./services/ingestion_service && \
	docker build -t $(IMAGE_RETRIEVAL) ./services/retrieval_service

# 🔐 Login no GitHub Container Registry
docker-login-ghcr:
	# echo "$$GITHUB_TOKEN" | docker login ghcr.io -u $$GITHUB_USERNAME --password-stdin

# 🚀 Push imagens
push: docker-login-ghcr build-prod
	docker push $(IMAGE_INGESTION)
	docker push $(IMAGE_RETRIEVAL)

prune:clean-images
	docker system prune -f --volumes

clean-images:
	@if [ -n "$$(docker images -q)" ]; then \
		echo "🔴 Removendo todas as imagens Docker..."; \
		docker rmi -f $$(docker images -q); \
	else \
		echo "✅ Nenhuma imagem para remover."; \
	fi


goingestion:
	docker exec -it ingestion_service /bin/bash

goretrieval:
	docker exec -it retrieval_service /bin/bash

query:
	curl -X POST http://localhost:5004/query \
	  -H "Content-Type: application/json" \
	  -d '{"question": "$(q)"}'

# Nome do serviço (pode ser ajustado)
SERVICE=retrieval_service

# Reconstrói somente o serviço de retrieval com cache limpo
build-retrieval:
	docker-compose build --no-cache $(SERVICE)

# Sobe todos os serviços em background
up:
	docker-compose up -d

# Encerra todos os serviços
down:
	docker-compose down

# Reinicia o serviço de retrieval
restart-retrieval:
	docker-compose stop $(SERVICE)
	docker-compose rm -f $(SERVICE)
	docker-compose build $(SERVICE)
	docker-compose up -d $(SERVICE)

# Mostra logs do serviço de retrieval
logs:
	docker-compose logs -f $(SERVICE)

# Mostra logs de todos os serviços
logs-all:
	docker-compose logs -f

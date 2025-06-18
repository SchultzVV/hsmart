# FROM python:3.9-slim
FROM python:3.10-slim


# Define diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y git
RUN rm -rf /root/.cache/pip
# Copia o código-fonte da aplicação
RUN apt-get install -y git
COPY . .

# Exponha a porta, caso esteja rodando localmente
EXPOSE 5000

# Variável de ambiente para evitar buffering de logs no Docker
ENV PYTHONUNBUFFERED=1

# Comando de inicialização (pode ser main.py ou gunicorn, veja abaixo)
CMD ["python", "main.py"]

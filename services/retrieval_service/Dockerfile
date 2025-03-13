FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cu118
RUN pip install torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir huggingface_hub

# Recebe o token como argumento da build
ARG HUGGINGFACE_TOKEN
ENV HUGGINGFACE_TOKEN=$HUGGINGFACE_TOKEN

# Debug: Exibir o token (remova depois de testar)
RUN echo "Token recebido no Dockerfile: $HUGGINGFACE_TOKEN"

# Fazer login corretamente na Hugging Face
RUN huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential

COPY . .

CMD ["python", "main.py"]

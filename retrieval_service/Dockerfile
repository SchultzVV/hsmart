# FROM python:3.9
FROM python:3.10-slim


WORKDIR /app

COPY retrieval_service .
COPY ../shared ./shared



RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y git
RUN git config --global credential.helper store

RUN pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cu118
RUN pip install torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir huggingface_hub
RUN rm -rf /root/.cache/pip

# Recebe o token como argumento da build
ARG HUGGINGFACE_TOKEN
ENV HUGGINGFACE_TOKEN=$HUGGINGFACE_TOKEN



# Fazer login na Hugging Face no runtime, não no build
CMD huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential && python main.py

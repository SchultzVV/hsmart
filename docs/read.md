Plano de Execução (3 Dias)

#### Dia 1: Configuração do Ambiente e Estruturação
*   Configurar o ambiente Docker e criar um docker-compose.yaml básico.
*   Escolher e configurar um Vector Database open-source (exemplo: FAISS, ChromaDB, Weaviate).
*   Criar a estrutura dos microsserviços:
*   Service 1: API para processar documentos e armazenar embeddings no Vector DB.
*   Service 2: API para receber perguntas, recuperar contexto e gerar respostas via LLM.
#### Dia 2: Implementação das APIs
*   Implementar a API de ingestão de documentos:
*   Extrair texto da página fornecida.
*   Gerar embeddings do texto com Sentence Transformers ou OpenAI embeddings.
*   Armazenar embeddings no Vector Database.
*   Implementar a API de consulta:
*   Receber perguntas.
*   Buscar os trechos mais relevantes no Vector DB.
*   Passar o contexto para um modelo LLM (ex: Llama, GPT, Mistral).
*   Retornar a resposta gerada.
#### Dia 3: Testes e Documentação
*   Criar scripts de teste para cURL/Postman.
*   Testar os microsserviços juntos.
*   Criar o README.md com instruções de execução.
*   Subir o código para o GitHub e validar a execução com docker-compose up.
*   Se precisar de ajuda com alguma parte específica, posso te guiar na implementação! 🚀

echo "TOKEN_GITHUB" | docker login ghcr.io -u SEU_USUARIO --password-stdin

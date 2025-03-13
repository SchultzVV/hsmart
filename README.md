#### Teste 1 
Após fazer os serviços de ingestão e resposta, testar os endpoints:

##### Ingestion    
```bash
curl -X POST "http://127.0.0.1:5003/ingest" \
     -H "Content-Type: application/json" \
     -d '{"text": "A Hotmart é uma plataforma para criadores de conteúdo venderem seus produtos digitais."}'
```
Deve receber uma resposta JSON:
```json
{"message": "Texto armazenado com sucesso"}
```

##### Retrivial
```bash
curl -X POST "http://127.0.0.1:5004/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "O que é a Hotmart?"}'
```
Deve receber uma resposta JSON:
```json
{"response": "Resposta gerada para a pergunta: O que é a Hotmart?"}
```


## RESPOSTA 
Após construir os serviços de ingestão e resposta, podemos obter o resultado pedido no PDF com o endpoint:

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

##### Ingestion    
A imagem de ingestão de informações no banco de vetores qdrant faz automaticamente a coleta, ingestão e incorporação das informações. Sendo assim não foi utilizado o endpoint de ingestão, porém pode ser 

```bash
curl -X POST "http://127.0.0.1:5003/ingest" \
     -H "Content-Type: application/json" \
     -d '{"text": "A Hotmart é uma plataforma para criadores de conteúdo venderem seus produtos digitais."}'
```
Deve receber uma resposta JSON:
```json
{"message": "Texto armazenado com sucesso"}
```

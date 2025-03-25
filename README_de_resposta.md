## Construção dos serviços

Para construir os serviços de ingestão e resposta rode na pasta raiz do projeto:
```bash
docker-compose up --build
```

## Endpoints
Teste os endpoints que são apresentados em duas etapas, a primeira (1)  é uma ingestão manual e depois uma pergunta sobre o contexto de MLOPS. Depois em (2) é apresentada a ingestão automatica do site hotmart seguida de duas perguntas sobre o contexto hotmart. Por último são mostrados endpoins para deletar coleções.

### **1 - Ingestion_service Manual**
A imagem de ingestão de informações no banco de vetores `qdrant` faz automaticamente a coleta, ingestão e incorporação das informações. O endpoint de ingestão pode ser usado assim: 

*    Endpoint para ingestão manual pode ser feito especificando uma coleção ou não, caso queira especificar a coleção use conforme abaixo
```bash
curl -X POST http://127.0.0.1:5003/ingest_manual \
     -H "Content-Type: application/json" \
     -d '{"text": "MLOps é a combinação de ML com DevOps para escalar modelos em produção.", "collection": "mlops_knowledge"}'
```
Deve receber uma resposta JSON:
```json
{"message": "Texto armazenado com sucesso"}
```
*    Endpoint para listar os documentos
     ```bash
     curl -X GET http://localhost:5003/get_all_documents
     ```
### **1 - Retrieval_service**

```bash
curl -X POST http://localhost:5004/query -H      "Content-Type:  application/json" -d '{"question": "o que é mlops?"}'  
```
A última resposta será salva num arquivo [`ultima_resposta.txt`](services/retrieval_service/ultima_resposta.txt)
 e será algo do tipo:
```text
Pergunta: o que é mlops?

Contexto utilizado:
MLOps é a combinação de ML com DevOps para escalar modelos em produção.

Resposta gerada:
MLOps é a combinaço de ML com DevOps para escalar modelos em produço.
```


### **2 - Ingestão do site hotmart**
*    Endpoint para ingerir os dados do site hotmart

```bash
curl -X POST http://localhost:5003/ingest_hotmart
```

### **2 - Retrieval_service do site hotmart**
```bash
curl -X POST "http://127.0.0.1:5004/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "O que é a Hotmart?"}'
```
```text
Pergunta: O que é a Hotmart?

Contexto utilizado:
A Hotmart é um ecossistema completo e em constante evolução para trazer ainda mais soluções para criar e escalar negócios digitais.
Dados mostram que, na Hotmart, creators faturam 35% mais, sem mexer no esforço operacional.
Isso graças ao rápido carregamento, alta taxa de aprovação, variedade de formas de pagamento, usabilidade agradável e ferramentas específicas para aumentar as vendas, como o Order Bump e Funil de Vendas, por exemplo.
VÍDEO: Como funciona a Hotmart? Tudo que você precisa saber para vender na Hotmart!

O cadastro e o uso da Hotmart são gratuitos Uma das empresas da Hotmart Company, que conta com integração com a Hotmart é a eNotas, que realiza exatamente este serviço.
Você pode contratar pela própria Hotmart e ter a garantia de que todas as Notas Fiscais estão sendo emitidas corretamente e otimizar o seu tempo, focando no crescimento do seu negócio online.
Ficamos felizes que você tenha tomado a decisão de conhecer os cursos disponíveis no universo da Hotmart ou de se tornar um Produtor ou Afiliado No ecossistema, a grande diferença é que tem mais serviços em torno de um serviço ou de um público inicial, vamos dizer assim”, revelou João Pedro Resende, CEO e co-fundador da Hotmart.
A Hotmart ainda oferece ferramentas e soluções que ajudam na hospedagem, divulgação e venda de produtos digitais E acho que todo criador de conteúdo que decidir construir disso um negócio pra vida dele, ele vai olhar pra Hotmart como um grande parceiro pra ajudar com muitas coisas

Resposta gerada:
A Hotmart é um ecossistema completo e in constante evoluciono para trazer ainda mais soluçes para criar e escalar negócios digital.
```
*    Uma outra pergunta poderia ser:
```bash
curl -X POST "http://127.0.0.1:5004/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "a hotmart foi fundada quando??"}'
```
O que tem como resposta:
```text
Pergunta: a hotmart foi fundada quando?

Contexto utilizado:
Em 2011, a Hotmart foi fudada!
A maior missão é possibilitar que todos possam viver de suas paixões, compartilhando conhecimento e ajudando no crescimento profissional e pessoal de outras pessoas

Resposta gerada:
2011.

```

### Endpoints auxiliares

#### Deletar coleções
```bash
curl -X POST http://127.0.0.1:5003/delete_collection \
     -H "Content-Type: application/json" \
     -d '{"collection": "hotmart_knowledge"}'
```

#### listar documentos
```bash
curl -X GET http://localhost:5003/get_all_documents
```

### Considerações

Durante a implementação do `retrieval_service`, optei por não utilizar a GPU e executei os modelos exclusivamente na CPU. A decisão foi baseada na configuração da máquina utilizada, que possui uma CPU com 16GB de RAM e uma GPU mais antiga, o que poderia comprometer a estabilidade e compatibilidade do processamento. Para garantir melhor desempenho na inferência do modelo, selecionei o google/flan-t5-small, uma opção otimizada para execução em CPU.

Podemos considerar o teste das melhorias futuras.
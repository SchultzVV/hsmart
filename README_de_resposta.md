## RESPOSTA 
Após construir os serviços de ingestão e resposta, podemos obter o resultado pedido no PDF com o endpoint:

##### Usando o Retrivial_service
```bash
curl -X POST "http://127.0.0.1:5004/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "O que é a Hotmart?"}'
```
Deve receber uma resposta JSON:
```json
{
  "response": ": A Hotmart \u00e9 um ecossistema completo em constante evolucion\u00e1ria para trazer ainda mais solu\u00e7es para criar e escalar neg\u00f3cios digital. Dados mostram que, na Hotmart, creators faturam 35% mais, sem mexer no esfor\u00e7o operacional. Isso gra\u00e7as ao rapid carregamento, alta taxa de aprova\u00e7o, variedade de formas de pagamento, usabilidade agrad\u00e1vel e ferramentas especficas para aumentar as vendas, como o Order Bump & Funil de Vendas, por exemplo."
}
```
A resposta ajustada é 
```text
Resposta:
A Hotmart é um ecossistema completo em constante evolucionária para trazer ainda mais soluçes para criar e escalar negócios digital. Dados mostram que, na Hotmart, creators faturam 35% mais, sem mexer no esforço operacional. Isso graças ao rapid carregamento, alta taxa de aprovaço, variedade de formas de pagamento, usabilidade agradável e ferramentas especficas para aumentar as vendas, como o Order Bump & Funil de Vendas, por exemplo.
```
A resposta também é salva num arquivo [`ultima_resposta.txt`](services/retrieval_service/ultima_resposta.txt)


##### Ingestion_service  
A imagem de ingestão de informações no banco de vetores qdrant faz automaticamente a coleta, ingestão e incorporação das informações. O endpoint de ingestão pode ser usado assim: 

```bash
curl -X POST "http://127.0.0.1:5003/ingest" \
     -H "Content-Type: application/json" \
     -d '{"text": "A Hotmart é uma plataforma para criadores de conteúdo venderem seus produtos digitais."}'
```
Deve receber uma resposta JSON:
```json
{"message": "Texto armazenado com sucesso"}
```


### Considerações

Durante a implementação do `retrieval_service`, optei por não utilizar a GPU e executei os modelos exclusivamente na CPU. A decisão foi baseada na configuração da máquina utilizada, que possui uma CPU com 16GB de RAM e uma GPU mais antiga, o que poderia comprometer a estabilidade e compatibilidade do processamento. Para garantir melhor desempenho na inferência do modelo, selecionei o google/flan-t5-small, uma opção otimizada para execução em CPU.

Podemos considerar o teste das melhorias futuras.

#### 📜 Possíveis Melhorias Futuras

Embora o sistema esteja funcional e operacional, há algumas otimizações que podem aprimorar a precisão das respostas e a eficiência do modelo:

##### **1️⃣ Melhoria na Geração das Respostas**
- Testar modelos mais robustos, como **`google/flan-t5-base`** ou **`tiiuae/falcon-7b-instruct`**, caso haja mais recursos computacionais disponíveis.

- Refinar o **pós-processamento das respostas**, eliminando padrões degenerativos e garantindo maior fluidez na linguagem.

##### **2️⃣ Otimização da Recuperação de Contexto**
- Ajustar a **quantidade de trechos retornados do Qdrant** para fornecer mais informações ao modelo na hora de gerar respostas.

- Implementar **re-ranking dos resultados**, priorizando os trechos mais relevantes para cada pergunta.

- Testar o uso de embeddings mais avançados para melhorar a qualidade da busca semântica.

##### **4️⃣ Expansão da Base de Conhecimento**
- Criar um endpoint para **ingestão contínua de novos documentos**, permitindo a atualização da base de conhecimento sem necessidade de reinicialização.

- Habilitar um **mecanismo de feedback**, onde os usuários possam avaliar as respostas geradas, permitindo que o sistema aprenda e melhore continuamente.

- Integrar uma API externa para complementar o conhecimento armazenado, garantindo que informações atualizadas possam ser incorporadas automaticamente.

Essas melhorias podem tornar o sistema mais inteligente, eficiente e adaptável, garantindo respostas mais precisas e relevantes para diferentes tipos de perguntas.

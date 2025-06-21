import os
import logging
# from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
from langchain_openai import OpenAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_embedding_model():
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # logger.info(f"🔌 Embedding model usando dispositivo: {device}")
    # model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    # from openai import OpenAI

    # openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = OpenAIEmbeddings()#client=openai_client, model="text-embedding-3-small")

    return model

# def load_generator_model():
#     MODEL_PATH = "./fine_tuned_flan_t5"
#     device = 0 if torch.cuda.is_available() else -1

#     if os.path.exists(MODEL_PATH):
#         logger.info("✅ Carregando modelo fine-tuned do Flan-T5...")
#         tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
#         model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
#     else:
#         logger.warning("⚠️ Nenhum modelo fine-tuned encontrado, usando modelo base.")
#         tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
#         model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")

#     pipe = pipeline(
#         "text2text-generation",
#         model=model,
#         tokenizer=tokenizer,
#         device=device
#     )

#     logger.info("🧠 Pipeline de geração de texto carregado!")
#     return pipe

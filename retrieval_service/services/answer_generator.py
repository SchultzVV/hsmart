import re
import logging

logger = logging.getLogger(__name__)


def clean_response(response: str) -> str:
    """
    Limpa a resposta gerada para evitar palavras incompletas, repetições e truncamentos feios.
    """
    # Remove repetições tipo: "Hotmart, Hotmart, Hotmart"
    response = re.sub(r"\b(\w+)(, \1)+\b", r"\1", response)

    # Corta se a resposta terminar no meio de uma palavra ou símbolo estranho
    response = re.split(r"[.!?]", response)[0].strip() + "."

    # Remove quebras de linha e espaços duplicados
    response = re.sub(r"\s+", " ", response)

    return response.strip()


def generate_answer(question: str, context: str, generator) -> str:
    """
    Gera a resposta com base na pergunta e no contexto usando o pipeline Hugging Face.

    Parameters:
        question (str): A pergunta do usuário.
        context (str): O contexto recuperado das coleções.
        generator (pipeline): Pipeline de geração (Flan-T5 ou fine-tuned).

    Returns:
        str: Resposta gerada.
    """
    if "Não há informações suficientes" in context:
        return "Não sei a resposta."

    prompt = f"""
    Responda à pergunta abaixo de forma clara, objetiva e apenas com base no contexto fornecido.

    Pergunta: {question}
    Contexto: {context}
    """

    try:
        result = generator(
            prompt,
            max_length=120,
            min_length=40,
            truncation=True,
            do_sample=False,
            temperature=0.5,
            top_k=40,
            top_p=0.8,
            repetition_penalty=1.2
        )
        raw_response = result[0]["generated_text"]
        logger.info(f"🤖 Resposta bruta gerada: {raw_response}")
        return clean_response(raw_response)

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        return "Houve um erro ao gerar a resposta."

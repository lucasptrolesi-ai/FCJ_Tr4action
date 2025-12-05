from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from openai import OpenAIError, APIError, APITimeoutError
from core.config import OPENAI_API_KEY, OPENAI_MODEL
import asyncio
import logging

logger = logging.getLogger(__name__)

# ============================================================
# 🔐 VERIFICAÇÃO INICIAL — GARANTE QUE A API KEY EXISTE
# ============================================================
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY não está configurada no .env")


# ============================================================
# 🤖 CLIENTE OFICIAL (ASSÍNCRONO)
# ============================================================
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# 🛠 FUNÇÃO PRINCIPAL — CHAT COMPLETION (RESPONSES API)
# ============================================================
async def chat_completion(
    messages: List[Dict[str, Any]],
    temperature: float = 0.2,
    model: str = OPENAI_MODEL,
    timeout: int = 25,
) -> str:
    """
    Chamada robusta ao modelo via Responses API.
    - Compatível com gpt-5-nano, gpt-4.1, etc.
    - Timeout automático
    - Tratamento de exceção
    - Garantia de retorno limpo
    """

    # ======= 🔍 Sanitização mínima (evita erros comuns) =======
    if not messages or not isinstance(messages, list):
        raise ValueError("O parâmetro 'messages' deve ser uma lista de mensagens.")

    # ======= 🚨 Fail-safe: garante que há pelo menos um system_msg =======
    if messages[0]["role"] != "system":
        raise RuntimeError("A primeira mensagem deve ser 'system'. O estilo TR4CTION exige isso.")

    # ======= ⏳ Timeout seguro =======
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=800,
            ),
            timeout=timeout
        )
        logger.info(f"Chat completion bem-sucedido com modelo {model}")

    except asyncio.TimeoutError:
        logger.error(f"Timeout ao chamar OpenAI modelo {model} após {timeout}s")
        raise RuntimeError("Tempo limite excedido ao tentar chamar o modelo.")

    except APITimeoutError as e:
        logger.error(f"OpenAI API timeout: {str(e)}")
        raise RuntimeError(f"API OpenAI não respondeu a tempo: {str(e)}")

    except APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        # ====== fallback automático ======
        if model != "gpt-4o-mini":
            try:
                logger.info(f"Tentando fallback para gpt-4o-mini")
                fallback_model = "gpt-4o-mini"
                response = await client.chat.completions.create(
                    model=fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=800,
                )
                logger.info("Fallback para gpt-4o-mini bem-sucedido")
            except OpenAIError as fallback_error:
                logger.error(f"Fallback também falhou: {str(fallback_error)}")
                raise RuntimeError(
                    f"Erro ao chamar modelo principal ({model}) e fallback ({fallback_model}). "
                    f"Detalhe do erro principal: {e} | fallback: {fallback_error}"
                )
        else:
            raise RuntimeError(f"Erro ao chamar modelo {model}: {e}")

    except OpenAIError as e:
        logger.error(f"OpenAI error genérico: {str(e)}")
        raise RuntimeError(f"Erro ao chamar OpenAI: {str(e)}")

    # ============================================================
    # 🔁 PROCESSAMENTO DA RESPOSTA
    # ============================================================

    if not response.choices or len(response.choices) == 0:
        raise RuntimeError("A API retornou uma estrutura inesperada (sem choices).")

    output = response.choices[0].message.content or ""

    # Evita retornos nulos ou vazios
    if not output.strip():
        raise RuntimeError("A OpenAI retornou uma resposta vazia.")

    return output.strip()

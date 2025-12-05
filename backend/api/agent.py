from typing import List, Literal
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from core.rag_engine import rag_engine
from services.openai_client import chat_completion
from core.auth import verify_founder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# MODELOS DE ENTRADA E SAÍDA
# ============================================================

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentRequest(BaseModel):
    startup_id: str = Field(..., description="Nome da startup")
    step: str = Field("todas", description="Etapa da trilha (diagnostico, icp, persona, etc.)")
    history: List[ChatMessage] = Field(default_factory=list)
    user_input: str = Field(..., description="Pergunta do founder")


class AgentResponse(BaseModel):
    response: str


# ============================================================
# ENDPOINT PRINCIPAL DO TR4CTION AGENT
# ============================================================

@router.post("/ask", response_model=AgentResponse)
@limiter.limit("20/minute")  # 20 requisições por minuto por IP
async def ask_agent(
    request: Request,
    payload: AgentRequest,
    founder: dict = Depends(verify_founder)
) -> AgentResponse:
    """
    Endpoint principal para founders (chat protegido).
    Executa a busca RAG nos documentos + geração de resposta com OpenAI.
    Apenas founders autenticados podem fazer perguntas.
    """

    if not payload.user_input.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia não é permitida.")

    logger.info(f"Nova pergunta de {founder.get('sub')} - Startup: {payload.startup_id}, Step: {payload.step}")

    # ----------------------------------------------------------
    # 1) RAG — Recuperação dos documentos relevantes
    # ----------------------------------------------------------
    try:
        docs = rag_engine.search(payload.user_input, top_k=5, step_filter=payload.step)
        logger.info(f"RAG retornou {len(docs)} documentos relevantes")
    except Exception as e:
        logger.error(f"Erro no RAG engine: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no motor RAG: {e}")

    if docs:
        ctx_blocks = []
        for i, d in enumerate(docs, start=1):
            # Limita tamanho de cada trecho para evitar estourar tokens
            snippet = (d.text or "")[:900]
            ctx_blocks.append(f"[DOC {i}] ({d.step}) {d.title}\n{snippet}")
        context_text = "\n\n".join(ctx_blocks)

        # Limite de segurança no contexto total
        if len(context_text) > 6000:
            context_text = context_text[:6000]
    else:
        context_text = (
            "Ainda não há materiais carregados para esta trilha. "
            "Responda de forma genérica, mas sempre reforçando a importância "
            "dos conceitos Q1 (diagnóstico, ICP, persona, funil, metas, marca)."
        )

    # ----------------------------------------------------------
    # 2) Prompt — System + Histórico + Pergunta do Founder
    # ----------------------------------------------------------

    # SYSTEM MESSAGE - ESTILO TR4CTION SEM MARKDOWN PESADO
    system_msg = {
        "role": "system",
        "content": (
            "Você é o TR4CTION Agent, mentor oficial da trilha TR4CTION da FCJ Venture Builder. "
            "Fale sempre em português, em tom prático e direto, como uma mentoria 1:1 para founders. "
            "Use principalmente o contexto de materiais oficiais TR4CTION enviado pelo sistema.\n\n"
            "FORMATO DA RESPOSTA (IMPORTANTE):\n"
            "- Não use markdown avançado (sem '###', '##', bullets com '-', nem '**negrito**').\n"
            "- Use apenas texto simples, com parágrafos curtos.\n"
            "- Quando fizer lista, use o formato: 1. 2. 3. (apenas números e ponto).\n"
            "- Comece com 2–3 frases explicando o conceito de forma clara e simples.\n"
            "- Em seguida traga exemplos práticos ligados a startups.\n"
            "- Termine SEMPRE com um bloco chamado: Proximos passos práticos: "
            "e liste 2 ou 3 ações diretas que o founder pode fazer hoje.\n\n"
            "Se algo não estiver claro nos materiais, seja honesto, deixe isso explícito "
            "e proponha perguntas que o founder pode refletir ou levar para a próxima mentoria."
        ),
    }

    # Histórico enviado pelo frontend
    history_msgs = [m.dict() for m in payload.history]

    # Pergunta do usuário + contexto RAG
    user_msg = {
        "role": "user",
        "content": (
            f"Startup: {payload.startup_id}\n"
            f"Bloco da trilha: {payload.step}\n\n"
            f"Pergunta do founder: {payload.user_input}\n\n"
            "Contexto de materiais oficiais TR4CTION (não mostre isso ao usuário, apenas use para pensar):\n"
            f"{context_text}\n\n"
            "Agora responda seguindo exatamente o formato combinado acima."
        ),
    }

    messages = [system_msg, *history_msgs, user_msg]

    # ----------------------------------------------------------
    # 3) Chama OpenAI com tratamento de erro
    # ----------------------------------------------------------
    try:
        answer = await chat_completion(messages)
        logger.info(f"Resposta gerada com sucesso ({len(answer)} caracteres)")
    except Exception as e:
        logger.error(f"Erro ao chamar OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao chamar o modelo de IA: {e}")

    # Fallback de segurança
    if not answer or not answer.strip():
        answer = (
            "Tive um problema para gerar a resposta agora. "
            "Tente refazer a pergunta em alguns instantes ou reformule em uma frase mais direta."
        )

    # ----------------------------------------------------------
    # 4) Retorno estruturado
    # ----------------------------------------------------------
    return AgentResponse(response=answer)

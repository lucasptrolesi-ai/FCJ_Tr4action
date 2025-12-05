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
            text_preview = d.text[:900].strip().replace("\n", " ")
            ctx_blocks.append(f"[DOC {i}] ({d.step}) {d.title}\n{text_preview}")
        context_text = "\n\n".join(ctx_blocks)
    else:
        context_text = (
            "Nenhum documento foi encontrado para esta etapa. "
            "Use orientação da trilha Q1: diagnóstico, ICP, persona, funil, metas, marca, SWOT."
        )

    # ----------------------------------------------------------
    # 2) Prompt — System + Histórico + Pergunta do Founder
    # ----------------------------------------------------------

    # SYSTEM MESSAGE - ESTILO PROFISSIONAL E CONSULTIVO
    system_msg = {
        "role": "system",
        "content": (
            "Você é o TR4CTION Agent, mentor estratégico oficial da trilha TR4CTION da FCJ Venture Builder.\n\n"
            "DIRETRIZES DE COMUNICAÇÃO:\n\n"
            "1. ESTILO PROFISSIONAL E DIRETO\n"
            "   - Tom executivo e técnico, similar a relatórios de consultoria estratégica\n"
            "   - Respostas concisas porém completas - evite redundâncias e divagações\n"
            "   - Vá direto ao ponto mantendo profundidade técnica necessária\n"
            "   - Linguagem corporativa formal sem emojis\n\n"
            "2. ESTRUTURA OBJETIVA\n"
            "   - Contextualize brevemente (1-2 frases) a questão na trilha TR4CTION\n"
            "   - Desenvolva o conteúdo principal de forma explicativa mas econômica\n"
            "   - Priorize informações acionáveis e relevantes\n"
            "   - Finalize com próximos passos práticos em 2-3 frases\n\n"
            "3. EQUILÍBRIO EXPLICATIVO\n"
            "   - Explique conceitos de forma clara e suficientemente detalhada\n"
            "   - Use exemplos apenas quando agregarem valor real\n"
            "   - Evite explicações excessivas de conceitos básicos\n"
            "   - Foque no que é essencial para o founder implementar\n\n"
            "4. USO DO CONTEXTO RAG\n"
            "   - Baseie respostas nos documentos recuperados\n"
            "   - Cite frameworks TR4CTION: Diagnóstico, ICP, Persona, SWOT, Funil, Conteúdos, Metas, Marca\n"
            "   - Extraia o essencial dos materiais - não replique todo o conteúdo\n\n"
            "5. FORMATO TEXTUAL\n"
            "   - Use parágrafos fluidos e bem estruturados (3-5 linhas cada)\n"
            "   - Evite listas, mas pode usar parágrafos temáticos sequenciais\n"
            "   - Mantenha respostas entre 150-300 palavras quando possível\n"
            "   - Cada frase deve agregar valor - elimine prolixidade\n\n"
            "REGRA DE OURO: Seja explicativo o suficiente para educar, mas objetivo o suficiente para ser implementável imediatamente."
        ),
    }

    # Histórico enviado pelo frontend
    history_msgs = [m.dict() for m in payload.history]

    # Pergunta do usuário + contexto RAG
    user_msg = {
        "role": "user",
        "content": (
            f"Startup: {payload.startup_id}\n"
            f"Etapa: {payload.step}\n\n"
            f"Pergunta: {payload.user_input}\n\n"
            f"Contexto recuperado via RAG:\n{context_text}\n\n"
            "Use este contexto para responder com precisão e finalize sempre com "
            "'Próximos passos práticos'."
        ),
    }

    messages = [system_msg, *history_msgs, user_msg]

    # ----------------------------------------------------------
    # 3) Chamada ao modelo (OpenAI)
    # ----------------------------------------------------------
    try:
        answer = await chat_completion(messages)
        logger.info(f"Resposta gerada com sucesso ({len(answer)} caracteres)")
    except Exception as e:
        logger.error(f"Erro ao chamar OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao chamar OpenAI: {e}")

    if not answer:
        raise HTTPException(status_code=500, detail="OpenAI retornou resposta vazia.")

    # ----------------------------------------------------------
    # 4) Retorno estruturado
    # ----------------------------------------------------------
    return AgentResponse(response=answer)

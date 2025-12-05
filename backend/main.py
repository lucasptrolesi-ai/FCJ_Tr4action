from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging

from api.agent import router as agent_router
from api.admin import router as admin_router
from api.auth import router as auth_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TR4CTION Agent Backend",
    version="1.0.0",
    description="Backend FastAPI com RAG + OpenAI para o agente TR4CTION.",
)

# Adicionar rate limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Configurado para produção e desenvolvimento
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]  # Remove espaços extras

logger.info(f"CORS configurado para origens: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Usa variável do .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"status": "ok", "message": "TR4CTION backend operacional"}

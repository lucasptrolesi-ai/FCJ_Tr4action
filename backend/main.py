from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api.agent import router as agent_router
from api.admin import router as admin_router
from api.auth import router as auth_router

app = FastAPI(
    title="TR4CTION Agent Backend",
    version="1.0.0",
    description="Backend FastAPI com RAG + OpenAI para o agente TR4CTION.",
)

# CORS - Configurado para produção e desenvolvimento
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aceita todas as origens
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

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import os
import logging
from core.config import BASE_DIR

logger = logging.getLogger(__name__)

# Configuração de autenticação
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY não configurada. Gere uma chave segura com: "
        "python -c 'import secrets; print(secrets.token_hex(32))'"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Credenciais de admin (em produção, usar banco de dados)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_USERNAME e ADMIN_PASSWORD devem ser configuradas no arquivo .env"
    )

ADMIN_CREDENTIALS = {
    "username": ADMIN_USERNAME,
    "password": ADMIN_PASSWORD,
}

security = HTTPBearer()


def create_access_token(data: dict, role: str) -> str:
    """Gera token JWT com role (admin ou founder)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": role})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verifica e decodifica o token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de acesso com token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError as e:
        logger.warning(f"Token JWT inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


def require_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependency para proteger rotas admin"""
    payload = verify_token(credentials)
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas criadores de conteúdo FCJ podem acessar."
        )
    return payload


def verify_founder(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependency para verificar founders (opcional - permite acesso livre ou com token)"""
    payload = verify_token(credentials)
    if payload.get("role") not in ["founder", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas founders podem acessar o chat."
        )
    return payload

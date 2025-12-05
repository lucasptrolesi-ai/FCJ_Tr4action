from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import os
from core.config import BASE_DIR

# Configuração de autenticação
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tr4ction-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Credenciais de admin (em produção, usar banco de dados)
ADMIN_CREDENTIALS = {
    "username": os.getenv("ADMIN_USERNAME", "fcj_creator"),
    "password": os.getenv("ADMIN_PASSWORD", "fcj2025@tr4ction"),
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
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

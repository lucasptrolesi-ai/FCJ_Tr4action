from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from core.auth import create_access_token, ADMIN_CREDENTIALS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    message: str


class FounderLoginRequest(BaseModel):
    startup_name: str
    founder_name: str


@router.post("/admin/login", response_model=LoginResponse)
def admin_login(credentials: LoginRequest):
    """
    Login para criadores de conteúdo FCJ (admin)
    Acesso ao painel administrativo para alimentar a base de conhecimento
    """
    if (
        credentials.username == ADMIN_CREDENTIALS["username"]
        and credentials.password == ADMIN_CREDENTIALS["password"]
    ):
        logger.info(f"Login admin bem-sucedido: {credentials.username}")
        token = create_access_token(
            data={"sub": credentials.username},
            role="admin"
        )
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role="admin",
            message="Login admin realizado com sucesso"
        )
    
    logger.warning(f"Tentativa de login admin falhou: {credentials.username}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas"
    )


@router.post("/founder/login", response_model=LoginResponse)
def founder_login(data: FounderLoginRequest):
    """
    Login para founders (acesso ao chat)
    Validação simples por nome da startup
    """
    if not data.startup_name.strip() or not data.founder_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome da startup e founder são obrigatórios"
        )
    
    logger.info(f"Login founder: {data.founder_name} - Startup: {data.startup_name}")
    
    token = create_access_token(
        data={
            "sub": data.founder_name,
            "startup": data.startup_name
        },
        role="founder"
    )
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        role="founder",
        message=f"Bem-vindo(a) à trilha TR4CTION, {data.founder_name}!"
    )

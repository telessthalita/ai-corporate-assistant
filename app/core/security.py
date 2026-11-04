
import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

bearer = HTTPBearer(auto_error=False)


def autenticar_usuario(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer)
) -> str:
    admin_token = os.getenv("ADMIN_API_TOKEN")
    analyst_token = os.getenv("ANALYST_API_TOKEN")

    # Impede autenticação com configuração incompleta.
    if (
        not admin_token
        or not analyst_token
        or admin_token == analyst_token
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Autenticação não configurada"
        )

    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso obrigatório",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credenciais.credentials

    if secrets.compare_digest(token, admin_token):
        return "admin"

    if secrets.compare_digest(token, analyst_token):
        return "analyst"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"}
    )


def exigir_admin(
    perfil: str = Depends(autenticar_usuario)
) -> str:
    if perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administrador necessária"
        )

    return perfil

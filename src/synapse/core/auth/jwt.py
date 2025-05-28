"""Utilitários para autenticação JWT.

Este módulo contém funções para criação, validação e gerenciamento
de tokens JWT para autenticação de usuários.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from synapse.config import settings
from synapse.exceptions import authentication_exception

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Logger
logger = logging.getLogger(__name__)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT com as informações do usuário.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração personalizado (opcional)
        
    Returns:
        Token JWT codificado
        
    Raises:
        ValueError: Se a SECRET_KEY não estiver definida
    """
    if not settings.secret_key:
        raise ValueError("SECRET_KEY não definida. Impossível criar token.")
    
    to_encode = data.copy()
    
    # Definir expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    # Codificar token
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Valida o token JWT e retorna informações do usuário.
    
    Args:
        token: Token JWT de autenticação
        
    Returns:
        Dicionário com informações do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        # Decodificar token
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        # Extrair ID do usuário
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token sem subject (sub) encontrado")
            raise authentication_exception("Credenciais inválidas")
        
        return {
            "id": user_id,
            "username": payload.get("username", "unknown"),
            "role": payload.get("role", "user"),
            "scopes": payload.get("scopes", []),
        }
    except jwt.PyJWTError as exc:
        logger.error(f"Erro na validação do token JWT: {str(exc)}")
        raise authentication_exception("Credenciais inválidas") from exc


def verify_admin_access(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Verifica se o usuário tem acesso de administrador.
    
    Args:
        current_user: Informações do usuário atual
        
    Returns:
        Informações do usuário se tiver acesso de administrador
        
    Raises:
        HTTPException: Se o usuário não tiver permissão de administrador
    """
    if current_user.get("role") != "admin":
        logger.warning(
            f"Tentativa de acesso administrativo negada para usuário {current_user.get('id')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Acesso de administrador necessário.",
        )
    return current_user


def verify_scope(required_scope: str):
    """Cria uma dependência que verifica se o usuário tem o escopo necessário.
    
    Args:
        required_scope: Escopo necessário para acessar o recurso
        
    Returns:
        Função de dependência que verifica o escopo do usuário
    """
    def _verify_scope(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if required_scope not in current_user.get("scopes", []):
            logger.warning(
                f"Acesso negado por escopo insuficiente para usuário {current_user.get('id')}: "
                f"requer '{required_scope}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Escopo '{required_scope}' necessário.",
            )
        return current_user
    
    return _verify_scope

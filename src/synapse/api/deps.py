"""
Dependências para os endpoints da API.

Este módulo define as dependências comuns utilizadas pelos endpoints da API,
como autenticação, validação e injeção de dependências.
"""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.synapse.config import settings
from src.synapse.core.auth.jwt import decode_token, verify_token
from src.synapse.logging import get_logger

logger = get_logger(__name__)

# Esquema de autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Obtém o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT de autenticação
        
    Returns:
        Dados do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        # Verificar token
        is_valid = verify_token(token)
        if not is_valid:
            logger.warning(f"Token inválido: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decodificar token
        payload = decode_token(token)
        
        # Verificar se o usuário existe
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token sem identificação de usuário")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Em uma implementação real, aqui verificaríamos o usuário no banco de dados
        # Por simplicidade, retornamos os dados do token
        user_data = {
            "id": user_id,
            "username": payload.get("username", "unknown"),
            "email": payload.get("email", "unknown@example.com"),
            "roles": payload.get("roles", ["user"]),
        }
        
        return user_data
        
    except HTTPException:
        # Repassar exceções HTTP
        raise
    except Exception as e:
        logger.error(f"Erro ao autenticar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_admin_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Verifica se o usuário atual é um administrador.
    
    Args:
        current_user: Dados do usuário atual
        
    Returns:
        Dados do usuário administrador
        
    Raises:
        HTTPException: Se o usuário não for administrador
    """
    if "admin" not in current_user.get("roles", []):
        logger.warning(f"Acesso de administrador negado para usuário {current_user['id']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administrador necessária",
        )
    
    return current_user

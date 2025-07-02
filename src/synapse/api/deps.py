"""
Dependências para os endpoints da API.

Este módulo define as dependências comuns utilizadas pelos endpoints da API,
como autenticação, validação e injeção de dependências.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import uuid
from typing import Union, Optional

from synapse.core.config import settings
from synapse.database import get_db
from synapse.models.user import User
from synapse.core.auth.jwt import verify_token
from synapse.core.auth.password import verify_password

# Esquema de autenticação OAuth2 (Bearer Token)
# Removido auto_error=False para evitar conflitos na documentação
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,  # Não gerar erro automaticamente
)

# Esquema de autenticação básica (email/senha) para documentação
basic_auth = HTTPBasic(auto_error=False)


async def get_current_user_basic(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtém o usuário atual a partir das credenciais básicas (email/senha).
    Usado principalmente na documentação Swagger para facilitar o login.

    Args:
        credentials: Credenciais básicas (email como username, senha)
        db: Sessão do banco de dados

    Returns:
        Objeto User do usuário autenticado

    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha inválidos",
        headers={"WWW-Authenticate": "Basic"},
    )

    if not credentials:
        raise credentials_exception

    # Buscar usuário por email (username na autenticação básica)
    user = db.query(User).filter(User.email == credentials.username).first()

    if not user:
        raise credentials_exception

    # Verificar senha
    if not verify_password(credentials.password, user.hashed_password):
        raise credentials_exception

    # Verificar se usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )

    return user


async def get_current_user_jwt(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtém o usuário atual a partir do token JWT.

    Args:
        token: Token JWT de autenticação
        db: Sessão do banco de dados

    Returns:
        Objeto User do usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificar se o token foi fornecido (pode ser None devido ao auto_error=False)
    if token is None:
        raise credentials_exception

    try:
        # Decodificar token JWT
        payload = verify_token(token)
        user_id_or_email: str = payload.get("user_id") or payload.get("sub")

        if user_id_or_email is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Buscar usuário no banco de dados
    user = None
    try:
        # Tenta converter para UUID
        user_uuid = uuid.UUID(user_id_or_email)
        user = db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, TypeError):
        # Não é UUID, buscar por email
        user = db.query(User).filter(User.email == user_id_or_email).first()

    if user is None:
        raise credentials_exception

    # Verificar se usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )

    return user


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    credentials: Optional[HTTPBasicCredentials] = Depends(basic_auth),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtém o usuário atual usando tanto JWT quanto Basic Auth.
    Tenta primeiro JWT, depois Basic Auth se JWT não estiver disponível.

    Args:
        token: Token JWT de autenticação (opcional)
        credentials: Credenciais básicas (opcional)
        db: Sessão do banco de dados

    Returns:
        Objeto User do usuário autenticado

    Raises:
        HTTPException: Se nenhuma autenticação válida for fornecida
    """
    # Tentar autenticação JWT primeiro
    if token:
        try:
            return await get_current_user_jwt(token, db)
        except HTTPException:
            pass  # Se JWT falhar, tenta Basic Auth

    # Tentar autenticação Basic se JWT não funcionou ou não foi fornecido
    if credentials:
        try:
            return await get_current_user_basic(credentials, db)
        except HTTPException:
            pass  # Se Basic Auth também falhar, lança erro

    # Se nenhuma autenticação funcionou
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação necessárias",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica se o usuário atual é um administrador.

    Args:
        current_user: Usuário atual

    Returns:
        Objeto User do administrador

    Raises:
        HTTPException: Se o usuário não for administrador
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administrador necessária",
        )

    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependência para obter o usuário atual ativo.

    Args:
        current_user: Usuário atual

    Returns:
        Objeto User do usuário ativo

    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo",
        )

    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependência que requer que o usuário atual seja um administrador.

    Args:
        current_user: Usuário atual ativo

    Returns:
        Objeto User do administrador

    Raises:
        HTTPException: Se o usuário não for administrador
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administrador necessária. Apenas usuários com privilégios de superusuário podem acessar este recurso.",
        )

    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Verifica se o usuário atual é um superusuário/administrador.

    Args:
        current_user: Usuário atual

    Returns:
        Objeto User do superusuário

    Raises:
        HTTPException: Se o usuário não for superusuário
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões de superusuário necessárias",
        )

    return current_user

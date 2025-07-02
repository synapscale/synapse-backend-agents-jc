"""
Users endpoints - Gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_db, get_current_superuser
from synapse.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserListResponse,
    UserStatus,
    UserRole,
)
from synapse.models import User
from synapse.core.auth.password import get_password_hash


router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Obter perfil do usuário atual"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        profile_image_url=current_user.profile_image_url,
        bio=current_user.bio,
        status=current_user.status,
        metadata=current_user.metadata or {},
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        failed_login_attempts=current_user.failed_login_attempts,
        account_locked_until=current_user.account_locked_until,
        tenant_id=current_user.tenant_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar perfil do usuário atual"""

    # Verificar se email já existe (se sendo alterado)
    if user_update.email and user_update.email != current_user.email:
        result = await db.execute(
            select(User).where(
                and_(User.email == user_update.email, User.id != current_user.id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso por outro usuário",
            )

    # Verificar se username já existe (se sendo alterado)
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(
            select(User).where(
                and_(User.username == user_update.username, User.id != current_user.id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já está em uso por outro usuário",
            )

    # Atualizar campos
    update_data = user_update.model_dump(exclude_unset=True)

    # Hash da nova senha se fornecida
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        # Se mudou senha, requer verificação novamente
        update_data["is_verified"] = False

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        profile_image_url=current_user.profile_image_url,
        bio=current_user.bio,
        status=current_user.status,
        metadata=current_user.metadata or {},
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        failed_login_attempts=current_user.failed_login_attempts,
        account_locked_until=current_user.account_locked_until,
        tenant_id=current_user.tenant_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.get("/", response_model=UserListResponse)
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(
        None, description="Buscar por nome, email ou username"
    ),
    status: Optional[UserStatus] = Query(None, description="Filtrar por status"),
    is_active: Optional[bool] = Query(None, description="Filtrar por usuários ativos"),
    is_verified: Optional[bool] = Query(
        None, description="Filtrar por usuários verificados"
    ),
):
    """Listar usuários (apenas superusuários)"""

    # Construir query base
    query = select(User)

    # Aplicar filtros
    conditions = []

    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.username.ilike(search_term),
            )
        )

    if status:
        conditions.append(User.status == status.value)

    if is_active is not None:
        conditions.append(User.is_active == is_active)

    if is_verified is not None:
        conditions.append(User.is_verified == is_verified)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(User.created_at.desc())

    # Executar query
    result = await db.execute(query)
    users = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    user_responses = [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            profile_image_url=user.profile_image_url,
            bio=user.bio,
            status=user.status,
            metadata=user.metadata or {},
            last_login_at=user.last_login_at,
            login_count=user.login_count,
            failed_login_attempts=user.failed_login_attempts,
            account_locked_until=user.account_locked_until,
            tenant_id=user.tenant_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]

    return UserListResponse(
        items=user_responses, total=total, page=page, pages=pages, size=size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter usuário por ID"""

    # Verificar se é o próprio usuário ou superusuário
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a ver este usuário",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        profile_image_url=user.profile_image_url,
        bio=user.bio,
        status=user.status,
        metadata=user.metadata or {},
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        failed_login_attempts=user.failed_login_attempts,
        account_locked_until=user.account_locked_until,
        tenant_id=user.tenant_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Atualizar usuário (apenas superusuários)"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Verificar se email já existe (se sendo alterado)
    if user_update.email and user_update.email != user.email:
        result = await db.execute(
            select(User).where(
                and_(User.email == user_update.email, User.id != user_id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso por outro usuário",
            )

    # Verificar se username já existe (se sendo alterado)
    if user_update.username and user_update.username != user.username:
        result = await db.execute(
            select(User).where(
                and_(User.username == user_update.username, User.id != user_id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já está em uso por outro usuário",
            )

    # Atualizar campos
    update_data = user_update.model_dump(exclude_unset=True)

    # Hash da nova senha se fornecida
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        profile_image_url=user.profile_image_url,
        bio=user.bio,
        status=user.status,
        metadata=user.metadata or {},
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        failed_login_attempts=user.failed_login_attempts,
        account_locked_until=user.account_locked_until,
        tenant_id=user.tenant_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Deletar usuário (apenas superusuários)"""

    # Não permitir deletar a si mesmo
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar seu próprio usuário",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Soft delete - marcar como inativo e status deleted
    user.is_active = False
    user.status = UserStatus.DELETED.value

    await db.commit()

    return {"message": "Usuário deletado com sucesso"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Ativar usuário (apenas superusuários)"""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    user.is_active = True
    user.status = UserStatus.ACTIVE.value
    user.failed_login_attempts = 0
    user.account_locked_until = None

    await db.commit()

    return {"message": "Usuário ativado com sucesso"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Desativar usuário (apenas superusuários)"""

    # Não permitir desativar a si mesmo
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar seu próprio usuário",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    user.is_active = False
    user.status = UserStatus.INACTIVE.value

    await db.commit()

    return {"message": "Usuário desativado com sucesso"}

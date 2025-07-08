"""
Tenants endpoints - Gerenciamento de multi-tenancy
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
import secrets

from synapse.api.deps import get_current_active_user, get_db, get_current_superuser
from synapse.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
    TenantStatus,
)
from synapse.models import Tenant, User, Plan
from synapse.database import get_async_db


router = APIRouter()


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter tenant do usuário atual"""

    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não possui tenant associado",
        )

    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.plan))
        .where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        domain=tenant.domain,
        status=tenant.status,
        plan_id=tenant.plan_id,
        settings=tenant.settings or {},
        theme=tenant.theme,
        default_language=tenant.default_language,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        favicon_url=tenant.favicon_url,
        custom_css=tenant.custom_css,
        metadata=tenant.metadata or {},
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        # Dados do plano
        plan_name=tenant.plan.name if tenant.plan else None,
        plan_type=tenant.plan.type if tenant.plan else None,
    )


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),  # Apenas superusuários
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Buscar por nome, slug ou domínio"),
    status: Optional[TenantStatus] = Query(None, description="Filtrar por status"),
    plan_id: Optional[uuid.UUID] = Query(None, description="Filtrar por plano"),
):
    """Listar todos os tenants (apenas superusuários)"""

    # Query base
    query = select(Tenant).options(selectinload(Tenant.plan))

    conditions = []

    # Aplicar filtros
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Tenant.name.ilike(search_term),
                Tenant.slug.ilike(search_term),
                Tenant.domain.ilike(search_term),
            )
        )

    if status:
        conditions.append(Tenant.status == status.value)

    if plan_id:
        conditions.append(Tenant.plan_id == plan_id)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Tenant.created_at.desc())

    # Executar query
    result = await db.execute(query)
    tenants = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    tenant_responses = [
        TenantResponse(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            domain=tenant.domain,
            status=tenant.status,
            plan_id=tenant.plan_id,
            settings=tenant.settings or {},
            theme=tenant.theme,
            default_language=tenant.default_language,
            timezone=tenant.timezone,
            logo_url=tenant.logo_url,
            favicon_url=tenant.favicon_url,
            custom_css=tenant.custom_css,
            metadata=tenant.metadata or {},
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            plan_name=tenant.plan.name if tenant.plan else None,
            plan_type=tenant.plan.type if tenant.plan else None,
        )
        for tenant in tenants
    ]

    return TenantListResponse(
        items=tenant_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),  # Apenas superusuários
):
    """Criar novo tenant (apenas superusuários)"""

    # Verificar se slug é único
    if tenant_data.slug:
        existing_slug = await db.execute(
            select(Tenant).where(Tenant.slug == tenant_data.slug)
        )
        if existing_slug.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug já está em uso"
            )
    else:
        # Gerar slug baseado no nome
        base_slug = tenant_data.name.lower().replace(" ", "-")
        # Remover caracteres especiais
        import re

        base_slug = re.sub(r"[^a-z0-9-]", "", base_slug)
        tenant_data.slug = base_slug

    # Verificar se domínio é único (se fornecido)
    if tenant_data.domain:
        existing_domain = await db.execute(
            select(Tenant).where(Tenant.domain == tenant_data.domain)
        )
        if existing_domain.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Domínio já está em uso"
            )

    # Verificar se plano existe (se fornecido)
    if tenant_data.plan_id:
        plan_result = await db.execute(
            select(Plan).where(Plan.id == tenant_data.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado"
            )

    # Criar tenant
    tenant = Tenant(
        name=tenant_data.name,
        slug=tenant_data.slug,
        domain=tenant_data.domain,
        plan_id=tenant_data.plan_id,
        settings=tenant_data.settings,
        theme=tenant_data.theme,
        default_language=tenant_data.default_language,
        timezone=tenant_data.timezone,
        logo_url=tenant_data.logo_url,
        favicon_url=tenant_data.favicon_url,
        custom_css=tenant_data.custom_css,
        metadata=tenant_data.metadata,
        status=TenantStatus.ACTIVE.value,
    )

    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        domain=tenant.domain,
        status=tenant.status,
        plan_id=tenant.plan_id,
        settings=tenant.settings or {},
        theme=tenant.theme,
        default_language=tenant.default_language,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        favicon_url=tenant.favicon_url,
        custom_css=tenant.custom_css,
        metadata=tenant.metadata or {},
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),  # Apenas superusuários
):
    """Obter tenant específico (apenas superusuários)"""

    result = await db.execute(
        select(Tenant).options(selectinload(Tenant.plan)).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        domain=tenant.domain,
        status=tenant.status,
        plan_id=tenant.plan_id,
        settings=tenant.settings or {},
        theme=tenant.theme,
        default_language=tenant.default_language,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        favicon_url=tenant.favicon_url,
        custom_css=tenant.custom_css,
        metadata=tenant.metadata or {},
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        plan_name=tenant.plan.name if tenant.plan else None,
        plan_type=tenant.plan.type if tenant.plan else None,
    )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    tenant_update: TenantUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),  # Apenas superusuários
):
    """Atualizar tenant (apenas superusuários)"""

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    # Verificar se slug é único se sendo alterado
    if tenant_update.slug and tenant_update.slug != tenant.slug:
        existing_slug = await db.execute(
            select(Tenant).where(
                and_(Tenant.slug == tenant_update.slug, Tenant.id != tenant_id)
            )
        )
        if existing_slug.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug já está em uso"
            )

    # Verificar se domínio é único se sendo alterado
    if tenant_update.domain and tenant_update.domain != tenant.domain:
        existing_domain = await db.execute(
            select(Tenant).where(
                and_(Tenant.domain == tenant_update.domain, Tenant.id != tenant_id)
            )
        )
        if existing_domain.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Domínio já está em uso"
            )

    # Verificar se plano existe se sendo alterado
    if tenant_update.plan_id and tenant_update.plan_id != tenant.plan_id:
        plan_result = await db.execute(
            select(Plan).where(Plan.id == tenant_update.plan_id)
        )
        if not plan_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado"
            )

    # Atualizar campos
    update_data = tenant_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        domain=tenant.domain,
        status=tenant.status,
        plan_id=tenant.plan_id,
        settings=tenant.settings or {},
        theme=tenant.theme,
        default_language=tenant.default_language,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        favicon_url=tenant.favicon_url,
        custom_css=tenant.custom_css,
        metadata=tenant.metadata or {},
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),  # Apenas superusuários
):
    """Deletar tenant (apenas superusuários)"""

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    # Verificar se existem usuários ativos no tenant
    users_count = await db.execute(
        select(func.count(User.id)).where(
            and_(User.tenant_id == tenant_id, User.is_active == True)
        )
    )
    if users_count.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar tenant com usuários ativos",
        )

    # Soft delete
    tenant.status = TenantStatus.DELETED.value

    await db.commit()

    return {"message": "Tenant deletado com sucesso"}


@router.post("/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),
):
    """Ativar tenant (apenas superusuários)"""

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    tenant.status = TenantStatus.ACTIVE.value

    await db.commit()

    return {"message": "Tenant ativado com sucesso"}


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),
):
    """Suspender tenant (apenas superusuários)"""

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant não encontrado"
        )

    tenant.status = TenantStatus.SUSPENDED.value

    await db.commit()

    return {"message": "Tenant suspenso com sucesso"}

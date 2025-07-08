"""
Workspaces endpoints - Gerenciamento de workspaces colaborativos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
import secrets

from synapse.api.deps import get_current_active_user
from synapse.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
    WorkspaceListResponse,
    WorkspaceStatus,
    WorkspaceType,
)
from synapse.schemas.workspace_member import (
    WorkspaceMemberResponse,
    WorkspaceMemberCreate,
    WorkspaceMemberListResponse,
)
# TODO: Add missing schemas when available:
# WorkspaceInvitationCreate, WorkspaceInvitationResponse, WorkspaceInvitationListResponse
from synapse.models import (
    Workspace,
    User,
    WorkspaceMember,
    # WorkspaceActivity,  # TODO: Add when model is available
    # WorkspaceInvitation,  # TODO: Add when model is available
    Tenant,
)
from synapse.database import get_async_db

router = APIRouter()


@router.get("/", response_model=WorkspaceListResponse)
async def list_workspaces(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    type: Optional[WorkspaceType] = Query(None, description="Filtrar por tipo"),
    status: Optional[WorkspaceStatus] = Query(None, description="Filtrar por status"),
    is_owner: Optional[bool] = Query(None, description="Filtrar workspaces próprios"),
):
    """Listar workspaces do usuário"""

    # Query base - workspaces onde o usuário é owner ou membro
    query = select(Workspace).options(
        selectinload(Workspace.owner), selectinload(Workspace.tenant)
    )

    conditions = []

    # Filtrar por workspaces do usuário
    if is_owner:
        conditions.append(Workspace.user_id == current_user.id)
    else:
        # Workspaces onde é owner OU membro
        member_subquery = select(WorkspaceMember.workspace_id).where(
            WorkspaceMember.user_id == current_user.id
        )
        conditions.append(
            or_(
                Workspace.user_id == current_user.id, Workspace.id.in_(member_subquery)
            )
        )

    # Aplicar filtros adicionais
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Workspace.name.ilike(search_term),
                Workspace.description.ilike(search_term),
            )
        )

    if type:
        conditions.append(Workspace.type == type.value)

    if status:
        conditions.append(Workspace.status == status.value)
    else:
        # Por padrão, só mostrar workspaces ativos
        conditions.append(Workspace.status == WorkspaceStatus.ACTIVE.value)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Workspace.updated_at.desc())

    # Executar query
    result = await db.execute(query)
    workspaces = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    workspace_responses = []
    for workspace in workspaces:
        workspace_responses.append(
            WorkspaceResponse(
                id=workspace.id,
                name=workspace.name,
                slug=workspace.slug,
                type=workspace.type,
                description=workspace.description,
                avatar_url=workspace.avatar_url,
                color=workspace.color,
                owner_id=workspace.owner_id,
                tenant_id=workspace.tenant_id,
                is_public=workspace.is_public,
                is_template=workspace.is_template,
                allow_guest_access=workspace.allow_guest_access,
                require_approval=workspace.require_approval,
                max_members=workspace.max_members,
                max_projects=workspace.max_projects,
                max_storage_mb=workspace.max_storage_mb,
                enable_real_time_editing=workspace.enable_real_time_editing,
                enable_comments=workspace.enable_comments,
                enable_chat=workspace.enable_chat,
                enable_video_calls=workspace.enable_video_calls,
                email_notifications=workspace.email_notifications,
                push_notifications=workspace.push_notifications,
                member_count=workspace.member_count,
                project_count=workspace.project_count,
                activity_count=workspace.activity_count,
                storage_used_mb=workspace.storage_used_mb,
                api_calls_today=workspace.api_calls_today,
                api_calls_this_month=workspace.api_calls_this_month,
                feature_usage_count=workspace.feature_usage_count or {},
                status=workspace.status,
                created_at=workspace.created_at,
                updated_at=workspace.updated_at,
                last_activity_at=workspace.last_activity_at,
                # Dados relacionados
                owner_name=workspace.owner.full_name if workspace.owner else None,
                tenant_name=workspace.tenant.name if workspace.tenant else None,
            )
        )

    return WorkspaceListResponse(
        items=workspace_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Criar novo workspace"""

    # Verificar se o usuário pode criar mais workspaces
    if current_user.tenant:
        user_workspaces_count = await db.execute(
            select(func.count(Workspace.id)).where(
                and_(
                    Workspace.user_id == current_user.id,
                    Workspace.status == WorkspaceStatus.ACTIVE.value,
                )
            )
        )
        current_count = user_workspaces_count.scalar()

        if (
            current_user.tenant.plan
            and current_count >= current_user.tenant.plan.max_workspaces
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limite de workspaces atingido ({current_user.tenant.plan.max_workspaces})",
            )

    # Verificar se slug é único
    if workspace_data.slug:
        existing = await db.execute(
            select(Workspace).where(Workspace.slug == workspace_data.slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug já está em uso"
            )
    else:
        # Gerar slug baseado no nome
        base_slug = workspace_data.name.lower().replace(" ", "-").replace("_", "-")
        # Remover caracteres especiais
        import re

        base_slug = re.sub(r"[^a-z0-9-]", "", base_slug)
        workspace_data.slug = base_slug

    # Criar workspace
    workspace = Workspace(
        name=workspace_data.name,
        slug=workspace_data.slug,
        type=workspace_data.type,
        description=workspace_data.description,
        avatar_url=workspace_data.avatar_url,
        color=workspace_data.color,
        owner_id=current_user.id,
        tenant_id=current_user.tenant_id,
        is_public=workspace_data.is_public,
        allow_guest_access=workspace_data.allow_guest_access,
        require_approval=workspace_data.require_approval,
        max_members=workspace_data.max_members,
        max_projects=workspace_data.max_projects,
        max_storage_mb=workspace_data.max_storage_mb,
        enable_real_time_editing=workspace_data.enable_real_time_editing,
        enable_comments=workspace_data.enable_comments,
        enable_chat=workspace_data.enable_chat,
        enable_video_calls=workspace_data.enable_video_calls,
        email_notifications=workspace_data.email_notifications,
        push_notifications=workspace_data.push_notifications,
    )

    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    # Criar atividade
    activity = WorkspaceActivity(
        workspace_id=workspace.id,
        user_id=current_user.id,
        action="workspace_created",
        metadata={"workspace_name": workspace.name},
    )
    db.add(activity)
    await db.commit()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        type=workspace.type,
        description=workspace.description,
        avatar_url=workspace.avatar_url,
        color=workspace.color,
        owner_id=workspace.owner_id,
        tenant_id=workspace.tenant_id,
        is_public=workspace.is_public,
        is_template=workspace.is_template,
        allow_guest_access=workspace.allow_guest_access,
        require_approval=workspace.require_approval,
        max_members=workspace.max_members,
        max_projects=workspace.max_projects,
        max_storage_mb=workspace.max_storage_mb,
        enable_real_time_editing=workspace.enable_real_time_editing,
        enable_comments=workspace.enable_comments,
        enable_chat=workspace.enable_chat,
        enable_video_calls=workspace.enable_video_calls,
        email_notifications=workspace.email_notifications,
        push_notifications=workspace.push_notifications,
        member_count=workspace.member_count,
        project_count=workspace.project_count,
        activity_count=workspace.activity_count,
        storage_used_mb=workspace.storage_used_mb,
        api_calls_today=workspace.api_calls_today,
        api_calls_this_month=workspace.api_calls_this_month,
        feature_usage_count=workspace.feature_usage_count or {},
        status=workspace.status,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        last_activity_at=workspace.last_activity_at,
        owner_name=current_user.full_name,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter workspace específico"""

    # Verificar acesso ao workspace
    result = await db.execute(
        select(Workspace)
        .options(selectinload(Workspace.owner), selectinload(Workspace.tenant))
        .where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace não encontrado"
        )

    # Verificar se tem acesso
    has_access = False
    if workspace.owner_id == current_user.id:
        has_access = True
    elif workspace.is_public:
        has_access = True
    else:
        # Verificar se é membro
        member_result = await db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id,
                )
            )
        )
        if member_result.scalar_one_or_none():
            has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este workspace",
        )

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        type=workspace.type,
        description=workspace.description,
        avatar_url=workspace.avatar_url,
        color=workspace.color,
        owner_id=workspace.owner_id,
        tenant_id=workspace.tenant_id,
        is_public=workspace.is_public,
        is_template=workspace.is_template,
        allow_guest_access=workspace.allow_guest_access,
        require_approval=workspace.require_approval,
        max_members=workspace.max_members,
        max_projects=workspace.max_projects,
        max_storage_mb=workspace.max_storage_mb,
        enable_real_time_editing=workspace.enable_real_time_editing,
        enable_comments=workspace.enable_comments,
        enable_chat=workspace.enable_chat,
        enable_video_calls=workspace.enable_video_calls,
        email_notifications=workspace.email_notifications,
        push_notifications=workspace.push_notifications,
        member_count=workspace.member_count,
        project_count=workspace.project_count,
        activity_count=workspace.activity_count,
        storage_used_mb=workspace.storage_used_mb,
        api_calls_today=workspace.api_calls_today,
        api_calls_this_month=workspace.api_calls_this_month,
        feature_usage_count=workspace.feature_usage_count or {},
        status=workspace.status,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        last_activity_at=workspace.last_activity_at,
        owner_name=workspace.owner.full_name if workspace.owner else None,
        tenant_name=workspace.tenant.name if workspace.tenant else None,
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: uuid.UUID,
    workspace_update: WorkspaceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar workspace"""

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace não encontrado"
        )

    # Verificar se é owner ou tem permissão de admin
    if workspace.owner_id != current_user.id:
        # TODO: Verificar se é admin do workspace via WorkspaceMember
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode atualizar o workspace",
        )

    # Verificar slug único se sendo alterado
    if workspace_update.slug and workspace_update.slug != workspace.slug:
        existing = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.slug == workspace_update.slug,
                    Workspace.id != workspace_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Slug já está em uso"
            )

    # Atualizar campos
    update_data = workspace_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)

    await db.commit()
    await db.refresh(workspace)

    # Criar atividade
    activity = WorkspaceActivity(
        workspace_id=workspace.id,
        user_id=current_user.id,
        action="workspace_updated",
        metadata={"updated_fields": list(update_data.keys())},
    )
    db.add(activity)
    await db.commit()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        type=workspace.type,
        description=workspace.description,
        avatar_url=workspace.avatar_url,
        color=workspace.color,
        owner_id=workspace.owner_id,
        tenant_id=workspace.tenant_id,
        is_public=workspace.is_public,
        is_template=workspace.is_template,
        allow_guest_access=workspace.allow_guest_access,
        require_approval=workspace.require_approval,
        max_members=workspace.max_members,
        max_projects=workspace.max_projects,
        max_storage_mb=workspace.max_storage_mb,
        enable_real_time_editing=workspace.enable_real_time_editing,
        enable_comments=workspace.enable_comments,
        enable_chat=workspace.enable_chat,
        enable_video_calls=workspace.enable_video_calls,
        email_notifications=workspace.email_notifications,
        push_notifications=workspace.push_notifications,
        member_count=workspace.member_count,
        project_count=workspace.project_count,
        activity_count=workspace.activity_count,
        storage_used_mb=workspace.storage_used_mb,
        api_calls_today=workspace.api_calls_today,
        api_calls_this_month=workspace.api_calls_this_month,
        feature_usage_count=workspace.feature_usage_count or {},
        status=workspace.status,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        last_activity_at=workspace.last_activity_at,
    )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deletar workspace"""

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace não encontrado"
        )

    # Verificar se é owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode deletar o workspace",
        )

    # Soft delete
    workspace.status = WorkspaceStatus.DELETED.value

    await db.commit()

    # Criar atividade
    activity = WorkspaceActivity(
        workspace_id=workspace.id,
        user_id=current_user.id,
        action="workspace_deleted",
        metadata={"workspace_name": workspace.name},
    )
    db.add(activity)
    await db.commit()

    return {"message": "Workspace deletado com sucesso"}


# ENDPOINTS DE MEMBROS


@router.get("/{workspace_id}/members", response_model=WorkspaceMemberListResponse)
async def list_workspace_members(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """Listar membros do workspace"""

    # Verificar acesso ao workspace
    workspace = await _get_workspace_with_access(db, workspace_id, current_user)

    # Query membros
    query = (
        select(WorkspaceMember)
        .options(selectinload(WorkspaceMember.user))
        .where(WorkspaceMember.workspace_id == workspace_id)
    )

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    members = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    member_responses = []
    for member in members:
        member_responses.append(
            WorkspaceMemberResponse(
                id=member.id,
                workspace_id=member.workspace_id,
                user_id=member.user_id,
                role=member.role,
                permissions=member.permissions or {},
                joined_at=member.joined_at,
                invited_by=member.invited_by,
                user_name=member.user.full_name if member.user else None,
                user_email=member.user.email if member.user else None,
            )
        )

    return WorkspaceMemberListResponse(
        items=member_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def add_workspace_member(
    workspace_id: uuid.UUID,
    member_data: WorkspaceMemberCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Adicionar membro ao workspace"""

    workspace = await _get_workspace_with_access(db, workspace_id, current_user)

    # Verificar se é owner ou admin
    if workspace.owner_id != current_user.id:
        # TODO: Verificar se é admin via WorkspaceMember
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode adicionar membros",
        )

    # Verificar se usuário existe
    user_result = await db.execute(select(User).where(User.id == member_data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Verificar se já é membro
    existing = await db.execute(
        select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == member_data.user_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já é membro do workspace",
        )

    # Verificar limite de membros
    if workspace.member_count >= workspace.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite de membros atingido ({workspace.max_members})",
        )

    # Criar membro
    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_data.user_id,
        role=member_data.role,
        permissions=member_data.permissions,
        invited_by=current_user.id,
    )

    db.add(member)

    # Atualizar contador
    workspace.member_count += 1

    await db.commit()
    await db.refresh(member)

    return WorkspaceMemberResponse(
        id=member.id,
        workspace_id=member.workspace_id,
        user_id=member.user_id,
        role=member.role,
        permissions=member.permissions or {},
        joined_at=member.joined_at,
        invited_by=member.invited_by,
        user_name=user.full_name,
        user_email=user.email,
    )


# FUNÇÃO AUXILIAR


async def _get_workspace_with_access(
    db: AsyncSession, workspace_id: uuid.UUID, user: User
) -> Workspace:
    """Obter workspace e verificar acesso"""
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace não encontrado"
        )

    # Verificar acesso
    has_access = False
    if workspace.owner_id == user.id:
        has_access = True
    elif workspace.is_public:
        has_access = True
    else:
        # Verificar se é membro
        member_result = await db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user.id,
                )
            )
        )
        if member_result.scalar_one_or_none():
            has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este workspace",
        )

    return workspace

"""
Agents endpoints - Gerenciamento de agentes de IA
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.schemas.agent import (
    AgentResponse,
    AgentCreate,
    AgentUpdate,
    AgentListResponse,
    AgentStatus,
    AgentEnvironment,
    AgentScope,
)
from synapse.models import Agent, User, Workspace, Tenant
from synapse.database import get_async_db


router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    workspace_id: Optional[uuid.UUID] = Query(
        None, description="Filtrar por workspace"
    ),
    search: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    status: Optional[AgentStatus] = Query(None, description="Filtrar por status"),
    environment: Optional[AgentEnvironment] = Query(
        None, description="Filtrar por ambiente"
    ),
    scope: Optional[AgentScope] = Query(None, description="Filtrar por escopo"),
    is_active: Optional[bool] = Query(None, description="Filtrar agentes ativos"),
):
    """Listar agentes do usuário"""

    # Query base
    query = select(Agent).options(
        selectinload(Agent.user), selectinload(Agent.workspace)
    )

    conditions = []

    # Filtrar por agentes do usuário
    conditions.append(Agent.user_id == current_user.id)

    # Filtrar por workspace se especificado
    if workspace_id:
        # Verificar se o usuário tem acesso ao workspace
        workspace_result = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.tenant_id == current_user.id,
                        Workspace.is_public == True,
                        # TODO: Verificar se é membro do workspace
                    ),
                )
            )
        )
        workspace = workspace_result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado ou sem acesso",
            )
        conditions.append(Agent.workspace_id == workspace_id)

    # Aplicar filtros adicionais
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(Agent.name.ilike(search_term), Agent.description.ilike(search_term))
        )

    if status:
        conditions.append(Agent.status == status.value)

    if environment:
        conditions.append(Agent.environment == environment.value)

    if scope:
        conditions.append(Agent.agent_scope == scope.value)

    if is_active is not None:
        conditions.append(Agent.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(Agent.updated_at.desc())

    # Executar query
    result = await db.execute(query)
    agents = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    agent_responses = []
    for agent in agents:
        agent_responses.append(
            AgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                version=agent.version,
                environment=agent.environment,
                status=agent.status,
                scope=agent.agent_scope,
                configuration=agent.configuration or {},
                metadata=agent.metadata or {},
                is_active=agent.is_active,
                user_id=agent.user_id,
                workspace_id=agent.workspace_id,
                tenant_id=agent.tenant_id,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                # Dados relacionados
                user_name=agent.user.full_name if agent.user else None,
                workspace_name=agent.workspace.name if agent.workspace else None,
            )
        )

    return AgentListResponse(
        items=agent_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Criar novo agente"""

    # Verificar se workspace existe e usuário tem acesso
    if agent_data.workspace_id:
        workspace_result = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.id == agent_data.workspace_id,
                    or_(
                        Workspace.tenant_id == current_user.id,
                        # TODO: Verificar se é membro do workspace
                    ),
                )
            )
        )
        workspace = workspace_result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado ou sem acesso",
            )

    # Verificar se nome é único no escopo (workspace ou tenant)
    name_conditions = [Agent.name == agent_data.name, Agent.user_id == current_user.id]

    if agent_data.scope == AgentScope.WORKSPACE and agent_data.workspace_id:
        name_conditions.append(Agent.workspace_id == agent_data.workspace_id)
    elif agent_data.scope == AgentScope.PRIVATE:
        name_conditions.append(Agent.agent_scope == AgentScope.PRIVATE.value)

    existing_agent = await db.execute(select(Agent).where(and_(*name_conditions)))
    if existing_agent.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um agente com este nome no escopo especificado",
        )

    # Criar agente
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        version=agent_data.version,
        environment=agent_data.environment,
        status=AgentStatus.DRAFT.value,  # Sempre criar como draft
        scope=agent_data.scope,
        configuration=agent_data.configuration,
        metadata=agent_data.metadata,
        is_active=False,  # Sempre criar como inativo
        user_id=current_user.id,
        workspace_id=agent_data.workspace_id,
        tenant_id=current_user.tenant_id,
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        version=agent.version,
        environment=agent.environment,
        status=agent.status,
        scope=agent.agent_scope,
        configuration=agent.configuration or {},
        metadata=agent.metadata or {},
        is_active=agent.is_active,
        user_id=agent.user_id,
        workspace_id=agent.workspace_id,
        tenant_id=agent.tenant_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        user_name=current_user.full_name,
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter agente por ID"""

    result = await db.execute(
        select(Agent)
        .options(selectinload(Agent.user), selectinload(Agent.workspace))
        .where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Verificar acesso
    has_access = False

    # Owner sempre tem acesso
    if agent.user_id == current_user.id:
        has_access = True
    # Agentes globais são acessíveis por todos
    elif agent.agent_scope == AgentScope.GLOBAL.value:
        has_access = True
    # Agentes de workspace são acessíveis por membros
    elif agent.agent_scope == AgentScope.WORKSPACE.value and agent.workspace:
        if agent.workspace.owner_id == current_user.id or agent.workspace.is_public:
            has_access = True
        # TODO: Verificar se é membro do workspace

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este agente",
        )

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        version=agent.version,
        environment=agent.environment,
        status=agent.status,
        scope=agent.agent_scope,
        configuration=agent.configuration or {},
        metadata=agent.metadata or {},
        is_active=agent.is_active,
        user_id=agent.user_id,
        workspace_id=agent.workspace_id,
        tenant_id=agent.tenant_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        user_name=agent.user.full_name if agent.user else None,
        workspace_name=agent.workspace.name if agent.workspace else None,
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar agente"""

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Apenas owner pode atualizar
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode atualizar o agente",
        )

    # Verificar se nome é único se sendo alterado
    if agent_update.name and agent_update.name != agent.name:
        name_conditions = [
            Agent.name == agent_update.name,
            Agent.user_id == current_user.id,
            Agent.id != agent_id,
        ]

        if agent.agent_scope == AgentScope.WORKSPACE.value and agent.workspace_id:
            name_conditions.append(Agent.workspace_id == agent.workspace_id)
        elif agent.agent_scope == AgentScope.PRIVATE.value:
            name_conditions.append(Agent.agent_scope == AgentScope.PRIVATE.value)

        existing = await db.execute(select(Agent).where(and_(*name_conditions)))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um agente com este nome no escopo especificado",
            )

    # Atualizar campos
    update_data = agent_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        version=agent.version,
        environment=agent.environment,
        status=agent.status,
        scope=agent.agent_scope,
        configuration=agent.configuration or {},
        metadata=agent.metadata or {},
        is_active=agent.is_active,
        user_id=agent.user_id,
        workspace_id=agent.workspace_id,
        tenant_id=agent.tenant_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deletar agente"""

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Apenas owner pode deletar
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode deletar o agente",
        )

    # Soft delete
    agent.status = AgentStatus.ARCHIVED.value
    agent.is_active = False

    await db.commit()

    return {"message": "Agente deletado com sucesso"}


@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ativar agente"""

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Apenas owner pode ativar
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode ativar o agente",
        )

    # Verificar se configuração está válida
    if not agent.configuration or not agent.configuration.get("model_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agente precisa ter configuração válida para ser ativado",
        )

    agent.is_active = True
    agent.status = AgentStatus.ACTIVE.value

    await db.commit()

    return {"message": "Agente ativado com sucesso"}


@router.post("/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Desativar agente"""

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Apenas owner pode desativar
    if agent.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode desativar o agente",
        )

    agent.is_active = False
    agent.status = AgentStatus.INACTIVE.value

    await db.commit()

    return {"message": "Agente desativado com sucesso"}


@router.post("/{agent_id}/clone", response_model=AgentResponse)
async def clone_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    new_name: Optional[str] = Query(None, description="Nome para o clone"),
):
    """Clonar agente"""

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado"
        )

    # Verificar se tem acesso para clonar
    has_access = False
    if agent.user_id == current_user.id:
        has_access = True
    elif agent.agent_scope == AgentScope.GLOBAL.value:
        has_access = True
    elif agent.agent_scope == AgentScope.WORKSPACE.value and agent.workspace:
        if agent.workspace.owner_id == current_user.id or agent.workspace.is_public:
            has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a clonar este agente",
        )

    # Gerar nome único
    clone_name = new_name or f"{agent.name} (Clone)"
    counter = 1
    while True:
        existing = await db.execute(
            select(Agent).where(
                and_(
                    Agent.name == clone_name,
                    Agent.user_id == current_user.id,
                    Agent.agent_scope == AgentScope.PRIVATE.value,
                )
            )
        )
        if not existing.scalar_one_or_none():
            break
        clone_name = f"{agent.name} (Clone {counter})"
        counter += 1

    # Criar clone
    clone = Agent(
        name=clone_name,
        description=f"Clone de {agent.name}",
        version="1.0.0",
        environment=agent.environment,
        status=AgentStatus.DRAFT.value,
        scope=AgentScope.PRIVATE.value,  # Clones são sempre privados
        configuration=agent.configuration.copy() if agent.configuration else {},
        metadata=agent.metadata.copy() if agent.metadata else {},
        is_active=False,
        user_id=current_user.id,
        workspace_id=None,  # Clones não herdam workspace
        tenant_id=current_user.tenant_id,
    )

    db.add(clone)
    await db.commit()
    await db.refresh(clone)

    return AgentResponse(
        id=clone.id,
        name=clone.name,
        description=clone.description,
        version=clone.version,
        environment=clone.environment,
        status=clone.status,
        scope=clone.scope,
        configuration=clone.configuration or {},
        metadata=clone.metadata or {},
        is_active=clone.is_active,
        user_id=clone.user_id,
        workspace_id=clone.workspace_id,
        tenant_id=clone.tenant_id,
        created_at=clone.created_at,
        updated_at=clone.updated_at,
        user_name=current_user.full_name,
    )

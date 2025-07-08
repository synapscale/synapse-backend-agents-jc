"""
LLMs endpoints - Gerenciamento de modelos de linguagem
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_db, get_current_superuser
from synapse.schemas.llm import (
    LLMResponse,
    LLMCreate,
    LLMUpdate,
    LLMListResponse,
    LLMConversationCreate,
    LLMConversationResponse,
    LLMConversationListResponse,
    LLMMessageCreate,
    LLMMessageResponse,
    LLMMessageListResponse,
)
from synapse.models import LLM, User, LLMConversation, LLMMessage, Workspace
from synapse.database import get_async_db


router = APIRouter()


@router.get("/", response_model=LLMListResponse)
async def list_llms(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Buscar por nome ou provedor"),
    provider: Optional[str] = Query(None, description="Filtrar por provedor"),
    is_active: Optional[bool] = Query(None, description="Filtrar modelos ativos"),
    is_public: Optional[bool] = Query(None, description="Filtrar modelos públicos"),
):
    """Listar modelos LLM disponíveis"""

    # Query base
    query = select(LLM)
    conditions = []

    # Filtrar apenas modelos acessíveis ao usuário
    conditions.append(LLM.tenant_id == current_user.tenant_id)

    # Aplicar filtros
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                LLM.name.ilike(search_term),
                LLM.provider.ilike(search_term),
                LLM.model_version.ilike(search_term),
            )
        )

    if provider:
        conditions.append(LLM.provider.ilike(f"%{provider}%"))

    if is_active is not None:
        conditions.append(LLM.is_active == is_active)

    if is_public is not None:
        conditions.append(LLM.is_active == is_public)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(LLM.name)

    # Executar query
    result = await db.execute(query)
    llms = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    llm_responses = [
        LLMResponse(
            id=llm.id,
            name=llm.name,
            provider=llm.provider,
            model_id=llm.model_id,
            description=llm.description,
            max_tokens=llm.max_tokens,
            temperature=llm.temperature,
            top_p=llm.top_p,
            frequency_penalty=llm.frequency_penalty,
            presence_penalty=llm.presence_penalty,
            cost_per_1k_input_tokens=llm.cost_per_1k_input_tokens,
            cost_per_1k_output_tokens=llm.cost_per_1k_output_tokens,
            is_active=llm.is_active,
            is_public=llm.is_active,
            created_at=llm.created_at,
            updated_at=llm.updated_at,
        )
        for llm in llms
    ]

    return LLMListResponse(
        items=llm_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/", response_model=LLMResponse)
async def create_llm(
    llm_data: LLMCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(
        get_current_superuser
    ),  # Apenas admins podem criar LLMs
):
    """Criar novo modelo LLM"""

    # Verificar se nome é único
    existing = await db.execute(select(LLM).where(LLM.name == llm_data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um LLM com este nome",
        )

    # Verificar se model_id é único para o provedor
    existing_model = await db.execute(
        select(LLM).where(
            and_(LLM.provider == llm_data.provider, LLM.model_id == llm_data.model_id)
        )
    )
    if existing_model.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um LLM com este model_id para este provedor",
        )

    # Criar LLM
    llm = LLM(
        name=llm_data.name,
        provider=llm_data.provider,
        model_id=llm_data.model_id,
        description=llm_data.description,
        max_tokens=llm_data.max_tokens,
        temperature=llm_data.temperature,
        top_p=llm_data.top_p,
        frequency_penalty=llm_data.frequency_penalty,
        presence_penalty=llm_data.presence_penalty,
        cost_per_1k_input_tokens=llm_data.cost_per_1k_input_tokens,
        cost_per_1k_output_tokens=llm_data.cost_per_1k_output_tokens,
        is_active=llm_data.is_active,
        is_public=llm_data.is_public,
        user_id=current_user.id,
    )

    db.add(llm)
    await db.commit()
    await db.refresh(llm)

    return LLMResponse(
        id=llm.id,
        name=llm.name,
        provider=llm.provider,
        model_id=llm.model_id,
        description=llm.description,
        max_tokens=llm.max_tokens,
        temperature=llm.temperature,
        top_p=llm.top_p,
        frequency_penalty=llm.frequency_penalty,
        presence_penalty=llm.presence_penalty,
        cost_per_1k_input_tokens=llm.cost_per_1k_input_tokens,
        cost_per_1k_output_tokens=llm.cost_per_1k_output_tokens,
        is_active=llm.is_active,
        is_public=llm.is_active,
        created_at=llm.created_at,
        updated_at=llm.updated_at,
    )


@router.get("/{llm_id}", response_model=LLMResponse)
async def get_llm(
    llm_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter LLM por ID"""

    result = await db.execute(select(LLM).where(LLM.id == llm_id))
    llm = result.scalar_one_or_none()

    if not llm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM não encontrado"
        )

    # Verificar acesso
    if (
        not llm.is_active
        and llm.user_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este LLM",
        )

    return LLMResponse(
        id=llm.id,
        name=llm.name,
        provider=llm.provider,
        model_id=llm.model_id,
        description=llm.description,
        max_tokens=llm.max_tokens,
        temperature=llm.temperature,
        top_p=llm.top_p,
        frequency_penalty=llm.frequency_penalty,
        presence_penalty=llm.presence_penalty,
        cost_per_1k_input_tokens=llm.cost_per_1k_input_tokens,
        cost_per_1k_output_tokens=llm.cost_per_1k_output_tokens,
        is_active=llm.is_active,
        is_public=llm.is_active,
        created_at=llm.created_at,
        updated_at=llm.updated_at,
    )


@router.put("/{llm_id}", response_model=LLMResponse)
async def update_llm(
    llm_id: uuid.UUID,
    llm_update: LLMUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),
):
    """Atualizar LLM"""

    result = await db.execute(select(LLM).where(LLM.id == llm_id))
    llm = result.scalar_one_or_none()

    if not llm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM não encontrado"
        )

    # Verificar se nome é único se sendo alterado
    if llm_update.name and llm_update.name != llm.name:
        existing = await db.execute(
            select(LLM).where(and_(LLM.name == llm_update.name, LLM.id != llm_id))
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um LLM com este nome",
            )

    # Atualizar campos
    update_data = llm_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(llm, field, value)

    await db.commit()
    await db.refresh(llm)

    return LLMResponse(
        id=llm.id,
        name=llm.name,
        provider=llm.provider,
        model_id=llm.model_id,
        description=llm.description,
        max_tokens=llm.max_tokens,
        temperature=llm.temperature,
        top_p=llm.top_p,
        frequency_penalty=llm.frequency_penalty,
        presence_penalty=llm.presence_penalty,
        cost_per_1k_input_tokens=llm.cost_per_1k_input_tokens,
        cost_per_1k_output_tokens=llm.cost_per_1k_output_tokens,
        is_active=llm.is_active,
        is_public=llm.is_active,
        created_at=llm.created_at,
        updated_at=llm.updated_at,
    )


@router.delete("/{llm_id}")
async def delete_llm(
    llm_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_superuser),
):
    """Deletar LLM"""

    result = await db.execute(select(LLM).where(LLM.id == llm_id))
    llm = result.scalar_one_or_none()

    if not llm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LLM não encontrado"
        )

    # Verificar se não há conversas ativas usando este LLM
    conversations_count = await db.execute(
        select(func.count(LLMConversation.id)).where(
            and_(LLMConversation.llm_id == llm_id, LLMConversation.status == "active")
        )
    )
    if conversations_count.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar LLM com conversas ativas",
        )

    # Soft delete - desativar
    llm.is_active = False

    await db.commit()

    return {"message": "LLM desativado com sucesso"}


# ENDPOINTS DE CONVERSAS


@router.get("/{llm_id}/conversations", response_model=LLMConversationListResponse)
async def list_llm_conversations(
    llm_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    workspace_id: Optional[uuid.UUID] = Query(
        None, description="Filtrar por workspace"
    ),
):
    """Listar conversas do LLM"""

    # Verificar se LLM existe e é acessível
    llm_result = await db.execute(
        select(LLM).where(
            and_(
                LLM.id == llm_id,
                LLM.tenant_id == current_user.tenant_id,
            )
        )
    )
    llm = llm_result.scalar_one_or_none()
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM não encontrado ou sem acesso",
        )

    # Query conversas
    query = (
        select(LLMConversation)
        .options(selectinload(LLMConversation.workspace))
        .where(
            and_(
                LLMConversation.llm_id == llm_id,
                LLMConversation.user_id == current_user.id,
            )
        )
    )

    conditions = []

    if workspace_id:
        conditions.append(LLMConversation.workspace_id == workspace_id)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(LLMConversation.updated_at.desc())

    result = await db.execute(query)
    conversations = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    conversation_responses = [
        LLMConversationResponse(
            id=conv.id,
            title=conv.title,
            llm_id=conv.llm_id,
            workspace_id=conv.workspace_id,
            user_id=conv.user_id,
            system_prompt=conv.system_prompt,
            temperature=conv.temperature,
            max_tokens=conv.max_tokens,
            tags=conv.tags or [],
            metadata=conv.metadata or {},
            status=conv.status,
            total_messages=conv.total_messages,
            total_tokens_used=conv.total_tokens_used,
            total_cost=conv.total_cost,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            last_message_at=conv.last_message_at,
            llm_name=llm.name,
            workspace_name=conv.workspace.name if conv.workspace else None,
        )
        for conv in conversations
    ]

    return LLMConversationListResponse(
        items=conversation_responses, total=total, page=page, pages=pages, size=size
    )


@router.post("/{llm_id}/conversations", response_model=LLMConversationResponse)
async def create_llm_conversation(
    llm_id: uuid.UUID,
    conversation_data: LLMConversationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Criar nova conversa com LLM"""

    # Verificar se LLM existe e é acessível
    llm_result = await db.execute(
        select(LLM).where(
            and_(
                LLM.id == llm_id,
                LLM.tenant_id == current_user.tenant_id,
            )
        )
    )
    llm = llm_result.scalar_one_or_none()
    if not llm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM não encontrado ou sem acesso",
        )

    # Verificar se workspace existe se especificado
    if conversation_data.workspace_id:
        workspace_result = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.id == conversation_data.workspace_id,
                    or_(
                        Workspace.user_id == current_user.id,
                        Workspace.is_public == True,
                        # TODO: Verificar se é membro
                    ),
                )
            )
        )
        if not workspace_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado ou sem acesso",
            )

    # Criar conversa
    conversation = LLMConversation(
        title=conversation_data.title,
        llm_id=llm_id,
        workspace_id=conversation_data.workspace_id,
        user_id=current_user.id,
        system_prompt=conversation_data.system_prompt,
        temperature=conversation_data.temperature,
        max_tokens=conversation_data.max_tokens,
        tags=conversation_data.tags,
        metadata=conversation_data.metadata,
        status="active",
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return LLMConversationResponse(
        id=conversation.id,
        title=conversation.title,
        llm_id=conversation.llm_id,
        workspace_id=conversation.workspace_id,
        user_id=conversation.user_id,
        system_prompt=conversation.system_prompt,
        temperature=conversation.temperature,
        max_tokens=conversation.max_tokens,
        tags=conversation.tags or [],
        metadata=conversation.metadata or {},
        status=conversation.status,
        total_messages=conversation.total_messages,
        total_tokens_used=conversation.total_tokens_used,
        total_cost=conversation.total_cost,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=conversation.last_message_at,
        llm_name=llm.name,
    )


@router.get(
    "/conversations/{conversation_id}/messages", response_model=LLMMessageListResponse
)
async def list_conversation_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
):
    """Listar mensagens da conversa"""

    # Verificar se conversa existe e pertence ao usuário
    conversation_result = await db.execute(
        select(LLMConversation).where(
            and_(
                LLMConversation.id == conversation_id,
                LLMConversation.user_id == current_user.id,
            )
        )
    )
    conversation = conversation_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada"
        )

    # Query mensagens
    query = (
        select(LLMMessage)
        .where(LLMMessage.conversation_id == conversation_id)
        .order_by(LLMMessage.created_at)
    )

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    messages = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    message_responses = [
        LLMMessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            token_count=msg.token_count,
            cost=msg.cost,
            metadata=msg.metadata or {},
            created_at=msg.created_at,
            finish_reason=msg.finish_reason,
            model_used=msg.model_used,
        )
        for msg in messages
    ]

    return LLMMessageListResponse(
        items=message_responses, total=total, page=page, pages=pages, size=size
    )


@router.post(
    "/conversations/{conversation_id}/messages", response_model=LLMMessageResponse
)
async def create_conversation_message(
    conversation_id: uuid.UUID,
    message_data: LLMMessageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Adicionar mensagem à conversa"""

    # Verificar se conversa existe e pertence ao usuário
    conversation_result = await db.execute(
        select(LLMConversation).where(
            and_(
                LLMConversation.id == conversation_id,
                LLMConversation.user_id == current_user.id,
            )
        )
    )
    conversation = conversation_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada"
        )

    # Criar mensagem
    message = LLMMessage(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        metadata=message_data.metadata,
        token_count=len(message_data.content.split()),  # Estimativa simples
        cost=0.0,  # Será calculado pelo sistema de billing
    )

    db.add(message)

    # Atualizar estatísticas da conversa
    conversation.total_messages += 1
    conversation.last_message_at = message.created_at

    await db.commit()
    await db.refresh(message)

    return LLMMessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        token_count=message.token_count,
        cost=message.cost,
        metadata=message.metadata or {},
        created_at=message.created_at,
        finish_reason=message.finish_reason,
        model_used=message.model_used,
    )

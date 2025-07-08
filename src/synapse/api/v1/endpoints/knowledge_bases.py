"""
Endpoints for managing Knowledge Bases.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.models.user import User
from synapse.database import get_async_db
from synapse.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseList,
    KnowledgeBaseSearch,
    KnowledgeBaseStatistics,
    KnowledgeBaseExport,
    KnowledgeBaseIndexing,
)
from synapse.models import KnowledgeBase, User

router = APIRouter()


@router.post("/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb_in: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new knowledge base."""
    db_kb = KnowledgeBase(**kb_in.model_dump(), tenant_id=current_user.tenant_id)
    db.add(db_kb)
    await db.commit()
    await db.refresh(db_kb)
    return db_kb


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific knowledge base by its ID."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )
    return kb


@router.get("/", response_model=KnowledgeBaseList)
async def list_knowledge_bases(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in title and content"),
):
    """List all knowledge bases for the current tenant."""
    query = select(KnowledgeBase).where(KnowledgeBase.tenant_id == current_user.tenant_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                KnowledgeBase.title.ilike(search_term),
                KnowledgeBase.content.ilike(search_term),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    kbs = result.scalars().all()

    return KnowledgeBaseList(
        items=kbs,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: uuid.UUID,
    kb_in: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing knowledge base."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    db_kb = result.scalar_one_or_none()

    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )

    update_data = kb_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_kb, field, value)

    await db.commit()
    await db.refresh(db_kb)
    return db_kb


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a knowledge base."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    db_kb = result.scalar_one_or_none()

    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )

    await db.delete(db_kb)
    await db.commit()


@router.post("/search", response_model=List[KnowledgeBaseResponse])
async def search_knowledge_bases(
    search_params: KnowledgeBaseSearch,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Advanced search in knowledge bases."""
    query = select(KnowledgeBase).where(KnowledgeBase.tenant_id == current_user.tenant_id)
    
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.where(
            or_(
                KnowledgeBase.title.ilike(search_term),
                KnowledgeBase.content.ilike(search_term),
            )
        )
    
    if search_params.limit:
        query = query.limit(search_params.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{kb_id}/sync", response_model=KnowledgeBaseIndexing)
async def sync_knowledge_base(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Sync knowledge base with external sources."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )

    # Implementar lógica de sincronização aqui
    return KnowledgeBaseIndexing(
        kb_id=kb.kb_id,
        sync_status="completed",
        synced_items=0,
        errors=[]
    )


@router.get("/{kb_id}/stats", response_model=KnowledgeBaseStatistics)
async def get_knowledge_base_stats(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics for a knowledge base."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )

    # Calcular estatísticas
    content_length = len(kb.content) if kb.content else 0
    
    return KnowledgeBaseStatistics(
        kb_id=kb.kb_id,
        total_items=1,  # Simplificado por agora
        total_size_bytes=content_length,
        last_updated=kb.updated_at,
        usage_count=0
    )


@router.get("/{kb_id}/export", response_model=KnowledgeBaseExport)
async def export_knowledge_base(
    kb_id: uuid.UUID,
    format: str = Query("json", description="Export format (json, csv, txt)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Export knowledge base data."""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.kb_id == kb_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    kb = result.scalar_one_or_none()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Knowledge base not found"
        )

    # Gerar dados de exportação baseado no formato
    if format == "json":
        export_data = kb.to_dict() if hasattr(kb, 'to_dict') else {"title": kb.title, "content": kb.content}
    else:
        export_data = {"error": f"Format {format} not supported yet"}

    return KnowledgeBaseExport(
        kb_id=kb.kb_id,
        format=format,
        data=export_data,
        file_size=len(str(export_data))
    )

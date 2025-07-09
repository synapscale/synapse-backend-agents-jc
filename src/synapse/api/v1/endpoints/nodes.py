"""
Nodes endpoints - Simple version with basic functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.models.node import Node, NodeStatus
from synapse.models.user import User

router = APIRouter()

@router.get("/")
async def list_nodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List nodes - basic version
    """
    try:
        # Simple query
        query = select(Node).where(
            Node.tenant_id == current_user.tenant_id
        ).order_by(desc(Node.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        nodes = result.scalars().all()

        # Convert to simple dict response
        node_list = []
        for node in nodes:
            node_list.append({
                "id": str(node.id),
                "name": node.name,
                "description": node.description,
                "category": node.category,
                "status": node.status,
                "is_public": node.is_public,
                "user_id": str(node.user_id),
                "tenant_id": str(node.tenant_id),
                "created_at": node.created_at.isoformat(),
                "updated_at": node.updated_at.isoformat(),
            })

        return {"items": node_list, "total": len(node_list)}

    except Exception as e:
        logger.error(f"Erro ao listar nodes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{node_id}")
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific node
    """
    try:
        # Convert to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node_id format"
            )

        # Query node
        query = select(Node).where(
            Node.id == node_uuid,
            Node.tenant_id == current_user.tenant_id
        )

        result = await db.execute(query)
        node = result.scalar_one_or_none()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node não encontrado"
            )

        return {
            "id": str(node.id),
            "name": node.name,
            "description": node.description,
            "category": node.category,
            "status": node.status,
            "is_public": node.is_public,
            "user_id": str(node.user_id),
            "tenant_id": str(node.tenant_id),
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar node: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

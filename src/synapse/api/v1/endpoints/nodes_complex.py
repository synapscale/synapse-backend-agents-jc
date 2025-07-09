"""
Nodes endpoints - Fixed with proper async/await pattern
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
from synapse.schemas.node import (
    NodeCreate,
    NodeUpdate, 
    NodeResponse,
    NodeListResponse,
    NodeExecutionStatsResponse,
)
from synapse.schemas.base import PaginatedResponse
from synapse.models.node import Node, NodeStatus
from synapse.models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[NodeResponse])
async def list_nodes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_public: Optional[bool] = Query(None, description="Filter by public visibility"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List nodes with filtering and pagination
    """
    try:
        # Base query
        query = select(Node).options(
            selectinload(Node.user)
        ).where(
            Node.tenant_id == current_user.tenant_id
        )

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Node.name.ilike(search_term),
                    Node.description.ilike(search_term)
                )
            )

        if category:
            query = query.where(Node.category == category)

        if status:
            query = query.where(Node.status == status)

        if is_public is not None:
            query = query.where(Node.is_public == is_public)

        if workspace_id:
            try:
                workspace_uuid = uuid.UUID(workspace_id)
                query = query.where(Node.workspace_id == workspace_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid workspace_id format"
                )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and sorting
        query = query.order_by(desc(Node.created_at)).offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        nodes = result.scalars().all()

        # Convert to response
        node_responses = []
        for node in nodes:
            node_dict = {
                "id": node.id,
                "name": node.name,
                "description": node.description,
                "category": node.category,
                "status": node.status,
                "is_public": node.is_public,
                "user_id": node.user_id,
                "tenant_id": node.tenant_id,
                "workspace_id": node.workspace_id,
                "version": node.version,
                "created_at": node.created_at,
                "updated_at": node.updated_at,
            }
            node_responses.append(NodeResponse(**node_dict))

        return PaginatedResponse(
            items=node_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar nodes: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_data: NodeCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new node
    """
    try:
        # Create node
        new_node = Node(
            name=node_data.name,
            description=node_data.description,
            category=node_data.category,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            workspace_id=node_data.workspace_id,
            is_public=node_data.is_public,
            version=node_data.version or "1.0.0",
            status="active"
        )

        db.add(new_node)
        await db.commit()
        await db.refresh(new_node)

        # Convert to response
        node_dict = {
            "id": new_node.id,
            "name": new_node.name,
            "description": new_node.description,
            "category": new_node.category,
            "status": new_node.status,
            "is_public": new_node.is_public,
            "user_id": new_node.user_id,
            "tenant_id": new_node.tenant_id,
            "workspace_id": new_node.workspace_id,
            "version": new_node.version,
            "created_at": new_node.created_at,
            "updated_at": new_node.updated_at,
        }

        return NodeResponse(**node_dict)

    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao criar node: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific node by ID
    """
    try:
        # Convert string to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node_id format"
            )

        # Query node
        query = select(Node).options(
            selectinload(Node.user)
        ).where(
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

        # Convert to response
        node_dict = {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "category": node.category,
            "status": node.status,
            "is_public": node.is_public,
            "user_id": node.user_id,
            "tenant_id": node.tenant_id,
            "workspace_id": node.workspace_id,
            "version": node.version,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
        }

        return NodeResponse(**node_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar node: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    node_update: NodeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a specific node
    """
    try:
        # Convert string to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node_id format"
            )

        # Get node
        query = select(Node).where(
            Node.id == node_uuid,
            Node.tenant_id == current_user.tenant_id,
            Node.user_id == current_user.id  # Only owner can update
        )

        result = await db.execute(query)
        node = result.scalar_one_or_none()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node não encontrado"
            )

        # Update fields
        update_data = node_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)

        await db.commit()
        await db.refresh(node)

        # Convert to response
        node_dict = {
            "id": node.id,
            "name": node.name,
            "description": node.description,
            "category": node.category,
            "status": node.status,
            "is_public": node.is_public,
            "user_id": node.user_id,
            "tenant_id": node.tenant_id,
            "workspace_id": node.workspace_id,
            "version": node.version,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
        }

        return NodeResponse(**node_dict)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao atualizar node: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a specific node
    """
    try:
        # Convert string to UUID
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node_id format"
            )

        # Get node
        query = select(Node).where(
            Node.id == node_uuid,
            Node.tenant_id == current_user.tenant_id,
            Node.user_id == current_user.id  # Only owner can delete
        )

        result = await db.execute(query)
        node = result.scalar_one_or_none()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node não encontrado"
            )

        # Soft delete
        node.status = "archived"

        await db.commit()

        return

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao deletar node: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

"""
Nodes endpoints with comprehensive CRUD operations and database integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from synapse.api.deps import get_current_active_user, get_db
from synapse.schemas.node import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    NodeListResponse,
    NodeExecutionStatsResponse,
)
from synapse.schemas.base import PaginatedResponse
from synapse.models.node import Node, NodeStatus
from synapse.models.node_execution import NodeExecution
from synapse.models.user import User
from synapse.models.workspace import Workspace

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NodeResponse])
async def list_nodes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    # REMOVED: node_type filter (type field does not exist in database)
    status: Optional[NodeStatus] = Query(None, description="Filter by status"),
    is_public: Optional[bool] = Query(None, description="Filter by public visibility"),
    workspace_id: Optional[str] = Query(None, description="Filter by workspace"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List nodes with comprehensive filtering, search, and pagination
    """
    try:
        # Base query with relationships
        query = db.query(Node).options(
            joinedload(Node.user),
            joinedload(Node.workspace)
        )

        # Apply tenant filtering
        query = query.filter(Node.tenant_id == current_user.tenant_id)

        # Apply workspace filtering if specified
        if workspace_id:
            try:
                workspace_uuid = uuid.UUID(workspace_id)
                query = query.filter(Node.workspace_id == workspace_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid workspace_id format"
                )

        # Apply text search
        if search:
            search_filter = or_(
                Node.name.ilike(f"%{search}%"),
                Node.description.ilike(f"%{search}%"),
                Node.category.ilike(f"%{search}%"),
                Node.documentation.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Apply filters
        if category:
            query = query.filter(Node.category.ilike(f"%{category}%"))
        
        # REMOVED: node_type filter (type field does not exist in database)
        
        if status:
            query = query.filter(Node.status == status)
        
        if is_public is not None:
            query = query.filter(Node.is_public == is_public)
        
        if min_rating is not None:
            query = query.filter(Node.rating_average >= min_rating)

        # Apply access control - users can see public nodes or their own nodes
        access_filter = or_(
            Node.is_public == True,
            Node.user_id == current_user.id
        )
        query = query.filter(access_filter)

        # Apply sorting
        sort_column = getattr(Node, sort_by, Node.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count for pagination
        total = query.count()

        # Apply pagination
        nodes = query.offset(skip).limit(limit).all()

        # Convert to response format
        node_responses = []
        for node in nodes:
            node_data = NodeResponse.from_orm(node)
            node_responses.append(node_data)

        return PaginatedResponse(
            items=node_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing nodes: {str(e)}"
        )


@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_data: NodeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new node
    """
    try:
        # Validate workspace access
        if node_data.workspace_id:
            workspace = db.query(Workspace).filter(
                and_(
                    Workspace.id == node_data.workspace_id,
                    Workspace.tenant_id == current_user.tenant_id
                )
            ).first()
            if not workspace:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workspace not found or access denied"
                )

        # Create new node
        node = Node(
            id=uuid.uuid4(),
            name=node_data.name,
            category=node_data.category,
            description=node_data.description,
            version=node_data.version or "1.0.0",
            definition=node_data.definition,
            code_template=node_data.code_template,
            input_schema=node_data.input_schema,
            output_schema=node_data.output_schema,
            parameters_schema=node_data.parameters_schema,
            icon=node_data.icon,
            color=node_data.color,
            documentation=node_data.documentation,
            examples=node_data.examples,
            timeout_seconds=node_data.timeout_seconds or 300,
            retry_count=node_data.retry_count or 0,
            is_public=node_data.is_public or False,
            user_id=current_user.id,
            workspace_id=node_data.workspace_id,
            tenant_id=current_user.tenant_id,
            status="active",  # Use string status as per database default
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(node)
        db.commit()
        db.refresh(node)

        return NodeResponse.from_orm(node)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating node: {str(e)}"
        )


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific node by ID
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Query node with relationships
        node = db.query(Node).options(
            joinedload(Node.user),
            joinedload(Node.workspace)
        ).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )

        # Check access permissions
        if not node.is_public and node.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this node"
            )

        # Increment usage count
        node.usage_count = (node.usage_count or 0) + 1
        node.updated_at = datetime.utcnow()
        db.commit()

        return NodeResponse.from_orm(node)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving node: {str(e)}"
        )


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    node_update: NodeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a specific node
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Find node
        node = db.query(Node).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id,
                Node.user_id == current_user.id  # Only owner can update
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found or access denied"
            )

        # Update fields
        update_data = node_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(node, field):
                setattr(node, field, value)

        node.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(node)

        return NodeResponse.from_orm(node)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating node: {str(e)}"
        )


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a specific node
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Find node
        node = db.query(Node).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id,
                Node.user_id == current_user.id  # Only owner can delete
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found or access denied"
            )

        # Soft delete by setting status to DELETED
        node.status = NodeStatus.DELETED
        node.updated_at = datetime.utcnow()
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting node: {str(e)}"
        )


@router.get("/{node_id}/executions", response_model=PaginatedResponse[Dict[str, Any]])
async def get_node_executions(
    node_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by execution status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get execution history for a specific node
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Verify node exists and user has access
        node = db.query(Node).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )

        # Check access permissions
        if not node.is_public and node.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this node"
            )

        # Query executions
        query = db.query(NodeExecution).filter(
            and_(
                NodeExecution.node_id == node_uuid,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        )

        if status:
            # Note: This assumes NodeExecution has a status field
            # You may need to adjust based on actual field name
            query = query.filter(NodeExecution.status == status)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        executions = query.order_by(desc(NodeExecution.created_at)).offset(skip).limit(limit).all()

        # Convert to response format
        execution_data = []
        for execution in executions:
            execution_dict = {
                "id": execution.id,
                "execution_id": execution.execution_id,
                "workflow_execution_id": execution.workflow_execution_id,
                "node_key": execution.node_key,
                "node_type": execution.node_type,
                "node_name": execution.node_name,
                "execution_order": execution.execution_order,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "duration_ms": execution.duration_ms,
                "retry_count": execution.retry_count,
                "error_message": execution.error_message,
                "created_at": execution.created_at,
                "updated_at": execution.updated_at
            }
            execution_data.append(execution_dict)

        return PaginatedResponse(
            items=execution_data,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving node executions: {str(e)}"
        )


@router.get("/{node_id}/stats", response_model=NodeExecutionStatsResponse)
async def get_node_stats(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get execution statistics for a specific node
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Verify node exists and user has access
        node = db.query(Node).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )

        # Check access permissions
        if not node.is_public and node.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this node"
            )

        # Get execution statistics
        total_executions = db.query(func.count(NodeExecution.id)).filter(
            and_(
                NodeExecution.node_id == node_uuid,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        ).scalar() or 0

        avg_duration = db.query(func.avg(NodeExecution.duration_ms)).filter(
            and_(
                NodeExecution.node_id == node_uuid,
                NodeExecution.tenant_id == current_user.tenant_id,
                NodeExecution.duration_ms.isnot(None)
            )
        ).scalar() or 0

        total_retries = db.query(func.sum(NodeExecution.retry_count)).filter(
            and_(
                NodeExecution.node_id == node_uuid,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        ).scalar() or 0

        failed_executions = db.query(func.count(NodeExecution.id)).filter(
            and_(
                NodeExecution.node_id == node_uuid,
                NodeExecution.tenant_id == current_user.tenant_id,
                NodeExecution.error_message.isnot(None)
            )
        ).scalar() or 0

        success_rate = 0.0
        if total_executions > 0:
            success_rate = ((total_executions - failed_executions) / total_executions) * 100

        return NodeExecutionStatsResponse(
            node_id=str(node_uuid),
            total_executions=total_executions,
            failed_executions=failed_executions,
            success_rate=round(success_rate, 2),
            avg_duration_ms=round(float(avg_duration), 2) if avg_duration else 0.0,
            total_retries=total_retries,
            usage_count=node.usage_count or 0,
            downloads_count=node.downloads_count or 0,
            rating_average=node.rating_average,
            rating_count=node.rating_count or 0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving node statistics: {str(e)}"
        )


@router.post("/{node_id}/rate")
async def rate_node(
    node_id: str,
    rating: float = Query(..., ge=1.0, le=5.0, description="Rating from 1 to 5"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Rate a node (1-5 stars)
    """
    try:
        # Validate UUID format
        try:
            node_uuid = uuid.UUID(node_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )

        # Find node
        node = db.query(Node).filter(
            and_(
                Node.id == node_uuid,
                Node.tenant_id == current_user.tenant_id
            )
        ).first()

        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )

        # Check access permissions
        if not node.is_public and node.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this node"
            )

        # Update rating using the model method
        node.update_rating(rating)
        node.updated_at = datetime.utcnow()
        db.commit()

        return {
            "message": "Rating updated successfully",
            "new_average": node.rating_average,
            "total_ratings": node.rating_count
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rating node: {str(e)}"
        )

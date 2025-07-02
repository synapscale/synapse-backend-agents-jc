"""
Executions endpoints with comprehensive workflow and node execution management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime

from synapse.api.deps import get_current_active_user, get_db
from synapse.schemas.workflow_execution import (
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
    WorkflowExecutionResponse,
    WorkflowExecutionWithNodesResponse,
    NodeExecutionResponse,
    ExecutionMetricsResponse,
)
from synapse.schemas.base import PaginatedResponse
from synapse.models.workflow_execution import WorkflowExecution, ExecutionStatus
from synapse.models.node_execution import NodeExecution
from synapse.models.workflow import Workflow
from synapse.models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[WorkflowExecutionResponse])
async def list_executions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    status: Optional[ExecutionStatus] = Query(None, description="Filter by execution status"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    start_date: Optional[datetime] = Query(None, description="Filter executions started after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter executions started before this date"),
    min_progress: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum progress percentage"),
    has_errors: Optional[bool] = Query(None, description="Filter executions with/without errors"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List workflow executions with comprehensive filtering, search, and pagination
    """
    try:
        # Base query with relationships
        query = db.query(WorkflowExecution).options(
            joinedload(WorkflowExecution.workflow),
            joinedload(WorkflowExecution.user)
        )

        # Apply tenant filtering
        query = query.filter(WorkflowExecution.tenant_id == current_user.tenant_id)

        # Apply filters
        if status:
            query = query.filter(WorkflowExecution.status == status)
        
        if workflow_id:
            try:
                workflow_uuid = uuid.UUID(workflow_id)
                query = query.filter(WorkflowExecution.workflow_id == workflow_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid workflow_id format"
                )
        
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id)
                query = query.filter(WorkflowExecution.user_id == user_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id format"
                )
        
        if priority:
            query = query.filter(WorkflowExecution.priority == priority)
        
        if start_date:
            query = query.filter(WorkflowExecution.started_at >= start_date)
        
        if end_date:
            query = query.filter(WorkflowExecution.started_at <= end_date)
        
        if min_progress is not None:
            query = query.filter(WorkflowExecution.progress_percentage >= min_progress)
        
        if has_errors is not None:
            if has_errors:
                query = query.filter(WorkflowExecution.error_message.isnot(None))
            else:
                query = query.filter(WorkflowExecution.error_message.is_(None))

        # Apply sorting
        sort_column = getattr(WorkflowExecution, sort_by, WorkflowExecution.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count for pagination
        total = query.count()

        # Apply pagination
        executions = query.offset(skip).limit(limit).all()

        # Convert to response format
        execution_responses = []
        for execution in executions:
            execution_data = WorkflowExecutionResponse.from_orm(execution)
            execution_responses.append(execution_data)

        return PaginatedResponse(
            items=execution_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing executions: {str(e)}"
        )


@router.post("/", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_data: WorkflowExecutionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create and start a new workflow execution
    """
    try:
        # Validate workflow exists and user has access
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == execution_data.workflow_id,
                Workflow.tenant_id == current_user.tenant_id
            )
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found or access denied"
            )

        # Generate execution ID
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"

        # Create new execution
        execution = WorkflowExecution(
            id=uuid.uuid4(),
            execution_id=execution_id,
            workflow_id=execution_data.workflow_id,
            user_id=current_user.id,
            status=ExecutionStatus.PENDING,
            priority=execution_data.priority or "medium",
            input_data=execution_data.input_data or {},
            context_data=execution_data.context_data or {},
            variables=execution_data.variables or {},
            total_nodes=0,  # Will be updated when workflow is parsed
            completed_nodes=0,
            failed_nodes=0,
            progress_percentage=0.0,
            max_retries=execution_data.max_retries or 3,
            auto_retry=execution_data.auto_retry or False,
            notify_on_completion=execution_data.notify_on_completion or False,
            notify_on_failure=execution_data.notify_on_failure or True,
            tags=execution_data.tags,
            metadata=execution_data.metadata or {},
            tenant_id=current_user.tenant_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        # TODO: Integrate with execution service to start the workflow
        # This would typically enqueue the execution for processing
        
        return WorkflowExecutionResponse.from_orm(execution)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating execution: {str(e)}"
        )


@router.get("/{execution_id}", response_model=WorkflowExecutionWithNodesResponse)
async def get_execution(
    execution_id: str,
    include_nodes: bool = Query(True, description="Include node executions in response"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific workflow execution by ID with optional node executions
    """
    try:
        # Try to parse as UUID first, then check execution_id field
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).options(
                joinedload(WorkflowExecution.workflow),
                joinedload(WorkflowExecution.user)
            ).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            # If not a valid UUID, search by execution_id field
            execution = db.query(WorkflowExecution).options(
                joinedload(WorkflowExecution.workflow),
                joinedload(WorkflowExecution.user)
            ).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Get node executions if requested
        node_executions = []
        if include_nodes:
            node_executions = db.query(NodeExecution).filter(
                and_(
                    NodeExecution.workflow_execution_id == execution.id,
                    NodeExecution.tenant_id == current_user.tenant_id
                )
            ).order_by(NodeExecution.execution_order).all()

        # Convert to response format
        execution_response = WorkflowExecutionResponse.from_orm(execution)
        
        if include_nodes:
            node_responses = [NodeExecutionResponse.from_orm(node) for node in node_executions]
            return WorkflowExecutionWithNodesResponse(
                **execution_response.dict(),
                node_executions=node_responses
            )
        else:
            return WorkflowExecutionWithNodesResponse(
                **execution_response.dict(),
                node_executions=[]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving execution: {str(e)}"
        )


@router.put("/{execution_id}/status")
async def update_execution_status(
    execution_id: str,
    new_status: ExecutionStatus = Query(..., description="New execution status"),
    error_message: Optional[str] = Query(None, description="Error message if status is failed"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update the status of a workflow execution
    """
    try:
        # Find execution
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Update status and related fields
        old_status = execution.status
        execution.status = new_status
        execution.updated_at = datetime.utcnow()

        if new_status == ExecutionStatus.RUNNING and old_status == ExecutionStatus.PENDING:
            execution.started_at = datetime.utcnow()
        elif new_status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
            execution.completed_at = datetime.utcnow()
            if execution.started_at:
                duration = execution.completed_at - execution.started_at
                execution.actual_duration = int(duration.total_seconds())

        if new_status == ExecutionStatus.FAILED and error_message:
            execution.error_message = error_message

        if new_status == ExecutionStatus.COMPLETED:
            execution.progress_percentage = 100.0

        db.commit()

        return {
            "message": f"Execution status updated to {new_status}",
            "execution_id": execution.execution_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_at": execution.updated_at
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating execution status: {str(e)}"
        )


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_execution(
    execution_id: str,
    force: bool = Query(False, description="Force cancel even if already completed"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a workflow execution
    """
    try:
        # Find execution
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Check if cancellation is allowed
        if not force and execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel execution with status {execution.status}"
            )

        # Update status to cancelled
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        execution.updated_at = datetime.utcnow()
        
        if execution.started_at:
            duration = execution.completed_at - execution.started_at
            execution.actual_duration = int(duration.total_seconds())

        db.commit()

        # TODO: Integrate with execution service to actually stop the workflow

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling execution: {str(e)}"
        )


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    node_id: Optional[str] = Query(None, description="Filter logs by specific node"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get execution logs for a workflow execution
    """
    try:
        # Find execution
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Get workflow execution logs
        workflow_logs = []
        if execution.execution_log:
            workflow_logs.append({
                "timestamp": execution.updated_at,
                "level": "INFO",
                "source": "workflow",
                "message": execution.execution_log
            })

        # Get node execution logs
        node_query = db.query(NodeExecution).filter(
            and_(
                NodeExecution.workflow_execution_id == execution.id,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        )

        if node_id:
            try:
                node_uuid = uuid.UUID(node_id)
                node_query = node_query.filter(NodeExecution.node_id == node_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid node_id format"
                )

        node_executions = node_query.order_by(NodeExecution.execution_order).all()

        node_logs = []
        for node_exec in node_executions:
            if node_exec.execution_log:
                log_entry = {
                    "timestamp": node_exec.updated_at,
                    "level": "ERROR" if node_exec.error_message else "INFO",
                    "source": f"node_{node_exec.node_key}",
                    "node_id": str(node_exec.node_id),
                    "node_name": node_exec.node_name,
                    "message": node_exec.execution_log
                }
                
                if node_exec.error_message:
                    log_entry["error"] = node_exec.error_message
                
                node_logs.append(log_entry)

        # Combine and sort logs by timestamp
        all_logs = workflow_logs + node_logs
        all_logs.sort(key=lambda x: x["timestamp"] or datetime.min)

        # Apply log level filter
        if log_level:
            all_logs = [log for log in all_logs if log["level"].upper() == log_level.upper()]

        return {
            "execution_id": execution.execution_id,
            "execution_status": execution.status,
            "total_logs": len(all_logs),
            "logs": all_logs
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving execution logs: {str(e)}"
        )


@router.get("/{execution_id}/metrics", response_model=ExecutionMetricsResponse)
async def get_execution_metrics(
    execution_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get execution metrics and statistics
    """
    try:
        # Find execution
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Get node execution metrics
        node_executions = db.query(NodeExecution).filter(
            and_(
                NodeExecution.workflow_execution_id == execution.id,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        ).all()

        # Calculate metrics
        total_duration = execution.actual_duration or 0
        avg_node_duration = 0
        max_node_duration = 0
        min_node_duration = 0
        total_retries = execution.retry_count or 0
        
        if node_executions:
            durations = [ne.duration_ms for ne in node_executions if ne.duration_ms]
            if durations:
                avg_node_duration = sum(durations) / len(durations)
                max_node_duration = max(durations)
                min_node_duration = min(durations)
            
            total_retries += sum(ne.retry_count or 0 for ne in node_executions)

        # Node breakdown
        nodes_by_status = {}
        for node_exec in node_executions:
            if node_exec.error_message:
                status_key = "failed"
            elif node_exec.completed_at:
                status_key = "completed"
            elif node_exec.started_at:
                status_key = "running"
            else:
                status_key = "pending"
            
            nodes_by_status[status_key] = nodes_by_status.get(status_key, 0) + 1

        return ExecutionMetricsResponse(
            execution_id=execution.execution_id,
            workflow_id=str(execution.workflow_id),
            status=execution.status,
            total_duration_seconds=total_duration,
            progress_percentage=execution.progress_percentage or 0.0,
            total_nodes=execution.total_nodes or 0,
            completed_nodes=execution.completed_nodes or 0,
            failed_nodes=execution.failed_nodes or 0,
            pending_nodes=(execution.total_nodes or 0) - (execution.completed_nodes or 0) - (execution.failed_nodes or 0),
            total_retries=total_retries,
            avg_node_duration_ms=round(avg_node_duration, 2),
            max_node_duration_ms=max_node_duration,
            min_node_duration_ms=min_node_duration,
            nodes_by_status=nodes_by_status,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            created_at=execution.created_at,
            updated_at=execution.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving execution metrics: {str(e)}"
        )


@router.get("/{execution_id}/nodes", response_model=PaginatedResponse[NodeExecutionResponse])
async def get_execution_nodes(
    execution_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    node_status: Optional[str] = Query(None, description="Filter by node execution status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get node executions for a specific workflow execution
    """
    try:
        # Find execution
        execution = None
        
        try:
            execution_uuid = uuid.UUID(execution_id)
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.id == execution_uuid,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()
        except ValueError:
            execution = db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.execution_id == execution_id,
                    WorkflowExecution.tenant_id == current_user.tenant_id
                )
            ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Query node executions
        query = db.query(NodeExecution).filter(
            and_(
                NodeExecution.workflow_execution_id == execution.id,
                NodeExecution.tenant_id == current_user.tenant_id
            )
        )

        # Apply status filter
        if node_status:
            if node_status.lower() == "failed":
                query = query.filter(NodeExecution.error_message.isnot(None))
            elif node_status.lower() == "completed":
                query = query.filter(
                    and_(
                        NodeExecution.completed_at.isnot(None),
                        NodeExecution.error_message.is_(None)
                    )
                )
            elif node_status.lower() == "running":
                query = query.filter(
                    and_(
                        NodeExecution.started_at.isnot(None),
                        NodeExecution.completed_at.is_(None)
                    )
                )
            elif node_status.lower() == "pending":
                query = query.filter(NodeExecution.started_at.is_(None))

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        node_executions = query.order_by(NodeExecution.execution_order).offset(skip).limit(limit).all()

        # Convert to response format
        node_responses = [NodeExecutionResponse.from_orm(node) for node in node_executions]

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving execution nodes: {str(e)}"
        )


# Legacy functions for backward compatibility
async def initialize_execution_service(websocket_manager):
    """Initialize execution service (placeholder implementation)"""
    # TODO: Implement actual execution service initialization
    pass


async def shutdown_execution_service():
    """Shutdown execution service (placeholder implementation)"""
    # TODO: Implement actual execution service shutdown
    pass

"""
Workflows endpoints - Fixed with proper async/await
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func, desc, select
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from synapse.api.deps import get_current_active_user
from synapse.models.workflow import Workflow
from synapse.models.workflow_execution import WorkflowExecution
from synapse.models.user import User
from synapse.models.workspace import Workspace
from synapse.models.workspace_member import WorkspaceMember
from synapse.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowExecutionCreate,
    WorkflowExecutionResponse
)
from synapse.exceptions import WorkflowError
from synapse.database import get_async_db

router = APIRouter()

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    search: Optional[str] = Query(None, description="Search in name or description"),
    workspace_id: Optional[uuid.UUID] = Query(None, description="Filter by workspace"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Listar workflows do usuário com filtros e paginação"""
    try:
        # Build base query
        query = select(Workflow).where(
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                Workflow.is_public == True
            )
        ).options(
            selectinload(Workflow.workspace)
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Workflow.name.ilike(search_term),
                    Workflow.description.ilike(search_term)
                )
            )
        
        if workspace_id:
            query = query.where(Workflow.workspace_id == workspace_id)
            
        if status:
            query = query.where(Workflow.status == status)
            
        if is_active is not None:
            query = query.where(Workflow.is_active == is_active)
        
        # Order by last update
        query = query.order_by(desc(Workflow.updated_at))
        
        # Pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * size
        workflows_result = await db.execute(query.offset(offset).limit(size))
        workflows = workflows_result.scalars().all()
        
        # Convert to response
        response_workflows = []
        for workflow in workflows:
            workflow_dict = {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "category": workflow.category,
                "tags": workflow.tags or [],
                "is_public": workflow.is_public,
                "definition": workflow.definition or {},
                "status": workflow.status,
                "is_active": workflow.is_active,
                "user_id": workflow.user_id,
                "tenant_id": workflow.tenant_id,
                "workspace_id": workflow.workspace_id,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at
            }
            response_workflows.append(WorkflowResponse(**workflow_dict))
        
        return response_workflows
        
    except Exception as e:
        logger.error(f"Erro ao listar workflows: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Criar workflow"""
    try:
        # Create workflow
        new_workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            definition=workflow_data.definition,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            is_active=True
        )
        
        db.add(new_workflow)
        await db.commit()
        await db.refresh(new_workflow)
        
        # Convert to response
        workflow_dict = {
            "id": new_workflow.id,
            "name": new_workflow.name,
            "description": new_workflow.description,
            "category": new_workflow.category,
            "tags": new_workflow.tags,
            "is_public": new_workflow.is_public,
            "definition": new_workflow.definition,
            "status": new_workflow.status,
            "is_active": new_workflow.is_active,
            "user_id": new_workflow.user_id,
            "tenant_id": new_workflow.tenant_id,
            "workspace_id": new_workflow.workspace_id,
            "created_at": new_workflow.created_at,
            "updated_at": new_workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao criar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Obter workflow específico"""
    try:
        query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                Workflow.is_public == True
            )
        ).options(selectinload(Workflow.workspace))
        
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "category": workflow.category,
            "tags": workflow.tags or [],
            "is_public": workflow.is_public,
            "definition": workflow.definition or {},
            "status": workflow.status,
            "is_active": workflow.is_active,
            "user_id": workflow.user_id,
            "tenant_id": workflow.tenant_id,
            "workspace_id": workflow.workspace_id,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: uuid.UUID,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Atualizar workflow"""
    try:
        query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            Workflow.user_id == current_user.id  # Only owner can update
        )
        
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Update fields
        update_data = workflow_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        await db.commit()
        await db.refresh(workflow)
        
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "category": workflow.category,
            "tags": workflow.tags or [],
            "is_public": workflow.is_public,
            "definition": workflow.definition or {},
            "status": workflow.status,
            "is_active": workflow.is_active,
            "user_id": workflow.user_id,
            "tenant_id": workflow.tenant_id,
            "workspace_id": workflow.workspace_id,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao atualizar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Deletar workflow"""
    try:
        query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            Workflow.user_id == current_user.id  # Only owner can delete
        )
        
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Soft delete - set status to archived
        workflow.status = "archived"
        workflow.is_active = False
        
        await db.commit()
        
        return {"message": "Workflow deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao deletar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: uuid.UUID,
    execution_data: WorkflowExecutionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Executar workflow"""
    try:
        # Get workflow
        query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                Workflow.is_public == True
            ),
            Workflow.is_active == True
        )
        
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Create execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            input_data=execution_data.input_data or {},
            status="running",
            started_at=datetime.utcnow()
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Return execution info
        execution_dict = {
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "workflow_name": workflow.name,
            "user_id": execution.user_id,
            "tenant_id": execution.tenant_id,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "status": execution.status,
            "progress": 0,
            "error_message": execution.error_message,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "created_at": execution.created_at,
            "updated_at": execution.updated_at
        }
        
        return WorkflowExecutionResponse(**execution_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao executar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100)
):
    """Listar execuções do workflow"""
    try:
        # Verify workflow access
        workflow_query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                Workflow.is_public == True
            )
        )
        
        workflow_result = await db.execute(workflow_query)
        workflow = workflow_result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Get executions
        query = select(WorkflowExecution).where(
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.tenant_id == current_user.tenant_id
        ).order_by(desc(WorkflowExecution.created_at))
        
        offset = (page - 1) * size
        executions_result = await db.execute(query.offset(offset).limit(size))
        executions = executions_result.scalars().all()
        
        # Convert to response
        response_executions = []
        for execution in executions:
            execution_dict = {
                "id": execution.id,
                "workflow_id": execution.workflow_id,
                "workflow_name": workflow.name,
                "user_id": execution.user_id,
                "tenant_id": execution.tenant_id,
                "input_data": execution.input_data or {},
                "output_data": execution.output_data or {},
                "status": execution.status,
                "progress": getattr(execution, 'progress', 0),
                "error_message": execution.error_message,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "created_at": execution.created_at,
                "updated_at": execution.updated_at
            }
            response_executions.append(WorkflowExecutionResponse(**execution_dict))
        
        return response_executions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar execuções: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Duplicar workflow"""
    try:
        # Get original workflow
        query = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                Workflow.is_public == True
            )
        )
        
        result = await db.execute(query)
        original_workflow = result.scalar_one_or_none()
        
        if not original_workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Create duplicate
        duplicate_workflow = Workflow(
            name=f"{original_workflow.name} (Copy)",
            description=original_workflow.description,
            category=original_workflow.category,
            tags=original_workflow.tags,
            is_public=False,  # Duplicates are private by default
            definition=original_workflow.definition,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            workspace_id=None,
            status="draft",
            is_active=False
        )
        
        db.add(duplicate_workflow)
        await db.commit()
        await db.refresh(duplicate_workflow)
        
        workflow_dict = {
            "id": duplicate_workflow.id,
            "name": duplicate_workflow.name,
            "description": duplicate_workflow.description,
            "category": duplicate_workflow.category,
            "tags": duplicate_workflow.tags or [],
            "is_public": duplicate_workflow.is_public,
            "definition": duplicate_workflow.definition or {},
            "status": duplicate_workflow.status,
            "is_active": duplicate_workflow.is_active,
            "user_id": duplicate_workflow.user_id,
            "tenant_id": duplicate_workflow.tenant_id,
            "workspace_id": duplicate_workflow.workspace_id,
            "created_at": duplicate_workflow.created_at,
            "updated_at": duplicate_workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao duplicar workflow: {str(e)}", extra={"error_type": type(e).__name__})
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

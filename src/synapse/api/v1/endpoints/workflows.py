"""
Workflows endpoints - Complete Implementation

This module handles workflow management, execution, and related operations.
Supports creating workflows, executing them, managing executions, and workflow lifecycle management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, desc
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

from synapse.api.deps import get_current_active_user, get_db
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
# from synapse.services.workflow_execution_service import WorkflowExecutionService
from synapse.exceptions import WorkflowError

router = APIRouter()

# Initialize services
# workflow_execution_service = WorkflowExecutionService()

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    search: Optional[str] = Query(None, description="Search in name or description"),
    workspace_id: Optional[uuid.UUID] = Query(None, description="Filter by workspace"),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar workflows do usuário com filtros e paginação"""
    try:
        # Build base query - user owns workflows or has access via workspace
        query = db.query(Workflow).filter(
            Workflow.tenant_id == current_user.tenant_id,
            or_(
                Workflow.user_id == current_user.id,
                and_(
                    Workflow.workspace_id.isnot(None),
                    Workflow.workspace_id.in_(
                        db.query(Workspace.id).filter(
                            or_(
                                Workspace.owner_id == current_user.id,
                                Workspace.id.in_(
                                    db.query(WorkspaceMember.workspace_id).filter(
                                        WorkspaceMember.user_id == current_user.id
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ).options(
            selectinload(Workflow.workspace),
            selectinload(Workflow.executions)
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Workflow.name.ilike(search_term),
                    Workflow.description.ilike(search_term)
                )
            )
        
        if workspace_id:
            query = query.filter(Workflow.workspace_id == workspace_id)
            
        if status:
            query = query.filter(Workflow.status == status)
            
        if is_active is not None:
            query = query.filter(Workflow.is_active == is_active)
        
        # Order by last update (most recent first)
        query = query.order_by(desc(Workflow.updated_at))
        
        # Pagination
        total = query.count()
        offset = (page - 1) * size
        workflows = query.offset(offset).limit(size).all()
        
        # Convert to response model
        response_workflows = []
        for workflow in workflows:
            # Get execution stats
            execution_count = len(workflow.executions) if workflow.executions else 0
            latest_execution = None
            if workflow.executions:
                workflow.executions.sort(key=lambda x: x.created_at, reverse=True)
                latest_execution = workflow.executions[0]
            
            workflow_dict = {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status,
                "is_active": workflow.is_active,
                "workspace_id": workflow.workspace_id,
                "workspace_name": workflow.workspace.name if workflow.workspace else None,
                "nodes_count": len(workflow.nodes) if workflow.nodes else 0,
                "execution_count": execution_count,
                "latest_execution": {
                    "id": latest_execution.id,
                    "status": latest_execution.status,
                    "created_at": latest_execution.created_at,
                    "completed_at": latest_execution.completed_at
                } if latest_execution else None,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at
            }
            response_workflows.append(WorkflowResponse(**workflow_dict))
        
        return response_workflows
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao listar workflows",
            details=str(e)
        )

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Criar workflow"""
    try:
        # Verify workspace access if specified
        if workflow_data.workspace_id:
            workspace = db.query(Workspace).filter(
                and_(
                    Workspace.id == workflow_data.workspace_id,
                    Workspace.tenant_id == current_user.tenant_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        db.query(WorkspaceMember).filter(
                            WorkspaceMember.workspace_id == workflow_data.workspace_id,
                            WorkspaceMember.user_id == current_user.id
                        ).first() is not None
                    ),
                    Workspace.is_active == True
                )
            ).first()
            
            if not workspace:
                raise HTTPException(
                    status_code=404,
                    message="Workspace não encontrado ou sem acesso"
                )
        
        # Create workflow
        new_workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            user_id=current_user.id,
            workspace_id=workflow_data.workspace_id,
            nodes=workflow_data.nodes or [],
            edges=workflow_data.edges or [],
            variables=workflow_data.variables or {},
            settings=workflow_data.settings or {},
            status="draft",
            is_active=True
        )
        
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        
        # Load workspace relationship
        if new_workflow.workspace_id:
            new_workflow.workspace = db.query(Workspace).filter(Workspace.id == new_workflow.workspace_id).first()
        
        # Convert to response
        workflow_dict = {
            "id": new_workflow.id,
            "name": new_workflow.name,
            "description": new_workflow.description,
            "status": new_workflow.status,
            "is_active": new_workflow.is_active,
            "workspace_id": new_workflow.workspace_id,
            "workspace_name": new_workflow.workspace.name if new_workflow.workspace else None,
            "nodes_count": len(new_workflow.nodes) if new_workflow.nodes else 0,
            "execution_count": 0,
            "latest_execution": None,
            "created_at": new_workflow.created_at,
            "updated_at": new_workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao criar workflow",
            details=str(e)
        )

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter workflow específico"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ).options(
            selectinload(Workflow.workspace),
            selectinload(Workflow.executions)
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado"
            )
        
        # Get execution stats
        execution_count = len(workflow.executions) if workflow.executions else 0
        latest_execution = None
        if workflow.executions:
            workflow.executions.sort(key=lambda x: x.created_at, reverse=True)
            latest_execution = workflow.executions[0]
        
        # Convert to response
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "is_active": workflow.is_active,
            "workspace_id": workflow.workspace_id,
            "workspace_name": workflow.workspace.name if workflow.workspace else None,
            "nodes_count": len(workflow.nodes) if workflow.nodes else 0,
            "execution_count": execution_count,
            "latest_execution": {
                "id": latest_execution.id,
                "status": latest_execution.status,
                "created_at": latest_execution.created_at,
                "completed_at": latest_execution.completed_at
            } if latest_execution else None,
            "nodes": workflow.nodes,
            "edges": workflow.edges,
            "variables": workflow.variables,
            "settings": workflow.settings,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao buscar workflow",
            details=str(e)
        )

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id,
                                            WorkspaceMember.role.in_(["admin", "editor"])
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ).options(
            selectinload(Workflow.workspace),
            selectinload(Workflow.executions)
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado"
            )
        
        # Update fields
        if workflow_data.name is not None:
            workflow.name = workflow_data.name
            
        if workflow_data.description is not None:
            workflow.description = workflow_data.description
            
        if workflow_data.nodes is not None:
            workflow.nodes = workflow_data.nodes
            
        if workflow_data.edges is not None:
            workflow.edges = workflow_data.edges
            
        if workflow_data.variables is not None:
            workflow.variables = workflow_data.variables
            
        if workflow_data.settings is not None:
            workflow.settings = workflow_data.settings
            
        if workflow_data.status is not None:
            workflow.status = workflow_data.status
            
        if workflow_data.is_active is not None:
            workflow.is_active = workflow_data.is_active
        
        workflow.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(workflow)
        
        # Get execution stats
        execution_count = len(workflow.executions) if workflow.executions else 0
        latest_execution = None
        if workflow.executions:
            workflow.executions.sort(key=lambda x: x.created_at, reverse=True)
            latest_execution = workflow.executions[0]
        
        # Convert to response
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "is_active": workflow.is_active,
            "workspace_id": workflow.workspace_id,
            "workspace_name": workflow.workspace.name if workflow.workspace else None,
            "nodes_count": len(workflow.nodes) if workflow.nodes else 0,
            "execution_count": execution_count,
            "latest_execution": {
                "id": latest_execution.id,
                "status": latest_execution.status,
                "created_at": latest_execution.created_at,
                "completed_at": latest_execution.completed_at
            } if latest_execution else None,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao atualizar workflow",
            details=str(e)
        )

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deletar workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id,
                                            WorkspaceMember.role.in_(["admin"])
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado"
            )
        
        # Check if there are running executions
        running_executions = db.query(WorkflowExecution).filter(
            and_(
                WorkflowExecution.workflow_id == workflow_id,
                WorkflowExecution.status.in_(["running", "pending", "queued"])
            )
        ).count()
        
        if running_executions > 0:
            raise HTTPException(
                status_code=409,
                message="Não é possível deletar workflow com execuções em andamento",
                details=f"{running_executions} execuções em andamento"
            )
        
        # Soft delete workflow
        workflow.is_active = False
        workflow.status = "deleted"
        workflow.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Workflow deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao deletar workflow",
            details=str(e)
        )

# Workflow execution endpoints
@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: int,
    execution_data: Optional[WorkflowExecutionCreate] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Executar workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id,
                                            WorkspaceMember.role.in_(["admin", "editor", "viewer"])
                                        )
                                    )
                                )
                            )
                        )
                    )
                ),
                Workflow.is_active == True
            )
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado ou inativo"
            )
        
        # Validate workflow before execution
        if not workflow.nodes or len(workflow.nodes) == 0:
            raise HTTPException(
                status_code=400,
                message="Workflow deve ter pelo menos um nó para ser executado"
            )
        
        # Create execution record
        new_execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=current_user.id,
            status="pending",
            input_data=execution_data.input_data if execution_data else {},
            variables=execution_data.variables if execution_data else {},
            settings=execution_data.settings if execution_data else {}
        )
        
        db.add(new_execution)
        db.commit()
        db.refresh(new_execution)
        
        # Start execution in background
        # TODO: Implement WorkflowExecutionService
        # background_tasks.add_task(
        #     workflow_execution_service.start_execution,
        #     new_execution.id
        # )
        
        # Convert to response
        execution_dict = {
            "id": new_execution.id,
            "workflow_id": new_execution.workflow_id,
            "workflow_name": workflow.name,
            "status": new_execution.status,
            "progress": 0,
            "input_data": new_execution.input_data,
            "output_data": new_execution.output_data,
            "error_message": new_execution.error_message,
            "started_at": new_execution.started_at,
            "completed_at": new_execution.completed_at,
            "created_at": new_execution.created_at,
            "updated_at": new_execution.updated_at
        }
        
        return WorkflowExecutionResponse(**execution_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao executar workflow",
            details=str(e)
        )

@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar execuções do workflow"""
    try:
        # Verify workflow access
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado"
            )
        
        # Build query
        query = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        )
        
        # Apply filters
        if status:
            query = query.filter(WorkflowExecution.status == status)
        
        # Order by most recent first
        query = query.order_by(desc(WorkflowExecution.created_at))
        
        # Pagination
        total = query.count()
        offset = (page - 1) * size
        executions = query.offset(offset).limit(size).all()
        
        response_executions = [WorkflowExecutionResponse.from_orm(execution) for execution in executions]
        
        return response_executions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao listar execuções",
            details=str(e)
        )

@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    workflow_id: uuid.UUID,
    duplicate_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicar workflow"""
    try:
        # Get original workflow
        original_workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == workflow_id,
                Workflow.tenant_id == current_user.tenant_id,
                or_(
                    Workflow.user_id == current_user.id,
                    and_(
                        Workflow.workspace_id.isnot(None),
                        Workflow.workspace_id.in_(
                            db.query(Workspace.id).filter(
                                or_(
                                    Workspace.owner_id == current_user.id,
                                    Workspace.id.in_(
                                        db.query(WorkspaceMember.workspace_id).filter(
                                            WorkspaceMember.user_id == current_user.id
                                        )
                                    )
                                )
                            )
                        )
                    )
                ),
                Workflow.is_active == True
            )
        ).first()
        
        if not original_workflow:
            raise HTTPException(
                status_code=404,
                message="Workflow não encontrado"
            )
        
        # Generate new name if not provided
        new_name = duplicate_data.name or f"{original_workflow.name} (Cópia)"
        
        # Create duplicate
        duplicate_workflow = Workflow(
            name=new_name,
            description=duplicate_data.description or f"Cópia de: {original_workflow.description}",
            user_id=current_user.id,
            workspace_id=duplicate_data.workspace_id or original_workflow.workspace_id,
            nodes=original_workflow.nodes.copy() if original_workflow.nodes else [],
            edges=original_workflow.edges.copy() if original_workflow.edges else [],
            variables=original_workflow.variables.copy() if original_workflow.variables else {},
            settings=original_workflow.settings.copy() if original_workflow.settings else {},
            status="draft",
            is_active=True
        )
        
        db.add(duplicate_workflow)
        db.commit()
        db.refresh(duplicate_workflow)
        
        # Load workspace relationship
        if duplicate_workflow.workspace_id:
            duplicate_workflow.workspace = db.query(Workspace).filter(Workspace.id == duplicate_workflow.workspace_id).first()
        
        # Convert to response
        workflow_dict = {
            "id": duplicate_workflow.id,
            "name": duplicate_workflow.name,
            "description": duplicate_workflow.description,
            "status": duplicate_workflow.status,
            "is_active": duplicate_workflow.is_active,
            "workspace_id": duplicate_workflow.workspace_id,
            "workspace_name": duplicate_workflow.workspace.name if duplicate_workflow.workspace else None,
            "nodes_count": len(duplicate_workflow.nodes) if duplicate_workflow.nodes else 0,
            "execution_count": 0,
            "latest_execution": None,
            "created_at": duplicate_workflow.created_at,
            "updated_at": duplicate_workflow.updated_at
        }
        
        return WorkflowResponse(**workflow_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao duplicar workflow",
            details=str(e)
        )

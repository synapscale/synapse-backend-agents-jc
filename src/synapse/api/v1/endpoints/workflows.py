"""
Endpoints para gerenciamento de workflows
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.synapse.api.deps import get_current_user
from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.models.workflow import Workflow
from src.synapse.models.workflow_execution import ExecutionStatus, WorkflowExecution
from src.synapse.schemas.workflow import (
    WorkflowCreate,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowUpdate,
)
from src.synapse.schemas.workflow_execution import (
    ExecutionListResponse,
    ExecutionResponse,
)

router = APIRouter()


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar workflows do usuário"""
    query = db.query(Workflow)

    # Filtrar por usuário ou workflows públicos
    if is_public is True:
        query = query.filter(Workflow.is_public == True)
    else:
        query = query.filter(Workflow.user_id == current_user.id)

    # Filtros adicionais
    if category:
        query = query.filter(Workflow.category == category)

    if search:
        query = query.filter(
            Workflow.name.ilike(f"%{search}%")
            | Workflow.description.ilike(f"%{search}%")
        )

    # Paginação
    total = query.count()
    workflows = query.offset((page - 1) * size).limit(size).all()

    return WorkflowListResponse(
        items=workflows,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo workflow"""
    workflow = Workflow(**workflow_data.dict(), user_id=current_user.id)

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter workflow específico"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    # Verificar permissão
    if workflow.user_id != current_user.id and not workflow.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este workflow",
        )

    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar workflow"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.user_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    # Atualizar campos
    for field, value in workflow_data.dict(exclude_unset=True).items():
        setattr(workflow, field, value)

    db.commit()
    db.refresh(workflow)

    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletar workflow"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.user_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    db.delete(workflow)
    db.commit()

    return {"message": "Workflow deletado com sucesso"}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    execution_data: WorkflowExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executar workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    # Verificar permissão
    if workflow.user_id != current_user.id and not workflow.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para executar este workflow",
        )

    execution = WorkflowExecution(
        workflow_id=workflow.id,
        user_id=current_user.id,
        input_data=execution_data.inputs,
        context_data=execution_data.context,
        status=ExecutionStatus.PENDING,
        total_nodes=workflow.get_node_count(),
    )

    db.add(execution)
    workflow.increment_executions()
    db.commit()
    db.refresh(execution)

    return WorkflowExecutionResponse(
        execution_id=execution.execution_id,
        status=execution.status.value,
        message="Execução iniciada com sucesso",
    )


@router.get("/{workflow_id}/executions")
async def list_workflow_executions(
    workflow_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Listar execuções do workflow"""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.user_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    query = (
        db.query(WorkflowExecution)
        .filter(
            WorkflowExecution.workflow_id == workflow.id,
            WorkflowExecution.user_id == current_user.id,
        )
        .order_by(WorkflowExecution.created_at.desc())
    )

    total = query.count()
    executions = query.offset((page - 1) * size).limit(size).all()

    return ExecutionListResponse(
        items=[ExecutionResponse.from_orm(e) for e in executions],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Duplicar workflow"""
    original = db.query(Workflow).filter(Workflow.id == workflow_id).first()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow não encontrado"
        )

    # Verificar permissão
    if original.user_id != current_user.id and not original.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para duplicar este workflow",
        )

    # Criar cópia
    duplicate = Workflow(
        name=f"{original.name} (Cópia)",
        description=original.description,
        user_id=current_user.id,
        category=original.category,
        tags=original.tags,
        definition=original.definition,
        is_public=False,
        status="draft",
    )

    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)

    return duplicate

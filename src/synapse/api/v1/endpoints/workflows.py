"""
Endpoints para gerenciamento de workflows
Criado por José - um desenvolvedor Full Stack
API completa para CRUD e execução de workflows
"""

import logging
from typing import Optional, Dict, Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user
from synapse.database import get_db
from synapse.models.user import User
from synapse.models.workflow import Workflow
from synapse.models.workflow_execution import ExecutionStatus, WorkflowExecution
from synapse.schemas.workflow import (
    WorkflowCreate,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowUpdate,
)
from synapse.schemas.workflow_execution import (
    ExecutionListResponse,
    ExecutionResponse,
)
from synapse.schemas.response import (
    wrap_data_response,
    wrap_list_response,
    wrap_empty_response
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Listar workflows",
    tags=["workflows"],
)
async def list_workflows(
    request: Request,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    is_public: Optional[bool] = Query(None, description="Filtrar workflows públicos"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Lista workflows do usuário com filtros e paginação.
    
    Retorna workflows próprios ou públicos dependendo dos filtros,
    com suporte a busca textual e paginação.
    
    Args:
        page: Número da página (1-based)
        size: Número de itens por página
        category: Categoria específica para filtrar
        is_public: Se True, mostra apenas workflows públicos
        search: Termo para buscar em nome e descrição
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowListResponse: Lista paginada de workflows
        
    Raises:
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando workflows para usuário {current_user.id} - página: {page}, público: {is_public}")
        
        query = db.query(Workflow)

        # Filtrar por usuário ou workflows públicos
        if is_public is True:
            query = query.filter(Workflow.is_public == True)
            logger.info("Filtrando apenas workflows públicos")
        else:
            query = query.filter(Workflow.user_id == current_user.id)
            logger.info(f"Filtrando workflows do usuário {current_user.id}")

        # Filtros adicionais
        if category:
            query = query.filter(Workflow.category == category)
            logger.info(f"Filtrando por categoria: {category}")

        if search:
            query = query.filter(
                Workflow.name.ilike(f"%{search}%")
                | Workflow.description.ilike(f"%{search}%"),
            )
            logger.info(f"Filtrando por busca: '{search}'")

        # Paginação
        total = query.count()
        workflows = query.offset((page - 1) * size).limit(size).all()

        logger.info(f"Retornados {len(workflows)} workflows de {total} total para usuário {current_user.id}")
        
        workflow_list_response = WorkflowListResponse(
            items=[w.to_dict() for w in workflows],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )
        
        return wrap_list_response(
            request=request,
            data=workflow_list_response,
            message=f"Retornados {len(workflows)} workflows com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao listar workflows para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/", response_model=Dict[str, Any], summary="Criar workflow", tags=["workflows"])
async def create_workflow(
    request: Request,
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Cria um novo workflow para o usuário.
    
    Cria um workflow com os dados fornecidos e associa
    ao usuário autenticado.
    
    Args:
        workflow_data: Dados do workflow a ser criado
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowResponse: Workflow criado
        
    Raises:
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Criando workflow '{workflow_data.name}' para usuário {current_user.id}")
        
        workflow = Workflow(**workflow_data.dict(), user_id=current_user.id)

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        logger.info(f"Workflow '{workflow.name}' criado com sucesso (ID: {workflow.id}) para usuário {current_user.id}")
        
        return wrap_data_response(
            request=request,
            data=workflow.to_dict(),
            message=f"Workflow '{workflow.name}' criado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao criar workflow para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{workflow_id}", response_model=Dict[str, Any], summary="Obter workflow", tags=["workflows"])
async def get_workflow(
    request: Request,
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtém um workflow específico por ID.
    
    Retorna dados completos do workflow se o usuário
    tiver permissão de acesso.
    
    Args:
        workflow_id: ID único do workflow
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowResponse: Dados do workflow
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo workflow {workflow_id} para usuário {current_user.id}")
        
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        workflow = db.query(Workflow).filter(Workflow.id == workflow_uuid).first()

        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )

        # Verificar permissão
        if workflow.user_id != current_user.id and not workflow.is_public:
            logger.warning(f"Usuário {current_user.id} sem permissão para acessar workflow {workflow_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este workflow",
            )

        logger.info(f"Workflow {workflow_id} obtido com sucesso para usuário {current_user.id}")
        
        return wrap_data_response(
            request=request,
            data=workflow.to_dict(),
            message="Workflow obtido com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{workflow_id}", response_model=Dict[str, Any], summary="Atualizar workflow", tags=["workflows"])
async def update_workflow(
    request: Request,
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Atualiza um workflow existente do usuário.
    
    Permite modificar dados do workflow se o usuário
    for o proprietário.
    
    Args:
        workflow_id: ID único do workflow
        workflow_data: Dados atualizados do workflow
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowResponse: Workflow atualizado
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Atualizando workflow {workflow_id} para usuário {current_user.id}")
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        workflow = (
            db.query(Workflow)
            .filter(Workflow.id == workflow_uuid, Workflow.user_id == current_user.id)
            .first()
        )
        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado ou sem permissão para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )
        update_count = 0
        for field, value in workflow_data.dict(exclude_unset=True).items():
            if getattr(workflow, field) != value:
                setattr(workflow, field, value)
                update_count += 1
        if update_count > 0:
            db.commit()
            db.refresh(workflow)
            logger.info(f"Workflow {workflow_id} atualizado com sucesso - {update_count} campos modificados")
        else:
            logger.info(f"Nenhuma alteração necessária no workflow {workflow_id}")
        return wrap_data_response(
            request=request,
            data=workflow.to_dict(),
            message="Workflow atualizado com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{workflow_id}", response_model=Dict[str, Any], summary="Deletar workflow", tags=["workflows"])
async def delete_workflow(
    request: Request,
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Remove um workflow do usuário.
    
    Deleta permanentemente o workflow se o usuário
    for o proprietário.
    
    Args:
        workflow_id: ID único do workflow
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Deletando workflow {workflow_id} para usuário {current_user.id}")
        
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        workflow = (
            db.query(Workflow)
            .filter(Workflow.id == workflow_uuid, Workflow.user_id == current_user.id)
            .first()
        )

        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado ou sem permissão para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )

        workflow_name = workflow.name
        db.delete(workflow)
        db.commit()

        logger.info(f"Workflow '{workflow_name}' (ID: {workflow_id}) deletado com sucesso para usuário {current_user.id}")
        return wrap_empty_response(message="Workflow deletado com sucesso")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse, summary="Executar workflow", tags=["workflows"])
async def execute_workflow(
    workflow_id: str,
    execution_data: WorkflowExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowExecutionResponse:
    """
    Executa um workflow com dados de entrada.
    
    Cria uma nova execução do workflow com os dados
    fornecidos e inicia o processamento.
    
    Args:
        workflow_id: ID único do workflow
        execution_data: Dados de entrada para execução
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowExecutionResponse: Detalhes da execução criada
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se sem permissão de execução
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Executando workflow {workflow_id} para usuário {current_user.id}")
        
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        workflow = db.query(Workflow).filter(Workflow.id == workflow_uuid).first()

        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )

        # Verificar permissão
        if workflow.user_id != current_user.id and not workflow.is_public:
            logger.warning(f"Usuário {current_user.id} sem permissão para executar workflow {workflow_id}")
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
            total_nodes=workflow.get_node_count() if hasattr(workflow, 'get_node_count') else 0,
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        logger.info(f"Execução {execution.id} criada para workflow {workflow_id} por usuário {current_user.id}")
        
        # Aqui seria integrado com o serviço de execução para processar
        # execution_service.start_execution(execution.id)
        
        return WorkflowExecutionResponse(
            execution_id=str(execution.id),
            status=execution.status.value if hasattr(execution.status, 'value') else str(execution.status),
            message="Execução criada com sucesso",
            outputs=None,
            error=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{workflow_id}/executions", response_model=ExecutionListResponse, summary="Listar execuções", tags=["workflows"])
async def list_workflow_executions(
    workflow_id: str,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExecutionListResponse:
    """
    Lista execuções de um workflow específico.
    
    Retorna histórico de execuções do workflow
    com paginação e detalhes de status.
    
    Args:
        workflow_id: ID único do workflow
        page: Número da página
        size: Itens por página
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        ExecutionListResponse: Lista paginada de execuções
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando execuções do workflow {workflow_id} para usuário {current_user.id}")
        
        # Verificar se o workflow existe e se o usuário tem permissão
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        workflow = db.query(Workflow).filter(Workflow.id == workflow_uuid).first()
        
        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )

        if workflow.user_id != current_user.id and not workflow.is_public:
            logger.warning(f"Usuário {current_user.id} sem permissão para acessar execuções do workflow {workflow_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar execuções deste workflow",
            )

        # Buscar execuções
        query = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_uuid
        ).order_by(WorkflowExecution.created_at.desc())

        total = query.count()
        executions = query.offset((page - 1) * size).limit(size).all()

        logger.info(f"Retornadas {len(executions)} execuções de {total} total para workflow {workflow_id}")

        # Serializar execuções para o schema correto
        items = [
            ExecutionResponse(
                id=exec.id,
                execution_id=str(exec.execution_id),
                workflow_id=exec.workflow_id,
                user_id=exec.user_id,
                status=exec.status,
                output_data=getattr(exec, 'output_data', None),
                total_nodes=getattr(exec, 'total_nodes', 0),
                completed_nodes=getattr(exec, 'completed_nodes', 0),
                failed_nodes=getattr(exec, 'failed_nodes', 0),
                progress_percentage=getattr(exec, 'progress_percentage', 0),
                started_at=getattr(exec, 'started_at', None),
                completed_at=getattr(exec, 'completed_at', None),
                error_message=getattr(exec, 'error_message', None),
                retry_count=getattr(exec, 'retry_count', 0),
                created_at=getattr(exec, 'created_at', None),
                updated_at=getattr(exec, 'updated_at', None),
            )
            for exec in executions
        ]

        return ExecutionListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar execuções do workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{workflow_id}/duplicate", response_model=Dict[str, Any], summary="Duplicar workflow", tags=["workflows"])
async def duplicate_workflow(
    request: Request,
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Cria uma cópia de um workflow existente.
    
    Duplica um workflow público ou próprio, criando
    uma nova instância para o usuário.
    
    Args:
        workflow_id: ID único do workflow a ser duplicado
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowResponse: Workflow duplicado
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Duplicando workflow {workflow_id} para usuário {current_user.id}")
        
        # Buscar workflow original
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except (ValueError, TypeError):
            logger.warning(f"workflow_id inválido: {workflow_id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        original_workflow = db.query(Workflow).filter(Workflow.id == workflow_uuid).first()
        
        if not original_workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado para duplicação")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow não encontrado",
            )

        # Verificar permissão
        if original_workflow.user_id != current_user.id and not original_workflow.is_public:
            logger.warning(f"Usuário {current_user.id} sem permissão para duplicar workflow {workflow_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para duplicar este workflow",
            )

        # Criar cópia
        duplicate_data = {
            "name": f"{original_workflow.name} (Cópia)",
            "description": original_workflow.description,
            "category": original_workflow.category,
            "is_public": False,  # Cópias sempre privadas inicialmente
            "nodes": original_workflow.nodes,
            "connections": original_workflow.connections,
            "user_id": current_user.id,
        }

        duplicate_workflow = Workflow(**duplicate_data)
        db.add(duplicate_workflow)
        db.commit()
        db.refresh(duplicate_workflow)

        logger.info(f"Workflow '{original_workflow.name}' duplicado com sucesso (novo ID: {duplicate_workflow.id}) para usuário {current_user.id}")
        return wrap_data_response(
            request=request,
            data=duplicate_workflow.to_dict(),
            message="Workflow duplicado com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao duplicar workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

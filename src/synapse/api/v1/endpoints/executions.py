"""
Endpoints para Execução de Workflows
Criado por José - um desenvolvedor Full Stack
API completa para gerenciamento de execuções em tempo real
"""

import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from synapse.database import get_db
from synapse.api.deps import get_current_user
from synapse.models.user import User
from synapse.schemas.workflow_execution import (
    ExecutionCreate,
    ExecutionResponse,
    NodeExecutionResponse,
    ExecutionStats,
    ExecutionFilter,
    ExecutionControl,
    ExecutionBatch,
    WorkflowValidation,
)
from synapse.services.execution_service import ExecutionService
from synapse.core.websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

# Router para execuções
router = APIRouter()

# Instância global do serviço (será inicializada no startup)
execution_service: Optional[ExecutionService] = None
websocket_manager: Optional[ConnectionManager] = None


def get_execution_service() -> ExecutionService:
    """
    Obtém a instância do serviço de execução.
    
    Returns:
        ExecutionService: Instância do serviço de execução
        
    Raises:
        RuntimeError: Se o serviço não foi inicializado
    """
    global execution_service
    
    # Verifica se a engine está habilitada PRIMEIRO
    execution_engine_enabled = os.getenv('EXECUTION_ENGINE_ENABLED', 'true').lower() == 'true'
    if not execution_engine_enabled:
        raise HTTPException(
            status_code=503, 
            detail="🚫 Engine de execução desabilitada. Configure EXECUTION_ENGINE_ENABLED=true para habilitar."
        )
    
    # Só cria se realmente habilitado
    if execution_service is None:
        raise HTTPException(
            status_code=503,
            detail="🚫 Serviço de execução não foi inicializado. Verifique se EXECUTION_ENGINE_ENABLED=true."
        )
    
    return execution_service


@router.post("/", response_model=ExecutionResponse, status_code=201, summary="Criar execução de workflow", tags=["workflows"])
async def create_execution(
    execution_data: ExecutionCreate,
    start_immediately: bool = Query(
        default=True, description="Iniciar execução imediatamente"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> ExecutionResponse:
    """
    Cria uma nova execução de workflow com configurações personalizadas.
    
    Permite criar e opcionalmente iniciar uma execução de workflow
    com dados de entrada, variáveis e prioridade específicos.
    
    Args:
        execution_data: Dados da execução a ser criada
        start_immediately: Se deve iniciar a execução imediatamente
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        ExecutionResponse: Dados da execução criada
        
    Raises:
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Criando execução do workflow {execution_data.workflow_id} para usuário {current_user.id} - início imediato: {start_immediately}")
        execution = await service.create_and_start_execution(
            db,
            execution_data,
            current_user.id,
            start_immediately,
        )
        logger.info(f"Execução {execution.id} criada com sucesso para usuário {current_user.id}")
        return execution
    except ValueError as e:
        logger.warning(f"Dados inválidos para execução do workflow {execution_data.workflow_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar execução do workflow {execution_data.workflow_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", response_model=List[ExecutionResponse], summary="Listar execuções do usuário", tags=["workflows"])
async def list_executions(
    status: Optional[List[str]] = Query(None, description="Filtrar por status"),
    workflow_ids: Optional[List[int]] = Query(
        None, description="Filtrar por IDs de workflow"
    ),
    created_after: Optional[datetime] = Query(None, description="Criado após esta data"),
    created_before: Optional[datetime] = Query(
        None, description="Criado antes desta data"
    ),
    tags: Optional[List[str]] = Query(None, description="Filtrar por tags"),
    limit: int = Query(default=50, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(default=0, ge=0, description="Offset para paginação"),
    order_by: str = Query(
        default="created_at",
        pattern="^(created_at|updated_at|started_at|completed_at|priority)$",
        description="Campo para ordenação"
    ),
    order_direction: str = Query(default="desc", pattern="^(asc|desc)$", description="Direção da ordenação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> List[ExecutionResponse]:
    """
    Lista execuções do usuário com filtros avançados e paginação.
    
    Permite filtrar por status, workflows, datas, tags e aplicar
    ordenação e paginação para navegação eficiente.
    
    Args:
        status: Lista de status para filtrar (opcional)
        workflow_ids: IDs de workflows para filtrar (opcional)
        created_after: Data mínima de criação (opcional)
        created_before: Data máxima de criação (opcional)
        tags: Tags para filtrar (opcional)
        limit: Limite de resultados por página
        offset: Offset para paginação
        order_by: Campo para ordenação
        order_direction: Direção da ordenação (asc/desc)
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        List[ExecutionResponse]: Lista de execuções
        
    Raises:
        HTTPException: 400 se filtros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        # Validação de datas
        if created_after and created_before and created_after > created_before:
            raise HTTPException(status_code=400, detail="Data inicial deve ser anterior à data final")
            
        logger.info(f"Listando execuções para usuário {current_user.id} - limite: {limit}, offset: {offset}")
        
        # Converte status strings para enum se fornecido
        status_enums = None
        if status:
            from synapse.models.workflow_execution import ExecutionStatus
            status_enums = [
                ExecutionStatus(s)
                for s in status
                if s in ExecutionStatus.__members__.values()
            ]

        filters = ExecutionFilter(
            status=status_enums,
            workflow_ids=workflow_ids,
            created_after=created_after,
            created_before=created_before,
            tags=tags,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction,
        )

        executions = await service.get_user_executions(db, current_user.id, filters)
        logger.info(f"Retornadas {len(executions)} execuções para usuário {current_user.id}")
        return executions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar execuções para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/stats", response_model=ExecutionStats, summary="Estatísticas de execução", tags=["workflows"])
async def get_execution_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> ExecutionStats:
    """
    Obtém estatísticas completas de execução do usuário.
    
    Retorna métricas agregadas incluindo contadores, taxas de sucesso,
    durações médias e tendências de performance.
    
    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        ExecutionStats: Estatísticas de execução
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo estatísticas de execução para usuário {current_user.id}")
        stats = await service.get_execution_statistics(db, current_user.id)
        logger.info(f"Estatísticas de execução obtidas para usuário {current_user.id}")
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{execution_id}", response_model=ExecutionResponse, summary="Obter execução específica", tags=["workflows"])
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> ExecutionResponse:
    """
    Obtém detalhes completos de uma execução específica.
    
    Retorna informações detalhadas sobre status, progresso,
    dados de entrada/saída e métricas da execução.
    
    Args:
        execution_id: ID único da execução
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        ExecutionResponse: Dados completos da execução
        
    Raises:
        HTTPException: 404 se execução não encontrada
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo execução {execution_id} para usuário {current_user.id}")
        execution = await service.get_execution_status(
            db, execution_id, current_user.id
        )
        if not execution:
            logger.warning(f"Execução {execution_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        logger.info(f"Execução {execution_id} obtida com sucesso para usuário {current_user.id}")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter execução {execution_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{execution_id}/control", summary="Controlar execução", tags=["workflows"])
async def control_execution(
    execution_id: str,
    control: ExecutionControl,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Controla uma execução através de ações específicas.
    
    Permite executar ações de controle como iniciar, pausar, resumir,
    cancelar ou reiniciar uma execução específica.
    
    Args:
        execution_id: ID único da execução
        control: Configuração da ação de controle
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Resultado da ação de controle
        
    Raises:
        HTTPException: 404 se execução não encontrada
        HTTPException: 400 se ação inválida ou não permitida
        HTTPException: 403 se sem permissão de controle
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Executando ação '{control.action}' na execução {execution_id} para usuário {current_user.id}")
        
        if control.action == "cancel":
            success = await service.cancel_execution(
                db, execution_id, current_user.id, control.reason
            )
        elif control.action == "retry":
            success = await service.retry_execution(db, execution_id, current_user.id)
        elif control.action == "start":
            success = await service.engine.start_execution(execution_id)
        elif control.action == "pause":
            success = await service.engine.pause_execution(execution_id)
        elif control.action == "resume":
            success = await service.engine.resume_execution(execution_id)
        else:
            logger.warning(f"Ação inválida '{control.action}' solicitada para execução {execution_id}")
            raise HTTPException(status_code=400, detail=f"Ação '{control.action}' não suportada")

        if not success:
            logger.warning(f"Falha ao executar ação '{control.action}' na execução {execution_id}")
            raise HTTPException(
                status_code=400, 
                detail=f"Não foi possível executar a ação '{control.action}' na execução"
            )
            
        logger.info(f"Ação '{control.action}' executada com sucesso na execução {execution_id} para usuário {current_user.id}")
        return {"success": True, "action": control.action, "execution_id": execution_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar ação '{control.action}' na execução {execution_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/batch", summary="Controle em lote de execuções", tags=["workflows"])
async def batch_control_executions(
    batch: ExecutionBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Executa ações de controle em múltiplas execuções simultaneamente.
    
    Permite aplicar a mesma ação (cancelar, pausar, etc.) em
    várias execuções de uma só vez para operações em lote.
    
    Args:
        batch: Configuração da operação em lote
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Resultado das operações em lote
        
    Raises:
        HTTPException: 400 se configuração inválida
        HTTPException: 403 se sem permissão para algumas execuções
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Executando ação em lote '{batch.action}' em {len(batch.execution_ids)} execuções para usuário {current_user.id}")
        
        results = []
        successful = 0
        failed = 0
        
        for execution_id in batch.execution_ids:
            try:
                if batch.action == "cancel":
                    success = await service.cancel_execution(
                        db, execution_id, current_user.id, batch.reason
                    )
                elif batch.action == "retry":
                    success = await service.retry_execution(db, execution_id, current_user.id)
                elif batch.action == "pause":
                    success = await service.engine.pause_execution(execution_id)
                elif batch.action == "resume":
                    success = await service.engine.resume_execution(execution_id)
                else:
                    logger.warning(f"Ação inválida '{batch.action}' em operação em lote")
                    raise HTTPException(status_code=400, detail=f"Ação '{batch.action}' não suportada")
                
                if success:
                    successful += 1
                    results.append({"execution_id": execution_id, "success": True})
                else:
                    failed += 1
                    results.append({"execution_id": execution_id, "success": False, "error": "Operação falhou"})
                    
            except Exception as e:
                failed += 1
                results.append({"execution_id": execution_id, "success": False, "error": str(e)})
                logger.warning(f"Falha na operação '{batch.action}' para execução {execution_id}: {str(e)}")
        
        logger.info(f"Operação em lote concluída para usuário {current_user.id}: {successful} sucessos, {failed} falhas")
        return {
            "action": batch.action,
            "total": len(batch.execution_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na operação em lote para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{execution_id}/nodes", response_model=List[NodeExecutionResponse], summary="Obter nós da execução", tags=["workflows"])
async def get_execution_nodes(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> List[NodeExecutionResponse]:
    """
    Obtém informações de execução de todos os nós de uma execução.
    
    Retorna status, dados de entrada/saída, duração e
    métricas para cada nó executado no workflow.
    
    Args:
        execution_id: ID único da execução
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        List[NodeExecutionResponse]: Lista de execuções de nós
        
    Raises:
        HTTPException: 404 se execução não encontrada
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo nós da execução {execution_id} para usuário {current_user.id}")
        nodes = await service.get_execution_nodes(db, execution_id, current_user.id)
        if nodes is None:
            logger.warning(f"Execução {execution_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        logger.info(f"Retornados {len(nodes)} nós da execução {execution_id} para usuário {current_user.id}")
        return nodes
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter nós da execução {execution_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{execution_id}/logs", summary="Obter logs da execução", tags=["workflows"])
async def get_execution_logs(
    execution_id: str,
    include_nodes: bool = Query(default=True, description="Incluir logs dos nós"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Obtém logs completos de uma execução e seus nós.
    
    Retorna logs estruturados da execução principal e
    opcionalmente de todos os nós executados.
    
    Args:
        execution_id: ID único da execução
        include_nodes: Se deve incluir logs dos nós individuais
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Logs estruturados da execução
        
    Raises:
        HTTPException: 404 se execução não encontrada
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo logs da execução {execution_id} para usuário {current_user.id} - incluir nós: {include_nodes}")
        logs = await service.get_execution_logs(
            db, execution_id, current_user.id, include_nodes
        )
        if not logs:
            logger.warning(f"Execução {execution_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        logger.info(f"Logs da execução {execution_id} obtidos para usuário {current_user.id}")
        return logs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter logs da execução {execution_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{execution_id}/metrics", summary="Obter métricas da execução", tags=["workflows"])
async def get_execution_metrics(
    execution_id: str,
    metric_types: Optional[List[str]] = Query(
        None, description="Filtrar por tipos de métrica"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Obtém métricas detalhadas de performance de uma execução.
    
    Retorna métricas de tempo, memória, CPU e outras métricas
    de performance coletadas durante a execução.
    
    Args:
        execution_id: ID único da execução
        metric_types: Tipos específicos de métricas para filtrar
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Métricas de performance da execução
        
    Raises:
        HTTPException: 404 se execução não encontrada
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo métricas da execução {execution_id} para usuário {current_user.id} - tipos: {metric_types}")
        metrics = await service.get_execution_metrics(
            db, execution_id, current_user.id, metric_types
        )
        if not metrics:
            logger.warning(f"Execução {execution_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        logger.info(f"Métricas da execução {execution_id} obtidas para usuário {current_user.id}")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter métricas da execução {execution_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/validate-workflow", summary="Validar workflow para execução", tags=["workflows"])
async def validate_workflow_for_execution(
    workflow_id: int,
    variables: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowValidation:
    """
    Valida se um workflow está pronto para execução.
    
    Verifica configurações, dependências, variáveis obrigatórias
    e recursos necessários antes de iniciar uma execução.
    
    Args:
        workflow_id: ID do workflow a ser validado
        variables: Variáveis personalizadas para validação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        WorkflowValidation: Resultado da validação com detalhes
        
    Raises:
        HTTPException: 404 se workflow não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Validando workflow {workflow_id} para execução por usuário {current_user.id}")
        
        # Obtém o workflow
        from synapse.services.workflow_service import WorkflowService
        workflow_service = WorkflowService()
        workflow = await workflow_service.get_workflow(db, workflow_id, current_user.id)
        
        if not workflow:
            logger.warning(f"Workflow {workflow_id} não encontrado para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Workflow não encontrado")

        validation_result = {
            "valid": True,
            "workflow_id": workflow_id,
            "errors": [],
            "warnings": [],
            "requirements": {
                "nodes_count": len(workflow.nodes) if workflow.nodes else 0,
                "connections_count": len(workflow.connections) if workflow.connections else 0,
                "required_variables": [],
                "optional_variables": [],
            },
            "estimated_duration": None,
            "resource_requirements": {
                "memory_mb": 256,  # Estimativa base
                "cpu_cores": 1,
                "storage_mb": 100,
            }
        }

        # Validações específicas
        if not workflow.nodes:
            validation_result["valid"] = False
            validation_result["errors"].append("Workflow não possui nós definidos")
        
        if not workflow.is_active:
            validation_result["valid"] is False
            validation_result["warnings"].append("Workflow está inativo")

        # Valida variáveis obrigatórias
        if variables is None:
            variables = current_user.variables or {}
            
        required_vars = workflow.required_variables or []
        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Variáveis obrigatórias não fornecidas: {missing_vars}")
        
        validation_result["requirements"]["required_variables"] = required_vars
        validation_result["requirements"]["optional_variables"] = workflow.optional_variables or []

        logger.info(f"Validação do workflow {workflow_id} concluída - válido: {validation_result['valid']}")
        return WorkflowValidation(**validation_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao validar workflow {workflow_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/queue/status", summary="Status da fila de execução", tags=["workflows"])
async def get_queue_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtém status detalhado da fila de execução do usuário.
    
    Retorna informações sobre execuções pendentes, em andamento,
    posição na fila e estimativas de tempo.
    
    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, Any]: Status completo da fila de execução
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo status da fila para usuário {current_user.id}")
        
        # Obtém estatísticas da fila
        from synapse.models.workflow_execution import ExecutionStatus
        from sqlalchemy import func
        
        # Execuções pendentes do usuário
        pending_executions = db.query(func.count()).filter(
            db.query(WorkflowExecution).filter(
                WorkflowExecution.user_id == current_user.id,
                WorkflowExecution.status == ExecutionStatus.PENDING
            ).subquery()
        ).scalar() or 0
        
        # Execuções em andamento do usuário
        running_executions = db.query(func.count()).filter(
            db.query(WorkflowExecution).filter(
                WorkflowExecution.user_id == current_user.id,
                WorkflowExecution.status == ExecutionStatus.RUNNING
            ).subquery()
        ).scalar() or 0
        
        # Execuções em pausa do usuário
        paused_executions = db.query(func.count()).filter(
            db.query(WorkflowExecution).filter(
                WorkflowExecution.user_id == current_user.id,
                WorkflowExecution.status == ExecutionStatus.PAUSED
            ).subquery()
        ).scalar() or 0
        
        # Posição na fila global (aproximada)
        total_pending = db.query(func.count()).filter(
            db.query(WorkflowExecution).filter(
                WorkflowExecution.status == ExecutionStatus.PENDING
            ).subquery()
        ).scalar() or 0
        
        queue_status = {
            "user_queue": {
                "pending": pending_executions,
                "running": running_executions,
                "paused": paused_executions,
                "total_active": pending_executions + running_executions + paused_executions
            },
            "global_queue": {
                "total_pending": total_pending,
                "estimated_wait_time_minutes": max(total_pending * 2, 1) if total_pending > 0 else 0
            },
            "limits": {
                "max_concurrent_executions": current_user.execution_limit or 5,
                "max_queue_size": current_user.queue_limit or 100
            },
            "status": "healthy" if total_pending < 1000 else "congested"
        }
        
        logger.info(f"Status da fila obtido para usuário {current_user.id} - pendentes: {pending_executions}, rodando: {running_executions}")
        return queue_status
        
    except Exception as e:
        logger.error(f"Erro ao obter status da fila para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/admin/engine-status", summary="Status do engine de execução", tags=["workflows", "advanced"])
async def get_engine_status(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Obtém status detalhado do engine de execução (admin only).
    
    Retorna informações sobre performance, saúde, recursos
    e estatísticas operacionais do engine.
    
    Args:
        current_user: Usuário autenticado (deve ser admin)
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Status completo do engine
        
    Raises:
        HTTPException: 403 se não for admin
        HTTPException: 500 se erro interno do servidor
    """
    try:
        # Verifica se é admin
        if not getattr(current_user, 'is_admin', False):
            logger.warning(f"Usuário {current_user.id} tentou acessar status do engine sem ser admin")
            raise HTTPException(status_code=403, detail="Acesso negado - apenas administradores")
            
        logger.info(f"Obtendo status do engine para admin {current_user.id}")
        engine_status = await service.get_engine_status()
        logger.info(f"Status do engine obtido para admin {current_user.id}")
        return engine_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do engine para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/admin/engine/start", summary="Iniciar engine de execução", tags=["workflows", "advanced"])
async def start_engine(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Inicia o engine de execução de workflows (admin only).
    
    Ativa o engine para processar execuções pendentes
    e aceitar novas solicitações de execução.
    
    Args:
        current_user: Usuário autenticado (deve ser admin)
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Resultado da operação de inicialização
        
    Raises:
        HTTPException: 403 se não for admin
        HTTPException: 400 se engine já estiver rodando
        HTTPException: 500 se erro interno do servidor
    """
    try:
        # Verifica se é admin
        if not getattr(current_user, 'is_admin', False):
            logger.warning(f"Usuário {current_user.id} tentou iniciar engine sem ser admin")
            raise HTTPException(status_code=403, detail="Acesso negado - apenas administradores")
            
        logger.info(f"Iniciando engine por admin {current_user.id}")
        success = await service.start_engine()
        
        if not success:
            logger.warning(f"Falha ao iniciar engine por admin {current_user.id}")
            raise HTTPException(status_code=400, detail="Não foi possível iniciar o engine")
            
        logger.info(f"Engine iniciado com sucesso por admin {current_user.id}")
        return {"success": True, "message": "Engine iniciado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar engine por usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/admin/engine/stop", summary="Parar engine de execução", tags=["workflows", "advanced"])
async def stop_engine(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Para o engine de execução de workflows (admin only).
    
    Interrompe o processamento de novas execuções e
    finaliza execuções em andamento de forma segura.
    
    Args:
        current_user: Usuário autenticado (deve ser admin)
        service: Serviço de execução
        
    Returns:
        Dict[str, Any]: Resultado da operação de parada
        
    Raises:
        HTTPException: 403 se não for admin
        HTTPException: 400 se engine já estiver parado
        HTTPException: 500 se erro interno do servidor
    """
    try:
        # Verifica se é admin
        if not getattr(current_user, 'is_admin', False):
            logger.warning(f"Usuário {current_user.id} tentou parar engine sem ser admin")
            raise HTTPException(status_code=403, detail="Acesso negado - apenas administradores")
            
        logger.info(f"Parando engine por admin {current_user.id}")
        success = await service.stop_engine()
        
        if not success:
            logger.warning(f"Falha ao parar engine por admin {current_user.id}")
            raise HTTPException(status_code=400, detail="Não foi possível parar o engine")
            
        logger.info(f"Engine parado com sucesso por admin {current_user.id}")
        return {"success": True, "message": "Engine parado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parar engine por usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Funções de lifecycle do serviço
async def initialize_execution_service(ws_manager: Optional[ConnectionManager] = None) -> None:
    """
    Inicializa o serviço de execução com websocket manager.
    
    Configura conexões, recursos e estado inicial do serviço
    para processar execuções de workflow.
    
    Args:
        ws_manager: Manager de conexões websocket (opcional)
        
    Raises:
        RuntimeError: Se falha na inicialização
    """
    global execution_service, websocket_manager
    
    # Verifica se a engine está habilitada
    execution_engine_enabled = os.getenv('EXECUTION_ENGINE_ENABLED', 'true').lower() == 'true'
    if not execution_engine_enabled:
        logger.info("⚠️  Engine de Execução desabilitada via EXECUTION_ENGINE_ENABLED=false")
        return
    
    try:
        logger.info("Inicializando serviço de execução")
        websocket_manager = ws_manager
        execution_service = ExecutionService(websocket_manager)
        await execution_service.initialize()
        logger.info("Serviço de execução inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar serviço de execução: {str(e)}")
        raise RuntimeError(f"Falha na inicialização do serviço de execução: {str(e)}")


async def shutdown_execution_service() -> None:
    """
    Finaliza o serviço de execução de forma segura.
    
    Para execuções em andamento, salva estado e
    libera recursos do sistema.
    
    Raises:
        RuntimeError: Se falha no shutdown
    """
    global execution_service
    
    # Verifica se a engine está habilitada
    execution_engine_enabled = os.getenv('EXECUTION_ENGINE_ENABLED', 'true').lower() == 'true'
    if not execution_engine_enabled:
        logger.info("ℹ️  Engine de Execução já estava desabilitada")
        return
    
    try:
        if execution_service:
            logger.info("Finalizando serviço de execução")
            await execution_service.shutdown()
            execution_service = None
            logger.info("Serviço de execução finalizado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao finalizar serviço de execução: {str(e)}")
        raise RuntimeError(f"Falha no shutdown do serviço de execução: {str(e)}")

"""
Endpoints para Execução de Workflows
Criado por José - O melhor Full Stack do mundo
API completa para gerenciamento de execuções em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.synapse.database import get_db
from src.synapse.api.deps import get_current_user
from src.synapse.models.user import User
from src.synapse.schemas.workflow_execution import (
    ExecutionCreate, ExecutionUpdate, ExecutionResponse,
    NodeExecutionResponse, ExecutionStats, ExecutionFilter,
    ExecutionControl, ExecutionBatch, WorkflowValidation
)
from src.synapse.services.execution_service import ExecutionService
from src.synapse.core.websockets.manager import ConnectionManager

# Router para execuções
router = APIRouter(prefix="/executions", tags=["Workflow Executions"])

# Instância global do serviço (será inicializada no startup)
execution_service: Optional[ExecutionService] = None
websocket_manager: Optional[ConnectionManager] = None


def get_execution_service() -> ExecutionService:
    """Obtém a instância do serviço de execução"""
    global execution_service
    if execution_service is None:
        execution_service = ExecutionService(websocket_manager)
    return execution_service


@router.post("/", response_model=ExecutionResponse, status_code=201)
async def create_execution(
    execution_data: ExecutionCreate,
    start_immediately: bool = Query(default=True, description="Iniciar execução imediatamente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Cria uma nova execução de workflow
    
    - **workflow_id**: ID do workflow a ser executado
    - **input_data**: Dados de entrada para o workflow
    - **variables**: Variáveis personalizadas (opcional, usa as do usuário se não fornecido)
    - **priority**: Prioridade da execução (1-10, maior = mais prioritário)
    - **start_immediately**: Se deve iniciar a execução imediatamente
    """
    try:
        execution = await service.create_and_start_execution(
            db, execution_data, current_user.id, start_immediately
        )
        return execution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    status: Optional[List[str]] = Query(None, description="Filtrar por status"),
    workflow_ids: Optional[List[int]] = Query(None, description="Filtrar por IDs de workflow"),
    created_after: Optional[datetime] = Query(None, description="Criado após esta data"),
    created_before: Optional[datetime] = Query(None, description="Criado antes desta data"),
    tags: Optional[List[str]] = Query(None, description="Filtrar por tags"),
    limit: int = Query(default=50, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(default=0, ge=0, description="Offset para paginação"),
    order_by: str = Query(default="created_at", pattern="^(created_at|updated_at|started_at|completed_at|priority)$"),
    order_direction: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Lista execuções do usuário com filtros opcionais
    
    Suporta filtros por status, workflow, datas, tags e paginação.
    """
    try:
        # Converte status strings para enum se fornecido
        status_enums = None
        if status:
            from src.synapse.models.workflow_execution import ExecutionStatus
            status_enums = [ExecutionStatus(s) for s in status if s in ExecutionStatus.__members__.values()]
        
        filters = ExecutionFilter(
            status=status_enums,
            workflow_ids=workflow_ids,
            created_after=created_after,
            created_before=created_before,
            tags=tags,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction
        )
        
        executions = await service.get_user_executions(db, current_user.id, filters)
        return executions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/stats", response_model=ExecutionStats)
async def get_execution_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém estatísticas de execução do usuário
    
    Retorna contadores, taxas de sucesso, durações médias e trends.
    """
    try:
        stats = await service.get_execution_statistics(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém detalhes de uma execução específica
    """
    try:
        execution = await service.get_execution_status(db, execution_id, current_user.id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/{execution_id}/control")
async def control_execution(
    execution_id: str,
    control: ExecutionControl,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Controla uma execução (start, pause, resume, cancel, retry)
    
    - **start**: Inicia uma execução pendente
    - **pause**: Pausa uma execução em andamento (se suportado)
    - **resume**: Resume uma execução pausada (se suportado)
    - **cancel**: Cancela uma execução
    - **retry**: Reinicia uma execução que falhou
    """
    try:
        if control.action == "cancel":
            success = await service.cancel_execution(db, execution_id, current_user.id, control.reason)
        elif control.action == "retry":
            success = await service.retry_execution(db, execution_id, current_user.id)
        elif control.action == "start":
            success = await service.engine.start_execution(db, execution_id, current_user.id)
        else:
            raise HTTPException(status_code=400, detail=f"Ação '{control.action}' não implementada")
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Não foi possível executar a ação '{control.action}'")
        
        return {"success": True, "action": control.action, "execution_id": execution_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/batch")
async def batch_control_executions(
    batch: ExecutionBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Controla múltiplas execuções em lote
    
    - **cancel**: Cancela múltiplas execuções
    - **retry**: Reinicia múltiplas execuções que falharam
    - **delete**: Remove múltiplas execuções (apenas concluídas)
    """
    try:
        results = []
        
        for execution_id in batch.execution_ids:
            try:
                if batch.action == "cancel":
                    success = await service.cancel_execution(db, execution_id, current_user.id, batch.reason)
                elif batch.action == "retry":
                    success = await service.retry_execution(db, execution_id, current_user.id)
                elif batch.action == "delete":
                    # Implementar delete se necessário
                    success = False
                else:
                    success = False
                
                results.append({
                    "execution_id": execution_id,
                    "success": success,
                    "error": None if success else f"Falha ao executar {batch.action}"
                })
            except Exception as e:
                results.append({
                    "execution_id": execution_id,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "action": batch.action,
            "total_requested": len(batch.execution_ids),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{execution_id}/nodes", response_model=List[NodeExecutionResponse])
async def get_execution_nodes(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém execuções de nós de um workflow
    
    Retorna detalhes de cada nó executado, incluindo status, duração e logs.
    """
    try:
        node_executions = await service.get_node_executions(db, execution_id, current_user.id)
        return node_executions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    include_nodes: bool = Query(default=True, description="Incluir logs dos nós"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém logs detalhados de uma execução
    
    Inclui logs da execução principal e opcionalmente dos nós individuais.
    """
    try:
        logs = await service.get_execution_logs(db, execution_id, current_user.id)
        
        if not include_nodes and "nodes" in logs:
            del logs["nodes"]
        
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{execution_id}/metrics")
async def get_execution_metrics(
    execution_id: str,
    metric_types: Optional[List[str]] = Query(None, description="Filtrar por tipos de métrica"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém métricas de performance de uma execução
    
    Inclui métricas de tempo, uso de recursos, chamadas de API, etc.
    """
    try:
        metrics = await service.get_execution_metrics(db, execution_id, current_user.id)
        
        # Filtra por tipos se especificado
        if metric_types:
            metrics = [m for m in metrics if m["type"] in metric_types]
        
        return {
            "execution_id": execution_id,
            "total_metrics": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/validate-workflow")
async def validate_workflow_for_execution(
    workflow_id: int,
    variables: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Valida um workflow antes da execução
    
    Verifica se o workflow está pronto para execução, incluindo:
    - Estrutura válida
    - Variáveis necessárias disponíveis
    - Dependências satisfeitas
    - Estimativa de duração
    """
    try:
        from src.synapse.models.workflow import Workflow
        from src.synapse.services.variable_service import VariableService
        
        # Carrega o workflow
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Carrega variáveis do usuário se não fornecidas
        if variables is None:
            variable_service = VariableService()
            variables = await variable_service.get_user_variables_dict(db, current_user.id)
        
        # Valida o workflow
        service = get_execution_service()
        validation = await service.engine._validate_workflow(db, workflow, variables)
        
        return WorkflowValidation(
            is_valid=validation["is_valid"],
            errors=validation["errors"],
            warnings=validation.get("warnings", []),
            estimated_duration_seconds=validation.get("estimated_duration_seconds"),
            total_nodes=validation["total_nodes"],
            required_variables=validation.get("required_variables", []),
            optional_variables=[],
            dependencies={}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/queue/status")
async def get_queue_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém status da fila de execução
    
    Mostra quantas execuções estão na fila, processando, etc.
    """
    try:
        from src.synapse.models.workflow_execution import ExecutionQueue
        
        # Contadores da fila
        queued = db.query(ExecutionQueue).filter(
            ExecutionQueue.user_id == current_user.id,
            ExecutionQueue.status == "queued"
        ).count()
        
        processing = db.query(ExecutionQueue).filter(
            ExecutionQueue.user_id == current_user.id,
            ExecutionQueue.status == "processing"
        ).count()
        
        completed = db.query(ExecutionQueue).filter(
            ExecutionQueue.user_id == current_user.id,
            ExecutionQueue.status == "completed"
        ).count()
        
        failed = db.query(ExecutionQueue).filter(
            ExecutionQueue.user_id == current_user.id,
            ExecutionQueue.status == "failed"
        ).count()
        
        return {
            "queue_status": {
                "queued": queued,
                "processing": processing,
                "completed": completed,
                "failed": failed,
                "total": queued + processing + completed + failed
            },
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


# Endpoints para administração (se necessário)
@router.get("/admin/engine-status")
async def get_engine_status(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Obtém status da engine de execução (admin only)
    """
    # Verificar se é admin (implementar verificação de permissão)
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        return {
            "engine_running": service.engine.is_running,
            "active_executions": len(service.engine.running_executions),
            "execution_ids": list(service.engine.running_executions.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/admin/engine/start")
async def start_engine(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Inicia a engine de execução (admin only)
    """
    try:
        await service.start_engine()
        return {"success": True, "message": "Engine iniciada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/admin/engine/stop")
async def stop_engine(
    current_user: User = Depends(get_current_user),
    service: ExecutionService = Depends(get_execution_service)
):
    """
    Para a engine de execução (admin only)
    """
    try:
        await service.stop_engine()
        return {"success": True, "message": "Engine parada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


# Função para inicializar o serviço (chamada no startup da aplicação)
async def initialize_execution_service(ws_manager: ConnectionManager = None):
    """
    Inicializa o serviço de execução
    Deve ser chamada no startup da aplicação
    """
    global execution_service, websocket_manager
    websocket_manager = ws_manager
    execution_service = ExecutionService(ws_manager)
    await execution_service.start_engine()


# Função para finalizar o serviço (chamada no shutdown da aplicação)
async def shutdown_execution_service():
    """
    Finaliza o serviço de execução
    Deve ser chamada no shutdown da aplicação
    """
    global execution_service
    if execution_service:
        await execution_service.stop_engine()


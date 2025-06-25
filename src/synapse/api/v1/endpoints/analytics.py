"""
Endpoints da API para Analytics
Criado por José - um desenvolvedor Full Stack
Endpoints para gerenciar analytics e insights
"""

import logging
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from synapse.database import get_db
from synapse.models.user import User
from synapse.services.analytics_service import AnalyticsService
from synapse.schemas.analytics import (
    EventCreate,
    EventResponse,
    AnalyticsQuery,
    QueryResponse,
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardData,
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportExecutionResponse,
    InsightRequest,
    InsightResponse,
    SystemInsights,
    FunnelAnalysis,
    FunnelResult,
    CohortAnalysis,
    CohortResult,
    ABTestConfig,
    ABTestResult,
    ExportRequest,
    ExportResponse,
    RealTimeStats,
    AlertRule,
    AlertResponse,
    AnalyticsOverview,
)
from synapse.api.deps import get_current_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== EVENTOS ====================


@router.post("/events", response_model=EventResponse, summary="Registrar evento de analytics", tags=["analytics"])
async def track_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EventResponse:
    """
    Registra um evento de analytics no sistema.
    
    Este endpoint permite rastrear eventos específicos do usuário para análise posterior.
    Os eventos são fundamentais para entender o comportamento dos usuários e gerar insights.
    
    Args:
        event_data: Dados do evento a ser registrado
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        EventResponse: Dados do evento registrado
        
    Raises:
        HTTPException: 400 se os dados do evento são inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Registrando evento {event_data.event_type} para usuário {current_user.id}")
        service = AnalyticsService(db)
        result = service.track_event(event_data, current_user.id)
        logger.info(f"Evento {event_data.event_type} registrado com sucesso para usuário {current_user.id}")
        return result
    except ValueError as e:
        logger.warning(f"Dados inválidos para evento {event_data.event_type}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao registrar evento {event_data.event_type} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/events/batch", summary="Registrar múltiplos eventos", tags=["analytics"])
async def track_events_batch(
    events: List[EventCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """
    Registra múltiplos eventos em lote para melhor performance.
    
    Este endpoint é otimizado para registrar vários eventos simultaneamente,
    reduzindo a latência e melhorando a eficiência quando há muitos eventos.
    
    Args:
        events: Lista de eventos a serem registrados
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Quantidade de eventos processados e falhados
        
    Raises:
        HTTPException: 400 se algum evento é inválido
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Registrando {len(events)} eventos em lote para usuário {current_user.id}")
        service = AnalyticsService(db)
        result = service.track_events_batch(events, current_user.id)
        logger.info(f"Lote processado para usuário {current_user.id}: {result['processed']} sucessos, {result['failed']} falhas")
        return {"processed": result["processed"], "failed": result["failed"]}
    except Exception as e:
        logger.error(f"Erro ao processar lote de eventos para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/events", response_model=List[EventResponse], summary="Listar eventos do usuário", tags=["analytics"])
async def get_events(
    event_type: Optional[str] = Query(None, description="Tipo do evento"),
    start_date: Optional[datetime] = Query(None, description="Data de início"),
    end_date: Optional[datetime] = Query(None, description="Data de fim"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[EventResponse]:
    """
    Obtém eventos do usuário com filtros opcionais.
    
    Permite filtrar eventos por tipo, período e aplicar paginação
    para análise detalhada do comportamento do usuário.
    
    Args:
        event_type: Filtro por tipo de evento (opcional)
        start_date: Data de início do período (opcional)
        end_date: Data de fim do período (opcional)
        limit: Limite de resultados por página
        offset: Offset para paginação
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        List[EventResponse]: Lista de eventos do usuário
        
    Raises:
        HTTPException: 400 se as datas são inválidas
        HTTPException: 500 se erro interno do servidor
    """
    try:
        # Validação de datas
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
            
        logger.info(f"Buscando eventos para usuário {current_user.id} - tipo: {event_type}, período: {start_date} a {end_date}")
        service = AnalyticsService(db)
        events = service.get_user_events(
            current_user.id,
            event_type,
            start_date,
            end_date,
            limit,
            offset,
        )
        logger.info(f"Retornados {len(events)} eventos para usuário {current_user.id}")
        return events
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar eventos para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== MÉTRICAS ====================


@router.get("/metrics/user-behavior", summary="Métricas de comportamento do usuário", tags=["analytics"])
async def get_user_behavior_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("day", pattern="^(hour|day|week|month)$", description="Granularidade dos dados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Obtém métricas de comportamento do usuário no período especificado.
    
    Analisa padrões de uso, frequência de ações e outros indicadores
    comportamentais para o usuário autenticado.
    
    Args:
        start_date: Data de início da análise
        end_date: Data de fim da análise
        granularity: Granularidade dos dados (hour, day, week, month)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Métricas de comportamento do usuário
        
    Raises:
        HTTPException: 400 se as datas são inválidas
        HTTPException: 500 se erro interno do servidor
    """
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
            
        logger.info(f"Gerando métricas de comportamento para usuário {current_user.id} - período: {start_date} a {end_date}")
        service = AnalyticsService(db)
        metrics = service.get_user_behavior_metrics(
            current_user.id,
            start_date,
            end_date,
            granularity,
        )
        logger.info(f"Métricas de comportamento geradas para usuário {current_user.id}")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar métricas de comportamento para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/metrics/system-performance", summary="Métricas de performance do sistema", tags=["analytics", "advanced"])
async def get_system_performance_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("hour", pattern="^(minute|hour|day)$", description="Granularidade dos dados"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Obtém métricas de performance do sistema (apenas para administradores).
    
    Analisa performance, latência, throughput e outros indicadores
    técnicos do sistema para monitoramento operacional.
    
    Args:
        start_date: Data de início da análise
        end_date: Data de fim da análise
        granularity: Granularidade dos dados (minute, hour, day)
        current_admin: Usuário administrador autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Métricas de performance do sistema
        
    Raises:
        HTTPException: 400 se as datas são inválidas
        HTTPException: 403 se usuário não é admin
        HTTPException: 500 se erro interno do servidor
    """
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
            
        logger.info(f"Gerando métricas de sistema por admin {current_admin.id} - período: {start_date} a {end_date}")
        service = AnalyticsService(db)
        metrics = service.get_system_performance_metrics(start_date, end_date, granularity)
        logger.info(f"Métricas de sistema geradas por admin {current_admin.id}")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar métricas de sistema por admin {current_admin.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/metrics/business", summary="Métricas de negócio", tags=["analytics", "advanced"])
async def get_business_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("day", pattern="^(day|week|month)$", description="Granularidade dos dados"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Obtém métricas de negócio (apenas para administradores).
    
    Analisa indicadores de performance de negócio como receita,
    conversões, retenção e outros KPIs importantes.
    
    Args:
        start_date: Data de início da análise
        end_date: Data de fim da análise
        granularity: Granularidade dos dados (day, week, month)
        current_admin: Usuário administrador autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Métricas de negócio
        
    Raises:
        HTTPException: 400 se as datas são inválidas
        HTTPException: 403 se usuário não é admin
        HTTPException: 500 se erro interno do servidor
    """
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
            
        logger.info(f"Gerando métricas de negócio por admin {current_admin.id} - período: {start_date} a {end_date}")
        service = AnalyticsService(db)
        metrics = service.get_business_metrics(start_date, end_date, granularity)
        logger.info(f"Métricas de negócio geradas por admin {current_admin.id}")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar métricas de negócio por admin {current_admin.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/metrics/real-time", response_model=RealTimeStats, summary="Métricas em tempo real", tags=["analytics"])
async def get_real_time_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RealTimeStats:
    """
    Obtém métricas em tempo real do usuário.
    
    Retorna estatísticas atualizadas sobre atividade recente,
    sessions ativas e outros indicadores em tempo real.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        RealTimeStats: Estatísticas em tempo real
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo métricas em tempo real para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        # Obtenha as métricas e converta para o modelo de resposta
        stats_data = service.get_real_time_stats()

        real_time_stats = RealTimeStats(
            active_users=stats_data.get("active_users", 0),
            active_sessions=stats_data.get("current_sessions", 0),
            requests_per_minute=stats_data.get("requests_per_minute", 0),
            average_response_time=stats_data.get("average_response_time", 0),
            error_rate=stats_data.get("error_rate", 0.0),
            cpu_usage=stats_data.get("system_load", 0.0),
            memory_usage=stats_data.get("memory_usage", 0.0),
            active_agents=stats_data.get("active_agents", 0),
            completed_workflows=stats_data.get("completed_workflows", 0),
            pending_workflows=stats_data.get("pending_workflows", 0)
        )

        logger.info(f"Métricas em tempo real obtidas para usuário {current_user.id}")
        return real_time_stats
    except ValueError as ve:
        logger.warning(f"Erro de validação ao obter métricas em tempo real: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter métricas em tempo real para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== CONSULTAS CUSTOMIZADAS ====================


@router.post("/queries", response_model=QueryResponse, summary="Executar consulta customizada", tags=["analytics"])
async def execute_analytics_query(
    query: AnalyticsQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Executa uma consulta customizada de analytics.
    
    Permite executar consultas personalizadas para análises
    específicas que não estão cobertas pelos endpoints padrão.
    
    Args:
        query: Dados da consulta a ser executada
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        QueryResponse: Resultado da consulta
        
    Raises:
        HTTPException: 400 se a consulta é inválida
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Executando consulta customizada para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        # Executa a consulta e prepara o modelo de resposta
        result_data = service.execute_analytics_query(query, current_user.id)

        query_response = QueryResponse(
            query_id=result_data.get("query_id"),
            status=result_data.get("status", "completed"),
            results=result_data.get("results", []),
            metadata={
                "execution_time_ms": result_data.get("execution_time", 0),
                "rows_returned": result_data.get("rows_returned", 0),
                "columns": result_data.get("columns", [])
            },
            execution_time_ms=result_data.get("execution_time", 0),
            created_at=datetime.utcnow()
        )

        logger.info(f"Consulta customizada executada com sucesso para usuário {current_user.id}")
        return query_response
    except ValueError as ve:
        logger.warning(f"Consulta inválida para usuário {current_user.id}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar consulta para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/queries/validate", summary="Validar consulta", tags=["analytics"])
async def validate_analytics_query(
    query: AnalyticsQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Valida uma consulta de analytics sem executá-la.
    
    Verifica se a sintaxe e estrutura da consulta estão corretas
    antes da execução, permitindo debug e validação prévia.
    
    Args:
        query: Consulta a ser validada
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Resultado da validação (valid, errors)
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Validando consulta para usuário {current_user.id}")
        service = AnalyticsService(db)
        validation = service.validate_query(query, current_user.id)
        logger.info(f"Validação concluída para usuário {current_user.id}: {validation['valid']}")
        return {"valid": validation["valid"], "errors": validation.get("errors", [])}
    except Exception as e:
        logger.error(f"Erro ao validar consulta para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/queries/saved", summary="Listar consultas salvas", tags=["analytics"])
async def get_saved_queries(
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Obtém consultas salvas do usuário.
    
    Retorna lista de consultas que o usuário salvou para reutilização,
    facilitando análises recorrentes.
    
    Args:
        limit: Limite de resultados por página
        offset: Offset para paginação
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Lista de consultas salvas
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo consultas salvas para usuário {current_user.id}")
        service = AnalyticsService(db)
        queries = service.get_saved_queries(current_user.id, limit, offset)
        logger.info(f"Retornadas {len(queries)} consultas salvas para usuário {current_user.id}")
        return queries
    except Exception as e:
        logger.error(f"Erro ao obter consultas salvas para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/queries/save", summary="Salvar consulta", tags=["analytics"])
async def save_query(
    query: AnalyticsQuery,
    name: str = Query(..., description="Nome da consulta"),
    description: Optional[str] = Query(None, description="Descrição"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Salva uma consulta para reutilização.
    
    Permite armazenar consultas customizadas com nome e descrição
    para facilitar análises recorrentes.
    
    Args:
        query: Consulta a ser salva
        name: Nome da consulta
        description: Descrição opcional
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Dados da consulta salva
        
    Raises:
        HTTPException: 400 se nome já existe
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Salvando consulta '{name}' para usuário {current_user.id}")
        service = AnalyticsService(db)
        saved_query = service.save_query(query, name, description, current_user.id)
        logger.info(f"Consulta '{name}' salva com sucesso para usuário {current_user.id}")
        return saved_query
    except ValueError as e:
        logger.warning(f"Erro ao salvar consulta '{name}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao salvar consulta '{name}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== DASHBOARDS ====================


@router.post("/dashboards", response_model=DashboardResponse, summary="Criar dashboard", tags=["analytics"])
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """
    Cria um novo dashboard personalizado.
    
    Permite criar dashboards customizados com widgets e visualizações
    específicas para análises personalizadas.
    
    Args:
        dashboard_data: Dados do dashboard a ser criado
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        DashboardResponse: Dashboard criado
        
    Raises:
        HTTPException: 400 se dados são inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Criando dashboard '{dashboard_data.name}' para usuário {current_user.id}")
        service = AnalyticsService(db)
        dashboard = service.create_dashboard(dashboard_data, current_user.id)
        logger.info(f"Dashboard '{dashboard_data.name}' criado com sucesso para usuário {current_user.id}")
        return dashboard
    except ValueError as e:
        logger.warning(f"Dados inválidos para dashboard '{dashboard_data.name}': {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar dashboard '{dashboard_data.name}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/dashboards", response_model=List[DashboardResponse], summary="Listar dashboards do usuário", tags=["analytics"])
async def get_user_dashboards(
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[DashboardResponse]:
    """
    Obtém dashboards do usuário com paginação.
    
    Retorna lista de todos os dashboards criados pelo usuário,
    permitindo navegação paginada.
    
    Args:
        limit: Limite de resultados por página
        offset: Offset para paginação
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        List[DashboardResponse]: Lista de dashboards do usuário
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando dashboards para usuário {current_user.id} - limite: {limit}, offset: {offset}")
        service = AnalyticsService(db)
        dashboards = service.get_user_dashboards(current_user.id, limit, offset)
        logger.info(f"Retornados {len(dashboards)} dashboards para usuário {current_user.id}")
        return dashboards
    except Exception as e:
        logger.error(f"Erro ao listar dashboards para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse, summary="Obter dashboard específico", tags=["analytics"])
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """
    Obtém detalhes de um dashboard específico.
    
    Retorna todas as informações de um dashboard, incluindo
    widgets, configurações e dados associados.
    
    Args:
        dashboard_id: ID do dashboard
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        DashboardResponse: Dados do dashboard
        
    Raises:
        HTTPException: 404 se dashboard não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo dashboard {dashboard_id} para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        dashboard_data = service.get_dashboard(dashboard_id, current_user.id)
        if not dashboard_data:
            logger.warning(f"Dashboard {dashboard_id} não encontrado para usuário {current_user.id}")
            raise HTTPException(status_code=404, detail="Dashboard não encontrado")

        dashboard_response = DashboardResponse(
            id=dashboard_data.get("id", dashboard_id),
            name=dashboard_data.get("name", "Dashboard Padrão"),
            description=dashboard_data.get("description", ""),
            is_public=dashboard_data.get("is_public", False),
            owner_id=current_user.id,
            widgets=dashboard_data.get("widgets", []),
            layout=dashboard_data.get("layout", {}),
            created_at=dashboard_data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=dashboard_data.get("updated_at", datetime.utcnow().isoformat())
        )
        
        logger.info(f"Dashboard {dashboard_id} obtido com sucesso para usuário {current_user.id}")
        return dashboard_response
    except ValueError as e:
        logger.warning(f"Dados inválidos ao obter dashboard {dashboard_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter dashboard {dashboard_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse, summary="Atualizar dashboard", tags=["analytics"])
async def update_dashboard(
    dashboard_id: int,
    dashboard_data: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """
    Atualiza um dashboard existente.
    
    Permite modificar nome, descrição, widgets e configurações
    de um dashboard existente do usuário.
    
    Args:
        dashboard_id: ID do dashboard
        dashboard_data: Dados atualizados do dashboard
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        DashboardResponse: Dashboard atualizado
        
    Raises:
        HTTPException: 404 se dashboard não encontrado
        HTTPException: 403 se sem permissão de edição
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Atualizando dashboard {dashboard_id} para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        try:
            updated_data = service.update_dashboard(dashboard_id, dashboard_data, current_user.id)
            if not updated_data:
                logger.warning(f"Dashboard {dashboard_id} não encontrado para usuário {current_user.id}")
                raise HTTPException(status_code=404, detail="Dashboard não encontrado")
            
            # Convert dictionary response to DashboardResponse model
            dashboard_response = DashboardResponse(
                id=updated_data.get("id", dashboard_id),
                name=updated_data.get("name", dashboard_data.name if hasattr(dashboard_data, 'name') else "Dashboard Atualizado"),
                description=updated_data.get("description", dashboard_data.description if hasattr(dashboard_data, 'description') else ""),
                is_public=updated_data.get("is_public", False),
                owner_id=current_user.id,
                widgets=updated_data.get("widgets", []),
                layout=updated_data.get("layout", {}),
                created_at=updated_data.get("created_at", datetime.utcnow().isoformat()),
                updated_at=updated_data.get("updated_at", datetime.utcnow().isoformat())
            )
            
            logger.info(f"Dashboard {dashboard_id} atualizado com sucesso para usuário {current_user.id}")
            return dashboard_response
            
        except ValueError as e:
            logger.warning(f"Dados inválidos ao atualizar dashboard {dashboard_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao atualizar dashboard {dashboard_id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao atualizar dashboard {dashboard_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/dashboards/{dashboard_id}/data", summary="Obter dados do dashboard", tags=["analytics"])
async def get_dashboard_data(
    dashboard_id: int,
    start_date: Optional[datetime] = Query(None, description="Data de início"),
    end_date: Optional[datetime] = Query(None, description="Data de fim"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Obtém dados atualizados para um dashboard específico.
    
    Retorna dados para populat widgets e visualizações
    do dashboard com informações atualizadas.
    
    Args:
        dashboard_id: ID do dashboard
        start_date: Data de início para filtrar dados (opcional)
        end_date: Data de fim para filtrar dados (opcional)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Dados do dashboard
        
    Raises:
        HTTPException: 404 se dashboard não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo dados do dashboard {dashboard_id} para usuário {current_user.id}")
        
        # Validate date parameters
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
        
        service = AnalyticsService(db)
        
        try:
            dashboard_data = service.get_dashboard_data(dashboard_id, current_user.id, start_date, end_date)
            if not dashboard_data:
                logger.warning(f"Dashboard {dashboard_id} não encontrado para usuário {current_user.id}")
                raise HTTPException(status_code=404, detail="Dashboard não encontrado")
            
            logger.info(f"Dados do dashboard {dashboard_id} obtidos com sucesso para usuário {current_user.id}")
            return dashboard_data
            
        except ValueError as e:
            logger.warning(f"Parâmetros inválidos para dashboard {dashboard_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Parâmetros inválidos: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter dados do dashboard {dashboard_id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao obter dados do dashboard {dashboard_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== INSIGHTS ====================


@router.get("/insights/user", summary="Insights do usuário", tags=["analytics"])
async def get_user_insights(
    period: str = Query("7d", pattern="^(1d|7d|30d|90d)$", description="Período de análise"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Obtém insights personalizados sobre o comportamento e performance do usuário.
    
    Analisa padrões de uso, tendências e métricas personalizadas
    para fornecer insights valiosos sobre a atividade do usuário.
    
    Args:
        period: Período de análise (1d, 7d, 30d, 90d)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Insights do usuário
        
    Raises:
        HTTPException: 400 se período inválido
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Gerando insights para usuário {current_user.id} - período: {period}")
        service = AnalyticsService(db)
        
        try:
            insights_data = service.get_user_insights(current_user.id, period)
            
            logger.info(f"Insights gerados com sucesso para usuário {current_user.id}")
            return insights_data
            
        except ValueError as e:
            logger.warning(f"Período inválido para insights do usuário {current_user.id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Período inválido: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao gerar insights do usuário {current_user.id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao gerar insights para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== REPORTS ====================


@router.get("/reports/{report_id}", summary="Obter relatório", tags=["analytics"])
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Obtém detalhes de um relatório específico.
    
    Retorna informações completas de um relatório,
    incluindo configurações e últimos resultados.
    
    Args:
        report_id: ID do relatório
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Dados do relatório
        
    Raises:
        HTTPException: 404 se relatório não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo relatório {report_id} para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        try:
            report_data = service.get_report(report_id, current_user.id)
            if not report_data:
                logger.warning(f"Relatório {report_id} não encontrado para usuário {current_user.id}")
                raise HTTPException(status_code=404, detail="Relatório não encontrado")
            
            logger.info(f"Relatório {report_id} obtido com sucesso para usuário {current_user.id}")
            return report_data
            
        except ValueError as e:
            logger.warning(f"Dados inválidos ao obter relatório {report_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter relatório {report_id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao obter relatório {report_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/reports/{report_id}", summary="Atualizar relatório", tags=["analytics"])
async def update_report(
    report_id: int,
    report_data: dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Atualiza um relatório existente.
    
    Permite modificar configurações, filtros e parâmetros
    de um relatório existente do usuário.
    
    Args:
        report_id: ID do relatório
        report_data: Dados atualizados do relatório
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Relatório atualizado
        
    Raises:
        HTTPException: 404 se relatório não encontrado
        HTTPException: 403 se sem permissão de edição
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Atualizando relatório {report_id} para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        try:
            updated_data = service.update_report(report_id, report_data, current_user.id)
            if not updated_data:
                logger.warning(f"Relatório {report_id} não encontrado para usuário {current_user.id}")
                raise HTTPException(status_code=404, detail="Relatório não encontrado")
            
            logger.info(f"Relatório {report_id} atualizado com sucesso para usuário {current_user.id}")
            return updated_data
            
        except ValueError as e:
            logger.warning(f"Dados inválidos ao atualizar relatório {report_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao atualizar relatório {report_id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao atualizar relatório {report_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/reports/{report_id}/execute", summary="Executar relatório", tags=["analytics"])
async def execute_report(
    report_id: int,
    parameters: Optional[dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Executa um relatório e retorna os resultados.
    
    Processa um relatório com os parâmetros fornecidos
    e retorna os dados resultantes.
    
    Args:
        report_id: ID do relatório
        parameters: Parâmetros opcionais para a execução
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Resultados da execução do relatório
        
    Raises:
        HTTPException: 404 se relatório não encontrado
        HTTPException: 403 se sem permissão de execução
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Executando relatório {report_id} para usuário {current_user.id}")
        service = AnalyticsService(db)
        
        try:
            execution_data = service.execute_report(report_id, current_user.id, parameters or {})
            if not execution_data:
                logger.warning(f"Relatório {report_id} não encontrado para usuário {current_user.id}")
                raise HTTPException(status_code=404, detail="Relatório não encontrado")
            
            logger.info(f"Relatório {report_id} executado com sucesso para usuário {current_user.id}")
            return execution_data
            
        except ValueError as e:
            logger.warning(f"Parâmetros inválidos ao executar relatório {report_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Parâmetros inválidos: {str(e)}")
        except Exception as service_error:
            logger.error(f"Erro no serviço ao executar relatório {report_id}: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro interno do servidor")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao executar relatório {report_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

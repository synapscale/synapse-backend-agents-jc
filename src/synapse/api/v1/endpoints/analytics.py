"""
Endpoints da API para Analytics
Criado por José - um desenvolvedor Full Stack
Endpoints para gerenciar analytics e insights
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.services.analytics_service import AnalyticsService
from src.synapse.schemas.analytics import (
    EventCreate, EventResponse, AnalyticsQuery, QueryResponse,
    DashboardCreate, DashboardUpdate, DashboardResponse, DashboardData,
    ReportCreate, ReportUpdate, ReportResponse, ReportExecutionResponse,
    InsightRequest, InsightResponse, SystemInsights, FunnelAnalysis,
    FunnelResult, CohortAnalysis, CohortResult, ABTestConfig, ABTestResult,
    ExportRequest, ExportResponse, RealTimeStats, AlertRule, AlertResponse
)
from src.synapse.api.deps import get_current_user, get_admin_user

router = APIRouter()

# ==================== EVENTOS ====================

@router.post("/events", response_model=EventResponse)
async def track_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra um evento de analytics"""
    service = AnalyticsService(db)
    return service.track_event(event_data, current_user.id)

@router.post("/events/batch")
async def track_events_batch(
    events: List[EventCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra múltiplos eventos em lote"""
    service = AnalyticsService(db)
    result = service.track_events_batch(events, current_user.id)
    return {"processed": result["processed"], "failed": result["failed"]}

@router.get("/events", response_model=List[EventResponse])
async def get_events(
    event_type: Optional[str] = Query(None, description="Tipo do evento"),
    start_date: Optional[datetime] = Query(None, description="Data de início"),
    end_date: Optional[datetime] = Query(None, description="Data de fim"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém eventos do usuário"""
    service = AnalyticsService(db)
    return service.get_user_events(
        current_user.id, event_type, start_date, end_date, limit, offset
    )

# ==================== MÉTRICAS ====================

@router.get("/metrics/user-behavior")
async def get_user_behavior_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("day", pattern="^(hour|day|week|month)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém métricas de comportamento do usuário"""
    service = AnalyticsService(db)
    return service.get_user_behavior_metrics(
        current_user.id, start_date, end_date, granularity
    )

@router.get("/metrics/system-performance")
async def get_system_performance_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("hour", pattern="^(minute|hour|day)$"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Obtém métricas de performance do sistema"""
    service = AnalyticsService(db)
    return service.get_system_performance_metrics(start_date, end_date, granularity)

@router.get("/metrics/business")
async def get_business_metrics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Obtém métricas de negócio"""
    service = AnalyticsService(db)
    return service.get_business_metrics(start_date, end_date, granularity)

@router.get("/metrics/real-time", response_model=RealTimeStats)
async def get_real_time_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém métricas em tempo real"""
    service = AnalyticsService(db)
    return service.get_real_time_metrics(current_user.id)

# ==================== CONSULTAS CUSTOMIZADAS ====================

@router.post("/queries", response_model=QueryResponse)
async def execute_analytics_query(
    query: AnalyticsQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa uma consulta customizada de analytics"""
    service = AnalyticsService(db)
    return service.execute_query(query, current_user.id)

@router.post("/queries/validate")
async def validate_analytics_query(
    query: AnalyticsQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Valida uma consulta de analytics"""
    service = AnalyticsService(db)
    validation = service.validate_query(query, current_user.id)
    return {"valid": validation["valid"], "errors": validation.get("errors", [])}

@router.get("/queries/saved")
async def get_saved_queries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém consultas salvas do usuário"""
    service = AnalyticsService(db)
    return service.get_saved_queries(current_user.id, limit, offset)

@router.post("/queries/save")
async def save_query(
    query: AnalyticsQuery,
    name: str = Query(..., description="Nome da consulta"),
    description: Optional[str] = Query(None, description="Descrição"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Salva uma consulta para reutilização"""
    service = AnalyticsService(db)
    saved_query = service.save_query(query, name, description, current_user.id)
    return {"id": saved_query.id, "message": "Consulta salva com sucesso"}

# ==================== DASHBOARDS ====================

@router.post("/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo dashboard"""
    service = AnalyticsService(db)
    return service.create_dashboard(dashboard_data, current_user.id)

@router.get("/dashboards", response_model=List[DashboardResponse])
async def get_user_dashboards(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém dashboards do usuário"""
    service = AnalyticsService(db)
    return service.get_user_dashboards(current_user.id, limit, offset)

@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um dashboard"""
    service = AnalyticsService(db)
    dashboard = service.get_dashboard(dashboard_id, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return dashboard

@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: int,
    dashboard_data: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um dashboard"""
    service = AnalyticsService(db)
    dashboard = service.update_dashboard(dashboard_id, dashboard_data, current_user.id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return dashboard

@router.delete("/dashboards/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um dashboard"""
    service = AnalyticsService(db)
    success = service.delete_dashboard(dashboard_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return {"message": "Dashboard removido com sucesso"}

@router.get("/dashboards/{dashboard_id}/data", response_model=DashboardData)
async def get_dashboard_data(
    dashboard_id: int,
    refresh: bool = Query(False, description="Forçar atualização dos dados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém dados do dashboard"""
    service = AnalyticsService(db)
    data = service.get_dashboard_data(dashboard_id, current_user.id, refresh)
    if not data:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return data

@router.post("/dashboards/{dashboard_id}/share")
async def share_dashboard(
    dashboard_id: int,
    public: bool = Query(True, description="Tornar público"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compartilha um dashboard"""
    service = AnalyticsService(db)
    share_info = service.share_dashboard(dashboard_id, public, current_user.id)
    if not share_info:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")
    return share_info

# ==================== RELATÓRIOS ====================

@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo relatório"""
    service = AnalyticsService(db)
    return service.create_report(report_data, current_user.id)

@router.get("/reports", response_model=List[ReportResponse])
async def get_user_reports(
    status: Optional[str] = Query(None, pattern="^(draft|scheduled|running|completed|failed)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém relatórios do usuário"""
    service = AnalyticsService(db)
    return service.get_user_reports(current_user.id, status, limit, offset)

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um relatório"""
    service = AnalyticsService(db)
    report = service.get_report(report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report

@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um relatório"""
    service = AnalyticsService(db)
    report = service.update_report(report_id, report_data, current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report

@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um relatório"""
    service = AnalyticsService(db)
    success = service.delete_report(report_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return {"message": "Relatório removido com sucesso"}

@router.post("/reports/{report_id}/execute", response_model=ReportExecutionResponse)
async def execute_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa um relatório"""
    service = AnalyticsService(db)
    execution = service.execute_report(report_id, current_user.id)
    if not execution:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    
    # Executar relatório em background
    background_tasks.add_task(service.process_report_execution, execution.id)
    
    return execution

@router.get("/reports/{report_id}/executions", response_model=List[ReportExecutionResponse])
async def get_report_executions(
    report_id: int,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém execuções de um relatório"""
    service = AnalyticsService(db)
    executions = service.get_report_executions(report_id, current_user.id, limit, offset)
    if executions is None:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return executions

# ==================== INSIGHTS ====================

@router.post("/insights", response_model=InsightResponse)
async def generate_insights(
    insight_request: InsightRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gera insights automáticos"""
    service = AnalyticsService(db)
    return service.generate_insights(insight_request, current_user.id)

@router.get("/insights/system", response_model=SystemInsights)
async def get_system_insights(
    days: int = Query(7, ge=1, le=90, description="Período em dias"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Obtém insights do sistema"""
    service = AnalyticsService(db)
    return service.get_system_insights(days)

@router.get("/insights/user")
async def get_user_insights(
    days: int = Query(30, ge=1, le=365, description="Período em dias"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém insights personalizados do usuário"""
    service = AnalyticsService(db)
    return service.get_user_insights(current_user.id, days)

@router.get("/insights/trends")
async def get_trending_insights(
    category: Optional[str] = Query(None, description="Categoria de insights"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém insights em tendência"""
    service = AnalyticsService(db)
    return service.get_trending_insights(category, limit, current_user.id)

# ==================== ANÁLISES AVANÇADAS ====================

@router.post("/analysis/funnel", response_model=FunnelResult)
async def analyze_funnel(
    funnel_config: FunnelAnalysis,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa análise de funil"""
    service = AnalyticsService(db)
    return service.analyze_funnel(funnel_config, current_user.id)

@router.post("/analysis/cohort", response_model=CohortResult)
async def analyze_cohort(
    cohort_config: CohortAnalysis,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa análise de coorte"""
    service = AnalyticsService(db)
    return service.analyze_cohort(cohort_config, current_user.id)

@router.post("/analysis/ab-test", response_model=ABTestResult)
async def analyze_ab_test(
    test_config: ABTestConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa análise de teste A/B"""
    service = AnalyticsService(db)
    return service.analyze_ab_test(test_config, current_user.id)

@router.get("/analysis/correlation")
async def analyze_correlation(
    metric1: str = Query(..., description="Primeira métrica"),
    metric2: str = Query(..., description="Segunda métrica"),
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analisa correlação entre métricas"""
    service = AnalyticsService(db)
    return service.analyze_correlation(metric1, metric2, start_date, end_date, current_user.id)

@router.get("/analysis/anomalies")
async def detect_anomalies(
    metric: str = Query(..., description="Métrica para análise"),
    days: int = Query(30, ge=7, le=365, description="Período em dias"),
    sensitivity: float = Query(0.95, ge=0.8, le=0.99, description="Sensibilidade"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detecta anomalias em métricas"""
    service = AnalyticsService(db)
    return service.detect_anomalies(metric, days, sensitivity, current_user.id)

# ==================== EXPORTAÇÃO ====================

@router.post("/export", response_model=ExportResponse)
async def export_data(
    export_request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exporta dados de analytics"""
    service = AnalyticsService(db)
    export_job = service.create_export_job(export_request, current_user.id)
    
    # Processar exportação em background
    background_tasks.add_task(service.process_export_job, export_job.id)
    
    return export_job

@router.get("/exports", response_model=List[ExportResponse])
async def get_user_exports(
    status: Optional[str] = Query(None, pattern="^(pending|processing|completed|failed)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém exportações do usuário"""
    service = AnalyticsService(db)
    return service.get_user_exports(current_user.id, status, limit, offset)

@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Faz download de uma exportação"""
    service = AnalyticsService(db)
    download_info = service.get_export_download(export_id, current_user.id)
    if not download_info:
        raise HTTPException(status_code=404, detail="Exportação não encontrada")
    return download_info

# ==================== ALERTAS ====================

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_rule: AlertRule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um alerta"""
    service = AnalyticsService(db)
    return service.create_alert(alert_rule, current_user.id)

@router.get("/alerts", response_model=List[AlertResponse])
async def get_user_alerts(
    status: Optional[str] = Query(None, pattern="^(active|paused|triggered)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém alertas do usuário"""
    service = AnalyticsService(db)
    return service.get_user_alerts(current_user.id, status, limit, offset)

@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_rule: AlertRule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um alerta"""
    service = AnalyticsService(db)
    alert = service.update_alert(alert_id, alert_rule, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return alert

@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um alerta"""
    service = AnalyticsService(db)
    success = service.delete_alert(alert_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"message": "Alerta removido com sucesso"}

@router.post("/alerts/{alert_id}/pause")
async def pause_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pausa um alerta"""
    service = AnalyticsService(db)
    success = service.pause_alert(alert_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"message": "Alerta pausado"}

@router.post("/alerts/{alert_id}/resume")
async def resume_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retoma um alerta"""
    service = AnalyticsService(db)
    success = service.resume_alert(alert_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"message": "Alerta retomado"}

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/stats")
async def get_admin_analytics_stats(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas administrativas de analytics"""
    service = AnalyticsService(db)
    return service.get_admin_stats()

@router.post("/admin/cleanup")
async def cleanup_old_data(
    days: int = Query(90, ge=30, le=365, description="Manter dados dos últimos N dias"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Limpa dados antigos de analytics"""
    service = AnalyticsService(db)
    result = service.cleanup_old_data(days)
    return {"message": f"Limpeza concluída. {result['deleted']} registros removidos"}

@router.post("/admin/recompute-metrics")
async def recompute_metrics(
    background_tasks: BackgroundTasks,
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Recomputa métricas para um período"""
    service = AnalyticsService(db)
    job_id = service.create_recompute_job(start_date, end_date)
    
    # Processar recomputação em background
    background_tasks.add_task(service.process_recompute_job, job_id)
    
    return {"message": "Recomputação iniciada", "job_id": job_id}


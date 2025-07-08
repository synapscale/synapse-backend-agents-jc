"""
Schemas para AnalyticsReport - relatórios de analytics
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AnalyticsReportBase(BaseModel):
    """Schema base para AnalyticsReport"""
    
    # Identificação
    name: str = Field(..., description="Nome do relatório")
    description: Optional[str] = Field(None, description="Descrição do relatório")
    
    # Tipo e categoria
    report_type: str = Field(..., description="Tipo do relatório")
    category: str = Field(..., description="Categoria do relatório")
    
    # Configuração do relatório
    configuration: Dict[str, Any] = Field(..., description="Configuração do relatório")
    
    # Período
    period_type: str = Field(..., description="Tipo de período (daily, weekly, monthly, custom)")
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    # Filtros
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")
    
    # Status
    status: str = Field("pending", description="Status do relatório")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário criador")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsReportCreate(AnalyticsReportBase):
    """Schema para criação de AnalyticsReport"""
    pass


class AnalyticsReportUpdate(BaseModel):
    """Schema para atualização de AnalyticsReport"""
    
    name: Optional[str] = Field(None, description="Nome do relatório")
    description: Optional[str] = Field(None, description="Descrição do relatório")
    
    report_type: Optional[str] = Field(None, description="Tipo do relatório")
    category: Optional[str] = Field(None, description="Categoria do relatório")
    
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração do relatório")
    
    period_type: Optional[str] = Field(None, description="Tipo de período")
    period_start: Optional[datetime] = Field(None, description="Início do período")
    period_end: Optional[datetime] = Field(None, description="Fim do período")
    
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")
    status: Optional[str] = Field(None, description="Status do relatório")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsReportResponse(AnalyticsReportBase):
    """Schema para resposta de AnalyticsReport"""
    
    id: UUID = Field(..., description="ID único do relatório")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Resultado do relatório
    result_data: Optional[Dict[str, Any]] = Field(None, description="Dados do resultado")
    
    # Métricas de execução
    execution_time_ms: Optional[int] = Field(None, description="Tempo de execução em ms")
    data_points: Optional[int] = Field(None, description="Número de pontos de dados")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário criador")
    
    # Timestamps de execução
    started_at: Optional[datetime] = Field(None, description="Início da execução")
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportList(BaseModel):
    """Schema para lista de AnalyticsReport"""
    
    items: List[AnalyticsReportResponse] = Field(..., description="Lista de relatórios")
    total: int = Field(..., description="Total de relatórios")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportExecution(BaseModel):
    """Schema para execução de AnalyticsReport"""
    
    report_id: UUID = Field(..., description="ID do relatório")
    
    # Parâmetros de execução
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de execução")
    
    # Configurações
    async_execution: bool = Field(True, description="Execução assíncrona")
    cache_results: bool = Field(True, description="Cachear resultados")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportResult(BaseModel):
    """Schema para resultado de AnalyticsReport"""
    
    report_id: UUID = Field(..., description="ID do relatório")
    execution_id: UUID = Field(..., description="ID da execução")
    
    # Resultado
    data: Dict[str, Any] = Field(..., description="Dados do resultado")
    
    # Estatísticas
    total_records: int = Field(..., description="Total de registros")
    processed_records: int = Field(..., description="Registros processados")
    
    # Métricas
    execution_time_ms: int = Field(..., description="Tempo de execução em ms")
    memory_used_mb: Optional[float] = Field(None, description="Memória usada em MB")
    
    # Timestamps
    generated_at: datetime = Field(..., description="Data de geração")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportSchedule(BaseModel):
    """Schema para agendamento de AnalyticsReport"""
    
    report_id: UUID = Field(..., description="ID do relatório")
    
    # Configuração do agendamento
    schedule_type: str = Field(..., description="Tipo de agendamento (cron, interval)")
    schedule_expression: str = Field(..., description="Expressão do agendamento")
    
    # Status
    is_active: bool = Field(True, description="Agendamento ativo")
    
    # Configurações
    timezone: str = Field("UTC", description="Fuso horário")
    
    # Notificações
    notify_on_completion: bool = Field(True, description="Notificar na conclusão")
    notify_on_failure: bool = Field(True, description="Notificar em falha")
    notification_recipients: Optional[List[str]] = Field(None, description="Destinatários das notificações")
    
    # Timestamps
    next_execution: Optional[datetime] = Field(None, description="Próxima execução")
    last_execution: Optional[datetime] = Field(None, description="Última execução")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportTemplate(BaseModel):
    """Schema para template de AnalyticsReport"""
    
    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    
    # Configuração do template
    template_config: Dict[str, Any] = Field(..., description="Configuração do template")
    
    # Categoria
    category: str = Field(..., description="Categoria do template")
    
    # Parâmetros
    parameters: List[Dict[str, Any]] = Field(..., description="Parâmetros do template")
    
    # Visualização
    visualization_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de visualização")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportStatistics(BaseModel):
    """Schema para estatísticas de AnalyticsReport"""
    
    total_reports: int = Field(..., description="Total de relatórios")
    active_reports: int = Field(..., description="Relatórios ativos")
    
    # Por status
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    
    # Execuções
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Performance
    average_execution_time_ms: float = Field(..., description="Tempo médio de execução")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportExport(BaseModel):
    """Schema para exportação de AnalyticsReport"""
    
    report_id: UUID = Field(..., description="ID do relatório")
    format: str = Field(..., description="Formato da exportação")
    
    # Configurações
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_charts: bool = Field(True, description="Incluir gráficos")
    
    model_config = ConfigDict(from_attributes=True)

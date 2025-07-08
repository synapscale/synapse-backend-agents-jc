"""
Schemas para AnalyticsMetric - métricas de analytics
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AnalyticsMetricBase(BaseModel):
    """Schema base para AnalyticsMetric"""
    
    # Identificação da métrica
    metric_name: str = Field(..., description="Nome da métrica")
    metric_type: str = Field(..., description="Tipo da métrica")
    
    # Valor da métrica
    value: float = Field(..., description="Valor da métrica")
    unit: Optional[str] = Field(None, description="Unidade de medida")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    
    # Dimensões
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Dimensões da métrica")
    
    # Timestamp
    timestamp: datetime = Field(..., description="Timestamp da métrica")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsMetricCreate(AnalyticsMetricBase):
    """Schema para criação de AnalyticsMetric"""
    pass


class AnalyticsMetricUpdate(BaseModel):
    """Schema para atualização de AnalyticsMetric"""
    
    value: Optional[float] = Field(None, description="Valor da métrica")
    unit: Optional[str] = Field(None, description="Unidade de medida")
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Dimensões da métrica")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsMetricResponse(AnalyticsMetricBase):
    """Schema para resposta de AnalyticsMetric"""
    
    id: UUID = Field(..., description="ID único da métrica")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    workspace_name: Optional[str] = Field(None, description="Nome do workspace")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricList(BaseModel):
    """Schema para lista de AnalyticsMetric"""
    
    items: List[AnalyticsMetricResponse] = Field(..., description="Lista de métricas")
    total: int = Field(..., description="Total de métricas")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricBatch(BaseModel):
    """Schema para lote de AnalyticsMetric"""
    
    metrics: List[AnalyticsMetricCreate] = Field(..., description="Lista de métricas")
    
    # Configurações do lote
    batch_id: Optional[str] = Field(None, description="ID do lote")
    source: Optional[str] = Field(None, description="Origem do lote")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricFilter(BaseModel):
    """Schema para filtros de AnalyticsMetric"""
    
    metric_name: Optional[str] = Field(None, description="Nome da métrica")
    metric_type: Optional[str] = Field(None, description="Tipo da métrica")
    
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    
    # Filtros de valor
    min_value: Optional[float] = Field(None, description="Valor mínimo")
    max_value: Optional[float] = Field(None, description="Valor máximo")
    
    # Filtros temporais
    start_time: Optional[datetime] = Field(None, description="Início do período")
    end_time: Optional[datetime] = Field(None, description="Fim do período")
    
    # Filtros de dimensões
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Filtros de dimensões")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricAggregation(BaseModel):
    """Schema para agregação de AnalyticsMetric"""
    
    # Configuração da agregação
    aggregation_type: str = Field(..., description="Tipo de agregação (sum, avg, min, max, count)")
    group_by: Optional[List[str]] = Field(None, description="Campos para agrupamento")
    
    # Filtros
    filters: Optional[AnalyticsMetricFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações temporais
    time_interval: Optional[str] = Field(None, description="Intervalo de tempo")
    time_zone: Optional[str] = Field(None, description="Fuso horário")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricAggregationResult(BaseModel):
    """Schema para resultado da agregação"""
    
    # Resultado
    data: List[Dict[str, Any]] = Field(..., description="Dados agregados")
    
    # Configuração usada
    aggregation_type: str = Field(..., description="Tipo de agregação")
    group_by: Optional[List[str]] = Field(None, description="Campos de agrupamento")
    
    # Métricas
    total_metrics: int = Field(..., description="Total de métricas")
    processed_metrics: int = Field(..., description="Métricas processadas")
    
    # Timestamps
    generated_at: datetime = Field(..., description="Data de geração")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricTimeSeries(BaseModel):
    """Schema para série temporal de AnalyticsMetric"""
    
    # Configuração da série temporal
    metric_name: str = Field(..., description="Nome da métrica")
    interval: str = Field(..., description="Intervalo da série temporal")
    
    # Filtros
    filters: Optional[AnalyticsMetricFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações
    fill_missing: bool = Field(True, description="Preencher valores ausentes")
    aggregation: str = Field("avg", description="Tipo de agregação")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricTimeSeriesResult(BaseModel):
    """Schema para resultado da série temporal"""
    
    # Resultado
    data: List[Dict[str, Any]] = Field(..., description="Dados da série temporal")
    
    # Configuração usada
    metric_name: str = Field(..., description="Nome da métrica")
    interval: str = Field(..., description="Intervalo usado")
    
    # Métricas
    data_points: int = Field(..., description="Número de pontos de dados")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricAlert(BaseModel):
    """Schema para alerta de AnalyticsMetric"""
    
    # Configuração do alerta
    metric_name: str = Field(..., description="Nome da métrica")
    condition: str = Field(..., description="Condição do alerta")
    threshold: float = Field(..., description="Valor limite")
    
    # Configurações
    is_active: bool = Field(True, description="Alerta ativo")
    aggregation_window: str = Field("5m", description="Janela de agregação")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário criador")
    
    # Notificação
    notification_channels: List[str] = Field(..., description="Canais de notificação")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricAlertTrigger(BaseModel):
    """Schema para trigger de alerta"""
    
    alert_id: UUID = Field(..., description="ID do alerta")
    metric_value: float = Field(..., description="Valor da métrica")
    threshold: float = Field(..., description="Valor limite")
    
    # Contexto
    triggered_at: datetime = Field(..., description="Data do trigger")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricStatistics(BaseModel):
    """Schema para estatísticas de AnalyticsMetric"""
    
    total_metrics: int = Field(..., description="Total de métricas")
    unique_metric_names: int = Field(..., description="Nomes únicos de métricas")
    
    # Por tipo
    by_metric_type: Dict[str, int] = Field(..., description="Por tipo de métrica")
    by_metric_name: Dict[str, int] = Field(..., description="Por nome da métrica")
    
    # Por contexto
    by_tenant: Dict[str, int] = Field(..., description="Por tenant")
    by_user: Dict[str, int] = Field(..., description="Por usuário")
    by_workspace: Dict[str, int] = Field(..., description="Por workspace")
    
    # Valores
    min_value: float = Field(..., description="Valor mínimo")
    max_value: float = Field(..., description="Valor máximo")
    avg_value: float = Field(..., description="Valor médio")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsMetricExport(BaseModel):
    """Schema para exportação de AnalyticsMetric"""
    
    format: str = Field(..., description="Formato da exportação")
    filters: Optional[AnalyticsMetricFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_dimensions: bool = Field(True, description="Incluir dimensões")
    max_records: Optional[int] = Field(None, description="Máximo de registros")
    
    model_config = ConfigDict(from_attributes=True)

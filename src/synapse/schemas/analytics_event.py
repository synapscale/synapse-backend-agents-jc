"""
Schemas para AnalyticsEvent - eventos de analytics
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AnalyticsEventBase(BaseModel):
    """Schema base para AnalyticsEvent"""
    
    # Identificação do evento
    event_type: str = Field(..., description="Tipo do evento")
    event_name: str = Field(..., description="Nome do evento")
    
    # Dados do evento
    event_data: Dict[str, Any] = Field(..., description="Dados do evento")
    
    # Contexto do usuário
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    
    # Contexto do sistema
    tenant_id: UUID = Field(..., description="ID do tenant")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    
    # Contexto técnico
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    platform: Optional[str] = Field(None, description="Plataforma")
    device_type: Optional[str] = Field(None, description="Tipo de dispositivo")
    
    # Geolocalização
    country: Optional[str] = Field(None, description="País")
    city: Optional[str] = Field(None, description="Cidade")
    
    # Timestamp
    timestamp: datetime = Field(..., description="Timestamp do evento")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsEventCreate(AnalyticsEventBase):
    """Schema para criação de AnalyticsEvent"""
    pass


class AnalyticsEventUpdate(BaseModel):
    """Schema para atualização de AnalyticsEvent"""
    
    event_data: Optional[Dict[str, Any]] = Field(None, description="Dados do evento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AnalyticsEventResponse(AnalyticsEventBase):
    """Schema para resposta de AnalyticsEvent"""
    
    id: UUID = Field(..., description="ID único do evento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    workspace_name: Optional[str] = Field(None, description="Nome do workspace")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventList(BaseModel):
    """Schema para lista de AnalyticsEvent"""
    
    items: List[AnalyticsEventResponse] = Field(..., description="Lista de eventos")
    total: int = Field(..., description="Total de eventos")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventBatch(BaseModel):
    """Schema para lote de AnalyticsEvent"""
    
    events: List[AnalyticsEventCreate] = Field(..., description="Lista de eventos")
    
    # Configurações do lote
    batch_id: Optional[str] = Field(None, description="ID do lote")
    source: Optional[str] = Field(None, description="Origem do lote")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventFilter(BaseModel):
    """Schema para filtros de AnalyticsEvent"""
    
    event_type: Optional[str] = Field(None, description="Tipo do evento")
    event_name: Optional[str] = Field(None, description="Nome do evento")
    
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    
    # Filtros temporais
    start_time: Optional[datetime] = Field(None, description="Início do período")
    end_time: Optional[datetime] = Field(None, description="Fim do período")
    
    # Filtros geográficos
    country: Optional[str] = Field(None, description="País")
    city: Optional[str] = Field(None, description="Cidade")
    
    # Filtros técnicos
    platform: Optional[str] = Field(None, description="Plataforma")
    device_type: Optional[str] = Field(None, description="Tipo de dispositivo")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventAggregation(BaseModel):
    """Schema para agregação de AnalyticsEvent"""
    
    # Configuração da agregação
    group_by: List[str] = Field(..., description="Campos para agrupamento")
    aggregation_type: str = Field(..., description="Tipo de agregação (count, sum, avg, etc)")
    
    # Filtros
    filters: Optional[AnalyticsEventFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações
    time_interval: Optional[str] = Field(None, description="Intervalo de tempo")
    limit: Optional[int] = Field(None, description="Limite de resultados")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventAggregationResult(BaseModel):
    """Schema para resultado da agregação"""
    
    # Resultado
    data: List[Dict[str, Any]] = Field(..., description="Dados agregados")
    
    # Configuração usada
    group_by: List[str] = Field(..., description="Campos de agrupamento")
    aggregation_type: str = Field(..., description="Tipo de agregação")
    
    # Métricas
    total_events: int = Field(..., description="Total de eventos")
    processed_events: int = Field(..., description="Eventos processados")
    
    # Timestamps
    generated_at: datetime = Field(..., description="Data de geração")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventStatistics(BaseModel):
    """Schema para estatísticas de AnalyticsEvent"""
    
    total_events: int = Field(..., description="Total de eventos")
    
    # Por tipo
    by_event_type: Dict[str, int] = Field(..., description="Por tipo de evento")
    by_event_name: Dict[str, int] = Field(..., description="Por nome do evento")
    
    # Por contexto
    by_user: Dict[str, int] = Field(..., description="Por usuário")
    by_workspace: Dict[str, int] = Field(..., description="Por workspace")
    by_platform: Dict[str, int] = Field(..., description="Por plataforma")
    by_device_type: Dict[str, int] = Field(..., description="Por tipo de dispositivo")
    
    # Por geografia
    by_country: Dict[str, int] = Field(..., description="Por país")
    by_city: Dict[str, int] = Field(..., description="Por cidade")
    
    # Por tempo
    events_by_hour: Dict[str, int] = Field(..., description="Eventos por hora")
    events_by_day: Dict[str, int] = Field(..., description="Eventos por dia")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventFunnel(BaseModel):
    """Schema para funil de AnalyticsEvent"""
    
    # Configuração do funil
    steps: List[Dict[str, Any]] = Field(..., description="Passos do funil")
    
    # Filtros
    filters: Optional[AnalyticsEventFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações
    time_window: Optional[str] = Field(None, description="Janela de tempo")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventFunnelResult(BaseModel):
    """Schema para resultado do funil"""
    
    # Resultado
    funnel_data: List[Dict[str, Any]] = Field(..., description="Dados do funil")
    
    # Métricas
    total_users: int = Field(..., description="Total de usuários")
    conversion_rate: float = Field(..., description="Taxa de conversão")
    
    # Por passo
    step_conversions: List[Dict[str, Any]] = Field(..., description="Conversões por passo")
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsEventExport(BaseModel):
    """Schema para exportação de AnalyticsEvent"""
    
    format: str = Field(..., description="Formato da exportação")
    filters: Optional[AnalyticsEventFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações
    include_metadata: bool = Field(True, description="Incluir metadata")
    max_records: Optional[int] = Field(None, description="Máximo de registros")
    
    model_config = ConfigDict(from_attributes=True)

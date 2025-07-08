"""
Schemas para AuditLog - logs de auditoria do sistema
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AuditLogBase(BaseModel):
    """Schema base para AuditLog"""
    
    # Identificação do usuário
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Ação realizada
    action: str = Field(..., description="Ação realizada")
    resource_type: str = Field(..., description="Tipo do recurso")
    resource_id: Optional[UUID] = Field(None, description="ID do recurso")
    
    # Detalhes da ação
    operation: str = Field(..., description="Operação (CREATE, UPDATE, DELETE, etc)")
    status: str = Field(..., description="Status da operação (SUCCESS, FAILED, etc)")
    
    # Dados da operação
    old_values: Optional[Dict[str, Any]] = Field(None, description="Valores antigos")
    new_values: Optional[Dict[str, Any]] = Field(None, description="Valores novos")
    
    # Contexto técnico
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Contexto do sistema
    system_context: Optional[Dict[str, Any]] = Field(None, description="Contexto do sistema")
    
    # Severity e categorização
    severity: str = Field("INFO", description="Severidade (INFO, WARNING, ERROR, CRITICAL)")
    category: str = Field("GENERAL", description="Categoria do log")


class AuditLogCreate(AuditLogBase):
    """Schema para criação de AuditLog"""
    pass


class AuditLogUpdate(BaseModel):
    """Schema para atualização de AuditLog"""
    
    status: Optional[str] = Field(None, description="Status da operação")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    severity: Optional[str] = Field(None, description="Severidade")
    category: Optional[str] = Field(None, description="Categoria")


class AuditLogResponse(AuditLogBase):
    """Schema para resposta de AuditLog"""
    
    id: UUID = Field(..., description="ID único do log")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    resource_name: Optional[str] = Field(None, description="Nome do recurso")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogList(BaseModel):
    """Schema para lista de AuditLog"""
    
    items: List[AuditLogResponse] = Field(..., description="Lista de logs")
    total: int = Field(..., description="Total de logs")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    """Schema para filtros de AuditLog"""
    
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")
    
    action: Optional[str] = Field(None, description="Ação")
    resource_type: Optional[str] = Field(None, description="Tipo do recurso")
    resource_id: Optional[UUID] = Field(None, description="ID do recurso")
    
    operation: Optional[str] = Field(None, description="Operação")
    status: Optional[str] = Field(None, description="Status")
    severity: Optional[str] = Field(None, description="Severidade")
    category: Optional[str] = Field(None, description="Categoria")
    
    # Filtros de tempo
    start_date: Optional[datetime] = Field(None, description="Data de início")
    end_date: Optional[datetime] = Field(None, description="Data de fim")
    
    # Filtros de contexto
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogStatistics(BaseModel):
    """Schema para estatísticas de AuditLog"""
    
    total_logs: int = Field(..., description="Total de logs")
    
    # Por status
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_operation: Dict[str, int] = Field(..., description="Por operação")
    by_severity: Dict[str, int] = Field(..., description="Por severidade")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    by_resource_type: Dict[str, int] = Field(..., description="Por tipo de recurso")
    
    # Por usuário
    top_users: List[Dict[str, Any]] = Field(..., description="Usuários mais ativos")
    
    # Por tempo
    logs_by_hour: Dict[str, int] = Field(..., description="Logs por hora")
    logs_by_day: Dict[str, int] = Field(..., description="Logs por dia")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogSummary(BaseModel):
    """Schema para resumo de AuditLog"""
    
    date: datetime = Field(..., description="Data")
    total_actions: int = Field(..., description="Total de ações")
    successful_actions: int = Field(..., description="Ações bem-sucedidas")
    failed_actions: int = Field(..., description="Ações falhadas")
    
    unique_users: int = Field(..., description="Usuários únicos")
    unique_resources: int = Field(..., description="Recursos únicos")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogAlert(BaseModel):
    """Schema para alertas de AuditLog"""
    
    alert_type: str = Field(..., description="Tipo do alerta")
    severity: str = Field(..., description="Severidade")
    message: str = Field(..., description="Mensagem do alerta")
    
    # Contexto
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Dados do alerta
    threshold_value: Optional[float] = Field(None, description="Valor do threshold")
    current_value: Optional[float] = Field(None, description="Valor atual")
    
    # Timestamps
    triggered_at: datetime = Field(..., description="Data do trigger")
    resolved_at: Optional[datetime] = Field(None, description="Data da resolução")
    
    model_config = ConfigDict(from_attributes=True)


class AuditLogExport(BaseModel):
    """Schema para exportação de AuditLog"""
    
    format: str = Field(..., description="Formato da exportação (csv, json, pdf)")
    filters: Optional[AuditLogFilter] = Field(None, description="Filtros aplicados")
    
    # Configurações de exportação
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_system_context: bool = Field(False, description="Incluir contexto do sistema")
    
    model_config = ConfigDict(from_attributes=True)

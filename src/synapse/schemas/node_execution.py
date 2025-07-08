"""
Schemas para NodeExecution - execuções de nós
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class NodeExecutionBase(BaseModel):
    """Schema base para NodeExecution"""
    
    # Relacionamentos
    node_id: UUID = Field(..., description="ID do nó")
    workflow_execution_id: Optional[UUID] = Field(None, description="ID da execução do workflow")
    
    # Dados de entrada
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    
    # Resultado da execução
    output_data: Optional[Dict[str, Any]] = Field(None, description="Dados de saída")
    
    # Status
    status: str = Field("pending", description="Status da execução")
    
    # Métricas
    execution_time_ms: Optional[int] = Field(None, description="Tempo de execução em ms")
    memory_used_mb: Optional[float] = Field(None, description="Memória usada em MB")
    cpu_usage_percent: Optional[float] = Field(None, description="Uso de CPU em %")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_stack: Optional[str] = Field(None, description="Stack trace do erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    
    # Timestamps
    started_at: Optional[datetime] = Field(None, description="Início da execução")
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class NodeExecutionCreate(NodeExecutionBase):
    """Schema para criação de NodeExecution"""
    pass


class NodeExecutionUpdate(BaseModel):
    """Schema para atualização de NodeExecution"""
    
    output_data: Optional[Dict[str, Any]] = Field(None, description="Dados de saída")
    status: Optional[str] = Field(None, description="Status da execução")
    
    execution_time_ms: Optional[int] = Field(None, description="Tempo de execução em ms")
    memory_used_mb: Optional[float] = Field(None, description="Memória usada em MB")
    cpu_usage_percent: Optional[float] = Field(None, description="Uso de CPU em %")
    
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_stack: Optional[str] = Field(None, description="Stack trace do erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class NodeExecutionResponse(NodeExecutionBase):
    """Schema para resposta de NodeExecution"""
    
    id: UUID = Field(..., description="ID único da execução")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    node_name: Optional[str] = Field(None, description="Nome do nó")
    node_type: Optional[str] = Field(None, description="Tipo do nó")
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    
    # Duração calculada
    duration_ms: Optional[int] = Field(None, description="Duração da execução em ms")
    
    # Status derivados
    is_completed: Optional[bool] = Field(None, description="Execução completada")
    is_failed: Optional[bool] = Field(None, description="Execução falhou")
    is_running: Optional[bool] = Field(None, description="Execução em andamento")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionList(BaseModel):
    """Schema para lista de NodeExecution"""
    
    items: List[NodeExecutionResponse] = Field(..., description="Lista de execuções")
    total: int = Field(..., description="Total de execuções")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionTrigger(BaseModel):
    """Schema para trigger de NodeExecution"""
    
    node_id: UUID = Field(..., description="ID do nó")
    
    # Dados de entrada
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    
    # Configurações da execução
    execution_config: Optional[Dict[str, Any]] = Field(None, description="Configuração da execução")
    
    # Contexto
    workflow_execution_id: Optional[UUID] = Field(None, description="ID da execução do workflow")
    
    # Prioridade
    priority: int = Field(1, description="Prioridade da execução")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionTriggerResult(BaseModel):
    """Schema para resultado do trigger"""
    
    execution_id: UUID = Field(..., description="ID da execução criada")
    node_id: UUID = Field(..., description="ID do nó")
    
    # Status
    status: str = Field(..., description="Status inicial")
    
    # Timestamp
    triggered_at: datetime = Field(..., description="Data do trigger")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionCancel(BaseModel):
    """Schema para cancelamento de NodeExecution"""
    
    execution_id: UUID = Field(..., description="ID da execução")
    
    # Motivo do cancelamento
    reason: Optional[str] = Field(None, description="Motivo do cancelamento")
    
    # Forçar cancelamento
    force: bool = Field(False, description="Forçar cancelamento")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionCancelResult(BaseModel):
    """Schema para resultado do cancelamento"""
    
    execution_id: UUID = Field(..., description="ID da execução")
    
    # Resultado
    cancelled: bool = Field(..., description="Cancelamento bem-sucedido")
    
    # Timestamp
    cancelled_at: datetime = Field(..., description="Data do cancelamento")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionRetry(BaseModel):
    """Schema para retry de NodeExecution"""
    
    execution_id: UUID = Field(..., description="ID da execução original")
    
    # Configurações do retry
    retry_config: Optional[Dict[str, Any]] = Field(None, description="Configuração do retry")
    
    # Novos dados de entrada (opcional)
    new_input_data: Optional[Dict[str, Any]] = Field(None, description="Novos dados de entrada")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionRetryResult(BaseModel):
    """Schema para resultado do retry"""
    
    original_execution_id: UUID = Field(..., description="ID da execução original")
    new_execution_id: UUID = Field(..., description="ID da nova execução")
    
    # Timestamp
    retried_at: datetime = Field(..., description="Data do retry")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatistics(BaseModel):
    """Schema para estatísticas de NodeExecution"""
    
    node_id: UUID = Field(..., description="ID do nó")
    
    # Execuções
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Performance
    average_execution_time_ms: float = Field(..., description="Tempo médio de execução")
    min_execution_time_ms: int = Field(..., description="Tempo mínimo de execução")
    max_execution_time_ms: int = Field(..., description="Tempo máximo de execução")
    
    # Recursos
    average_memory_used_mb: float = Field(..., description="Memória média usada")
    average_cpu_usage_percent: float = Field(..., description="Uso médio de CPU")
    
    # Por status
    executions_by_status: Dict[str, int] = Field(..., description="Execuções por status")
    
    # Erros
    most_common_errors: List[Dict[str, Any]] = Field(..., description="Erros mais comuns")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionMonitoring(BaseModel):
    """Schema para monitoramento de NodeExecution"""
    
    # Execuções em andamento
    running_executions: List[Dict[str, Any]] = Field(..., description="Execuções em andamento")
    
    # Fila de execuções
    queued_executions: List[Dict[str, Any]] = Field(..., description="Execuções na fila")
    
    # Métricas do sistema
    system_metrics: Dict[str, Any] = Field(..., description="Métricas do sistema")
    
    # Alertas
    alerts: List[Dict[str, Any]] = Field(..., description="Alertas ativos")
    
    # Timestamp
    monitored_at: datetime = Field(..., description="Data do monitoramento")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionLog(BaseModel):
    """Schema para log de NodeExecution"""
    
    execution_id: UUID = Field(..., description="ID da execução")
    
    # Log
    log_level: str = Field(..., description="Nível do log")
    message: str = Field(..., description="Mensagem do log")
    
    # Contexto
    step: Optional[str] = Field(None, description="Passo da execução")
    
    # Timestamp
    logged_at: datetime = Field(..., description="Data do log")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionExport(BaseModel):
    """Schema para exportação de NodeExecution"""
    
    # Filtros
    node_ids: Optional[List[UUID]] = Field(None, description="IDs dos nós")
    status: Optional[str] = Field(None, description="Status das execuções")
    date_from: Optional[datetime] = Field(None, description="Data de início")
    date_to: Optional[datetime] = Field(None, description="Data de fim")
    
    # Configurações
    format: str = Field(..., description="Formato da exportação")
    include_input_data: bool = Field(True, description="Incluir dados de entrada")
    include_output_data: bool = Field(True, description="Incluir dados de saída")
    include_logs: bool = Field(False, description="Incluir logs")
    
    model_config = ConfigDict(from_attributes=True)

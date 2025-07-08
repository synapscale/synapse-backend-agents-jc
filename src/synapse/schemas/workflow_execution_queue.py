"""
Schemas para WorkflowExecutionQueue - fila de execução de workflows
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class WorkflowExecutionQueueBase(BaseModel):
    """Schema base para WorkflowExecutionQueue"""
    
    # Relacionamentos
    workflow_id: UUID = Field(..., description="ID do workflow")
    
    # Dados de entrada
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    
    # Prioridade
    priority: int = Field(1, description="Prioridade da execução")
    
    # Status
    status: str = Field("queued", description="Status da execução")
    
    # Configurações
    execution_config: Optional[Dict[str, Any]] = Field(None, description="Configuração da execução")
    
    # Agendamento
    scheduled_at: Optional[datetime] = Field(None, description="Agendado para")
    
    # Retry
    retry_count: int = Field(0, description="Número de tentativas")
    max_retries: int = Field(3, description="Máximo de tentativas")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowExecutionQueueCreate(WorkflowExecutionQueueBase):
    """Schema para criação de WorkflowExecutionQueue"""
    pass


class WorkflowExecutionQueueUpdate(BaseModel):
    """Schema para atualização de WorkflowExecutionQueue"""
    
    priority: Optional[int] = Field(None, description="Prioridade da execução")
    status: Optional[str] = Field(None, description="Status da execução")
    
    execution_config: Optional[Dict[str, Any]] = Field(None, description="Configuração da execução")
    scheduled_at: Optional[datetime] = Field(None, description="Agendado para")
    
    retry_count: Optional[int] = Field(None, description="Número de tentativas")
    max_retries: Optional[int] = Field(None, description="Máximo de tentativas")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowExecutionQueueResponse(WorkflowExecutionQueueBase):
    """Schema para resposta de WorkflowExecutionQueue"""
    
    id: UUID = Field(..., description="ID único da entrada na fila")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    workflow_name: Optional[str] = Field(None, description="Nome do workflow")
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    
    # Timestamps de execução
    started_at: Optional[datetime] = Field(None, description="Início da execução")
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    # Resultado
    result_data: Optional[Dict[str, Any]] = Field(None, description="Dados do resultado")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_stack: Optional[str] = Field(None, description="Stack trace do erro")
    
    # Status derivados
    is_scheduled: Optional[bool] = Field(None, description="Execução agendada")
    is_running: Optional[bool] = Field(None, description="Execução em andamento")
    is_completed: Optional[bool] = Field(None, description="Execução completada")
    is_failed: Optional[bool] = Field(None, description="Execução falhou")
    
    # Tempo na fila
    queue_time_ms: Optional[int] = Field(None, description="Tempo na fila em ms")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueList(BaseModel):
    """Schema para lista de WorkflowExecutionQueue"""
    
    items: List[WorkflowExecutionQueueResponse] = Field(..., description="Lista de execuções na fila")
    total: int = Field(..., description="Total de execuções na fila")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueEnqueue(BaseModel):
    """Schema para enfileirar WorkflowExecution"""
    
    workflow_id: UUID = Field(..., description="ID do workflow")
    
    # Dados de entrada
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    
    # Configurações
    priority: int = Field(1, description="Prioridade da execução")
    scheduled_at: Optional[datetime] = Field(None, description="Agendado para")
    
    # Retry
    max_retries: int = Field(3, description="Máximo de tentativas")
    
    # Configuração da execução
    execution_config: Optional[Dict[str, Any]] = Field(None, description="Configuração da execução")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueEnqueueResult(BaseModel):
    """Schema para resultado do enqueue"""
    
    queue_id: UUID = Field(..., description="ID da entrada na fila")
    workflow_id: UUID = Field(..., description="ID do workflow")
    
    # Status
    status: str = Field(..., description="Status inicial")
    priority: int = Field(..., description="Prioridade atribuída")
    
    # Estimativa
    estimated_start_time: Optional[datetime] = Field(None, description="Tempo estimado de início")
    
    # Timestamp
    enqueued_at: datetime = Field(..., description="Data do enqueue")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueDequeue(BaseModel):
    """Schema para desenfileirar WorkflowExecution"""
    
    queue_id: UUID = Field(..., description="ID da entrada na fila")
    
    # Motivo da remoção
    reason: Optional[str] = Field(None, description="Motivo da remoção")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueDequeueResult(BaseModel):
    """Schema para resultado do dequeue"""
    
    queue_id: UUID = Field(..., description="ID da entrada na fila")
    
    # Resultado
    dequeued: bool = Field(..., description="Remoção bem-sucedida")
    
    # Timestamp
    dequeued_at: datetime = Field(..., description="Data da remoção")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueProcess(BaseModel):
    """Schema para processamento da fila"""
    
    # Configurações do processamento
    max_concurrent_executions: int = Field(5, description="Máximo de execuções simultâneas")
    batch_size: int = Field(10, description="Tamanho do lote")
    
    # Filtros
    priority_filter: Optional[int] = Field(None, description="Filtro de prioridade")
    workflow_filter: Optional[List[UUID]] = Field(None, description="Filtro de workflows")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueProcessResult(BaseModel):
    """Schema para resultado do processamento"""
    
    # Execuções processadas
    processed_executions: List[UUID] = Field(..., description="IDs das execuções processadas")
    
    # Estatísticas
    total_processed: int = Field(..., description="Total processado")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Timestamp
    processed_at: datetime = Field(..., description="Data do processamento")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueStatistics(BaseModel):
    """Schema para estatísticas da fila"""
    
    # Fila atual
    total_queued: int = Field(..., description="Total na fila")
    queued_by_priority: Dict[str, int] = Field(..., description="Por prioridade")
    queued_by_status: Dict[str, int] = Field(..., description="Por status")
    
    # Processamento
    total_processed: int = Field(..., description="Total processado")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Tempos
    average_queue_time_ms: float = Field(..., description="Tempo médio na fila")
    average_execution_time_ms: float = Field(..., description="Tempo médio de execução")
    
    # Por workflow
    executions_by_workflow: Dict[str, int] = Field(..., description="Execuções por workflow")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueMonitoring(BaseModel):
    """Schema para monitoramento da fila"""
    
    # Status da fila
    queue_status: str = Field(..., description="Status da fila")
    
    # Execuções ativas
    active_executions: List[Dict[str, Any]] = Field(..., description="Execuções ativas")
    
    # Fila de espera
    waiting_executions: List[Dict[str, Any]] = Field(..., description="Execuções esperando")
    
    # Métricas
    queue_metrics: Dict[str, Any] = Field(..., description="Métricas da fila")
    
    # Alertas
    alerts: List[Dict[str, Any]] = Field(..., description="Alertas")
    
    # Timestamp
    monitored_at: datetime = Field(..., description="Data do monitoramento")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueCleanup(BaseModel):
    """Schema para limpeza da fila"""
    
    # Critérios de limpeza
    cleanup_completed: bool = Field(True, description="Limpar execuções completadas")
    cleanup_failed: bool = Field(True, description="Limpar execuções falhadas")
    cleanup_older_than_days: int = Field(7, description="Limpar execuções mais antigas que X dias")
    
    # Configurações
    max_items_to_cleanup: Optional[int] = Field(None, description="Máximo de itens para limpar")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueCleanupResult(BaseModel):
    """Schema para resultado da limpeza"""
    
    # Itens removidos
    cleaned_items: int = Field(..., description="Itens limpos")
    
    # Detalhes
    completed_items_cleaned: int = Field(..., description="Itens completados limpos")
    failed_items_cleaned: int = Field(..., description="Itens falhados limpos")
    old_items_cleaned: int = Field(..., description="Itens antigos limpos")
    
    # Timestamp
    cleaned_at: datetime = Field(..., description="Data da limpeza")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionQueueExport(BaseModel):
    """Schema para exportação da fila"""
    
    # Filtros
    status: Optional[str] = Field(None, description="Status das execuções")
    workflow_ids: Optional[List[UUID]] = Field(None, description="IDs dos workflows")
    date_from: Optional[datetime] = Field(None, description="Data de início")
    date_to: Optional[datetime] = Field(None, description="Data de fim")
    
    # Configurações
    format: str = Field(..., description="Formato da exportação")
    include_input_data: bool = Field(True, description="Incluir dados de entrada")
    include_result_data: bool = Field(True, description="Incluir dados de resultado")
    
    model_config = ConfigDict(from_attributes=True)

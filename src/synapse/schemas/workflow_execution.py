"""
Schemas Pydantic para WorkflowExecution
Criado por José - um desenvolvedor Full Stack
Sistema completo de execução de workflows
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from src.synapse.models.workflow_execution import ExecutionStatus, NodeExecutionStatus


# Schemas base para execução
class ExecutionBase(BaseModel):
    """Schema base para execução de workflows"""
    input_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    priority: int = Field(default=5, ge=1, le=10)
    timeout_seconds: Optional[int] = Field(default=3600, gt=0)
    auto_retry: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    notify_on_completion: bool = True
    notify_on_failure: bool = True
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExecutionCreate(ExecutionBase):
    """Schema para criação de execução de workflow"""
    workflow_id: int = Field(..., gt=0)
    
    @validator('variables')
    def validate_variables(cls, v):
        """Valida as variáveis de entrada"""
        if v is not None:
            # Verifica se todas as chaves são strings
            for key in v.keys():
                if not isinstance(key, str):
                    raise ValueError("Todas as chaves de variáveis devem ser strings")
        return v


class ExecutionUpdate(BaseModel):
    """Schema para atualização de execução"""
    status: Optional[ExecutionStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
    completed_nodes: Optional[int] = Field(None, ge=0)
    failed_nodes: Optional[int] = Field(None, ge=0)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExecutionResponse(ExecutionBase):
    """Schema de resposta para execução de workflow"""
    id: int
    execution_id: str
    workflow_id: int
    user_id: int
    status: ExecutionStatus
    output_data: Optional[Dict[str, Any]] = None
    total_nodes: int
    completed_nodes: int
    failed_nodes: int
    progress_percentage: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    execution_log: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schemas para execução de nós
class NodeExecutionBase(BaseModel):
    """Schema base para execução de nós"""
    node_key: str = Field(..., min_length=1, max_length=255)
    node_type: str = Field(..., min_length=1, max_length=100)
    node_name: Optional[str] = Field(None, max_length=255)
    execution_order: int = Field(..., ge=0)
    input_data: Optional[Dict[str, Any]] = None
    config_data: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = Field(default=300, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_ms: int = Field(default=1000, ge=0)
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class NodeExecutionCreate(NodeExecutionBase):
    """Schema para criação de execução de nó"""
    workflow_execution_id: int = Field(..., gt=0)
    node_id: int = Field(..., gt=0)


class NodeExecutionUpdate(BaseModel):
    """Schema para atualização de execução de nó"""
    status: Optional[NodeExecutionStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class NodeExecutionResponse(NodeExecutionBase):
    """Schema de resposta para execução de nó"""
    id: int
    execution_id: str
    workflow_execution_id: int
    node_id: int
    status: NodeExecutionStatus
    output_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    execution_log: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    debug_info: Optional[Dict[str, Any]] = None
    retry_count: int
    dependents: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schemas para fila de execução
class QueueItemCreate(BaseModel):
    """Schema para adicionar item na fila"""
    workflow_execution_id: int = Field(..., gt=0)
    priority: int = Field(default=5, ge=1, le=10)
    scheduled_at: Optional[datetime] = None
    max_execution_time: int = Field(default=3600, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    metadata: Optional[Dict[str, Any]] = None


class QueueItemResponse(BaseModel):
    """Schema de resposta para item da fila"""
    id: int
    queue_id: str
    workflow_execution_id: int
    user_id: int
    priority: int
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    worker_id: Optional[str] = None
    max_execution_time: int
    retry_count: int
    max_retries: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schemas para métricas
class MetricCreate(BaseModel):
    """Schema para criação de métrica"""
    workflow_execution_id: int = Field(..., gt=0)
    node_execution_id: Optional[int] = Field(None, gt=0)
    metric_type: str = Field(..., min_length=1, max_length=100)
    metric_name: str = Field(..., min_length=1, max_length=255)
    value_numeric: Optional[int] = None
    value_float: Optional[str] = None
    value_text: Optional[str] = None
    value_json: Optional[Dict[str, Any]] = None
    context: Optional[str] = Field(None, max_length=255)
    tags: Optional[Dict[str, Any]] = None


class MetricResponse(BaseModel):
    """Schema de resposta para métrica"""
    id: int
    workflow_execution_id: int
    node_execution_id: Optional[int] = None
    metric_type: str
    metric_name: str
    value_numeric: Optional[int] = None
    value_float: Optional[str] = None
    value_text: Optional[str] = None
    value_json: Optional[Dict[str, Any]] = None
    context: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    measured_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas para estatísticas e relatórios
class ExecutionStats(BaseModel):
    """Estatísticas de execução"""
    total_executions: int
    running_executions: int
    completed_executions: int
    failed_executions: int
    cancelled_executions: int
    average_duration_seconds: Optional[float] = None
    success_rate_percentage: float
    total_nodes_executed: int
    average_nodes_per_execution: Optional[float] = None
    most_used_workflows: List[Dict[str, Any]]
    execution_trends: Dict[str, Any]


class NodeExecutionStats(BaseModel):
    """Estatísticas de execução de nós"""
    total_node_executions: int
    completed_node_executions: int
    failed_node_executions: int
    average_duration_ms: Optional[float] = None
    success_rate_percentage: float
    most_used_node_types: List[Dict[str, Any]]
    performance_by_type: Dict[str, Any]


class ExecutionSummary(BaseModel):
    """Resumo de execução"""
    execution: ExecutionResponse
    node_executions: List[NodeExecutionResponse]
    metrics: List[MetricResponse]
    stats: Dict[str, Any]


# Schemas para controle de execução
class ExecutionControl(BaseModel):
    """Schema para controle de execução"""
    action: str = Field(..., pattern="^(start|pause|resume|cancel|retry)$")
    reason: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class ExecutionBatch(BaseModel):
    """Schema para operações em lote"""
    execution_ids: List[str] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., pattern="^(cancel|retry|delete)$")
    reason: Optional[str] = Field(None, max_length=500)


# Schemas para busca e filtros
class ExecutionFilter(BaseModel):
    """Filtros para busca de execuções"""
    status: Optional[List[ExecutionStatus]] = None
    workflow_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None
    tags: Optional[List[str]] = None
    priority_min: Optional[int] = Field(None, ge=1, le=10)
    priority_max: Optional[int] = Field(None, ge=1, le=10)
    duration_min_seconds: Optional[int] = Field(None, ge=0)
    duration_max_seconds: Optional[int] = Field(None, ge=0)
    has_errors: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="created_at", pattern="^(created_at|updated_at|started_at|completed_at|priority)$")
    order_direction: str = Field(default="desc", pattern="^(asc|desc)$")


class NodeExecutionFilter(BaseModel):
    """Filtros para busca de execuções de nós"""
    status: Optional[List[NodeExecutionStatus]] = None
    workflow_execution_ids: Optional[List[int]] = None
    node_types: Optional[List[str]] = None
    node_keys: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    duration_min_ms: Optional[int] = Field(None, ge=0)
    duration_max_ms: Optional[int] = Field(None, ge=0)
    has_errors: Optional[bool] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="execution_order", pattern="^(execution_order|created_at|started_at|completed_at|duration_ms)$")
    order_direction: str = Field(default="asc", pattern="^(asc|desc)$")


# Schema para validação de workflow
class WorkflowValidation(BaseModel):
    """Resultado da validação de workflow"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    estimated_duration_seconds: Optional[int] = None
    total_nodes: int
    required_variables: List[str]
    optional_variables: List[str]
    dependencies: Dict[str, List[str]]


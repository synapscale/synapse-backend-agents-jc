"""
Schemas Pydantic para workflows
"""

import datetime
from typing import Any, Dict, List, Optional
import uuid
from enum import Enum

from pydantic import BaseModel, Field, validator


class WorkflowStatus(str, Enum):
    """Status do workflow"""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    ERROR = "error"


# Schemas base
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_public: bool = False


class WorkflowCreate(WorkflowBase):
    definition: dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None
    definition: dict[str, Any] | None = None
    status: WorkflowStatus | None = None  # Usar o enum importado


class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do novo workspace")
    version: str
    status: WorkflowStatus  # Usar o enum importado
    definition: dict[str, Any]
    thumbnail_url: str | None = None
    downloads_count: int
    rating_average: int
    rating_count: int
    execution_count: int
    last_executed_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

    @validator("id", "user_id", "tenant_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, "__str__"):
            return str(v)
        return v


class WorkflowListResponse(BaseModel):
    items: list[WorkflowResponse]
    total: int
    page: int
    size: int
    pages: int


class WorkflowExecutionRequest(BaseModel):
    inputs: dict[str, Any] | None = Field(default_factory=dict)
    context: dict[str, Any] | None = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    workflow_name: str
    status: str
    progress: int
    input_data: Optional[dict]
    output_data: Optional[dict]
    error_message: Optional[str]
    started_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime


class WorkflowSearch(BaseModel):
    """Schema para busca de workflows"""

    query: Optional[str] = Field(None, description="Termo de busca")
    tags: Optional[List[str]] = Field(None, description="Tags para filtrar")
    category: Optional[str] = Field(None, description="Categoria")
    status: Optional[str] = Field(None, description="Status do workflow")


class WorkflowStats(BaseModel):
    """Schema para estatísticas de workflow"""

    total_executions: int = Field(0, description="Total de execuções")
    success_rate: float = Field(0.0, description="Taxa de sucesso")
    avg_execution_time: float = Field(0.0, description="Tempo médio de execução")
    last_execution: Optional[datetime.datetime] = Field(
        None, description="Última execução"
    )


class WorkflowVersion(BaseModel):
    """Schema para versão de workflow"""

    version: str = Field(..., description="Número da versão")
    changelog: Optional[str] = Field(None, description="Log de mudanças")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    is_active: bool = Field(True, description="Versão ativa")


class WorkflowTemplate(BaseModel):
    """Schema para template de workflow"""

    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")


class WorkflowTemplateResponse(WorkflowTemplate):
    """Schema de resposta para template de workflow"""

    id: uuid.UUID = Field(..., description="ID do template")
    created_at: datetime.datetime = Field(..., description="Data de criação")


class NodeBase(BaseModel):
    """Schema base para nós"""

    name: str = Field(..., description="Nome do nó")
    type: str = Field(..., description="Tipo do nó")
    position_x: float = Field(0, description="Posição X")
    position_y: float = Field(0, description="Posição Y")


class NodeCreate(NodeBase):
    """Schema para criação de nós"""

    config: Optional[dict] = Field(None, description="Configuração do nó")


class NodeUpdate(BaseModel):
    """Schema para atualização de nós"""

    name: Optional[str] = Field(None, description="Nome do nó")
    config: Optional[dict] = Field(None, description="Configuração do nó")
    position_x: Optional[float] = Field(None, description="Posição X")
    position_y: Optional[float] = Field(None, description="Posição Y")


class NodeResponse(NodeBase):
    """Schema de resposta para nós"""

    id: uuid.UUID = Field(..., description="ID do nó")
    workflow_id: uuid.UUID = Field(..., description="ID do workflow")
    created_at: datetime.datetime = Field(..., description="Data de criação")


class ConnectionBase(BaseModel):
    """Schema base para conexões"""

    source_node_id: uuid.UUID = Field(..., description="ID do nó de origem")
    target_node_id: uuid.UUID = Field(..., description="ID do nó de destino")


class ConnectionCreate(ConnectionBase):
    """Schema para criação de conexões"""

    pass


class ConnectionUpdate(BaseModel):
    """Schema para atualização de conexões"""

    source_node_id: Optional[uuid.UUID] = Field(None, description="ID do nó de origem")
    target_node_id: Optional[uuid.UUID] = Field(None, description="ID do nó de destino")


class ConnectionResponse(ConnectionBase):
    """Schema de resposta para conexões"""

    id: uuid.UUID = Field(..., description="ID da conexão")
    workflow_id: uuid.UUID = Field(..., description="ID do workflow")
    created_at: datetime.datetime = Field(..., description="Data de criação")


class ExecutionLogResponse(BaseModel):
    """Schema de resposta para logs de execução"""

    id: uuid.UUID = Field(..., description="ID do log")
    execution_id: uuid.UUID = Field(..., description="ID da execução")
    level: str = Field(..., description="Nível do log")
    message: str = Field(..., description="Mensagem")
    timestamp: datetime.datetime = Field(..., description="Timestamp")


class WorkflowExecutionCreate(BaseModel):
    """Schema para criação de execução de workflow"""

    workflow_id: uuid.UUID = Field(..., description="ID do workflow")
    input_data: Optional[dict] = Field(None, description="Dados de entrada")


class WorkflowExecutionUpdate(BaseModel):
    """Schema para atualização de execução de workflow"""

    status: Optional[str] = Field(None, description="Status da execução")
    output_data: Optional[dict] = Field(None, description="Dados de saída")


class WorkflowMetrics(BaseModel):
    """Schema para métricas de workflow"""

    total_runs: int = Field(0, description="Total de execuções")
    success_rate: float = Field(0.0, description="Taxa de sucesso")
    avg_execution_time: float = Field(0.0, description="Tempo médio de execução")
    last_execution: Optional[datetime.datetime] = Field(
        None, description="Última execução"
    )


class WorkflowAnalytics(BaseModel):
    """Schema para analytics de workflow"""

    performance_score: float = Field(0.0, description="Score de performance")
    reliability_score: float = Field(0.0, description="Score de confiabilidade")
    usage_trend: List[dict] = Field(
        default_factory=list, description="Tendência de uso"
    )

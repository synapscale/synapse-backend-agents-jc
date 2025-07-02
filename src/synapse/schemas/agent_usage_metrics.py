"""
Schemas Pydantic para agent_usage_metrics
"""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class AgentUsageMetricBase(BaseModel):
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    calls_count: int = Field(..., ge=0, description="Número de chamadas")
    tokens_used: int = Field(..., ge=0, description="Tokens utilizados")
    cost_est: float = Field(..., ge=0, description="Custo estimado")


class AgentUsageMetricCreate(AgentUsageMetricBase):
    pass


class AgentUsageMetricResponse(AgentUsageMetricBase):
    metric_id: UUID = Field(..., description="ID da métrica")
    agent_id: UUID = Field(..., description="ID do agent")
    created_at: datetime = Field(..., description="Data de criação")

    # Campos calculados
    cost_per_token: float | None = Field(None, description="Custo por token")
    avg_tokens_per_call: float | None = Field(
        None, description="Média de tokens por chamada"
    )

    class Config:
        from_attributes = True


class AgentUsageMetricListResponse(BaseModel):
    items: List[AgentUsageMetricResponse]
    total: int
    page: int
    size: int


class AgentUsageMetricFilter(BaseModel):
    start_date: datetime | None = Field(None, description="Data inicial")
    end_date: datetime | None = Field(None, description="Data final")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Itens por página")


class AgentUsageMetricSummary(BaseModel):
    agent_id: UUID = Field(..., description="ID do agent")
    total_calls: int = Field(..., description="Total de chamadas")
    total_tokens: int = Field(..., description="Total de tokens")
    total_cost: float = Field(..., description="Custo total")
    avg_cost_per_call: float = Field(..., description="Custo médio por chamada")
    avg_tokens_per_call: float = Field(..., description="Tokens médios por chamada")
    period_start: datetime = Field(..., description="Início do período analisado")
    period_end: datetime = Field(..., description="Fim do período analisado")


class AgentUsageMetricTrend(BaseModel):
    date: datetime = Field(..., description="Data")
    calls_count: int = Field(..., description="Chamadas no dia")
    tokens_used: int = Field(..., description="Tokens no dia")
    cost_est: float = Field(..., description="Custo no dia")

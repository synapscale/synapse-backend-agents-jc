"""
Schemas Pydantic para agent_quotas
"""

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from uuid import UUID


class AgentQuotaBase(BaseModel):
    max_calls: int = Field(..., ge=0, description="Máximo de chamadas")
    max_tokens: int = Field(..., ge=0, description="Máximo de tokens")
    period: str = Field(..., description="Período (ex: '1 day', '1 month')")


class AgentQuotaCreate(AgentQuotaBase):
    pass


class AgentQuotaUpdate(AgentQuotaBase):
    pass


class AgentQuotaResponse(AgentQuotaBase):
    quota_id: UUID = Field(..., description="ID da quota")
    agent_id: UUID = Field(..., description="ID do agent")
    tenant_id: UUID = Field(..., description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")

    class Config:
        from_attributes = True


class AgentQuotaListResponse(BaseModel):
    items: List[AgentQuotaResponse]
    total: int


class AgentQuotaUsage(BaseModel):
    quota_id: UUID = Field(..., description="ID da quota")
    current_calls: int = Field(..., description="Chamadas utilizadas no período")
    current_tokens: int = Field(..., description="Tokens utilizados no período")
    remaining_calls: int = Field(..., description="Chamadas restantes")
    remaining_tokens: int = Field(..., description="Tokens restantes")
    usage_percentage: float = Field(..., description="Percentual de uso")
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")

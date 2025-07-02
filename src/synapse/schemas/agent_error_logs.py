"""
Schemas Pydantic para agent_error_logs
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class AgentErrorLogBase(BaseModel):
    error_code: str | None = Field(None, description="Código do erro")
    payload: Dict[str, Any] | None = Field(None, description="Dados do erro")


class AgentErrorLogCreate(AgentErrorLogBase):
    pass


class AgentErrorLogResponse(AgentErrorLogBase):
    error_id: UUID = Field(..., description="ID do erro")
    agent_id: UUID = Field(..., description="ID do agent")
    occurred_at: datetime = Field(..., description="Data/hora do erro")

    class Config:
        from_attributes = True


class AgentErrorLogListResponse(BaseModel):
    items: List[AgentErrorLogResponse]
    total: int
    page: int
    size: int


class AgentErrorLogFilter(BaseModel):
    error_code: str | None = Field(None, description="Filtrar por código de erro")
    start_date: datetime | None = Field(None, description="Data inicial")
    end_date: datetime | None = Field(None, description="Data final")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Itens por página")

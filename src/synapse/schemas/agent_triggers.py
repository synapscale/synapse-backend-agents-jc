"""
Schemas Pydantic para agent_triggers
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum


class TriggerTypeEnum(str, Enum):
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"


class AgentTriggerBase(BaseModel):
    trigger_type: TriggerTypeEnum = Field(..., description="Tipo do trigger")
    cron_expr: str | None = Field(None, description="Expressão cron (para schedule)")
    event_name: str | None = Field(None, description="Nome do evento (para event)")
    active: bool = Field(default=True, description="Se o trigger está ativo")


class AgentTriggerCreate(AgentTriggerBase):

    @validator("cron_expr")
    def validate_cron_expr(cls, v, values):
        if values.get("trigger_type") == TriggerTypeEnum.SCHEDULE and not v:
            raise ValueError("cron_expr é obrigatório para triggers do tipo schedule")
        return v

    @validator("event_name")
    def validate_event_name(cls, v, values):
        if values.get("trigger_type") == TriggerTypeEnum.EVENT and not v:
            raise ValueError("event_name é obrigatório para triggers do tipo event")
        return v


class AgentTriggerUpdate(BaseModel):
    cron_expr: str | None = Field(None, description="Nova expressão cron")
    event_name: str | None = Field(None, description="Novo nome do evento")
    active: bool | None = Field(None, description="Novo status ativo")


class AgentTriggerResponse(AgentTriggerBase):
    trigger_id: UUID = Field(..., description="ID do trigger")
    agent_id: UUID = Field(..., description="ID do agent")
    last_run_at: datetime | None = Field(None, description="Última execução")

    class Config:
        from_attributes = True


class AgentTriggerListResponse(BaseModel):
    items: List[AgentTriggerResponse]
    total: int


class AgentTriggerExecution(BaseModel):
    trigger_id: UUID = Field(..., description="ID do trigger")
    executed_at: datetime = Field(..., description="Data/hora da execução")
    success: bool = Field(..., description="Se a execução foi bem-sucedida")
    result: dict | None = Field(None, description="Resultado da execução")
    error_message: str | None = Field(None, description="Mensagem de erro se houver")

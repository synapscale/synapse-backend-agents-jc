"""
Schemas Pydantic para agent_kbs
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentKBBase(BaseModel):
    kb_id: UUID = Field(..., description="ID da knowledge base")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Configuração da KB"
    )


class AgentKBCreate(AgentKBBase):
    pass


class AgentKBUpdate(BaseModel):
    config: Dict[str, Any] = Field(..., description="Nova configuração da KB")


class AgentKBResponse(AgentKBBase):
    agent_id: UUID = Field(..., description="ID do agent")

    class Config:
        from_attributes = True


class AgentKBListResponse(BaseModel):
    items: List[AgentKBResponse]
    total: int


class AgentKBBulkUpdate(BaseModel):
    knowledge_bases: List[AgentKBCreate] = Field(
        ..., description="Lista de KBs a associar"
    )

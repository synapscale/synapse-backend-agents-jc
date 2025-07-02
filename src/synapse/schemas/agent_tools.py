"""
Schemas Pydantic para agent_tools
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentToolBase(BaseModel):
    tool_id: UUID = Field(..., description="ID da ferramenta")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Configuração da ferramenta"
    )


class AgentToolCreate(AgentToolBase):
    pass


class AgentToolUpdate(BaseModel):
    config: Dict[str, Any] = Field(..., description="Nova configuração da ferramenta")


class AgentToolResponse(AgentToolBase):
    agent_id: UUID = Field(..., description="ID do agent")

    class Config:
        from_attributes = True


class AgentToolListResponse(BaseModel):
    items: List[AgentToolResponse]
    total: int

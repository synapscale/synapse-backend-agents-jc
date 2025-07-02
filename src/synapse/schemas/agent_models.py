"""
Schemas Pydantic para agent_models
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentModelBase(BaseModel):
    llm_id: UUID = Field(..., description="ID do LLM")
    override: Dict[str, Any] = Field(
        default_factory=dict, description="Configurações que sobrescrevem o LLM"
    )


class AgentModelCreate(AgentModelBase):
    pass


class AgentModelUpdate(BaseModel):
    override: Dict[str, Any] = Field(..., description="Novas configurações de override")


class AgentModelResponse(AgentModelBase):
    agent_id: UUID = Field(..., description="ID do agent")

    class Config:
        from_attributes = True


class AgentModelListResponse(BaseModel):
    items: List[AgentModelResponse]
    total: int

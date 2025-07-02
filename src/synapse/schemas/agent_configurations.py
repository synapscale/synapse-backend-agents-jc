"""
Schemas Pydantic para agent_configurations
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class AgentConfigurationBase(BaseModel):
    params: Dict[str, Any] = Field(..., description="Parâmetros da configuração")


class AgentConfigurationCreate(AgentConfigurationBase):
    pass


class AgentConfigurationUpdate(AgentConfigurationBase):
    pass


class AgentConfigurationResponse(AgentConfigurationBase):
    config_id: UUID = Field(..., description="ID da configuração")
    agent_id: UUID = Field(..., description="ID do agent")
    version_num: int = Field(..., description="Número da versão")
    created_by: UUID = Field(..., description="ID do usuário que criou")
    created_at: datetime = Field(..., description="Data/hora de criação")

    class Config:
        from_attributes = True


class AgentConfigurationListResponse(BaseModel):
    items: List[AgentConfigurationResponse]
    total: int
    current_version: int | None = None

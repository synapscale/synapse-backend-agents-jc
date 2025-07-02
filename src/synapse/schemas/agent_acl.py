"""
Schemas Pydantic para agent_acl
"""

from typing import List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentACLBase(BaseModel):
    user_id: UUID = Field(..., description="ID do usuário")
    can_read: bool = Field(default=True, description="Permissão de leitura")
    can_write: bool = Field(default=False, description="Permissão de escrita")


class AgentACLCreate(AgentACLBase):
    pass


class AgentACLUpdate(BaseModel):
    can_read: bool | None = Field(None, description="Permissão de leitura")
    can_write: bool | None = Field(None, description="Permissão de escrita")


class AgentACLResponse(AgentACLBase):
    agent_id: UUID = Field(..., description="ID do agent")

    class Config:
        from_attributes = True


class AgentACLListResponse(BaseModel):
    items: List[AgentACLResponse]
    total: int


class AgentACLBulkUpdate(BaseModel):
    permissions: List[AgentACLCreate] = Field(
        ..., description="Lista de permissões a definir"
    )

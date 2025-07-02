"""
Schemas Pydantic para agent_hierarchy
"""

from typing import List
from pydantic import BaseModel, Field
from uuid import UUID


class AgentHierarchyBase(BaseModel):
    descendant: UUID = Field(..., description="ID do agent descendente")
    depth: int = Field(..., ge=0, description="Profundidade da relação")


class AgentHierarchyCreate(AgentHierarchyBase):
    pass


class AgentHierarchyResponse(AgentHierarchyBase):
    ancestor: UUID = Field(..., description="ID do agent ancestral")

    class Config:
        from_attributes = True


class AgentHierarchyListResponse(BaseModel):
    items: List[AgentHierarchyResponse]
    total: int


class AgentHierarchyTree(BaseModel):
    agent_id: UUID = Field(..., description="ID do agent")
    children: List["AgentHierarchyTree"] = Field(
        default_factory=list, description="Agents filhos"
    )
    depth: int = Field(0, description="Profundidade na árvore")


# Enable forward references
AgentHierarchyTree.model_rebuild()


class AgentParentUpdate(BaseModel):
    parent_id: UUID | None = Field(
        None, description="ID do novo agent pai (null para remover)"
    )

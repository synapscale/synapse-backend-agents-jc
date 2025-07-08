"""
Schemas for NodeStatus - a model for representing the status of nodes.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class NodeStatusName(str, Enum):
    """Enum for common node status names."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class NodeStatusBase(BaseModel):
    """Base schema for NodeStatus attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: NodeStatusName = Field(..., max_length=100, description="The unique name of the node status.")
    description: Optional[str] = Field(None, description="A detailed description of what the status means.")
    color: Optional[str] = Field(None, max_length=7, description="A hex color code for UI representation.")
    is_final: bool = Field(False, description="Indicates if this is a final status for a node.")
    is_error: bool = Field(False, description="Indicates if this status represents an error state.")
    is_active: bool = Field(True, description="Whether this status is active and can be assigned to nodes.")


class NodeStatusCreate(NodeStatusBase):
    """Schema for creating a new NodeStatus."""
    pass


class NodeStatusUpdate(BaseModel):
    """Schema for updating an existing NodeStatus. All fields are optional."""
    description: Optional[str] = Field(None, description="New description.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    is_final: Optional[bool] = Field(None, description="New final status.")
    is_error: Optional[bool] = Field(None, description="New error state.")
    is_active: Optional[bool] = Field(None, description="New active status.")


class NodeStatusResponse(NodeStatusBase):
    """Response schema for a NodeStatus, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the node status.")
    created_at: datetime = Field(..., description="Timestamp of when the status was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")


class NodeStatusListResponse(BaseModel):
    """Paginated list of NodeStatuses."""
    items: List[NodeStatusResponse] = Field(..., description="List of node statuses for the current page.")
    total: int = Field(..., description="Total number of node statuses.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

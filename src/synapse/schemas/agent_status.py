"""
Schemas for AgentStatus - a model for representing the status of agents.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class AgentStatusBase(BaseModel):
    """Base schema for AgentStatus attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=100, description="The unique name of the status (e.g., 'running', 'stopped').")
    display_name: str = Field(..., max_length=255, description="A human-readable name for the status (e.g., 'Running', 'Stopped').")
    description: Optional[str] = Field(None, description="A detailed description of what the status means.")
    color: Optional[str] = Field(None, max_length=7, description="A hex color code for UI representation.")
    is_operational: bool = Field(True, description="Indicates if an agent in this status can perform tasks.")
    is_error: bool = Field(False, description="Indicates if this status represents an error state.")
    requires_attention: bool = Field(False, description="Indicates if this status requires user attention.")
    is_active: bool = Field(True, description="Whether this status is active and can be assigned to agents.")

class AgentStatusCreate(AgentStatusBase):
    """Schema for creating a new agent status."""
    pass

class AgentStatusUpdate(BaseModel):
    """Schema for updating an existing agent status. All fields are optional."""
    display_name: Optional[str] = Field(None, max_length=255, description="New human-readable name.")
    description: Optional[str] = Field(None, description="New description.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    is_operational: Optional[bool] = Field(None, description="New operational status.")
    is_error: Optional[bool] = Field(None, description="New error state.")
    requires_attention: Optional[bool] = Field(None, description="New attention requirement.")
    is_active: Optional[bool] = Field(None, description="New active status.")

class AgentStatusResponse(AgentStatusBase):
    """Response schema for an agent status, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the agent status.")
    created_at: datetime = Field(..., description="Timestamp of when the status was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")

class AgentStatusListResponse(BaseModel):
    """Paginated list of agent statuses."""
    items: List[AgentStatusResponse] = Field(..., description="List of agent statuses for the current page.")
    total: int = Field(..., description="Total number of agent statuses.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

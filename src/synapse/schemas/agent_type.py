"""
Schemas for AgentType - a model for defining different types of agents.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class AgentTypeBase(BaseModel):
    """Base schema for AgentType attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=100, description="The unique name of the agent type (e.g., 'chatbot', 'automation').")
    display_name: str = Field(..., max_length=255, description="A human-readable name for the agent type.")
    description: Optional[str] = Field(None, description="A detailed description of the agent type and its purpose.")
    category: Optional[str] = Field(None, max_length=100, description="The category of the agent type (e.g., 'customer_support', 'sales').")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="A dictionary of the agent type's capabilities.")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="The default configuration for agents of this type.")
    icon: Optional[str] = Field(None, max_length=255, description="An icon for UI representation.")
    color: Optional[str] = Field(None, max_length=7, description="A hex color code for UI representation.")
    requires_training: bool = Field(False, description="Indicates if agents of this type require training.")
    supports_knowledge_base: bool = Field(True, description="Indicates if agents of this type support knowledge bases.")
    supports_tools: bool = Field(True, description="Indicates if agents of this type support tools.")
    supports_webhooks: bool = Field(False, description="Indicates if agents of this type support webhooks.")
    is_active: bool = Field(True, description="Whether this agent type is active and can be used to create new agents.")
    is_premium: bool = Field(False, description="Indicates if this is a premium agent type.")

class AgentTypeCreate(AgentTypeBase):
    """Schema for creating a new agent type."""
    pass

class AgentTypeUpdate(BaseModel):
    """Schema for updating an existing agent type. All fields are optional."""
    display_name: Optional[str] = Field(None, max_length=255, description="New human-readable name.")
    description: Optional[str] = Field(None, description="New description.")
    category: Optional[str] = Field(None, max_length=100, description="New category.")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="New capabilities.")
    default_config: Optional[Dict[str, Any]] = Field(None, description="New default configuration.")
    icon: Optional[str] = Field(None, max_length=255, description="New icon.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    requires_training: Optional[bool] = Field(None, description="New training requirement.")
    supports_knowledge_base: Optional[bool] = Field(None, description="New knowledge base support.")
    supports_tools: Optional[bool] = Field(None, description="New tools support.")
    supports_webhooks: Optional[bool] = Field(None, description="New webhooks support.")
    is_active: Optional[bool] = Field(None, description="New active status.")
    is_premium: Optional[bool] = Field(None, description="New premium status.")

class AgentTypeResponse(AgentTypeBase):
    """Response schema for an agent type, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the agent type.")
    created_at: datetime = Field(..., description="Timestamp of when the agent type was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")

class AgentTypeListResponse(BaseModel):
    """Paginated list of agent types."""
    items: List[AgentTypeResponse] = Field(..., description="List of agent types for the current page.")
    total: int = Field(..., description="Total number of agent types.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

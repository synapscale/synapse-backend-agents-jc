"""
Schemas for NodeTemplate - a model for defining reusable workflow node templates.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class NodeTemplateBase(BaseModel):
    """Base schema for NodeTemplate attributes."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=255, description="The name of the node template.")
    description: Optional[str] = Field(None, description="A detailed description of the node template.")
    category: Optional[str] = Field(None, max_length=100, description="The category of the node template (e.g., 'data_processing', 'integrations').")
    code_template: str = Field(..., description="The code template for the node.")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema defining the expected input for the node.")
    output_schema: Dict[str, Any] = Field(..., description="JSON schema defining the expected output from the node.")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema defining configurable parameters for the node.")
    icon: Optional[str] = Field(None, max_length=255, description="An icon for UI representation.")
    color: Optional[str] = Field(None, max_length=255, description="A color for UI representation.")
    documentation: Optional[str] = Field(None, description="Documentation for the node template.")
    examples: Optional[Dict[str, Any]] = Field(None, description="Examples of how to use the node template.")
    is_system: Optional[bool] = Field(None, description="Indicates if this is a system-defined template.")
    is_active: Optional[bool] = Field(None, description="Whether this template is active and can be used.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this template belongs.")


class NodeTemplateCreate(NodeTemplateBase):
    """Schema for creating a new NodeTemplate."""
    pass


class NodeTemplateUpdate(BaseModel):
    """Schema for updating an existing NodeTemplate. All fields are optional."""
    name: Optional[str] = Field(None, max_length=255, description="New name for the template.")
    description: Optional[str] = Field(None, description="New description.")
    category: Optional[str] = Field(None, max_length=100, description="New category.")
    code_template: Optional[str] = Field(None, description="New code template.")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="New input schema.")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="New output schema.")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="New parameters schema.")
    icon: Optional[str] = Field(None, max_length=255, description="New icon.")
    color: Optional[str] = Field(None, max_length=255, description="New color.")
    documentation: Optional[str] = Field(None, description="New documentation.")
    examples: Optional[Dict[str, Any]] = Field(None, description="New examples.")
    is_system: Optional[bool] = Field(None, description="New system status.")
    is_active: Optional[bool] = Field(None, description="New active status.")


class NodeTemplateResponse(NodeTemplateBase):
    """Response schema for a NodeTemplate, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the node template.")
    created_at: datetime = Field(..., description="Timestamp of when the template was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")


class NodeTemplateListResponse(BaseModel):
    """Paginated list of NodeTemplates."""
    items: List[NodeTemplateResponse] = Field(..., description="List of node templates for the current page.")
    total: int = Field(..., description="Total number of node templates.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

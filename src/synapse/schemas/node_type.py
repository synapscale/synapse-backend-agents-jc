"""
Schemas for NodeType - a model for defining different types of nodes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class NodeCategoryType(str, Enum):
    """Enum for common node category types."""
    INPUT = "input"
    OUTPUT = "output"
    PROCESSING = "processing"
    LOGIC = "logic"
    INTEGRATION = "integration"
    UTILITY = "utility"


class NodeInputOutputCardinality(str, Enum):
    """Enum for node input/output cardinality."""
    ONE = "1"
    MANY = "many"
    NONE = "none"


class NodeTypeBase(BaseModel):
    """Base schema for NodeType attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=100, description="The unique name of the node type.")
    display_name: str = Field(..., max_length=255, description="A human-readable name for the node type.")
    description: Optional[str] = Field(None, description="A detailed description of the node type.")
    category: NodeCategoryType = Field(..., description="The category of the node type.")
    config_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema defining the configuration properties for this node type.")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="Default configuration values for this node type.")
    icon: Optional[str] = Field(None, max_length=255, description="An icon for UI representation.")
    color: Optional[str] = Field(None, max_length=7, description="A hex color code for UI representation.")
    can_have_inputs: bool = Field(True, description="Indicates if this node type can accept inputs.")
    can_have_outputs: bool = Field(True, description="Indicates if this node type can produce outputs.")
    max_inputs: NodeInputOutputCardinality = Field(NodeInputOutputCardinality.MANY, description="Maximum number of inputs this node type can have.")
    max_outputs: NodeInputOutputCardinality = Field(NodeInputOutputCardinality.MANY, description="Maximum number of outputs this node type can have.")
    is_active: bool = Field(True, description="Whether this node type is active and can be used.")


class NodeTypeCreate(NodeTypeBase):
    """Schema for creating a new NodeType."""
    pass


class NodeTypeUpdate(BaseModel):
    """Schema for updating an existing NodeType. All fields are optional."""
    display_name: Optional[str] = Field(None, max_length=255, description="New human-readable name.")
    description: Optional[str] = Field(None, description="New description.")
    category: Optional[NodeCategoryType] = Field(None, description="New category.")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="New configuration schema.")
    default_config: Optional[Dict[str, Any]] = Field(None, description="New default configuration.")
    icon: Optional[str] = Field(None, max_length=255, description="New icon.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    can_have_inputs: Optional[bool] = Field(None, description="New input capability.")
    can_have_outputs: Optional[bool] = Field(None, description="New output capability.")
    max_inputs: Optional[NodeInputOutputCardinality] = Field(None, description="New maximum inputs.")
    max_outputs: Optional[NodeInputOutputCardinality] = Field(None, description="New maximum outputs.")
    is_active: Optional[bool] = Field(None, description="New active status.")


class NodeTypeResponse(NodeTypeBase):
    """Response schema for a NodeType, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the node type.")
    created_at: datetime = Field(..., description="Timestamp of when the node type was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")


class NodeTypeListResponse(BaseModel):
    """Paginated list of NodeTypes."""
    items: List[NodeTypeResponse] = Field(..., description="List of node types for the current page.")
    total: int = Field(..., description="Total number of node types.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

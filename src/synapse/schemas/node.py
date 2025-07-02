"""
Schemas for Node management.
"""

import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===== ENUMS ALINHADOS COM O BANCO =====


class NodeType(str, Enum):
    """Node types available in the system."""

    LLM = "llm"
    TRANSFORM = "transform"
    API = "api"
    CONDITION = "condition"
    TRIGGER = "trigger"
    OPERATION = "operation"
    FLOW = "flow"
    INPUT = "input"
    OUTPUT = "output"
    FILE_PROCESSOR = "file_processor"


class NodeStatus(str, Enum):
    """Possible statuses for a node."""

    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    PRIVATE = "private"


# ===== NODE SCHEMAS (ALIGNED PERFECTLY WITH THE DATABASE) =====


class NodeBase(BaseModel):
    """Base schema for node attributes."""

    name: str = Field(..., max_length=255, description="Node name")
    category: str = Field(..., max_length=100, description="Category")
    description: Optional[str] = Field(None, description="Description")
    version: str = Field("1.0.0", max_length=50, description="Version")
    definition: Dict[str, Any] = Field(..., description="Node JSON definition")
    code_template: str = Field(..., description="Code template")
    input_schema: Dict[str, Any] = Field(..., description="Input schema")
    output_schema: Dict[str, Any] = Field(..., description="Output schema")
    parameters_schema: Optional[Dict[str, Any]] = Field(
        None, description="Parameters schema"
    )
    icon: Optional[str] = Field(None, max_length=10, description="Icon")
    color: Optional[str] = Field(None, max_length=7, description="Color (hex)")
    documentation: Optional[str] = Field(None, description="Documentation")
    examples: Optional[Dict[str, Any]] = Field(None, description="Examples")
    is_public: bool = Field(False, description="Public node")
    timeout_seconds: int = Field(300, description="Timeout in seconds")
    retry_count: int = Field(3, description="Number of retries")
    workspace_id: Optional[uuid.UUID] = Field(None, description="Workspace ID")
    # REMOVED: type field (does not exist in database)


class NodeCreate(NodeBase):
    """Schema for node creation - ALIGNED WITH DATABASE"""

    pass


class NodeUpdate(BaseModel):
    """Schema for node updates - ALIGNED WITH DATABASE"""

    name: Optional[str] = Field(None, max_length=255, description="Node name")
    category: Optional[str] = Field(None, max_length=100, description="Category")
    description: Optional[str] = Field(None, description="Description")
    version: Optional[str] = Field(None, max_length=50, description="Version")
    definition: Optional[Dict[str, Any]] = Field(None, description="JSON definition")
    code_template: Optional[str] = Field(None, description="Code template")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Input schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Output schema")
    parameters_schema: Optional[Dict[str, Any]] = Field(
        None, description="Parameters schema"
    )
    icon: Optional[str] = Field(None, max_length=10, description="Icon")
    color: Optional[str] = Field(None, max_length=7, description="Color")
    documentation: Optional[str] = Field(None, description="Documentation")
    examples: Optional[Dict[str, Any]] = Field(None, description="Examples")
    is_public: Optional[bool] = Field(None, description="Public node")
    status: Optional[NodeStatus] = Field(None, description="Status")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds")
    retry_count: Optional[int] = Field(None, description="Number of retries")
    workspace_id: Optional[uuid.UUID] = Field(None, description="Workspace ID")
    # REMOVED: type field (does not exist in database)


class NodeResponse(NodeBase):
    """Response schema for a node - PERFECTLY ALIGNED WITH DATABASE"""

    id: uuid.UUID = Field(..., description="Node ID")
    downloads_count: Optional[int] = Field(None, description="Number of downloads")
    usage_count: Optional[int] = Field(None, description="Number of uses")
    rating_average: Optional[int] = Field(None, description="Average rating")
    rating_count: Optional[int] = Field(None, description="Number of ratings")
    status: Optional[str] = Field(None, description="Status")
    user_id: uuid.UUID = Field(..., description="User ID")
    workspace_id: Optional[uuid.UUID] = Field(None, description="Workspace ID")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Tenant ID")
    created_at: Optional[datetime.datetime] = Field(
        None, description="Creation timestamp"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Last update timestamp"
    )


class NodeListResponse(BaseModel):
    """Paginated list of nodes."""

    items: List[NodeResponse] = Field(..., description="List of nodes")
    total: int = Field(..., description="Total number of nodes")


# Re-export for compatibility from response_models.py
NodesResponse = NodeResponse


class NodeExecutionStatsResponse(BaseModel):
    """Statistics for node executions."""
    
    node_id: str = Field(..., description="Node ID")
    total_executions: int = Field(..., description="Total number of executions")
    failed_executions: int = Field(..., description="Number of failed executions")
    success_rate: float = Field(..., description="Success rate percentage")
    avg_duration_ms: float = Field(..., description="Average execution duration in milliseconds")
    total_retries: int = Field(..., description="Total number of retries across all executions")
    usage_count: int = Field(..., description="Total usage count")
    downloads_count: int = Field(..., description="Total downloads count")
    rating_average: Optional[int] = Field(None, description="Average rating")
    rating_count: int = Field(..., description="Number of ratings")

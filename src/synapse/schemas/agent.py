"""
Schemas for Agent management.
"""

import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===== ENUMS ALINHADOS COM O BANCO =====


class AgentStatus(str, Enum):
    """Agent status - ALIGNED WITH THE DATABASE"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    ERROR = "error"


class AgentEnvironment(str, Enum):
    """Agent environment - ALIGNED WITH THE DATABASE"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AgentScope(str, Enum):
    GLOBAL = "global"
    WORKSPACE = "workspace"
    PRIVATE = "private"


class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"


# ===== AGENT SCHEMAS (ALIGNED PERFECTLY WITH THE DATABASE) =====


class AgentBase(BaseModel):
    """Base schema for agent attributes."""

    name: str = Field(..., max_length=255, description="Agent name")
    description: Optional[str] = Field(None, description="Description")
    is_active: bool = Field(True, description="Active agent")
    status: Optional[str] = Field("active", description="Status")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Priority (1-10)")
    version: Optional[str] = Field("1.0.0", max_length=20, description="Version")
    environment: Optional[str] = Field("development", description="Environment")
    workspace_id: Optional[uuid.UUID] = Field(None, description="Workspace ID")
    current_config: Optional[uuid.UUID] = Field(
        None, description="Active configuration ID"
    )


class AgentCreate(AgentBase):
    """Schema for agent creation - ALIGNED WITH DATABASE"""

    pass


class AgentUpdate(BaseModel):
    """Schema for agent updates - ALIGNED WITH DATABASE"""

    name: Optional[str] = Field(None, max_length=255, description="Agent name")
    description: Optional[str] = Field(None, description="Description")
    is_active: Optional[bool] = Field(None, description="Active agent")
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Priority")
    version: Optional[str] = Field(None, max_length=20, description="Version")
    environment: Optional[str] = Field(None, description="Environment")
    current_config: Optional[uuid.UUID] = Field(
        None, description="Active configuration ID"
    )


class AgentResponse(AgentBase):
    """Response schema for an agent - PERFECTLY ALIGNED WITH DATABASE"""

    id: uuid.UUID = Field(..., description="Agent ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    user_name: Optional[str] = Field(None, description="User name")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")


class AgentListResponse(BaseModel):
    """Paginated list of agents."""

    items: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")


# Re-export for compatibility from response_models.py
AgentsResponse = AgentResponse

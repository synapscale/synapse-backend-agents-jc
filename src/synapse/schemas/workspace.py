"""
Schemas for Workspace management.
"""

import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ===== ENUMS ALINHADOS COM O BANCO =====


class WorkspaceType(str, Enum):
    """Workspace type - ALIGNED WITH THE DATABASE"""

    INDIVIDUAL = "individual"
    COLLABORATIVE = "collaborative"


class WorkspaceStatus(str, Enum):
    """Workspace status - ALIGNED WITH THE DATABASE"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# ===== WORKSPACE SCHEMAS (ALIGNED PERFECTLY WITH THE DATABASE) =====


class WorkspaceBase(BaseModel):
    """Base schema for workspace attributes."""

    name: str = Field(..., max_length=255, description="Workspace name")
    slug: str = Field(..., max_length=120, description="Unique slug")
    description: Optional[str] = Field(None, description="Description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    color: Optional[str] = Field(None, max_length=7, description="Color (hex)")
    is_public: bool = Field(False, description="Public workspace")
    is_template: bool = Field(False, description="Is a template")
    allow_guest_access: bool = Field(False, description="Allows guest access")
    require_approval: bool = Field(True, description="Requires approval")
    max_members: Optional[int] = Field(None, description="Maximum members")
    max_projects: Optional[int] = Field(None, description="Maximum projects")
    max_storage_mb: Optional[int] = Field(None, description="Maximum storage in MB")
    enable_real_time_editing: bool = Field(True, description="Real-time editing")
    enable_comments: bool = Field(True, description="Comments")
    enable_chat: bool = Field(True, description="Chat")
    enable_video_calls: bool = Field(True, description="Video calls")
    email_notifications: bool = Field(True, description="Email notifications")
    push_notifications: bool = Field(False, description="Push notifications")
    type: WorkspaceType = Field(WorkspaceType.INDIVIDUAL, description="Workspace type")


class WorkspaceCreate(WorkspaceBase):
    """Schema for workspace creation - ALIGNED WITH DATABASE"""

    pass


class WorkspaceUpdate(BaseModel):
    """Schema for workspace updates - ALIGNED WITH DATABASE"""

    name: Optional[str] = Field(None, max_length=255, description="Workspace name")
    description: Optional[str] = Field(None, description="Description")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    color: Optional[str] = Field(None, max_length=7, description="Color (hex)")
    is_public: Optional[bool] = Field(None, description="Public workspace")
    is_template: Optional[bool] = Field(None, description="Is a template")
    allow_guest_access: Optional[bool] = Field(None, description="Allows guest access")
    require_approval: Optional[bool] = Field(None, description="Requires approval")
    max_members: Optional[int] = Field(None, description="Maximum members")
    max_projects: Optional[int] = Field(None, description="Maximum projects")
    max_storage_mb: Optional[int] = Field(None, description="Maximum storage in MB")
    enable_real_time_editing: Optional[bool] = Field(
        None, description="Real-time editing"
    )
    enable_comments: Optional[bool] = Field(None, description="Comments")
    enable_chat: Optional[bool] = Field(None, description="Chat")
    enable_video_calls: Optional[bool] = Field(None, description="Video calls")
    email_notifications: Optional[bool] = Field(None, description="Email notifications")
    push_notifications: Optional[bool] = Field(None, description="Push notifications")
    status: Optional[WorkspaceStatus] = Field(None, description="Status")


class WorkspaceResponse(WorkspaceBase):
    """Response schema for a workspace - PERFECTLY ALIGNED WITH DATABASE"""

    id: uuid.UUID = Field(..., description="Workspace ID")
    owner_id: uuid.UUID = Field(..., description="Owner ID")
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    member_count: int = Field(..., description="Number of members")
    project_count: int = Field(..., description="Number of projects")
    activity_count: int = Field(..., description="Number of activities")
    storage_used_mb: float = Field(..., description="Storage used in MB")
    api_calls_today: Optional[int] = Field(None, description="API calls today")
    api_calls_this_month: Optional[int] = Field(
        None, description="API calls this month"
    )
    last_api_reset_daily: Optional[datetime.datetime] = Field(
        None, description="Last daily API reset"
    )
    last_api_reset_monthly: Optional[datetime.datetime] = Field(
        None, description="Last monthly API reset"
    )
    feature_usage_count: Optional[Dict[str, Any]] = Field(
        None, description="Feature usage count"
    )
    status: str = Field(..., description="Status")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")
    last_activity_at: datetime.datetime = Field(
        ..., description="Last activity timestamp"
    )


class WorkspaceListResponse(BaseModel):
    """Paginated list of workspaces."""

    items: List[WorkspaceResponse] = Field(..., description="List of workspaces")
    total: int = Field(..., description="Total number of workspaces")


# Re-export for compatibility from response_models.py
WorkspacesResponse = WorkspaceResponse


# ==================== MEMBER INVITE SCHEMAS ====================

class MemberInvite(BaseModel):
    """Schema para convite de membro para workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(..., description="Email do usuário a ser convidado")
    role: str = Field("member", description="Role do membro")
    message: Optional[str] = Field(
        None, max_length=500, description="Mensagem personalizada"
    )

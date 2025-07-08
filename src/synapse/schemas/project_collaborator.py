from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum


class PermissionLevel(str, Enum):
    """Enum for permission levels"""
    ADMIN = "admin"
    EDITOR = "editor"
    CONTRIBUTOR = "contributor"
    COMMENTER = "commenter"
    VIEWER = "viewer"


class ActivityStatus(str, Enum):
    """Enum for activity status"""
    ONLINE = "online"
    RECENTLY_ACTIVE = "recently_active"
    AWAY = "away"
    OFFLINE = "offline"


class CursorPosition(BaseModel):
    """Schema for cursor position"""
    x: Optional[float] = Field(None, description="X coordinate")
    y: Optional[float] = Field(None, description="Y coordinate")
    node_id: Optional[str] = Field(None, description="Node ID")


class ProjectCollaboratorBase(BaseModel):
    """Base schema for ProjectCollaborator"""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID")
    can_edit: bool = Field(default=False, description="Can edit project")
    can_comment: bool = Field(default=True, description="Can comment on project")
    can_share: bool = Field(default=False, description="Can share project")
    can_delete: bool = Field(default=False, description="Can delete project")
    is_online: bool = Field(default=False, description="Is currently online")
    current_cursor_position: Optional[Dict[str, Any]] = Field(None, description="Current cursor position")
    last_edit_at: Optional[datetime] = Field(None, description="Last edit timestamp")
    added_at: datetime = Field(..., description="Added to project timestamp")
    last_seen_at: datetime = Field(..., description="Last seen timestamp")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class ProjectCollaboratorCreate(BaseModel):
    """Schema for creating a new project collaborator"""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID")
    permission_level: PermissionLevel = Field(default=PermissionLevel.CONTRIBUTOR, description="Permission level")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class ProjectCollaboratorUpdate(BaseModel):
    """Schema for updating an existing project collaborator"""
    can_edit: Optional[bool] = Field(None, description="Can edit project")
    can_comment: Optional[bool] = Field(None, description="Can comment on project")
    can_share: Optional[bool] = Field(None, description="Can share project")
    can_delete: Optional[bool] = Field(None, description="Can delete project")
    is_online: Optional[bool] = Field(None, description="Is currently online")
    current_cursor_position: Optional[Dict[str, Any]] = Field(None, description="Current cursor position")
    permission_level: Optional[PermissionLevel] = Field(None, description="Permission level")


class ProjectCollaboratorInDB(ProjectCollaboratorBase):
    """Schema for project collaborator in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Collaborator ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ProjectCollaboratorResponse(ProjectCollaboratorInDB):
    """Schema for project collaborator response"""
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")
    user_avatar: Optional[str] = Field(None, description="User avatar URL")
    permission_level: PermissionLevel = Field(..., description="Permission level")
    activity_status: ActivityStatus = Field(..., description="Activity status")
    cursor_coordinates: Optional[CursorPosition] = Field(None, description="Cursor coordinates")
    time_since_last_edit: Optional[str] = Field(None, description="Time since last edit")
    time_since_last_seen: Optional[str] = Field(None, description="Time since last seen")
    has_been_active_recently: bool = Field(..., description="Has been active recently")


class ProjectCollaboratorListResponse(BaseModel):
    """Schema for project collaborator list response"""
    model_config = ConfigDict(from_attributes=True)
    
    collaborators: List[ProjectCollaboratorResponse] = Field(..., description="List of collaborators")
    total: int = Field(..., description="Total number of collaborators")
    online_count: int = Field(..., description="Number of online collaborators")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of collaborators per page")
    pages: int = Field(..., description="Total number of pages")


class ProjectCollaboratorPermissionUpdate(BaseModel):
    """Schema for updating collaborator permissions"""
    collaborator_id: UUID = Field(..., description="Collaborator ID")
    permission_level: PermissionLevel = Field(..., description="New permission level")
    custom_permissions: Optional[Dict[str, bool]] = Field(None, description="Custom permissions")


class ProjectCollaboratorInvite(BaseModel):
    """Schema for inviting a collaborator"""
    project_id: UUID = Field(..., description="Project ID")
    email: str = Field(..., description="Invitee email")
    permission_level: PermissionLevel = Field(default=PermissionLevel.CONTRIBUTOR, description="Permission level")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_at: Optional[datetime] = Field(None, description="Invitation expiration")


class ProjectCollaboratorInviteResponse(BaseModel):
    """Schema for collaborator invitation response"""
    success: bool = Field(..., description="Invitation success")
    invitation_id: UUID = Field(..., description="Invitation ID")
    message: str = Field(..., description="Response message")
    expires_at: Optional[datetime] = Field(None, description="Invitation expiration")


class ProjectCollaboratorBatch(BaseModel):
    """Schema for batch collaborator operations"""
    collaborator_ids: List[UUID] = Field(..., description="List of collaborator IDs")
    action: str = Field(..., description="Batch action (remove, update_permissions, etc.)")
    batch_data: Optional[Dict[str, Any]] = Field(None, description="Additional batch data")


class ProjectCollaboratorPresence(BaseModel):
    """Schema for collaborator presence"""
    collaborator_id: UUID = Field(..., description="Collaborator ID")
    is_online: bool = Field(..., description="Is online")
    cursor_position: Optional[CursorPosition] = Field(None, description="Cursor position")
    last_seen_at: datetime = Field(..., description="Last seen timestamp")
    current_activity: Optional[str] = Field(None, description="Current activity")


class ProjectCollaboratorStatistics(BaseModel):
    """Schema for project collaborator statistics"""
    project_id: UUID = Field(..., description="Project ID")
    total_collaborators: int = Field(..., description="Total collaborators")
    active_collaborators: int = Field(..., description="Active collaborators")
    online_collaborators: int = Field(..., description="Online collaborators")
    permission_distribution: Dict[str, int] = Field(..., description="Permission level distribution")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent activity")
    collaboration_score: float = Field(..., description="Collaboration score")


class ProjectCollaboratorActivity(BaseModel):
    """Schema for collaborator activity"""
    collaborator_id: UUID = Field(..., description="Collaborator ID")
    activity_type: str = Field(..., description="Activity type")
    activity_data: Dict[str, Any] = Field(..., description="Activity data")
    timestamp: datetime = Field(..., description="Activity timestamp")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")


class ProjectCollaboratorSession(BaseModel):
    """Schema for collaborator session"""
    collaborator_id: UUID = Field(..., description="Collaborator ID")
    session_id: str = Field(..., description="Session ID")
    started_at: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity time")
    is_active: bool = Field(..., description="Is session active")
    cursor_position: Optional[CursorPosition] = Field(None, description="Current cursor position")
    current_node: Optional[str] = Field(None, description="Current node")


class ProjectCollaboratorFilter(BaseModel):
    """Schema for collaborator filtering"""
    project_id: Optional[UUID] = Field(None, description="Filter by project")
    permission_level: Optional[PermissionLevel] = Field(None, description="Filter by permission level")
    is_online: Optional[bool] = Field(None, description="Filter by online status")
    activity_status: Optional[ActivityStatus] = Field(None, description="Filter by activity status")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    has_edited: Optional[bool] = Field(None, description="Filter by edit history")


class ProjectCollaboratorExport(BaseModel):
    """Schema for collaborator export"""
    project_id: UUID = Field(..., description="Project ID")
    filters: Optional[ProjectCollaboratorFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_activity: bool = Field(default=False, description="Include activity data")
    include_permissions: bool = Field(default=True, description="Include permission data")

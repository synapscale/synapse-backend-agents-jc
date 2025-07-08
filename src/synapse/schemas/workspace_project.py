from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ProjectStatus(str, Enum):
    """Enum for project status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    TEMPLATE = "template"
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class WorkspaceProjectBase(BaseModel):
    """Base schema for WorkspaceProject"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    workflow_id: UUID = Field(..., description="Workflow ID")
    name: str = Field(..., max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    color: Optional[str] = Field(None, max_length=7, description="Project color (hex)")
    status: ProjectStatus = Field(..., description="Project status")
    allow_concurrent_editing: bool = Field(default=True, description="Allow concurrent editing")
    auto_save_interval: Optional[int] = Field(None, description="Auto-save interval in seconds")
    version_control_enabled: bool = Field(default=True, description="Enable version control")
    is_template: bool = Field(default=False, description="Is project template")
    is_public: bool = Field(default=False, description="Is project public")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class WorkspaceProjectCreate(WorkspaceProjectBase):
    """Schema for creating a new workspace project"""
    pass


class WorkspaceProjectUpdate(BaseModel):
    """Schema for updating an existing workspace project"""
    name: Optional[str] = Field(None, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    color: Optional[str] = Field(None, max_length=7, description="Project color (hex)")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    allow_concurrent_editing: Optional[bool] = Field(None, description="Allow concurrent editing")
    auto_save_interval: Optional[int] = Field(None, description="Auto-save interval in seconds")
    version_control_enabled: Optional[bool] = Field(None, description="Enable version control")
    is_template: Optional[bool] = Field(None, description="Is project template")
    is_public: Optional[bool] = Field(None, description="Is project public")


class WorkspaceProjectInDB(WorkspaceProjectBase):
    """Schema for workspace project in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Project ID")
    collaborator_count: int = Field(..., description="Number of collaborators")
    edit_count: int = Field(..., description="Number of edits")
    comment_count: int = Field(..., description="Number of comments")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_edited_at: datetime = Field(..., description="Last edit timestamp")


class WorkspaceProjectResponse(WorkspaceProjectInDB):
    """Schema for workspace project response"""
    workspace_name: Optional[str] = Field(None, description="Workspace name")
    workflow_name: Optional[str] = Field(None, description="Workflow name")
    last_editor_name: Optional[str] = Field(None, description="Last editor name")
    is_owner: bool = Field(..., description="Whether current user is owner")
    permissions: Dict[str, bool] = Field(..., description="User permissions")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent activity")
    active_collaborators: int = Field(..., description="Active collaborators count")


class WorkspaceProjectListResponse(BaseModel):
    """Schema for workspace project list response"""
    model_config = ConfigDict(from_attributes=True)
    
    projects: List[WorkspaceProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    active_count: int = Field(..., description="Active projects count")
    template_count: int = Field(..., description="Template projects count")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of projects per page")
    pages: int = Field(..., description="Total number of pages")


class WorkspaceProjectClone(BaseModel):
    """Schema for cloning a workspace project"""
    project_id: UUID = Field(..., description="Project ID to clone")
    new_name: str = Field(..., description="New project name")
    new_description: Optional[str] = Field(None, description="New project description")
    target_workspace_id: Optional[UUID] = Field(None, description="Target workspace ID")
    clone_collaborators: bool = Field(default=False, description="Clone collaborators")
    clone_comments: bool = Field(default=False, description="Clone comments")
    clone_versions: bool = Field(default=True, description="Clone version history")


class WorkspaceProjectCloneResponse(BaseModel):
    """Schema for project clone response"""
    original_project_id: UUID = Field(..., description="Original project ID")
    cloned_project_id: UUID = Field(..., description="Cloned project ID")
    cloned_project: WorkspaceProjectResponse = Field(..., description="Cloned project details")
    success: bool = Field(..., description="Clone success")
    message: str = Field(..., description="Clone message")


class WorkspaceProjectArchive(BaseModel):
    """Schema for archiving a workspace project"""
    project_id: UUID = Field(..., description="Project ID to archive")
    archive_reason: Optional[str] = Field(None, description="Archive reason")
    notify_collaborators: bool = Field(default=True, description="Notify collaborators")


class WorkspaceProjectRestore(BaseModel):
    """Schema for restoring a workspace project"""
    project_id: UUID = Field(..., description="Project ID to restore")
    restore_reason: Optional[str] = Field(None, description="Restore reason")
    notify_collaborators: bool = Field(default=True, description="Notify collaborators")


class WorkspaceProjectTransfer(BaseModel):
    """Schema for transferring a workspace project"""
    project_id: UUID = Field(..., description="Project ID to transfer")
    target_workspace_id: UUID = Field(..., description="Target workspace ID")
    transfer_collaborators: bool = Field(default=True, description="Transfer collaborators")
    transfer_comments: bool = Field(default=True, description="Transfer comments")
    transfer_versions: bool = Field(default=True, description="Transfer version history")
    notify_collaborators: bool = Field(default=True, description="Notify collaborators")


class WorkspaceProjectStatistics(BaseModel):
    """Schema for workspace project statistics"""
    project_id: UUID = Field(..., description="Project ID")
    total_edits: int = Field(..., description="Total edits")
    total_comments: int = Field(..., description="Total comments")
    total_collaborators: int = Field(..., description="Total collaborators")
    active_collaborators: int = Field(..., description="Active collaborators")
    total_versions: int = Field(..., description="Total versions")
    lines_of_code: Optional[int] = Field(None, description="Lines of code")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    edit_frequency: Dict[str, int] = Field(..., description="Edit frequency by day")
    collaborator_activity: List[Dict[str, Any]] = Field(..., description="Collaborator activity")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent activity")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")


class WorkspaceProjectSettings(BaseModel):
    """Schema for workspace project settings"""
    project_id: UUID = Field(..., description="Project ID")
    allow_concurrent_editing: bool = Field(..., description="Allow concurrent editing")
    auto_save_interval: int = Field(..., description="Auto-save interval in seconds")
    version_control_enabled: bool = Field(..., description="Enable version control")
    comment_notifications: bool = Field(..., description="Enable comment notifications")
    edit_notifications: bool = Field(..., description="Enable edit notifications")
    public_sharing: bool = Field(..., description="Enable public sharing")
    guest_access: bool = Field(..., description="Enable guest access")
    backup_enabled: bool = Field(..., description="Enable automatic backups")
    backup_frequency: str = Field(..., description="Backup frequency")


class WorkspaceProjectFilter(BaseModel):
    """Schema for project filtering"""
    workspace_id: Optional[UUID] = Field(None, description="Filter by workspace")
    status: Optional[ProjectStatus] = Field(None, description="Filter by status")
    is_template: Optional[bool] = Field(None, description="Filter templates")
    is_public: Optional[bool] = Field(None, description="Filter public projects")
    collaborator_id: Optional[UUID] = Field(None, description="Filter by collaborator")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    search_term: Optional[str] = Field(None, description="Search in name/description")
    color: Optional[str] = Field(None, description="Filter by color")


class WorkspaceProjectExport(BaseModel):
    """Schema for project export"""
    project_id: UUID = Field(..., description="Project ID")
    format: str = Field(default="json", description="Export format")
    include_collaborators: bool = Field(default=True, description="Include collaborators")
    include_comments: bool = Field(default=True, description="Include comments")
    include_versions: bool = Field(default=False, description="Include version history")
    include_analytics: bool = Field(default=False, description="Include analytics")
    compress_output: bool = Field(default=True, description="Compress output")


class WorkspaceProjectBatch(BaseModel):
    """Schema for batch project operations"""
    project_ids: List[UUID] = Field(..., description="List of project IDs")
    action: str = Field(..., description="Batch action (archive, delete, etc.)")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action-specific data")


class WorkspaceProjectTemplate(BaseModel):
    """Schema for project template"""
    project_id: UUID = Field(..., description="Source project ID")
    template_name: str = Field(..., description="Template name")
    template_description: Optional[str] = Field(None, description="Template description")
    template_category: Optional[str] = Field(None, description="Template category")
    template_tags: List[str] = Field(default_factory=list, description="Template tags")
    is_public_template: bool = Field(default=False, description="Is public template")
    include_sample_data: bool = Field(default=True, description="Include sample data")


class WorkspaceProjectDuplicate(BaseModel):
    """Schema for duplicating a workspace project"""
    project_id: UUID = Field(..., description="Project ID to duplicate")
    new_name: str = Field(..., description="New project name")
    duplicate_in_workspace: bool = Field(default=True, description="Duplicate in same workspace")
    target_workspace_id: Optional[UUID] = Field(None, description="Target workspace ID")
    preserve_collaborators: bool = Field(default=False, description="Preserve collaborators")

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ProjectVersionBase(BaseModel):
    """Base schema for ProjectVersion"""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID")
    version_number: int = Field(..., description="Version number")
    version_name: Optional[str] = Field(None, description="Version name")
    description: Optional[str] = Field(None, description="Version description")
    workflow_data: Dict[str, Any] = Field(..., description="Workflow data")
    changes_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of changes")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="File checksum")
    is_major: bool = Field(default=False, description="Whether this is a major version")
    is_auto_save: bool = Field(default=False, description="Whether this is an auto-save version")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class ProjectVersionCreate(ProjectVersionBase):
    """Schema for creating a new project version"""
    pass


class ProjectVersionUpdate(BaseModel):
    """Schema for updating an existing project version"""
    version_name: Optional[str] = Field(None, description="Version name")
    description: Optional[str] = Field(None, description="Version description")
    workflow_data: Optional[Dict[str, Any]] = Field(None, description="Workflow data")
    changes_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of changes")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="File checksum")
    is_major: Optional[bool] = Field(None, description="Whether this is a major version")


class ProjectVersionInDB(ProjectVersionBase):
    """Schema for project version in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Version ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ProjectVersionResponse(ProjectVersionInDB):
    """Schema for project version response"""
    pass


class ProjectVersionListResponse(BaseModel):
    """Schema for project version list response"""
    model_config = ConfigDict(from_attributes=True)
    
    versions: list[ProjectVersionResponse] = Field(..., description="List of project versions")
    total: int = Field(..., description="Total number of versions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of versions per page")
    pages: int = Field(..., description="Total number of pages")


class ProjectVersionComparison(BaseModel):
    """Schema for comparing project versions"""
    from_version: ProjectVersionResponse = Field(..., description="Source version")
    to_version: ProjectVersionResponse = Field(..., description="Target version")
    changes: Dict[str, Any] = Field(..., description="Detailed changes between versions")
    added_nodes: list[str] = Field(..., description="Added nodes")
    removed_nodes: list[str] = Field(..., description="Removed nodes")
    modified_nodes: list[str] = Field(..., description="Modified nodes")
    similarity_score: float = Field(..., description="Similarity score (0-1)")


class ProjectVersionRestore(BaseModel):
    """Schema for version restore request"""
    version_id: UUID = Field(..., description="Version ID to restore")
    create_backup: bool = Field(default=True, description="Create backup before restore")
    restore_name: Optional[str] = Field(None, description="Name for the restore version")


class ProjectVersionRestoreResponse(BaseModel):
    """Schema for version restore response"""
    success: bool = Field(..., description="Restore success")
    restored_version: ProjectVersionResponse = Field(..., description="Restored version")
    backup_version: Optional[ProjectVersionResponse] = Field(None, description="Backup version created")
    message: str = Field(..., description="Response message")


class ProjectVersionStatistics(BaseModel):
    """Schema for project version statistics"""
    project_id: UUID = Field(..., description="Project ID")
    total_versions: int = Field(..., description="Total number of versions")
    major_versions: int = Field(..., description="Number of major versions")
    auto_save_versions: int = Field(..., description="Number of auto-save versions")
    latest_version: ProjectVersionResponse = Field(..., description="Latest version")
    version_history: list[ProjectVersionResponse] = Field(..., description="Version history")
    total_file_size: int = Field(..., description="Total file size across all versions")
    average_version_size: float = Field(..., description="Average version size")


class ProjectVersionBranch(BaseModel):
    """Schema for version branching"""
    base_version_id: UUID = Field(..., description="Base version ID")
    branch_name: str = Field(..., description="Branch name")
    description: Optional[str] = Field(None, description="Branch description")
    workflow_data: Dict[str, Any] = Field(..., description="Initial workflow data")


class ProjectVersionMerge(BaseModel):
    """Schema for version merging"""
    source_version_id: UUID = Field(..., description="Source version ID")
    target_version_id: UUID = Field(..., description="Target version ID")
    merge_strategy: str = Field(default="auto", description="Merge strategy")
    resolve_conflicts: bool = Field(default=False, description="Whether to resolve conflicts")
    merge_message: Optional[str] = Field(None, description="Merge message")


class ProjectVersionTag(BaseModel):
    """Schema for version tagging"""
    version_id: UUID = Field(..., description="Version ID")
    tag_name: str = Field(..., description="Tag name")
    tag_description: Optional[str] = Field(None, description="Tag description")
    tag_type: str = Field(default="release", description="Tag type")

"""
Schemas for ComponentVersion - a model for managing versions of marketplace components.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class VersionStatus(str, Enum):
    """Enum for the status of a component version."""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ComponentVersionBase(BaseModel):
    """Base schema for ComponentVersion attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    version: str = Field(..., max_length=20, description="The version number of the component (e.g., '1.0.0').")
    is_latest: bool = Field(..., description="Indicates if this is the latest version of the component.")
    is_stable: bool = Field(..., description="Indicates if this is a stable version.")
    changelog: Optional[str] = Field(None, description="The changelog for this version.")
    breaking_changes: Optional[str] = Field(None, description="A list of breaking changes in this version.")
    migration_guide: Optional[str] = Field(None, description="A guide for migrating to this version.")
    component_data: Dict[str, Any] = Field(..., description="The data of the component for this version.")
    file_size: Optional[int] = Field(None, description="The file size of the component in bytes.")
    min_platform_version: Optional[str] = Field(None, max_length=20, description="The minimum platform version required.")
    max_platform_version: Optional[str] = Field(None, max_length=20, description="The maximum platform version supported.")
    dependencies: Optional[Dict[str, Any]] = Field(None, description="A dictionary of dependencies for this version.")
    download_count: int = Field(0, description="The number of times this version has been downloaded.")
    status: VersionStatus = Field(..., description="The status of this version.")

class ComponentVersionCreate(ComponentVersionBase):
    """Schema for creating a new component version."""
    component_id: UUID = Field(..., description="The component to which this version belongs.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this version belongs.")

class ComponentVersionUpdate(BaseModel):
    """Schema for updating an existing component version. All fields are optional."""
    is_latest: Optional[bool] = Field(None, description="New latest status.")
    is_stable: Optional[bool] = Field(None, description="New stable status.")
    changelog: Optional[str] = Field(None, description="New changelog.")
    breaking_changes: Optional[str] = Field(None, description="New list of breaking changes.")
    migration_guide: Optional[str] = Field(None, description="New migration guide.")
    component_data: Optional[Dict[str, Any]] = Field(None, description="New component data.")
    file_size: Optional[int] = Field(None, description="New file size.")
    min_platform_version: Optional[str] = Field(None, max_length=20, description="New minimum platform version.")
    max_platform_version: Optional[str] = Field(None, max_length=20, description="New maximum platform version.")
    dependencies: Optional[Dict[str, Any]] = Field(None, description="New dependencies.")
    status: Optional[VersionStatus] = Field(None, description="New status.")

class ComponentVersionResponse(ComponentVersionBase):
    """Response schema for a component version, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the component version.")
    component_id: UUID = Field(..., description="The component to which this version belongs.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this version belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the version was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    deprecated_at: Optional[datetime] = Field(None, description="Timestamp of when the version was deprecated.")

class ComponentVersionListResponse(BaseModel):
    """Paginated list of component versions."""
    items: List[ComponentVersionResponse] = Field(..., description="List of component versions for the current page.")
    total: int = Field(..., description="Total number of component versions.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

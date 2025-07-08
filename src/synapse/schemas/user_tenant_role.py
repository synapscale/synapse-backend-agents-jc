"""
Schemas for UserTenantRole - a model for managing user roles within specific tenants.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class UserTenantRoleStatus(str, Enum):
    """Enum for the status of a user-tenant role assignment."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class UserTenantRoleBase(BaseModel):
    """Base schema for UserTenantRole attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    user_id: UUID = Field(..., description="The ID of the user.")
    tenant_id: UUID = Field(..., description="The ID of the tenant.")
    role_id: UUID = Field(..., description="The ID of the RBAC role assigned.")
    granted_by: Optional[UUID] = Field(None, description="The ID of the user who granted this role.")
    granted_at: Optional[datetime] = Field(None, description="Timestamp when the role was granted.")
    expires_at: Optional[datetime] = Field(None, description="Timestamp when the role assignment expires.")
    is_active: bool = Field(True, description="Indicates if the role assignment is currently active.")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions for the role assignment.")


class UserTenantRoleCreate(UserTenantRoleBase):
    """Schema for creating a new UserTenantRole assignment."""
    pass


class UserTenantRoleUpdate(BaseModel):
    """Schema for updating an existing UserTenantRole assignment. All fields are optional."""
    role_id: Optional[UUID] = Field(None, description="New RBAC role ID.")
    expires_at: Optional[datetime] = Field(None, description="New expiration timestamp.")
    is_active: Optional[bool] = Field(None, description="New active status.")
    conditions: Optional[Dict[str, Any]] = Field(None, description="New conditions.")


class UserTenantRoleResponse(UserTenantRoleBase):
    """Response schema for a UserTenantRole assignment, including database-generated fields and related data."""
    id: UUID = Field(..., description="Unique identifier for the role assignment.")
    created_at: datetime = Field(..., description="Timestamp of when the assignment was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    
    # Enriched data
    user_email: Optional[str] = Field(None, description="The email of the user.")
    tenant_name: Optional[str] = Field(None, description="The name of the tenant.")
    role_name: Optional[str] = Field(None, description="The name of the assigned role.")
    granted_by_user_email: Optional[str] = Field(None, description="The email of the user who granted the role.")
    is_expired: Optional[bool] = Field(None, description="Indicates if the role assignment has expired.")
    days_until_expiry: Optional[int] = Field(None, description="Number of days until the role expires (negative if expired).")


class UserTenantRoleListResponse(BaseModel):
    """Paginated list of UserTenantRole assignments."""
    items: List[UserTenantRoleResponse] = Field(..., description="List of user-tenant role assignments for the current page.")
    total: int = Field(..., description="Total number of assignments.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

"""
Schemas for RBACRolePermission - a model for managing role-permission assignments with conditions.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class RBACRolePermissionBase(BaseModel):
    """Base schema for RBACRolePermission attributes."""
    model_config = ConfigDict(from_attributes=True)

    role_id: UUID = Field(..., description="The ID of the RBAC role.")
    permission_id: UUID = Field(..., description="The ID of the RBAC permission.")
    granted: bool = Field(True, description="Indicates if the permission is granted or denied for this role.")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions under which the permission is granted.")


class RBACRolePermissionCreate(RBACRolePermissionBase):
    """Schema for creating a new RBACRolePermission assignment."""
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this assignment belongs.")


class RBACRolePermissionUpdate(BaseModel):
    """Schema for updating an existing RBACRolePermission assignment. All fields are optional."""
    granted: Optional[bool] = Field(None, description="New granted status.")
    conditions: Optional[Dict[str, Any]] = Field(None, description="New conditions.")


class RBACRolePermissionResponse(RBACRolePermissionBase):
    """Response schema for an RBACRolePermission assignment, including database-generated fields and related data."""
    id: UUID = Field(..., description="Unique identifier for the role-permission assignment.")
    created_at: datetime = Field(..., description="Timestamp of when the assignment was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this assignment belongs.")
    
    # Enriched data
    role_name: Optional[str] = Field(None, description="The name of the associated role.")
    permission_key: Optional[str] = Field(None, description="The key of the associated permission.")
    permission_description: Optional[str] = Field(None, description="The description of the associated permission.")


class RBACRolePermissionListResponse(BaseModel):
    """Paginated list of RBACRolePermission assignments."""
    items: List[RBACRolePermissionResponse] = Field(..., description="List of role-permission assignments for the current page.")
    total: int = Field(..., description="Total number of assignments.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

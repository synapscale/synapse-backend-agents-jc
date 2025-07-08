"""
Schemas para RBACRolePermission
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class RBACRolePermissionBase(BaseModel):
    """Base schema for RBACRolePermission"""
    role_id: UUID4
    permission_id: UUID4
    granted: bool = Field(default=True, description="Whether the permission is granted")
    conditions: Optional[Dict[str, Any]] = Field(default={}, description="Conditions for the permission")
    tenant_id: Optional[UUID4] = None
    
    @validator('conditions')
    def validate_conditions(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Conditions must be a dictionary")
        return v
    
    class Config:
        from_attributes = True

class RBACRolePermissionCreate(RBACRolePermissionBase):
    """Schema for creating RBACRolePermission"""
    pass

class RBACRolePermissionRead(RBACRolePermissionBase):
    """Schema for reading RBACRolePermission"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RBACRolePermissionUpdate(BaseModel):
    """Schema for updating RBACRolePermission"""
    granted: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    
    @validator('conditions')
    def validate_conditions(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Conditions must be a dictionary")
        return v
    
    class Config:
        from_attributes = True

class RBACRolePermissionWithDetails(RBACRolePermissionRead):
    """Schema for reading RBACRolePermission with role and permission details"""
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    permission_key: Optional[str] = None
    permission_resource: Optional[str] = None
    permission_action: Optional[str] = None
    
    class Config:
        from_attributes = True

class RBACRolePermissionCheck(BaseModel):
    """Schema for permission check request"""
    role_id: UUID4
    permission_key: str
    context: Optional[Dict[str, Any]] = Field(default={}, description="Context for condition evaluation")
    tenant_id: Optional[UUID4] = None
    
    class Config:
        from_attributes = True

class RBACRolePermissionCheckResult(BaseModel):
    """Schema for permission check result"""
    has_permission: bool
    role_id: UUID4
    permission_key: str
    conditions_met: bool
    details: Optional[str] = None
    
    class Config:
        from_attributes = True

class RBACRolePermissionBulkCreate(BaseModel):
    """Schema for bulk creating role permissions"""
    role_id: UUID4
    permissions: list[Dict[str, Any]] = Field(..., description="List of permission assignments")
    tenant_id: Optional[UUID4] = None
    
    class Config:
        from_attributes = True

class RBACRolePermissionBulkUpdate(BaseModel):
    """Schema for bulk updating role permissions"""
    role_id: UUID4
    permissions: list[Dict[str, Any]] = Field(..., description="List of permission updates")
    
    class Config:
        from_attributes = True

class RBACRolePermissionList(BaseModel):
    """Schema for role permission list with pagination"""
    permissions: list[RBACRolePermissionWithDetails]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class RBACRolePermissionSummary(BaseModel):
    """Schema for role permission summary"""
    total_permissions: int
    granted_permissions: int
    denied_permissions: int
    conditional_permissions: int
    
    class Config:
        from_attributes = True

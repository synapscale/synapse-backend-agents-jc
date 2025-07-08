"""
Schemas for User management and authentication.
"""

import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ===== ENUMS ALINHADOS COM O BANCO =====


class UserStatus(str, Enum):
    """User status - ALIGNED WITH THE DATABASE"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ERROR = "error"
    DELETED = "deleted"


class UserRole(str, Enum):
    """Roles based on the is_superuser field"""

    ADMIN = "admin"
    USER = "user"


# ===== USER SCHEMAS (ALIGNED PERFECTLY WITH THE DATABASE) =====


class UserBase(BaseModel):
    """Base schema for user attributes."""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    email: EmailStr = Field(..., max_length=255, description="Unique user email")
    username: str = Field(
        ..., min_length=3, max_length=255, description="Unique username"
    )
    full_name: str = Field(..., min_length=2, max_length=200, description="Full name")
    is_active: bool = Field(True, description="Whether the user is active")
    is_verified: bool = Field(False, description="Whether the email has been verified")
    is_superuser: bool = Field(
        False, description="Whether the user is an administrator"
    )
    status: UserStatus = Field(UserStatus.ACTIVE, description="User status")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL of the profile image"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class UserCreate(UserBase):
    """Schema for user creation - ALIGNED WITH DATABASE"""

    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Password (optional, will be auto-generated if not provided)",
    )


class UserUpdate(BaseModel):
    """Schema for user updates - ALIGNED WITH DATABASE"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    email: Optional[EmailStr] = Field(
        None, max_length=255, description="Unique user email"
    )
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Unique username"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Full name"
    )
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    is_verified: Optional[bool] = Field(
        None, description="Whether the email has been verified"
    )
    is_superuser: Optional[bool] = Field(
        None, description="Whether the user is an administrator"
    )
    status: Optional[UserStatus] = Field(None, description="User status")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL of the profile image"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UserResponse(UserBase):
    """Response schema for a user - PERFECTLY ALIGNED WITH DATABASE (excluding sensitive fields)"""

    id: uuid.UUID = Field(..., description="User ID")
    last_login_at: Optional[datetime.datetime] = Field(
        None, description="Last login timestamp"
    )
    login_count: Optional[int] = Field(None, description="Total login count")
    failed_login_attempts: Optional[int] = Field(
        None, description="Failed login attempts"
    )
    account_locked_until: Optional[datetime.datetime] = Field(
        None, description="Account locked until timestamp"
    )
    tenant_id: Optional[uuid.UUID] = Field(None, description="Tenant ID")
    created_at: Optional[datetime.datetime] = Field(
        None, description="Creation timestamp"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Last update timestamp"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        # Exclude sensitive fields from serialization
        exclude={"hashed_password"}
    )


class UserListResponse(BaseModel):
    """Paginated list of users."""

    items: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")
    size: int = Field(..., description="Number of items per page")


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    bio: Optional[str] = Field(None, description="User biography")


class UserProfileResponse(BaseModel):
    """User profile response."""

    id: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="Email")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    profile_image_url: Optional[str] = Field(
        None, description="URL of the profile image"
    )
    bio: Optional[str] = Field(None, description="User biography")
    is_active: bool = Field(..., description="Whether the user is active")
    is_verified: bool = Field(..., description="Whether the email has been verified")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")


# Re-export for compatibility from response_models.py
UsersResponse = UserResponse

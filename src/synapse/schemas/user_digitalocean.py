"""
Schemas para UserDigitalOcean
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

class UserDigitalOceanBase(BaseModel):
    """Base schema for UserDigitalOcean"""
    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, max_length=255, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user is superuser")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Username must be at least 3 characters")
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        return v
    
    class Config:
        from_attributes = True

class UserDigitalOceanCreate(UserDigitalOceanBase):
    """Schema for creating UserDigitalOcean"""
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserDigitalOceanRead(UserDigitalOceanBase):
    """Schema for reading UserDigitalOcean"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_verified: Optional[bool] = None
    
    class Config:
        from_attributes = True

class UserDigitalOceanUpdate(BaseModel):
    """Schema for updating UserDigitalOcean"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Username must be at least 3 characters")
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        return v
    
    class Config:
        from_attributes = True

class UserDigitalOceanPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    
    class Config:
        from_attributes = True

class UserDigitalOceanAuth(BaseModel):
    """Schema for user authentication"""
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

class UserDigitalOceanList(BaseModel):
    """Schema for user list with pagination"""
    users: list[UserDigitalOceanRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class UserDigitalOceanStats(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    superusers: int
    verified_users: int
    recent_signups: int
    
    class Config:
        from_attributes = True

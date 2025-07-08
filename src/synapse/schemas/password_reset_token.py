from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class PasswordResetTokenBase(BaseModel):
    """Base schema for PasswordResetToken"""
    token: str = Field(..., description="Reset token")
    user_id: UUID = Field(..., description="User ID")
    expires_at: datetime = Field(..., description="Token expiration time")
    is_used: Optional[bool] = Field(default=False, description="Whether token has been used")


class PasswordResetTokenCreate(PasswordResetTokenBase):
    """Schema for creating a new password reset token"""
    pass


class PasswordResetTokenUpdate(BaseModel):
    """Schema for updating an existing password reset token"""
    is_used: Optional[bool] = Field(None, description="Whether token has been used")


class PasswordResetTokenInDB(PasswordResetTokenBase):
    """Schema for password reset token in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Token ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PasswordResetTokenResponse(PasswordResetTokenInDB):
    """Schema for password reset token response"""
    pass


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: str = Field(..., description="User email")


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    message: str = Field(..., description="Response message")
    success: bool = Field(..., description="Operation success status")

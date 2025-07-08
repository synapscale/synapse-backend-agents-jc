from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class EmailVerificationTokenBase(BaseModel):
    """Base schema for EmailVerificationToken"""
    token: str = Field(..., description="Verification token")
    user_id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email to verify")
    expires_at: datetime = Field(..., description="Token expiration time")
    is_used: Optional[bool] = Field(default=False, description="Whether token has been used")


class EmailVerificationTokenCreate(EmailVerificationTokenBase):
    """Schema for creating a new email verification token"""
    pass


class EmailVerificationTokenUpdate(BaseModel):
    """Schema for updating an existing email verification token"""
    is_used: Optional[bool] = Field(None, description="Whether token has been used")


class EmailVerificationTokenInDB(EmailVerificationTokenBase):
    """Schema for email verification token in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Token ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class EmailVerificationTokenResponse(EmailVerificationTokenInDB):
    """Schema for email verification token response"""
    pass


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    email: EmailStr = Field(..., description="Email to verify")


class EmailVerificationConfirm(BaseModel):
    """Schema for confirming email verification"""
    token: str = Field(..., description="Verification token")


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response"""
    message: str = Field(..., description="Response message")
    success: bool = Field(..., description="Operation success status")
    verified: bool = Field(..., description="Whether email is verified")


class ResendVerificationRequest(BaseModel):
    """Schema for resending verification email"""
    email: EmailStr = Field(..., description="Email to resend verification to")

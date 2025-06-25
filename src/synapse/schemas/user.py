"""
Schemas para endpoints de usuário
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserPreferences(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "pt-BR"
    notifications: Optional[dict] = None
    workspace: Optional[dict] = None

    class Config:
        from_attributes = True

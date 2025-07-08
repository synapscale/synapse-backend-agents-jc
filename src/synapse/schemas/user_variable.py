"""
Schemas para UserVariable
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4, validator

class UserVariableBase(BaseModel):
    """Base schema for UserVariable"""
    key: str = Field(..., max_length=255, description="Variable key/name")
    value: str = Field(..., description="Variable value")
    is_secret: bool = Field(default=False, description="Whether this is a secret variable")
    category: Optional[str] = Field(None, max_length=100, description="Variable category")
    description: Optional[str] = Field(None, description="Variable description")
    is_encrypted: bool = Field(default=False, description="Whether the value is encrypted")
    is_active: bool = Field(default=True, description="Whether the variable is active")
    tenant_id: Optional[UUID4] = None
    
    @validator('key')
    def validate_key(cls, v):
        if not v.strip():
            raise ValueError("Key cannot be empty")
        # Remove any potentially dangerous characters
        if any(char in v for char in ['$', '`', ';', '|', '&']):
            raise ValueError("Key contains invalid characters")
        return v.strip()
    
    @validator('value')
    def validate_value(cls, v):
        if not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()
    
    class Config:
        from_attributes = True

class UserVariableCreate(UserVariableBase):
    """Schema for creating UserVariable"""
    user_id: UUID4

class UserVariableRead(UserVariableBase):
    """Schema for reading UserVariable"""
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    display_value: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserVariableUpdate(BaseModel):
    """Schema for updating UserVariable"""
    value: Optional[str] = None
    is_secret: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_encrypted: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('value')
    def validate_value(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip() if v else v
    
    class Config:
        from_attributes = True

class UserVariableSecure(BaseModel):
    """Schema for secure variable operations"""
    key: str = Field(..., max_length=255)
    value: str = Field(..., description="Encrypted or masked value")
    is_secret: bool = True
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserVariableList(BaseModel):
    """Schema for variable list with pagination"""
    variables: list[UserVariableRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class UserVariableStats(BaseModel):
    """Schema for user variable statistics"""
    total_variables: int
    secret_variables: int
    encrypted_variables: int
    active_variables: int
    by_category: dict[str, int]
    
    class Config:
        from_attributes = True

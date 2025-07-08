"""
Schemas para ExecutionStatus
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4, validator

class ExecutionStatusBase(BaseModel):
    """Base schema for ExecutionStatus"""
    name: str = Field(..., max_length=100, description="Unique status name")
    display_name: str = Field(..., max_length=255, description="Display name for the status")
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    is_final: bool = Field(default=False, description="Whether this is a final status")
    is_error: bool = Field(default=False, description="Whether this indicates an error")
    is_success: bool = Field(default=False, description="Whether this indicates success")
    can_retry: bool = Field(default=True, description="Whether retry is allowed from this status")
    is_active: bool = Field(default=True, description="Whether the status is active")
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Name must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    class Config:
        from_attributes = True

class ExecutionStatusCreate(ExecutionStatusBase):
    """Schema for creating ExecutionStatus"""
    pass

class ExecutionStatusRead(ExecutionStatusBase):
    """Schema for reading ExecutionStatus"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExecutionStatusUpdate(BaseModel):
    """Schema for updating ExecutionStatus"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)
    is_final: Optional[bool] = None
    is_error: Optional[bool] = None
    is_success: Optional[bool] = None
    can_retry: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    class Config:
        from_attributes = True

class ExecutionStatusSummary(BaseModel):
    """Schema for execution status summary"""
    total_statuses: int
    active_statuses: int
    final_statuses: int
    error_statuses: int
    success_statuses: int
    
    class Config:
        from_attributes = True

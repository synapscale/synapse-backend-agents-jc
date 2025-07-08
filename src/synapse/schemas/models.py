"""
Schemas para Models (generic model metadata)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4

class ModelsBase(BaseModel):
    """Base schema for Models metadata"""
    name: str = Field(..., max_length=255, description="Model name")
    table_name: str = Field(..., max_length=255, description="Database table name")
    schema_name: Optional[str] = Field(None, max_length=255, description="Database schema name")
    description: Optional[str] = None
    version: str = Field(default="1.0", max_length=50, description="Model version")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    is_active: bool = Field(default=True, description="Whether the model is active")
    
    class Config:
        from_attributes = True

class ModelsCreate(ModelsBase):
    """Schema for creating Models"""
    pass

class ModelsRead(ModelsBase):
    """Schema for reading Models"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ModelsUpdate(BaseModel):
    """Schema for updating Models"""
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class ModelsStats(BaseModel):
    """Schema for models statistics"""
    total_models: int
    active_models: int
    by_schema: Dict[str, int]
    recent_updates: int
    
    class Config:
        from_attributes = True

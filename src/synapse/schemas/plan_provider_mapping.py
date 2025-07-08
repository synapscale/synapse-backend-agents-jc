"""
Schemas para PlanProviderMapping
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4

class PlanProviderMappingBase(BaseModel):
    """Base schema for PlanProviderMapping"""
    plan_id: UUID4
    provider_id: UUID4
    external_plan_id: str = Field(..., max_length=255, description="External provider plan ID")
    mapping_config: Optional[Dict[str, Any]] = Field(default={}, description="Mapping configuration")
    is_active: bool = Field(default=True, description="Whether the mapping is active")
    
    class Config:
        from_attributes = True

class PlanProviderMappingCreate(PlanProviderMappingBase):
    """Schema for creating PlanProviderMapping"""
    pass

class PlanProviderMappingRead(PlanProviderMappingBase):
    """Schema for reading PlanProviderMapping"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlanProviderMappingUpdate(BaseModel):
    """Schema for updating PlanProviderMapping"""
    external_plan_id: Optional[str] = Field(None, max_length=255)
    mapping_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

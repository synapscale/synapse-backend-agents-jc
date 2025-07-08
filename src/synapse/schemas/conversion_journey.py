"""
Schemas para ConversionJourney
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, UUID4

class ConversionJourneyBase(BaseModel):
    """Base schema for ConversionJourney"""
    name: str = Field(..., max_length=255, description="Journey name")
    description: Optional[str] = None
    stages: List[Dict[str, Any]] = Field(default=[], description="Journey stages")
    conversion_rate: Optional[float] = Field(None, description="Overall conversion rate")
    is_active: bool = Field(default=True, description="Whether journey is active")
    tenant_id: Optional[UUID4] = None
    
    class Config:
        from_attributes = True

class ConversionJourneyCreate(ConversionJourneyBase):
    """Schema for creating ConversionJourney"""
    pass

class ConversionJourneyRead(ConversionJourneyBase):
    """Schema for reading ConversionJourney"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversionJourneyUpdate(BaseModel):
    """Schema for updating ConversionJourney"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    stages: Optional[List[Dict[str, Any]]] = None
    conversion_rate: Optional[float] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

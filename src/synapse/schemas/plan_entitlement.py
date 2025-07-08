"""
Schemas para PlanEntitlement
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class PlanEntitlementBase(BaseModel):
    """Base schema for PlanEntitlement"""
    plan_id: UUID4
    feature_id: UUID4
    limit_value: Optional[int] = Field(None, description="Limit value for the feature")
    is_unlimited: bool = Field(default=False, description="Whether the feature is unlimited")
    entitlement_metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    
    @validator('limit_value')
    def validate_limit_value(cls, v, values):
        if v is not None and v < 0:
            raise ValueError("Limit value must be non-negative")
        if values.get('is_unlimited') and v is not None:
            raise ValueError("Cannot set limit value when unlimited is True")
        return v
    
    @validator('is_unlimited')
    def validate_is_unlimited(cls, v, values):
        if v and values.get('limit_value') is not None:
            raise ValueError("Cannot set unlimited when limit value is specified")
        return v
    
    class Config:
        from_attributes = True

class PlanEntitlementCreate(PlanEntitlementBase):
    """Schema for creating PlanEntitlement"""
    pass

class PlanEntitlementRead(PlanEntitlementBase):
    """Schema for reading PlanEntitlement"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlanEntitlementUpdate(BaseModel):
    """Schema for updating PlanEntitlement"""
    limit_value: Optional[int] = Field(None, description="Limit value for the feature")
    is_unlimited: Optional[bool] = Field(None, description="Whether the feature is unlimited")
    entitlement_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('limit_value')
    def validate_limit_value(cls, v, values):
        if v is not None and v < 0:
            raise ValueError("Limit value must be non-negative")
        if values.get('is_unlimited') and v is not None:
            raise ValueError("Cannot set limit value when unlimited is True")
        return v
    
    @validator('is_unlimited')
    def validate_is_unlimited(cls, v, values):
        if v and values.get('limit_value') is not None:
            raise ValueError("Cannot set unlimited when limit value is specified")
        return v
    
    class Config:
        from_attributes = True

class PlanEntitlementWithFeature(PlanEntitlementRead):
    """Schema for reading PlanEntitlement with feature details"""
    feature_name: Optional[str] = None
    feature_key: Optional[str] = None
    feature_description: Optional[str] = None
    
    class Config:
        from_attributes = True

class PlanEntitlementSummary(BaseModel):
    """Schema for plan entitlement summary"""
    total_entitlements: int
    unlimited_entitlements: int
    limited_entitlements: int
    features_covered: int
    
    class Config:
        from_attributes = True

class PlanEntitlementBulkCreate(BaseModel):
    """Schema for bulk creating plan entitlements"""
    plan_id: UUID4
    entitlements: list[Dict[str, Any]] = Field(..., description="List of entitlement data")
    
    class Config:
        from_attributes = True

class PlanEntitlementBulkUpdate(BaseModel):
    """Schema for bulk updating plan entitlements"""
    entitlements: list[Dict[str, Any]] = Field(..., description="List of entitlement updates")
    
    class Config:
        from_attributes = True

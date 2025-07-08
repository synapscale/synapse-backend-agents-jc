"""
Schemas para TenantFeature
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class TenantFeatureBase(BaseModel):
    """Base schema for TenantFeature"""
    tenant_id: UUID4
    feature_id: UUID4
    is_enabled: bool = Field(default=True, description="Whether the feature is enabled")
    usage_count: int = Field(default=0, description="Current usage count")
    limit_value: Optional[int] = Field(None, description="Usage limit")
    config: Optional[Dict[str, Any]] = Field(default={}, description="Feature configuration")
    expires_at: Optional[datetime] = Field(None, description="Feature expiration date")
    
    @validator('usage_count')
    def validate_usage_count(cls, v):
        if v < 0:
            raise ValueError("Usage count cannot be negative")
        return v
    
    @validator('limit_value')
    def validate_limit_value(cls, v):
        if v is not None and v < 0:
            raise ValueError("Limit value cannot be negative")
        return v
    
    class Config:
        from_attributes = True

class TenantFeatureCreate(TenantFeatureBase):
    """Schema for creating TenantFeature"""
    pass

class TenantFeatureRead(TenantFeatureBase):
    """Schema for reading TenantFeature"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_available: Optional[bool] = None
    can_use: Optional[bool] = None
    
    class Config:
        from_attributes = True

class TenantFeatureUpdate(BaseModel):
    """Schema for updating TenantFeature"""
    is_enabled: Optional[bool] = None
    usage_count: Optional[int] = None
    limit_value: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    
    @validator('usage_count')
    def validate_usage_count(cls, v):
        if v is not None and v < 0:
            raise ValueError("Usage count cannot be negative")
        return v
    
    @validator('limit_value')
    def validate_limit_value(cls, v):
        if v is not None and v < 0:
            raise ValueError("Limit value cannot be negative")
        return v
    
    class Config:
        from_attributes = True

class TenantFeatureWithDetails(TenantFeatureRead):
    """Schema for reading TenantFeature with feature details"""
    feature_name: Optional[str] = None
    feature_key: Optional[str] = None
    feature_description: Optional[str] = None
    
    class Config:
        from_attributes = True

class TenantFeatureUsage(BaseModel):
    """Schema for feature usage tracking"""
    tenant_id: UUID4
    feature_id: UUID4
    usage_increment: int = Field(default=1, description="Amount to increment usage by")
    
    @validator('usage_increment')
    def validate_usage_increment(cls, v):
        if v <= 0:
            raise ValueError("Usage increment must be positive")
        return v
    
    class Config:
        from_attributes = True

class TenantFeatureList(BaseModel):
    """Schema for tenant feature list with pagination"""
    features: list[TenantFeatureWithDetails]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class TenantFeatureStats(BaseModel):
    """Schema for tenant feature statistics"""
    total_features: int
    enabled_features: int
    expired_features: int
    over_limit_features: int
    total_usage: int
    
    class Config:
        from_attributes = True

class TenantFeatureBulkUpdate(BaseModel):
    """Schema for bulk updating tenant features"""
    feature_updates: list[Dict[str, Any]] = Field(..., description="List of feature updates")
    
    class Config:
        from_attributes = True

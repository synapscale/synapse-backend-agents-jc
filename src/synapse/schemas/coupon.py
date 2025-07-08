"""
Schemas para Coupon
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field, UUID4, validator

class CouponBase(BaseModel):
    """Base schema for Coupon"""
    code: str = Field(..., max_length=100, description="Unique coupon code")
    name: Optional[str] = Field(None, max_length=255, description="Display name for the coupon")
    description: Optional[str] = None
    type: str = Field(default="percentage", description="Type of coupon: percentage or fixed")
    value: Decimal = Field(..., description="Discount value (percentage or fixed amount)")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    max_uses: Optional[int] = Field(None, description="Maximum number of uses")
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount to apply coupon")
    max_discount: Optional[Decimal] = Field(None, description="Maximum discount amount")
    valid_from: Optional[datetime] = Field(None, description="Valid from date")
    valid_until: Optional[datetime] = Field(None, description="Valid until date")
    is_active: bool = Field(default=True, description="Whether the coupon is active")
    is_stackable: bool = Field(default=False, description="Whether the coupon can be stacked with others")
    applicable_plans: Optional[List[str]] = Field(default=[], description="List of plan IDs this coupon applies to")
    restrictions: Optional[Dict[str, Any]] = Field(default={}, description="Additional restrictions")
    coupon_metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    tenant_id: Optional[UUID4] = None
    created_by: Optional[UUID4] = None
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['percentage', 'fixed']:
            raise ValueError("Type must be 'percentage' or 'fixed'")
        return v
    
    @validator('value')
    def validate_value(cls, v, values):
        if v < 0:
            raise ValueError("Value must be positive")
        if values.get('type') == 'percentage' and v > 100:
            raise ValueError("Percentage value cannot exceed 100")
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-character code")
        return v.upper()
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class CouponCreate(CouponBase):
    """Schema for creating Coupon"""
    pass

class CouponRead(CouponBase):
    """Schema for reading Coupon"""
    id: UUID4
    used_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    is_valid: Optional[bool] = None
    is_expired: Optional[bool] = None
    remaining_uses: Optional[int] = None
    usage_percentage: Optional[float] = None
    
    class Config:
        from_attributes = True

class CouponUpdate(BaseModel):
    """Schema for updating Coupon"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    max_uses: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_discount: Optional[Decimal] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_stackable: Optional[bool] = None
    applicable_plans: Optional[List[str]] = None
    restrictions: Optional[Dict[str, Any]] = None
    coupon_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class CouponStats(BaseModel):
    """Schema for coupon statistics"""
    total_coupons: int
    active_coupons: int
    expired_coupons: int
    used_coupons: int
    total_uses: int
    total_discount_amount: Decimal
    
    class Config:
        from_attributes = True

class CouponUsage(BaseModel):
    """Schema for coupon usage tracking"""
    coupon_id: UUID4
    code: str
    used_at: datetime
    order_id: Optional[str] = None
    discount_amount: Decimal
    user_id: Optional[UUID4] = None
    
    class Config:
        from_attributes = True

class CouponValidation(BaseModel):
    """Schema for coupon validation result"""
    is_valid: bool
    discount_amount: Decimal
    error_message: Optional[str] = None
    coupon_details: Optional[CouponRead] = None
    
    class Config:
        from_attributes = True

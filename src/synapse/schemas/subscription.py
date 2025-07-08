"""
Schemas for Subscription - a model for managing user subscriptions.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class SubscriptionStatus(str, Enum):
    """Enum for the status of a subscription."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    PENDING = "pending"


class SubscriptionBase(BaseModel):
    """Base schema for Subscription attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    user_id: UUID = Field(..., description="The ID of the user who owns the subscription.")
    plan_id: UUID = Field(..., description="The ID of the plan subscribed to.")
    status: SubscriptionStatus = Field(..., description="The current status of the subscription.")
    start_date: datetime = Field(..., description="The date when the subscription started.")
    end_date: Optional[datetime] = Field(None, description="The date when the subscription is set to end.")
    next_billing_date: Optional[datetime] = Field(None, description="The next date the subscription will be billed.")
    payment_provider_id: Optional[UUID] = Field(None, description="The ID of the payment provider used for this subscription.")
    external_subscription_id: Optional[str] = Field(None, description="The ID of the subscription in the external payment provider system.")
    monthly_price: Optional[float] = Field(None, ge=0, description="The monthly price of the subscription.")
    yearly_price: Optional[float] = Field(None, ge=0, description="The yearly price of the subscription.")
    current_price: Optional[float] = Field(None, ge=0, description="The current effective price of the subscription.")
    is_active: bool = Field(True, description="Indicates if the subscription is currently active.")
    auto_renew: bool = Field(True, description="Indicates if the subscription will automatically renew.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the subscription.")
    tenant_id: UUID = Field(..., description="The tenant to which this subscription belongs.")


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new Subscription."""
    pass


class SubscriptionUpdate(BaseModel):
    """Schema for updating an existing Subscription. All fields are optional."""
    plan_id: Optional[UUID] = Field(None, description="New plan ID.")
    status: Optional[SubscriptionStatus] = Field(None, description="New status for the subscription.")
    end_date: Optional[datetime] = Field(None, description="New end date.")
    next_billing_date: Optional[datetime] = Field(None, description="New next billing date.")
    payment_provider_id: Optional[UUID] = Field(None, description="New payment provider ID.")
    external_subscription_id: Optional[str] = Field(None, description="New external subscription ID.")
    monthly_price: Optional[float] = Field(None, ge=0, description="New monthly price.")
    yearly_price: Optional[float] = Field(None, ge=0, description="New yearly price.")
    current_price: Optional[float] = Field(None, ge=0, description="New current price.")
    is_active: Optional[bool] = Field(None, description="New active status.")
    auto_renew: Optional[bool] = Field(None, description="New auto-renew status.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata.")


class SubscriptionResponse(SubscriptionBase):
    """Response schema for a Subscription, including database-generated fields and related data."""
    id: UUID = Field(..., description="Unique identifier for the subscription.")
    created_at: datetime = Field(..., description="Timestamp of when the subscription was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    user_name: Optional[str] = Field(None, description="The name of the user.")
    user_email: Optional[str] = Field(None, description="The email of the user.")
    plan_name: Optional[str] = Field(None, description="The name of the subscribed plan.")
    plan_description: Optional[str] = Field(None, description="The description of the subscribed plan.")
    is_expired: Optional[bool] = Field(None, description="Indicates if the subscription has expired.")
    days_until_expiry: Optional[int] = Field(None, description="Number of days until the subscription expires (negative if expired).")


class SubscriptionListResponse(BaseModel):
    """Paginated list of Subscriptions."""
    items: List[SubscriptionResponse] = Field(..., description="List of subscriptions for the current page.")
    total: int = Field(..., description="Total number of subscriptions.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class SubscriptionSummary(BaseModel):
    """Schema for aggregated subscription statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_active: int = Field(..., description="Total number of active subscriptions.")
    total_expired: int = Field(..., description="Total number of expired subscriptions.")
    total_cancelled: int = Field(..., description="Total number of cancelled subscriptions.")
    monthly_revenue: float = Field(..., description="Estimated total monthly recurring revenue.")
    yearly_revenue: float = Field(..., description="Estimated total yearly recurring revenue.")
    by_plan: Dict[str, int] = Field(..., description="Breakdown of subscriptions by plan.")
    period_start: datetime = Field(..., description="The start date of the statistics period.")
    period_end: datetime = Field(..., description="The end date of the statistics period.")


class SubscriptionWithPlan(SubscriptionResponse):
    """Schema for Subscription with detailed plan information."""
    model_config = ConfigDict(from_attributes=True)

    plan_details: Dict[str, Any] = Field(..., description="Detailed information about the subscribed plan.")

"""
Schemas for BillingEvent - a model for tracking billing events.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class BillingEventType(str, Enum):
    """Enum for the type of billing event."""
    USAGE = "usage"
    SUBSCRIPTION = "subscription"
    CREDIT = "credit"
    REFUND = "refund"

class BillingEventStatus(str, Enum):
    """Enum for the status of a billing event."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class BillingEventBase(BaseModel):
    """Base schema for BillingEvent attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    event_type: BillingEventType = Field(..., description="The type of the billing event.")
    amount_usd: float = Field(..., description="The amount of the event in USD.")
    description: Optional[str] = Field(None, description="A detailed description of the event.")
    invoice_id: Optional[str] = Field(None, description="The ID of the associated invoice.")
    payment_provider: Optional[str] = Field(None, description="The payment provider used (e.g., 'stripe', 'paypal').")
    payment_transaction_id: Optional[str] = Field(None, description="The ID of the payment transaction.")
    billing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the event.")
    status: BillingEventStatus = Field(BillingEventStatus.PENDING, description="The current status of the event.")

class BillingEventCreate(BillingEventBase):
    """Schema for creating a new billing event."""
    user_id: UUID = Field(..., description="The user associated with the event.")
    tenant_id: UUID = Field(..., description="The tenant to which this event belongs.")
    workspace_id: Optional[UUID] = Field(None, description="The workspace associated with the event.")
    related_usage_log_id: Optional[UUID] = Field(None, description="The usage log associated with the event.")
    related_message_id: Optional[UUID] = Field(None, description="The message associated with the event.")

class BillingEventUpdate(BaseModel):
    """Schema for updating an existing billing event. All fields are optional."""
    status: Optional[BillingEventStatus] = Field(None, description="New status for the event.")
    invoice_id: Optional[str] = Field(None, description="New invoice ID.")
    payment_transaction_id: Optional[str] = Field(None, description="New payment transaction ID.")
    billing_metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata.")

class BillingEventResponse(BillingEventBase):
    """Response schema for a billing event, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the event.")
    user_id: UUID = Field(..., description="The user associated with the event.")
    tenant_id: UUID = Field(..., description="The tenant to which this event belongs.")
    workspace_id: Optional[UUID] = Field(None, description="The workspace associated with the event.")
    related_usage_log_id: Optional[UUID] = Field(None, description="The usage log associated with the event.")
    related_message_id: Optional[UUID] = Field(None, description="The message associated with the event.")
    processed_at: Optional[datetime] = Field(None, description="Timestamp of when the event was processed.")
    created_at: datetime = Field(..., description="Timestamp of when the event was created.")

class BillingEventListResponse(BaseModel):
    """Paginated list of billing events."""
    items: List[BillingEventResponse] = Field(..., description="List of billing events for the current page.")
    total: int = Field(..., description="Total number of billing events.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

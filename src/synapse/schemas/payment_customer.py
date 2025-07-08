"""
Schemas for PaymentCustomer - managing payment customers.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, validator, computed_field
from uuid import UUID


class PaymentCustomerBase(BaseModel):
    """Base schema for PaymentCustomer attributes."""
    model_config = ConfigDict(from_attributes=True)
    
    tenant_id: UUID = Field(..., description="Tenant ID")
    provider_id: UUID = Field(..., description="Payment provider ID")
    external_customer_id: str = Field(..., min_length=1, max_length=255, description="External customer ID from payment provider")
    customer_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Customer data from payment provider")
    is_active: bool = Field(default=True, description="Whether the customer is active")
    user_id: Optional[UUID] = Field(None, description="Optional link to specific user")
    
    @validator('customer_data')
    def validate_customer_data(cls, v):
        """Validate customer data is a dictionary."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('customer_data must be a dictionary')
        return v


class PaymentCustomerCreate(PaymentCustomerBase):
    """Schema for creating a new payment customer."""
    pass


class PaymentCustomerUpdate(BaseModel):
    """Schema for updating a payment customer."""
    model_config = ConfigDict(from_attributes=True)
    
    external_customer_id: Optional[str] = Field(None, min_length=1, max_length=255, description="External customer ID from payment provider")
    customer_data: Optional[Dict[str, Any]] = Field(None, description="Customer data from payment provider")
    is_active: Optional[bool] = Field(None, description="Whether the customer is active")
    user_id: Optional[UUID] = Field(None, description="Optional link to specific user")
    
    @validator('customer_data')
    def validate_customer_data(cls, v):
        """Validate customer data is a dictionary."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('customer_data must be a dictionary')
        return v


class PaymentCustomerRead(PaymentCustomerBase):
    """Schema for reading a payment customer."""
    id: UUID = Field(..., description="Unique identifier for the customer")
    created_at: datetime = Field(..., description="Timestamp when the customer was created")
    updated_at: datetime = Field(..., description="Timestamp when the customer was last updated")
    
    # Computed fields
    @computed_field
    @property
    def customer_email(self) -> Optional[str]:
        """Get customer email from customer data."""
        if self.customer_data:
            return self.customer_data.get("email")
        return None
    
    @computed_field
    @property
    def customer_name(self) -> Optional[str]:
        """Get customer name from customer data."""
        if self.customer_data:
            return self.customer_data.get("name") or self.customer_data.get("full_name")
        return None
    
    @computed_field
    @property
    def customer_phone(self) -> Optional[str]:
        """Get customer phone from customer data."""
        if self.customer_data:
            return self.customer_data.get("phone")
        return None


class PaymentCustomerResponse(PaymentCustomerRead):
    """Response schema for payment customer."""
    pass


class PaymentCustomerListResponse(BaseModel):
    """Paginated list of payment customers."""
    items: list[PaymentCustomerResponse] = Field(..., description="List of payment customers")
    total: int = Field(..., description="Total number of customers")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")


class PaymentCustomerCreateSimple(BaseModel):
    """Simple schema for creating a payment customer."""
    tenant_id: UUID = Field(..., description="Tenant ID")
    provider_id: UUID = Field(..., description="Payment provider ID")
    external_customer_id: str = Field(..., min_length=1, max_length=255, description="External customer ID from payment provider")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    user_id: Optional[UUID] = Field(None, description="Optional link to specific user")


class PaymentCustomerSearch(BaseModel):
    """Schema for searching payment customers."""
    external_customer_id: Optional[str] = Field(None, description="External customer ID to search for")
    provider_id: Optional[UUID] = Field(None, description="Payment provider ID to filter by")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID to filter by")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    customer_email: Optional[str] = Field(None, description="Customer email to search for")


class PaymentCustomerSummary(BaseModel):
    """Summary schema for payment customer."""
    id: UUID = Field(..., description="Customer ID")
    external_customer_id: str = Field(..., description="External customer ID")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    is_active: bool = Field(..., description="Whether the customer is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    payment_methods_count: int = Field(default=0, description="Number of payment methods")
    total_spent: float = Field(default=0.0, description="Total amount spent")
    subscription_count: int = Field(default=0, description="Number of active subscriptions")


class PaymentCustomerActivateDeactivate(BaseModel):
    """Schema for activating or deactivating a payment customer."""
    is_active: bool = Field(..., description="Whether to activate or deactivate the customer")
    reason: Optional[str] = Field(None, description="Reason for the status change")


class PaymentCustomerUpdateData(BaseModel):
    """Schema for updating customer data."""
    customer_data: Dict[str, Any] = Field(..., description="New customer data to merge with existing data")
    replace: bool = Field(default=False, description="Whether to replace all data or merge with existing")
    
    @validator('customer_data')
    def validate_customer_data(cls, v):
        """Validate customer data is a dictionary."""
        if not isinstance(v, dict):
            raise ValueError('customer_data must be a dictionary')
        return v

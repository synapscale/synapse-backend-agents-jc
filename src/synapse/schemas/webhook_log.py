from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class WebhookStatus(str, Enum):
    """Enum for webhook status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class WebhookEventType(str, Enum):
    """Enum for webhook event types"""
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    INVOICE_CREATED = "invoice.created"
    INVOICE_PAID = "invoice.paid"
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    REFUND_CREATED = "refund.created"
    DISPUTE_CREATED = "dispute.created"
    OTHER = "other"


class WebhookLogBase(BaseModel):
    """Base schema for WebhookLog"""
    provider_id: UUID = Field(..., description="Provider ID")
    event_type: str = Field(..., description="Event type")
    event_id: Optional[str] = Field(None, description="External event ID")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Request headers")
    status: WebhookStatus = Field(default=WebhookStatus.PENDING, description="Processing status")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class WebhookLogCreate(WebhookLogBase):
    """Schema for creating a new webhook log"""
    pass


class WebhookLogUpdate(BaseModel):
    """Schema for updating an existing webhook log"""
    status: Optional[WebhookStatus] = Field(None, description="Processing status")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: Optional[int] = Field(None, description="Number of retry attempts")


class WebhookLogInDB(WebhookLogBase):
    """Schema for webhook log in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Webhook log ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class WebhookLogResponse(WebhookLogInDB):
    """Schema for webhook log response"""
    pass


class WebhookLogListResponse(BaseModel):
    """Schema for webhook log list response"""
    model_config = ConfigDict(from_attributes=True)
    
    webhook_logs: list[WebhookLogResponse] = Field(..., description="List of webhook logs")
    total: int = Field(..., description="Total number of webhook logs")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of webhook logs per page")
    pages: int = Field(..., description="Total number of pages")


class WebhookLogStatistics(BaseModel):
    """Schema for webhook log statistics"""
    total_webhooks: int = Field(..., description="Total number of webhooks")
    success_count: int = Field(..., description="Number of successful webhooks")
    failed_count: int = Field(..., description="Number of failed webhooks")
    pending_count: int = Field(..., description="Number of pending webhooks")
    success_rate: float = Field(..., description="Success rate percentage")
    average_processing_time: float = Field(..., description="Average processing time in seconds")
    event_type_distribution: Dict[str, int] = Field(..., description="Distribution by event type")
    provider_statistics: Dict[str, Dict[str, int]] = Field(..., description="Statistics by provider")


class WebhookLogRetry(BaseModel):
    """Schema for webhook retry request"""
    webhook_id: UUID = Field(..., description="Webhook log ID")
    force_retry: bool = Field(default=False, description="Force retry even if max retries reached")
    delay_seconds: Optional[int] = Field(None, description="Delay before retry in seconds")


class WebhookLogBatch(BaseModel):
    """Schema for batch webhook operations"""
    webhook_ids: list[UUID] = Field(..., description="List of webhook log IDs")
    action: str = Field(..., description="Batch action (retry, cancel, archive)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class WebhookLogFilter(BaseModel):
    """Schema for webhook log filtering"""
    provider_id: Optional[UUID] = Field(None, description="Filter by provider ID")
    event_type: Optional[str] = Field(None, description="Filter by event type")
    status: Optional[WebhookStatus] = Field(None, description="Filter by status")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    retry_count_min: Optional[int] = Field(None, description="Minimum retry count")
    retry_count_max: Optional[int] = Field(None, description="Maximum retry count")


class WebhookLogExport(BaseModel):
    """Schema for webhook log export request"""
    filters: Optional[WebhookLogFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_payload: bool = Field(default=False, description="Include payload in export")
    include_headers: bool = Field(default=False, description="Include headers in export")
    max_records: Optional[int] = Field(None, description="Maximum number of records to export")


class WebhookLogSummary(BaseModel):
    """Schema for webhook log summary"""
    provider_id: UUID = Field(..., description="Provider ID")
    total_webhooks: int = Field(..., description="Total webhooks for this provider")
    recent_success_count: int = Field(..., description="Recent successful webhooks")
    recent_failure_count: int = Field(..., description="Recent failed webhooks")
    last_webhook_at: Optional[datetime] = Field(None, description="Last webhook timestamp")
    health_score: float = Field(..., description="Health score (0-100)")
    common_errors: list[str] = Field(..., description="Most common error messages")

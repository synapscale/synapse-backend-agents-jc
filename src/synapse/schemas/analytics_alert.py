"""
Schemas for AnalyticsAlert - a model for managing analytics alerts and notifications.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class AnalyticsAlertBase(BaseModel):
    """Base schema for AnalyticsAlert attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=255, description="The name of the alert.")
    description: Optional[str] = Field(None, description="A detailed description of the alert.")
    condition: Dict[str, Any] = Field(..., description="The condition that triggers the alert.")
    notification_config: Dict[str, Any] = Field(..., description="The configuration for sending notifications.")
    is_active: bool = Field(True, description="Whether the alert is active.")

class AnalyticsAlertCreate(AnalyticsAlertBase):
    """Schema for creating a new analytics alert."""
    owner_id: UUID = Field(..., description="The user who owns the alert.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this alert belongs.")

class AnalyticsAlertUpdate(BaseModel):
    """Schema for updating an existing analytics alert. All fields are optional."""
    name: Optional[str] = Field(None, max_length=255, description="New name for the alert.")
    description: Optional[str] = Field(None, description="New description.")
    condition: Optional[Dict[str, Any]] = Field(None, description="New condition.")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="New notification configuration.")
    is_active: Optional[bool] = Field(None, description="New active status.")

class AnalyticsAlertResponse(AnalyticsAlertBase):
    """Response schema for an analytics alert, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the alert.")
    owner_id: UUID = Field(..., description="The user who owns the alert.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this alert belongs.")
    last_triggered_at: Optional[datetime] = Field(None, description="Timestamp of when the alert was last triggered.")
    created_at: datetime = Field(..., description="Timestamp of when the alert was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")

class AnalyticsAlertListResponse(BaseModel):
    """Paginated list of analytics alerts."""
    items: List[AnalyticsAlertResponse] = Field(..., description="List of analytics alerts for the current page.")
    total: int = Field(..., description="Total number of analytics alerts.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

class TestAlertRequest(BaseModel):
    """Schema for testing an analytics alert."""
    alert_id: UUID = Field(..., description="The ID of the alert to test.")
    metrics: Dict[str, Any] = Field(..., description="A dictionary of metrics to test the alert against.")

class TestAlertResponse(BaseModel):
    """Response schema for the test alert operation."""
    triggered: bool = Field(..., description="Whether the alert was triggered.")
    message: str = Field(..., description="A message detailing the result of the test.")

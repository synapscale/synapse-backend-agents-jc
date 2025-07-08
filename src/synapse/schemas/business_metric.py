"""
Schemas for BusinessMetric - a model for tracking business metrics and KPIs.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class PeriodType(str, Enum):
    """Enum for the type of period."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BusinessMetricBase(BaseModel):
    """Base schema for BusinessMetric attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    period_type: PeriodType = Field(..., description="The type of the period.")
    total_users: int = Field(..., description="Total number of users.")
    new_users: int = Field(..., description="Number of new users.")
    active_users: int = Field(..., description="Number of active users.")
    churned_users: int = Field(..., description="Number of churned users.")
    total_sessions: int = Field(..., description="Total number of sessions.")
    avg_session_duration: float = Field(..., description="Average session duration in seconds.")
    total_page_views: int = Field(..., description="Total number of page views.")
    bounce_rate: float = Field(..., description="Bounce rate as a percentage.")
    workflows_created: int = Field(..., description="Number of new workflows created.")
    workflows_executed: int = Field(..., description="Number of workflows executed.")
    components_published: int = Field(..., description="Number of new components published.")
    components_downloaded: int = Field(..., description="Number of components downloaded.")
    workspaces_created: int = Field(..., description="Number of new workspaces created.")
    teams_formed: int = Field(..., description="Number of new teams formed.")
    collaborative_sessions: int = Field(..., description="Number of collaborative sessions.")
    total_revenue: float = Field(..., description="Total revenue in USD.")
    recurring_revenue: float = Field(..., description="Recurring revenue in USD.")
    marketplace_revenue: float = Field(..., description="Marketplace revenue in USD.")
    avg_revenue_per_user: float = Field(..., description="Average revenue per user in USD.")
    error_rate: float = Field(..., description="Error rate as a percentage.")
    avg_response_time: float = Field(..., description="Average response time in milliseconds.")
    uptime_percentage: float = Field(..., description="Uptime as a percentage.")
    customer_satisfaction: float = Field(..., description="Customer satisfaction score.")

class BusinessMetricCreate(BusinessMetricBase):
    """Schema for creating a new business metric."""
    date: datetime = Field(..., description="The date of the metric.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this metric belongs.")

class BusinessMetricResponse(BusinessMetricBase):
    """Response schema for a business metric, including database-generated fields."""
    id: int = Field(..., description="Unique identifier for the metric.")
    date: datetime = Field(..., description="The date of the metric.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this metric belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the metric was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")

class BusinessMetricListResponse(BaseModel):
    """Paginated list of business metrics."""
    items: List[BusinessMetricResponse] = Field(..., description="List of business metrics for the current page.")
    total: int = Field(..., description="Total number of business metrics.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class PeriodType(str, Enum):
    """Enum for period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ActivityLevel(str, Enum):
    """Enum for activity levels"""
    HIGHLY_ACTIVE = "highly_active"
    ACTIVE = "active"
    MODERATELY_ACTIVE = "moderately_active"
    LOW_ACTIVITY = "low_activity"
    INACTIVE = "inactive"


class UserType(str, Enum):
    """Enum for user types"""
    CREATOR = "creator"
    CONSUMER = "consumer"
    COLLABORATOR = "collaborator"
    BUILDER = "builder"
    VIEWER = "viewer"


class UserBehaviorMetricBase(BaseModel):
    """Base schema for UserBehaviorMetric"""
    user_id: UUID = Field(..., description="User ID")
    date: datetime = Field(..., description="Date of the metric")
    period_type: PeriodType = Field(..., description="Period type (daily, weekly, monthly)")
    session_count: int = Field(..., description="Number of sessions")
    total_session_duration: int = Field(..., description="Total session duration in seconds")
    avg_session_duration: float = Field(..., description="Average session duration in seconds")
    page_views: int = Field(..., description="Number of page views")
    unique_pages_visited: int = Field(..., description="Number of unique pages visited")
    workflows_created: int = Field(..., description="Number of workflows created")
    workflows_executed: int = Field(..., description="Number of workflows executed")
    components_used: int = Field(..., description="Number of components used")
    collaborations_initiated: int = Field(..., description="Number of collaborations initiated")
    marketplace_purchases: int = Field(..., description="Number of marketplace purchases")
    revenue_generated: float = Field(..., description="Revenue generated")
    components_published: int = Field(..., description="Number of components published")
    error_count: int = Field(..., description="Number of errors")
    support_tickets: int = Field(..., description="Number of support tickets")
    feature_requests: int = Field(..., description="Number of feature requests")
    engagement_score: float = Field(..., description="Engagement score (0-100)")
    satisfaction_score: float = Field(..., description="Satisfaction score (0-100)")
    value_score: float = Field(..., description="Value score (0-100)")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class UserBehaviorMetricCreate(UserBehaviorMetricBase):
    """Schema for creating a new user behavior metric"""
    pass


class UserBehaviorMetricUpdate(BaseModel):
    """Schema for updating an existing user behavior metric"""
    session_count: Optional[int] = Field(None, description="Number of sessions")
    total_session_duration: Optional[int] = Field(None, description="Total session duration in seconds")
    avg_session_duration: Optional[float] = Field(None, description="Average session duration in seconds")
    page_views: Optional[int] = Field(None, description="Number of page views")
    unique_pages_visited: Optional[int] = Field(None, description="Number of unique pages visited")
    workflows_created: Optional[int] = Field(None, description="Number of workflows created")
    workflows_executed: Optional[int] = Field(None, description="Number of workflows executed")
    components_used: Optional[int] = Field(None, description="Number of components used")
    collaborations_initiated: Optional[int] = Field(None, description="Number of collaborations initiated")
    marketplace_purchases: Optional[int] = Field(None, description="Number of marketplace purchases")
    revenue_generated: Optional[float] = Field(None, description="Revenue generated")
    components_published: Optional[int] = Field(None, description="Number of components published")
    error_count: Optional[int] = Field(None, description="Number of errors")
    support_tickets: Optional[int] = Field(None, description="Number of support tickets")
    feature_requests: Optional[int] = Field(None, description="Number of feature requests")
    engagement_score: Optional[float] = Field(None, description="Engagement score (0-100)")
    satisfaction_score: Optional[float] = Field(None, description="Satisfaction score (0-100)")
    value_score: Optional[float] = Field(None, description="Value score (0-100)")


class UserBehaviorMetricInDB(UserBehaviorMetricBase):
    """Schema for user behavior metric in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Metric ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserBehaviorMetricResponse(UserBehaviorMetricInDB):
    """Schema for user behavior metric response"""
    formatted_session_duration: str = Field(..., description="Formatted session duration")
    activity_level: ActivityLevel = Field(..., description="Activity level")
    user_type: UserType = Field(..., description="User type")
    productivity_score: float = Field(..., description="Productivity score")
    health_indicators: Dict[str, Any] = Field(..., description="Health indicators")


class UserBehaviorMetricListResponse(BaseModel):
    """Schema for user behavior metric list response"""
    model_config = ConfigDict(from_attributes=True)
    
    metrics: list[UserBehaviorMetricResponse] = Field(..., description="List of metrics")
    total: int = Field(..., description="Total number of metrics")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of metrics per page")
    pages: int = Field(..., description="Total number of pages")


class UserSegmentResponse(BaseModel):
    """Schema for user segment response"""
    highly_active: int = Field(..., description="Number of highly active users")
    active: int = Field(..., description="Number of active users")
    moderately_active: int = Field(..., description="Number of moderately active users")
    low_activity: int = Field(..., description="Number of low activity users")
    inactive: int = Field(..., description="Number of inactive users")


class ChurnRiskResponse(BaseModel):
    """Schema for churn risk response"""
    risk_level: str = Field(..., description="Risk level (critical, high, medium, low, minimal)")
    score: float = Field(..., description="Risk score (0-100)")
    factors: Dict[str, float] = Field(..., description="Risk factors")


class CohortAnalysisResponse(BaseModel):
    """Schema for cohort analysis response"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    avg_engagement: float = Field(..., description="Average engagement score")


class EngagementTrendResponse(BaseModel):
    """Schema for engagement trend response"""
    date: datetime = Field(..., description="Date")
    engagement_score: float = Field(..., description="Engagement score")


class UserBehaviorSummary(BaseModel):
    """Schema for user behavior summary"""
    user_id: UUID = Field(..., description="User ID")
    period_type: PeriodType = Field(..., description="Period type")
    total_sessions: int = Field(..., description="Total sessions")
    avg_engagement: float = Field(..., description="Average engagement")
    total_workflows: int = Field(..., description="Total workflows created")
    activity_level: ActivityLevel = Field(..., description="Activity level")
    user_type: UserType = Field(..., description="User type")
    churn_risk: ChurnRiskResponse = Field(..., description="Churn risk assessment")

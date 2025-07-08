from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class InsightType(str, Enum):
    """Enum for insight types"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    PREDICTION = "prediction"
    TREND = "trend"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    ENGAGEMENT = "engagement"
    PRODUCTIVITY = "productivity"


class InsightCategory(str, Enum):
    """Enum for insight categories"""
    WORKFLOWS = "workflows"
    AGENTS = "agents"
    COLLABORATION = "collaboration"
    PERFORMANCE = "performance"
    COST = "cost"
    SECURITY = "security"
    USAGE = "usage"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    GROWTH = "growth"


class InsightPriority(str, Enum):
    """Enum for insight priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserFeedback(str, Enum):
    """Enum for user feedback"""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    IRRELEVANT = "irrelevant"
    NEEDS_MORE_INFO = "needs_more_info"


class UserInsightBase(BaseModel):
    """Base schema for UserInsight"""
    user_id: UUID = Field(..., description="User ID")
    insight_type: InsightType = Field(..., description="Type of insight")
    category: InsightCategory = Field(..., description="Category of insight")
    priority: InsightPriority = Field(..., description="Priority level")
    title: str = Field(..., max_length=200, description="Insight title")
    description: str = Field(..., description="Detailed description")
    recommendation: Optional[str] = Field(None, description="Recommended action")
    supporting_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Supporting data")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")
    suggested_action: Optional[str] = Field(None, max_length=100, description="Suggested action")
    action_url: Optional[str] = Field(None, max_length=500, description="Action URL")
    action_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action data")
    is_read: bool = Field(default=False, description="Whether insight has been read")
    is_dismissed: bool = Field(default=False, description="Whether insight has been dismissed")
    is_acted_upon: bool = Field(default=False, description="Whether action has been taken")
    is_evergreen: bool = Field(default=False, description="Whether insight is evergreen")
    user_feedback: Optional[UserFeedback] = Field(None, description="User feedback")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class UserInsightCreate(UserInsightBase):
    """Schema for creating a new user insight"""
    pass


class UserInsightUpdate(BaseModel):
    """Schema for updating an existing user insight"""
    title: Optional[str] = Field(None, max_length=200, description="Insight title")
    description: Optional[str] = Field(None, description="Detailed description")
    recommendation: Optional[str] = Field(None, description="Recommended action")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (0-1)")
    suggested_action: Optional[str] = Field(None, max_length=100, description="Suggested action")
    action_url: Optional[str] = Field(None, max_length=500, description="Action URL")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action data")
    is_read: Optional[bool] = Field(None, description="Whether insight has been read")
    is_dismissed: Optional[bool] = Field(None, description="Whether insight has been dismissed")
    is_acted_upon: Optional[bool] = Field(None, description="Whether action has been taken")
    is_evergreen: Optional[bool] = Field(None, description="Whether insight is evergreen")
    user_feedback: Optional[UserFeedback] = Field(None, description="User feedback")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class UserInsightInDB(UserInsightBase):
    """Schema for user insight in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Insight ID")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    acted_at: Optional[datetime] = Field(None, description="Action timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserInsightResponse(UserInsightInDB):
    """Schema for user insight response"""
    pass


class UserInsightListResponse(BaseModel):
    """Schema for user insight list response"""
    model_config = ConfigDict(from_attributes=True)
    
    insights: list[UserInsightResponse] = Field(..., description="List of user insights")
    total: int = Field(..., description="Total number of insights")
    unread_count: int = Field(..., description="Number of unread insights")
    high_priority_count: int = Field(..., description="Number of high priority insights")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of insights per page")
    pages: int = Field(..., description="Total number of pages")


class UserInsightAction(BaseModel):
    """Schema for insight action request"""
    insight_id: UUID = Field(..., description="Insight ID")
    action_type: str = Field(..., description="Action type")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action data")
    feedback: Optional[UserFeedback] = Field(None, description="User feedback")


class UserInsightActionResponse(BaseModel):
    """Schema for insight action response"""
    success: bool = Field(..., description="Action success")
    message: str = Field(..., description="Response message")
    result: Optional[Dict[str, Any]] = Field(None, description="Action result")


class UserInsightBatch(BaseModel):
    """Schema for batch insight operations"""
    insight_ids: list[UUID] = Field(..., description="List of insight IDs")
    action: str = Field(..., description="Batch action (mark_read, dismiss, etc.)")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action data")


class UserInsightStatistics(BaseModel):
    """Schema for user insight statistics"""
    user_id: UUID = Field(..., description="User ID")
    total_insights: int = Field(..., description="Total insights")
    unread_insights: int = Field(..., description="Unread insights")
    high_priority_insights: int = Field(..., description="High priority insights")
    dismissed_insights: int = Field(..., description="Dismissed insights")
    acted_upon_insights: int = Field(..., description="Acted upon insights")
    insights_by_category: Dict[str, int] = Field(..., description="Insights by category")
    insights_by_type: Dict[str, int] = Field(..., description="Insights by type")
    average_confidence_score: float = Field(..., description="Average confidence score")
    recent_insights: list[UserInsightResponse] = Field(..., description="Recent insights")


class UserInsightFilter(BaseModel):
    """Schema for insight filtering"""
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    insight_type: Optional[InsightType] = Field(None, description="Filter by type")
    category: Optional[InsightCategory] = Field(None, description="Filter by category")
    priority: Optional[InsightPriority] = Field(None, description="Filter by priority")
    is_read: Optional[bool] = Field(None, description="Filter by read status")
    is_dismissed: Optional[bool] = Field(None, description="Filter by dismissed status")
    is_acted_upon: Optional[bool] = Field(None, description="Filter by action status")
    is_evergreen: Optional[bool] = Field(None, description="Filter by evergreen status")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    confidence_threshold: Optional[float] = Field(None, ge=0, le=1, description="Minimum confidence score")


class UserInsightExport(BaseModel):
    """Schema for insight export"""
    filters: Optional[UserInsightFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_supporting_data: bool = Field(default=False, description="Include supporting data")
    include_action_data: bool = Field(default=False, description="Include action data")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for export")

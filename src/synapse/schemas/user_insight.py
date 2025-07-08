"""
Schemas for UserInsight - a model for AI-generated insights and recommendations for users.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class InsightType(str, Enum):
    """Enum for the type of insight."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    SECURITY = "security"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"


class InsightCategory(str, Enum):
    """Enum for the category of insight."""
    WORKFLOW = "workflow"
    AGENT = "agent"
    ACCOUNT = "account"
    BILLING = "billing"
    GENERAL = "general"


class InsightPriority(str, Enum):
    """Enum for the priority of an insight."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserInsightBase(BaseModel):
    """Base schema for UserInsight attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    insight_type: InsightType = Field(..., description="The type of the insight.")
    category: InsightCategory = Field(..., description="The category of the insight.")
    priority: InsightPriority = Field(..., description="The priority level of the insight.")
    title: str = Field(..., max_length=200, description="A concise title for the insight.")
    description: str = Field(..., description="A detailed description of the insight.")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation based on the insight.")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="Additional data supporting the insight.")
    confidence_score: float = Field(..., ge=0, le=1, description="The confidence score of the insight (0-1).")
    suggested_action: Optional[str] = Field(None, max_length=100, description="A short suggested action for the user.")
    action_url: Optional[str] = Field(None, max_length=500, description="A URL related to the suggested action.")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the suggested action.")
    is_read: bool = Field(False, description="Indicates if the user has read the insight.")
    is_dismissed: bool = Field(False, description="Indicates if the user has dismissed the insight.")
    is_acted_upon: bool = Field(False, description="Indicates if the user has acted upon the insight.")
    user_feedback: Optional[str] = Field(None, max_length=20, description="User feedback on the insight (e.g., 'helpful', 'not_helpful').")
    expires_at: Optional[datetime] = Field(None, description="The date and time when the insight expires.")
    is_evergreen: bool = Field(False, description="Indicates if the insight is evergreen (does not expire).")


class UserInsightCreate(UserInsightBase):
    """Schema for creating a new UserInsight."""
    user_id: UUID = Field(..., description="The ID of the user to whom the insight belongs.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this insight belongs.")


class UserInsightUpdate(BaseModel):
    """Schema for updating an existing UserInsight. All fields are optional."""
    priority: Optional[InsightPriority] = Field(None, description="New priority level.")
    title: Optional[str] = Field(None, max_length=200, description="New title.")
    description: Optional[str] = Field(None, description="New description.")
    recommendation: Optional[str] = Field(None, description="New recommendation.")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="New supporting data.")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="New confidence score.")
    suggested_action: Optional[str] = Field(None, max_length=100, description="New suggested action.")
    action_url: Optional[str] = Field(None, max_length=500, description="New action URL.")
    action_data: Optional[Dict[str, Any]] = Field(None, description="New action data.")
    is_read: Optional[bool] = Field(None, description="New read status.")
    is_dismissed: Optional[bool] = Field(None, description="New dismissed status.")
    is_acted_upon: Optional[bool] = Field(None, description="New acted upon status.")
    user_feedback: Optional[str] = Field(None, max_length=20, description="New user feedback.")
    expires_at: Optional[datetime] = Field(None, description="New expiration date.")
    is_evergreen: Optional[bool] = Field(None, description="New evergreen status.")


class UserInsightResponse(UserInsightBase):
    """Response schema for a UserInsight, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the insight.")
    user_id: UUID = Field(..., description="The ID of the user to whom the insight belongs.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this insight belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the insight was created.")
    read_at: Optional[datetime] = Field(None, description="Timestamp of when the insight was read.")
    acted_at: Optional[datetime] = Field(None, description="Timestamp of when the insight was acted upon.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")


class UserInsightListResponse(BaseModel):
    """Paginated list of UserInsights."""
    items: List[UserInsightResponse] = Field(..., description="List of user insights for the current page.")
    total: int = Field(..., description="Total number of user insights.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

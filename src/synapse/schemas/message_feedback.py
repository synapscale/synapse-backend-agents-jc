from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class RatingType(str, Enum):
    """Enum for rating types"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    STAR_RATING = "star_rating"


class FeedbackCategory(str, Enum):
    """Enum for feedback categories"""
    ACCURACY = "accuracy"
    HELPFULNESS = "helpfulness"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    SPEED = "speed"
    OTHER = "other"


class MessageFeedbackBase(BaseModel):
    """Base schema for MessageFeedback"""
    message_id: UUID = Field(..., description="Message ID")
    user_id: UUID = Field(..., description="User ID")
    rating_type: RatingType = Field(..., description="Type of rating")
    rating_value: Optional[int] = Field(None, ge=1, le=5, description="Rating value (1-5 for star ratings)")
    feedback_text: Optional[str] = Field(None, description="Feedback text")
    feedback_category: Optional[FeedbackCategory] = Field(None, description="Category of feedback")
    improvement_suggestions: Optional[str] = Field(None, description="Improvement suggestions")
    is_public: bool = Field(default=False, description="Whether feedback is public")
    feedback_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class MessageFeedbackCreate(MessageFeedbackBase):
    """Schema for creating a new message feedback"""
    pass


class MessageFeedbackUpdate(BaseModel):
    """Schema for updating an existing message feedback"""
    rating_type: Optional[RatingType] = Field(None, description="Type of rating")
    rating_value: Optional[int] = Field(None, ge=1, le=5, description="Rating value (1-5 for star ratings)")
    feedback_text: Optional[str] = Field(None, description="Feedback text")
    feedback_category: Optional[FeedbackCategory] = Field(None, description="Category of feedback")
    improvement_suggestions: Optional[str] = Field(None, description="Improvement suggestions")
    is_public: Optional[bool] = Field(None, description="Whether feedback is public")
    feedback_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MessageFeedbackInDB(MessageFeedbackBase):
    """Schema for message feedback in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Feedback ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MessageFeedbackResponse(MessageFeedbackInDB):
    """Schema for message feedback response"""
    pass


class MessageFeedbackListResponse(BaseModel):
    """Schema for message feedback list response"""
    model_config = ConfigDict(from_attributes=True)
    
    feedback: list[MessageFeedbackResponse] = Field(..., description="List of message feedback")
    total: int = Field(..., description="Total number of feedback entries")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of feedback entries per page")
    pages: int = Field(..., description="Total number of pages")


class MessageFeedbackStatistics(BaseModel):
    """Schema for message feedback statistics"""
    total_feedback: int = Field(..., description="Total number of feedback entries")
    rating_distribution: Dict[str, int] = Field(..., description="Distribution of ratings")
    average_rating: float = Field(..., description="Average rating")
    category_distribution: Dict[str, int] = Field(..., description="Distribution by category")
    recent_feedback: list[MessageFeedbackResponse] = Field(..., description="Recent feedback entries")
    positive_feedback_ratio: float = Field(..., description="Ratio of positive feedback")


class MessageFeedbackSummary(BaseModel):
    """Schema for message feedback summary"""
    message_id: UUID = Field(..., description="Message ID")
    total_feedback: int = Field(..., description="Total feedback count")
    average_rating: Optional[float] = Field(None, description="Average rating")
    thumbs_up_count: int = Field(..., description="Number of thumbs up")
    thumbs_down_count: int = Field(..., description="Number of thumbs down")
    star_ratings: Dict[str, int] = Field(..., description="Distribution of star ratings")
    top_categories: list[str] = Field(..., description="Top feedback categories")
    has_improvement_suggestions: bool = Field(..., description="Whether there are improvement suggestions")


class MessageFeedbackBatch(BaseModel):
    """Schema for batch feedback operations"""
    message_ids: list[UUID] = Field(..., description="List of message IDs")
    action: str = Field(..., description="Batch action (export, archive, etc.)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class MessageFeedbackExport(BaseModel):
    """Schema for feedback export request"""
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for export")
    categories: Optional[list[FeedbackCategory]] = Field(None, description="Categories to include")
    rating_types: Optional[list[RatingType]] = Field(None, description="Rating types to include")
    format: str = Field(default="csv", description="Export format")
    include_metadata: bool = Field(default=False, description="Include metadata in export")

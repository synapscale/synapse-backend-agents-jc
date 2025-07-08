"""
Schemas para NodeRating
"""

from datetime import datetime, date
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, UUID4, validator

class NodeRatingBase(BaseModel):
    """Base schema for NodeRating"""
    node_id: UUID4
    user_id: UUID4
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    tenant_id: Optional[UUID4] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
    
    class Config:
        from_attributes = True

class NodeRatingCreate(NodeRatingBase):
    """Schema for creating NodeRating"""
    pass

class NodeRatingRead(NodeRatingBase):
    """Schema for reading NodeRating"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    rating_display: Optional[str] = None
    is_positive: Optional[bool] = None
    is_negative: Optional[bool] = None
    is_neutral: Optional[bool] = None
    
    class Config:
        from_attributes = True

class NodeRatingUpdate(BaseModel):
    """Schema for updating NodeRating"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
    
    class Config:
        from_attributes = True

class NodeRatingSummary(BaseModel):
    """Schema for node rating summary"""
    total_ratings: int
    average_rating: float
    rating_distribution: Dict[int, int]
    positive_percentage: float
    negative_percentage: float
    
    class Config:
        from_attributes = True

class NodeRatingTrend(BaseModel):
    """Schema for rating trends"""
    date: date
    average_rating: float
    rating_count: int
    
    class Config:
        from_attributes = True

class NodeRatingStats(BaseModel):
    """Schema for overall rating statistics"""
    total_ratings: int
    average_rating: float
    unique_nodes_rated: int
    unique_users_rating: int
    rating_distribution: Dict[int, Dict[str, float]]
    
    class Config:
        from_attributes = True

class TopRatedNode(BaseModel):
    """Schema for top rated nodes"""
    node_id: UUID4
    avg_rating: float
    rating_count: int
    
    class Config:
        from_attributes = True

class ActiveRater(BaseModel):
    """Schema for most active raters"""
    user_id: UUID4
    rating_count: int
    avg_rating_given: float
    
    class Config:
        from_attributes = True

class NodeRatingRequest(BaseModel):
    """Schema for rating request"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
    
    class Config:
        from_attributes = True

class NodeRatingResponse(BaseModel):
    """Schema for rating response"""
    success: bool
    message: str
    rating: Optional[NodeRatingRead] = None
    
    class Config:
        from_attributes = True

class NodeRatingList(BaseModel):
    """Schema for paginated rating list"""
    ratings: List[NodeRatingRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

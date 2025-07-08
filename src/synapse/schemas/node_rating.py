"""
Schemas for NodeRating - a model for user ratings of workflow nodes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, computed_field
from uuid import UUID
from enum import Enum


class RatingValue(int, Enum):
    """Enum for possible rating values (1-5 stars)."""
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class NodeRatingBase(BaseModel):
    """Base schema for NodeRating attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    node_id: UUID = Field(..., description="The ID of the node being rated.")
    user_id: UUID = Field(..., description="The ID of the user who provided the rating.")
    rating: RatingValue = Field(..., description="The rating value (1-5 stars).")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this rating belongs.")


class NodeRatingCreate(NodeRatingBase):
    """Schema for creating a new NodeRating."""
    pass


class NodeRatingUpdate(BaseModel):
    """Schema for updating an existing NodeRating. All fields are optional."""
    rating: Optional[RatingValue] = Field(None, description="New rating value (1-5 stars).")


class NodeRatingResponse(NodeRatingBase):
    """Response schema for a NodeRating, including database-generated fields and computed properties."""
    id: UUID = Field(..., description="Unique identifier for the rating.")
    created_at: datetime = Field(..., description="Timestamp of when the rating was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    
    # Computed fields (calculated, not stored in DB)
    @computed_field
    def rating_display(self) -> str:
        """Visual representation of the rating."""
        # Handle both enum value and int value
        rating_val = self.rating if isinstance(self.rating, int) else self.rating.value
        return "⭐" * rating_val
    
    @computed_field
    def is_positive(self) -> bool:
        """Indicates if the rating is considered positive (4-5 stars)."""
        rating_val = self.rating if isinstance(self.rating, int) else self.rating.value
        return rating_val >= 4
    
    @computed_field
    def is_negative(self) -> bool:
        """Indicates if the rating is considered negative (1-2 stars)."""
        rating_val = self.rating if isinstance(self.rating, int) else self.rating.value
        return rating_val <= 2
    
    @computed_field
    def is_neutral(self) -> bool:
        """Indicates if the rating is considered neutral (3 stars)."""
        rating_val = self.rating if isinstance(self.rating, int) else self.rating.value
        return rating_val == 3


class NodeRatingListResponse(BaseModel):
    """Paginated list of NodeRatings."""
    items: List[NodeRatingResponse] = Field(..., description="List of node ratings for the current page.")
    total: int = Field(..., description="Total number of node ratings.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class NodeRatingSummary(BaseModel):
    """Schema for aggregated rating summary for a node."""
    total_ratings: int = Field(..., description="Total number of ratings received.")
    average_rating: float = Field(..., description="Average rating value.")
    rating_distribution: Dict[RatingValue, int] = Field(..., description="Count of ratings for each star value.")
    positive_percentage: float = Field(..., description="Percentage of positive ratings.")
    negative_percentage: float = Field(..., description="Percentage of negative ratings.")

    model_config = ConfigDict(from_attributes=True)


class NodeRatingTrend(BaseModel):
    """Schema for daily rating trends."""
    date: str = Field(..., description="Date of the trend (YYYY-MM-DD).")
    average_rating: float = Field(..., description="Average rating for the day.")
    rating_count: int = Field(..., description="Number of ratings for the day.")

    model_config = ConfigDict(from_attributes=True)

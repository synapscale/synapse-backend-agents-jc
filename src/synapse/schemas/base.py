"""
Base and shared schemas for the API.
"""

from typing import List, Optional, Any, Dict, Generic, TypeVar
import uuid
from pydantic import BaseModel, Field, EmailStr

# ===== UTILITY SCHEMAS =====


class PaginationParams(BaseModel):
    """Parameters for pagination."""

    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Base for paginated responses compatible with endpoints."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of skipped items")
    limit: int = Field(..., description="Maximum items per page")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")


class ErrorDetail(BaseModel):
    """Error detail."""

    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
    errors: Optional[List[ErrorDetail]] = None


# ===== SHARED SCHEMAS =====
# Note: Auth schemas moved to auth.py for better organization

"""
Schemas for UserVariable - a model for user-defined variables.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class UserVariableBase(BaseModel):
    """Base schema for UserVariable attributes."""
    model_config = ConfigDict(from_attributes=True)

    key: str = Field(..., max_length=255, description="The unique key of the user variable.")
    value: str = Field(..., description="The value of the user variable.")
    is_secret: bool = Field(False, description="Indicates if the variable contains sensitive information.")
    category: Optional[str] = Field(None, max_length=100, description="A category for organizing the variable.")
    description: Optional[str] = Field(None, description="A detailed description of the variable.")
    is_encrypted: bool = Field(False, description="Indicates if the variable's value is encrypted.")
    is_active: bool = Field(True, description="Whether the variable is active and can be used.")


class UserVariableCreate(UserVariableBase):
    """Schema for creating a new UserVariable."""
    user_id: UUID = Field(..., description="The ID of the user who owns this variable.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this variable belongs.")


class UserVariableUpdate(BaseModel):
    """Schema for updating an existing UserVariable. All fields are optional."""
    value: Optional[str] = Field(None, description="New value for the variable.")
    is_secret: Optional[bool] = Field(None, description="New secret status.")
    category: Optional[str] = Field(None, max_length=100, description="New category.")
    description: Optional[str] = Field(None, description="New description.")
    is_encrypted: Optional[bool] = Field(None, description="New encryption status.")
    is_active: Optional[bool] = Field(None, description="New active status.")


class UserVariableResponse(UserVariableBase):
    """Response schema for a UserVariable, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the user variable.")
    user_id: UUID = Field(..., description="The ID of the user who owns this variable.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this variable belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the variable was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    display_value: Optional[str] = Field(None, description="Masked value for secrets.")


class UserVariableListResponse(BaseModel):
    """Paginated list of UserVariables."""
    items: List[UserVariableResponse] = Field(..., description="List of user variables for the current page.")
    total: int = Field(..., description="Total number of user variables.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

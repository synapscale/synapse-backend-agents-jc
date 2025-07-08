"""
Schemas for ContactTag - a model for organizing and categorizing contacts.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, constr
from uuid import UUID


class ContactTagBase(BaseModel):
    """Base schema for ContactTag attributes."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=100, description="Name of the tag, must be unique per tenant.")
    color: str = Field("#6B7280", max_length=7, description="Hex color code for the tag display.")
    description: Optional[str] = Field(None, description="Optional description of what the tag represents.")


class ContactTagCreate(ContactTagBase):
    """Schema for creating a new contact tag."""
    tenant_id: UUID = Field(..., description="The tenant to which the tag belongs.")


class ContactTagUpdate(BaseModel):
    """Schema for updating an existing contact tag. All fields are optional."""
    name: Optional[str] = Field(None, max_length=100, description="New name for the tag.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    description: Optional[str] = Field(None, description="New description.")


class ContactTagResponse(ContactTagBase):
    """Response schema for a contact tag, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the tag.")
    tenant_id: UUID = Field(..., description="The tenant to which the tag belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the tag was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    # Potentially include associated data
    contacts_count: Optional[int] = Field(None, description="Number of contacts associated with this tag.")


class ContactTagListResponse(BaseModel):
    """Paginated list of contact tags."""
    items: List[ContactTagResponse] = Field(..., description="List of contact tags for the current page.")
    total: int = Field(..., description="Total number of tags.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class AssignTagsToContacts(BaseModel):
    """Schema for assigning one or more tags to one or more contacts."""
    tag_ids: List[UUID] = Field(..., description="List of Tag IDs to assign.")
    contact_ids: List[UUID] = Field(..., description="List of Contact IDs to be tagged.")


class AssignTagsResponse(BaseModel):
    """Result schema for the assign tags operation."""
    successful_assignments: int = Field(..., description="Number of successful tag assignments.")
    failed_assignments: int = Field(..., description="Number of failed assignments due to errors or duplicates.")

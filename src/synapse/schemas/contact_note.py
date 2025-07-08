"""
Schemas for ContactNote - a model for storing notes related to contacts.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class NoteType(str, Enum):
    """Enum for the type of note."""
    NOTE = "note"
    CALL_LOG = "call_log"
    MEETING_SUMMARY = "meeting_summary"

class ContactNoteBase(BaseModel):
    """Base schema for ContactNote attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    content: str = Field(..., description="The content of the note.")
    type: NoteType = Field(NoteType.NOTE, description="The type of the note.")
    is_private: bool = Field(False, description="Whether the note is private to the author.")

class ContactNoteCreate(ContactNoteBase):
    """Schema for creating a new contact note."""
    contact_id: UUID = Field(..., description="The contact to which this note is associated.")
    user_id: UUID = Field(..., description="The user who authored the note.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this note belongs.")

class ContactNoteUpdate(BaseModel):
    """Schema for updating an existing contact note. All fields are optional."""
    content: Optional[str] = Field(None, description="New content for the note.")
    type: Optional[NoteType] = Field(None, description="New type for the note.")
    is_private: Optional[bool] = Field(None, description="New privacy status.")

class ContactNoteResponse(ContactNoteBase):
    """Response schema for a contact note, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the note.")
    contact_id: UUID = Field(..., description="The contact to which this note is associated.")
    user_id: UUID = Field(..., description="The user who authored the note.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this note belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the note was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    author_name: Optional[str] = Field(None, description="The name of the user who created the note.")

class ContactNoteListResponse(BaseModel):
    """Paginated list of contact notes."""
    items: List[ContactNoteResponse] = Field(..., description="List of contact notes for the current page.")
    total: int = Field(..., description="Total number of notes.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

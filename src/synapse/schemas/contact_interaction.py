from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class InteractionType(str, Enum):
    """Enum for interaction types"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    MEETING = "meeting"
    VIDEO_CALL = "video_call"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    NOTE = "note"
    TASK = "task"
    DEMO = "demo"
    FOLLOW_UP = "follow_up"


class InteractionDirection(str, Enum):
    """Enum for interaction directions"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class InteractionStatus(str, Enum):
    """Enum for interaction statuses"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class ContactInteractionBase(BaseModel):
    """Base schema for ContactInteraction"""
    contact_id: UUID = Field(..., description="Contact ID")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    direction: InteractionDirection = Field(..., description="Direction of interaction")
    subject: Optional[str] = Field(None, description="Interaction subject")
    content: Optional[str] = Field(None, description="Interaction content")
    status: InteractionStatus = Field(..., description="Interaction status")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_minutes: Optional[str] = Field(None, description="Duration in minutes")
    outcome: Optional[str] = Field(None, description="Interaction outcome")
    next_action: Optional[str] = Field(None, description="Next action to take")
    interaction_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_by: UUID = Field(..., description="User who created the interaction")


class ContactInteractionCreate(ContactInteractionBase):
    """Schema for creating a new contact interaction"""
    pass


class ContactInteractionUpdate(BaseModel):
    """Schema for updating an existing contact interaction"""
    interaction_type: Optional[InteractionType] = Field(None, description="Type of interaction")
    direction: Optional[InteractionDirection] = Field(None, description="Direction of interaction")
    subject: Optional[str] = Field(None, description="Interaction subject")
    content: Optional[str] = Field(None, description="Interaction content")
    status: Optional[InteractionStatus] = Field(None, description="Interaction status")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_minutes: Optional[str] = Field(None, description="Duration in minutes")
    outcome: Optional[str] = Field(None, description="Interaction outcome")
    next_action: Optional[str] = Field(None, description="Next action to take")
    interaction_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ContactInteractionInDB(ContactInteractionBase):
    """Schema for contact interaction in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Contact interaction ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ContactInteractionResponse(ContactInteractionInDB):
    """Schema for contact interaction response"""
    pass


class ContactInteractionListResponse(BaseModel):
    """Schema for contact interaction list response"""
    model_config = ConfigDict(from_attributes=True)
    
    interactions: list[ContactInteractionResponse] = Field(..., description="List of contact interactions")
    total: int = Field(..., description="Total number of interactions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of interactions per page")
    pages: int = Field(..., description="Total number of pages")


class ContactInteractionSummary(BaseModel):
    """Schema for contact interaction summary"""
    model_config = ConfigDict(from_attributes=True)
    
    total_interactions: int = Field(..., description="Total number of interactions")
    by_type: Dict[str, int] = Field(..., description="Interactions grouped by type")
    by_status: Dict[str, int] = Field(..., description="Interactions grouped by status")
    by_direction: Dict[str, int] = Field(..., description="Interactions grouped by direction")
    recent_interactions: list[ContactInteractionResponse] = Field(..., description="Recent interactions")

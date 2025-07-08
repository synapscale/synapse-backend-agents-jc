from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContactListBase(BaseModel):
    """Base schema for ContactList"""
    name: str = Field(..., description="Contact list name")
    description: Optional[str] = Field(None, description="Contact list description")
    type: Optional[str] = Field(None, description="List type (static/dynamic/smart)")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="List filters")


class ContactListCreate(ContactListBase):
    """Schema for creating a new contact list"""
    pass


class ContactListUpdate(BaseModel):
    """Schema for updating an existing contact list"""
    name: Optional[str] = Field(None, description="Contact list name")
    description: Optional[str] = Field(None, description="Contact list description")
    type: Optional[str] = Field(None, description="List type (static/dynamic/smart)")
    filters: Optional[Dict[str, Any]] = Field(None, description="List filters")


class ContactListInDB(ContactListBase):
    """Schema for contact list in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Contact list ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ContactListResponse(ContactListInDB):
    """Schema for contact list response"""
    pass


class ContactListWithStatsResponse(ContactListInDB):
    """Schema for contact list response with statistics"""
    contact_count: int = Field(..., description="Number of contacts in the list")
    active_contacts: int = Field(..., description="Number of active contacts")
    last_updated: datetime = Field(..., description="Last update timestamp")


class ContactListListResponse(BaseModel):
    """Schema for contact list pagination response"""
    model_config = ConfigDict(from_attributes=True)
    
    contact_lists: list[ContactListResponse] = Field(..., description="List of contact lists")
    total: int = Field(..., description="Total number of contact lists")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of contact lists per page")
    pages: int = Field(..., description="Total number of pages")

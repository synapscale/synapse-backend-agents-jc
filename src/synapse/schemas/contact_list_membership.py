"""
Pydantic schemas for ContactListMembership Model
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# Base Schema: Fields shared across all other schemas
class ContactListMembershipBase(BaseModel):
    status: Optional[str] = 'active'

# Schema for creating a new contact list membership
class ContactListMembershipCreate(ContactListMembershipBase):
    list_id: UUID
    contact_id: UUID
    added_by: Optional[UUID] = None
    tenant_id: Optional[UUID] = None

# Schema for updating an existing contact list membership
class ContactListMembershipUpdate(BaseModel):
    status: Optional[str] = None

# Schema for reading/returning contact list membership data from the API
class ContactListMembershipSchema(ContactListMembershipBase):
    id: UUID
    list_id: UUID
    contact_id: UUID
    added_by: Optional[UUID]
    added_at: datetime
    tenant_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

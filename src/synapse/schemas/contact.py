from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContactBase(BaseModel):
    """Base schema for Contact"""
    email: EmailStr = Field(..., description="Contact email address")
    first_name: Optional[str] = Field(None, description="Contact first name")
    last_name: Optional[str] = Field(None, description="Contact last name")
    phone: Optional[str] = Field(None, description="Contact phone number")
    company: Optional[str] = Field(None, description="Contact company")
    job_title: Optional[str] = Field(None, description="Contact job title")
    status: Optional[str] = Field(None, description="Contact status")
    lead_score: Optional[int] = Field(None, description="Contact lead score")
    source_id: Optional[UUID] = Field(None, description="Source ID reference")
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class ContactCreate(ContactBase):
    """Schema for creating a new contact"""
    pass


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact"""
    email: Optional[EmailStr] = Field(None, description="Contact email address")
    first_name: Optional[str] = Field(None, description="Contact first name")
    last_name: Optional[str] = Field(None, description="Contact last name")
    phone: Optional[str] = Field(None, description="Contact phone number")
    company: Optional[str] = Field(None, description="Contact company")
    job_title: Optional[str] = Field(None, description="Contact job title")
    status: Optional[str] = Field(None, description="Contact status")
    lead_score: Optional[int] = Field(None, description="Contact lead score")
    source_id: Optional[UUID] = Field(None, description="Source ID reference")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class ContactInDB(ContactBase):
    """Schema for contact in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Contact ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ContactResponse(ContactInDB):
    """Schema for contact response"""
    pass


class ContactListResponse(BaseModel):
    """Schema for contact list response"""
    model_config = ConfigDict(from_attributes=True)
    
    contacts: list[ContactResponse] = Field(..., description="List of contacts")
    total: int = Field(..., description="Total number of contacts")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of contacts per page")
    pages: int = Field(..., description="Total number of pages")

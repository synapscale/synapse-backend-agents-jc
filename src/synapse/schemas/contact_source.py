"""
Schemas for ContactSource - a model for storing contact integration sources.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class IntegrationType(str, Enum):
    """Enum for the type of integration."""
    API = "api"
    EMAIL = "email"
    CSV_IMPORT = "csv_import"
    WEB_FORM = "web_form"
    MANUAL = "manual"

class ContactSourceBase(BaseModel):
    """Base schema for ContactSource attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=100, description="Name of the contact source.")
    description: Optional[str] = Field(None, description="Detailed description of the source.")
    integration_type: IntegrationType = Field(..., description="The type of integration.")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the integration (e.g., API keys, hostnames)." )
    is_active: bool = Field(True, description="Whether this source is currently active and can receive contacts.")

class ContactSourceCreate(ContactSourceBase):
    """Schema for creating a new contact source."""
    tenant_id: UUID = Field(..., description="The tenant to which this source belongs.")

class ContactSourceUpdate(BaseModel):
    """Schema for updating an existing contact source. All fields are optional."""
    name: Optional[str] = Field(None, max_length=100, description="New name for the source.")
    description: Optional[str] = Field(None, description="New description.")
    config: Optional[Dict[str, Any]] = Field(None, description="New configuration.")
    is_active: Optional[bool] = Field(None, description="New active status.")

class ContactSourceResponse(ContactSourceBase):
    """Response schema for a contact source, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the source.")
    tenant_id: UUID = Field(..., description="The tenant to which this source belongs.")
    created_at: datetime = Field(..., description="Timestamp of when the source was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    contacts_count: Optional[int] = Field(None, description="Number of contacts originating from this source.")

class ContactSourceListResponse(BaseModel):
    """Paginated list of contact sources."""
    items: List[ContactSourceResponse] = Field(..., description="List of contact sources for the current page.")
    total: int = Field(..., description="Total number of sources.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

class TestConnectionRequest(BaseModel):
    """Schema for testing the connection of a contact source."""
    source_id: UUID = Field(..., description="The ID of the source to test.")

class TestConnectionResponse(BaseModel):
    """Response schema for the test connection operation."""
    success: bool = Field(..., description="Whether the connection test was successful.")
    message: str = Field(..., description="A message detailing the result of the connection test.")
    latency_ms: Optional[float] = Field(None, description="Connection latency in milliseconds.")

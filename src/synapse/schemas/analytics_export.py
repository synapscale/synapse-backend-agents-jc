"""
Schemas for AnalyticsExport - a model for managing analytics data exports.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum

class ExportStatus(str, Enum):
    """Enum for the status of an export."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExportType(str, Enum):
    """Enum for the type of export."""
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    XLSX = "xlsx"

class AnalyticsExportBase(BaseModel):
    """Base schema for AnalyticsExport attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., max_length=255, description="The name of the export.")
    export_type: ExportType = Field(..., description="The file format of the export.")
    export_query: Dict[str, Any] = Field(..., description="The query used to generate the export.")
    status: ExportStatus = Field(ExportStatus.PENDING, description="The current status of the export.")

class AnalyticsExportCreate(AnalyticsExportBase):
    """Schema for creating a new analytics export."""
    owner_id: UUID = Field(..., description="The user who owns the export.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this export belongs.")

class AnalyticsExportUpdate(BaseModel):
    """Schema for updating an existing analytics export. All fields are optional."""
    name: Optional[str] = Field(None, max_length=255, description="New name for the export.")
    status: Optional[ExportStatus] = Field(None, description="New status for the export.")

class AnalyticsExportResponse(AnalyticsExportBase):
    """Response schema for an analytics export, including database-generated fields."""
    id: UUID = Field(..., description="Unique identifier for the export.")
    owner_id: UUID = Field(..., description="The user who owns the export.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this export belongs.")
    file_path: Optional[str] = Field(None, description="The path to the exported file.")
    created_at: datetime = Field(..., description="Timestamp of when the export was created.")
    completed_at: Optional[datetime] = Field(None, description="Timestamp of when the export was completed.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update.")

class AnalyticsExportListResponse(BaseModel):
    """Paginated list of analytics exports."""
    items: List[AnalyticsExportResponse] = Field(..., description="List of analytics exports for the current page.")
    total: int = Field(..., description="Total number of analytics exports.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")

"""
Schemas for File management.
"""

import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ===== ENUMS ALINHADOS COM O BANCO =====


class FileStatus(str, Enum):
    """File status - ALIGNED WITH THE DATABASE"""

    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ScanStatus(str, Enum):
    """Security scan status - ALIGNED WITH THE DATABASE"""

    PENDING = "pending"
    SCANNING = "scanning"
    CLEAN = "clean"
    INFECTED = "infected"
    QUARANTINED = "quarantined"


# ===== FILE SCHEMAS (ALIGNED PERFECTLY WITH THE DATABASE) =====


class FileBase(BaseModel):
    """Base schema for file attributes."""

    filename: str = Field(..., max_length=255, description="File name")
    original_name: str = Field(..., max_length=255, description="Original name")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., max_length=100, description="MIME type")
    category: str = Field(..., max_length=50, description="Category")
    is_public: bool = Field(False, description="Public file")
    tags: Optional[Dict[str, Any]] = Field(None, description="Tags")
    description: Optional[str] = Field(None, description="Description")


class FileCreate(FileBase):
    """Schema for file creation - ALIGNED WITH DATABASE"""

    file_path: str = Field(..., max_length=500, description="Internal file path")


class FileUpdate(BaseModel):
    """Schema for file updates - ALIGNED WITH DATABASE"""

    filename: Optional[str] = Field(None, max_length=255, description="File name")
    is_public: Optional[bool] = Field(None, description="Public file")
    tags: Optional[Dict[str, Any]] = Field(None, description="Tags")
    description: Optional[str] = Field(None, description="Description")
    status: Optional[FileStatus] = Field(None, description="Status")


class FileResponse(FileBase):
    """Response schema for a file - PERFECTLY ALIGNED WITH DATABASE"""

    id: uuid.UUID = Field(..., description="File ID")
    # SECURITY: Do not expose file_path
    status: Optional[str] = Field(None, description="Status")
    scan_status: Optional[str] = Field(None, description="Scan status")
    access_count: Optional[int] = Field(None, description="Number of accesses")
    last_accessed_at: Optional[datetime.datetime] = Field(
        None, description="Last access timestamp"
    )
    user_id: uuid.UUID = Field(..., description="User ID")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Tenant ID")
    created_at: datetime.datetime = Field(..., description="Creation timestamp")
    updated_at: datetime.datetime = Field(..., description="Last update timestamp")


class FileListResponse(BaseModel):
    """Paginated list of files."""

    items: List[FileResponse] = Field(..., description="List of files")
    total: int = Field(..., description="Total number of files")


# Re-export for compatibility from response_models.py
FilesResponse = FileResponse

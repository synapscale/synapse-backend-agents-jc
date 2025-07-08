"""
Schemas para NodeStatus
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4

class NodeStatusBase(BaseModel):
    """Base schema for NodeStatus"""
    name: str = Field(..., max_length=100, description="Status name")
    display_name: str = Field(..., max_length=255, description="Display name")
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    is_final: bool = Field(default=False, description="Whether this is a final status")
    is_error: bool = Field(default=False, description="Whether this indicates an error")
    is_active: bool = Field(default=True, description="Whether the status is active")
    
    class Config:
        from_attributes = True

class NodeStatusCreate(NodeStatusBase):
    """Schema for creating NodeStatus"""
    pass

class NodeStatusRead(NodeStatusBase):
    """Schema for reading NodeStatus"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NodeStatusUpdate(BaseModel):
    """Schema for updating NodeStatus"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7)
    is_final: Optional[bool] = None
    is_error: Optional[bool] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

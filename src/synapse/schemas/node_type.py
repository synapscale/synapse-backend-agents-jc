"""
Schemas para NodeType
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class NodeTypeBase(BaseModel):
    """Base schema for NodeType"""
    name: str = Field(..., max_length=100, description="Unique node type name")
    display_name: str = Field(..., max_length=255, description="Display name for the node type")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100, description="Node category (input, output, processing, etc.)")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for node configuration")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration values")
    icon: Optional[str] = Field(None, max_length=255, description="Icon identifier")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    can_have_inputs: bool = Field(default=True, description="Whether this node type can have inputs")
    can_have_outputs: bool = Field(default=True, description="Whether this node type can have outputs")
    max_inputs: Optional[str] = Field(None, max_length=10, description="Maximum inputs (1, many, etc.)")
    max_outputs: Optional[str] = Field(None, max_length=10, description="Maximum outputs (1, many, etc.)")
    is_active: bool = Field(default=True, description="Whether the node type is active")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Name must contain only alphanumeric characters, hyphens, and underscores")
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = ['input', 'output', 'processing', 'trigger', 'action', 'condition', 'loop', 'data']
            if v not in valid_categories:
                raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v
    
    @validator('max_inputs', 'max_outputs')
    def validate_max_connections(cls, v):
        if v is not None:
            valid_values = ['0', '1', 'many', 'unlimited']
            if v not in valid_values:
                try:
                    int(v)  # Allow numeric strings
                except ValueError:
                    raise ValueError(f"Max connections must be one of: {', '.join(valid_values)} or a number")
        return v
    
    class Config:
        from_attributes = True

class NodeTypeCreate(NodeTypeBase):
    """Schema for creating NodeType"""
    pass

class NodeTypeRead(NodeTypeBase):
    """Schema for reading NodeType"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NodeTypeUpdate(BaseModel):
    """Schema for updating NodeType"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=7)
    can_have_inputs: Optional[bool] = None
    can_have_outputs: Optional[bool] = None
    max_inputs: Optional[str] = Field(None, max_length=10)
    max_outputs: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = ['input', 'output', 'processing', 'trigger', 'action', 'condition', 'loop', 'data']
            if v not in valid_categories:
                raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v
    
    @validator('max_inputs', 'max_outputs')
    def validate_max_connections(cls, v):
        if v is not None:
            valid_values = ['0', '1', 'many', 'unlimited']
            if v not in valid_values:
                try:
                    int(v)  # Allow numeric strings
                except ValueError:
                    raise ValueError(f"Max connections must be one of: {', '.join(valid_values)} or a number")
        return v
    
    class Config:
        from_attributes = True

class NodeTypeList(BaseModel):
    """Schema for node type list with pagination"""
    node_types: list[NodeTypeRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class NodeTypeStats(BaseModel):
    """Schema for node type statistics"""
    total_types: int
    active_types: int
    by_category: Dict[str, int]
    input_types: int
    output_types: int
    processing_types: int
    
    class Config:
        from_attributes = True

class NodeTypeValidation(BaseModel):
    """Schema for node type validation result"""
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    
    class Config:
        from_attributes = True

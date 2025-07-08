"""
Schemas para NodeTemplate
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, UUID4, validator

class NodeTemplateBase(BaseModel):
    """Base schema for NodeTemplate"""
    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100, description="Template category")
    code_template: str = Field(..., description="Code template content")
    input_schema: Dict[str, Any] = Field(..., description="Input schema definition")
    output_schema: Dict[str, Any] = Field(..., description="Output schema definition")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Parameters schema definition")
    icon: Optional[str] = Field(None, max_length=255, description="Template icon")
    color: Optional[str] = Field(None, max_length=255, description="Template color")
    documentation: Optional[str] = Field(None, description="Template documentation")
    examples: Optional[Dict[str, Any]] = Field(None, description="Usage examples")
    is_system: bool = Field(default=False, description="Whether this is a system template")
    is_active: bool = Field(default=True, description="Whether the template is active")
    tenant_id: Optional[UUID4] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @validator('code_template')
    def validate_code_template(cls, v):
        if not v.strip():
            raise ValueError("Code template cannot be empty")
        return v.strip()
    
    @validator('input_schema', 'output_schema')
    def validate_schemas(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Schema must be a dictionary")
        return v
    
    @validator('parameters_schema')
    def validate_parameters_schema(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Parameters schema must be a dictionary")
        return v
    
    class Config:
        from_attributes = True

class NodeTemplateCreate(NodeTemplateBase):
    """Schema for creating NodeTemplate"""
    pass

class NodeTemplateRead(NodeTemplateBase):
    """Schema for reading NodeTemplate"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NodeTemplateUpdate(BaseModel):
    """Schema for updating NodeTemplate"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    code_template: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=255)
    documentation: Optional[str] = None
    examples: Optional[Dict[str, Any]] = None
    is_system: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v
    
    @validator('code_template')
    def validate_code_template(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Code template cannot be empty")
        return v.strip() if v else v
    
    @validator('input_schema', 'output_schema')
    def validate_schemas(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Schema must be a dictionary")
        return v
    
    @validator('parameters_schema')
    def validate_parameters_schema(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("Parameters schema must be a dictionary")
        return v
    
    class Config:
        from_attributes = True

class NodeTemplateList(BaseModel):
    """Schema for template list with pagination"""
    templates: List[NodeTemplateRead]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True

class NodeTemplateStats(BaseModel):
    """Schema for template statistics"""
    total_templates: int
    active_templates: int
    system_templates: int
    by_category: Dict[str, int]
    
    class Config:
        from_attributes = True

class NodeTemplateSearch(BaseModel):
    """Schema for template search"""
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    is_system: Optional[bool] = Field(None, description="Filter by system templates")
    is_active: Optional[bool] = Field(default=True, description="Filter by active templates")
    
    class Config:
        from_attributes = True

class NodeTemplateValidation(BaseModel):
    """Schema for template validation result"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    
    class Config:
        from_attributes = True

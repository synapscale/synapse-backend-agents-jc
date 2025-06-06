"""
Schemas Pydantic para nodes
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Schemas base
class NodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., min_length=1)
    category: Optional[str] = None
    is_public: bool = False
    icon: str = Field(default="🔧")
    color: str = Field(default="#6366f1")

class NodeCreate(NodeBase):
    code_template: str = Field(..., min_length=1)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    parameters_schema: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    examples: List[Dict[str, Any]] = Field(default_factory=list)

class NodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    code_template: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None

class NodeResponse(NodeBase):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    status: str
    version: str
    code_template: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    parameters_schema: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    examples: List[Dict[str, Any]]
    downloads_count: int
    usage_count: int
    rating_average: float
    rating_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NodeListResponse(BaseModel):
    items: List[NodeResponse]
    total: int
    page: int
    size: int
    pages: int


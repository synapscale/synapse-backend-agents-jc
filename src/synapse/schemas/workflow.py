"""
Schemas Pydantic para workflows
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Schemas base
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False

class WorkflowCreate(WorkflowBase):
    definition: Dict[str, Any] = Field(default_factory=dict)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    definition: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class WorkflowResponse(WorkflowBase):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    version: str
    status: str
    definition: Dict[str, Any]
    thumbnail_url: Optional[str] = None
    downloads_count: int
    rating_average: float
    rating_count: int
    execution_count: int
    last_executed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WorkflowListResponse(BaseModel):
    items: List[WorkflowResponse]
    total: int
    page: int
    size: int
    pages: int

class WorkflowExecutionRequest(BaseModel):
    inputs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    status: str
    message: str
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


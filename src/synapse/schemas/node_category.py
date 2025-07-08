"""
Schemas para NodeCategory
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, UUID4, validator

class NodeCategoryBase(BaseModel):
    """Base schema for NodeCategory"""
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10, description="Icon identifier or emoji")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    parent_id: Optional[UUID4] = Field(None, description="Parent category ID")
    sort_order: Optional[int] = Field(None, description="Sort order within parent")
    is_active: bool = Field(default=True, description="Whether the category is active")
    tenant_id: Optional[UUID4] = None
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    @validator('icon')
    def validate_icon(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("Icon must be 10 characters or less")
        return v
    
    class Config:
        from_attributes = True

class NodeCategoryCreate(NodeCategoryBase):
    """Schema for creating NodeCategory"""
    pass

class NodeCategoryRead(NodeCategoryBase):
    """Schema for reading NodeCategory"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    full_path: Optional[str] = None
    depth_level: Optional[int] = None
    is_root_category: Optional[bool] = None
    is_leaf_category: Optional[bool] = None
    has_nodes: Optional[bool] = None
    node_count: Optional[int] = None
    total_node_count: Optional[int] = None
    
    class Config:
        from_attributes = True

class NodeCategoryUpdate(BaseModel):
    """Schema for updating NodeCategory"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=7)
    parent_id: Optional[UUID4] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return v
    
    @validator('icon')
    def validate_icon(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("Icon must be 10 characters or less")
        return v
    
    class Config:
        from_attributes = True

class NodeCategoryTree(BaseModel):
    """Schema for hierarchical category tree"""
    id: UUID4
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    node_count: int
    children: List['NodeCategoryTree'] = []
    
    class Config:
        from_attributes = True

class NodeCategoryBreadcrumb(BaseModel):
    """Schema for category breadcrumb"""
    id: UUID4
    name: str
    
    class Config:
        from_attributes = True

class NodeCategoryStats(BaseModel):
    """Schema for category statistics"""
    total_categories: int
    root_categories: int
    leaf_categories: int
    max_depth: int
    categories_with_nodes: int
    total_nodes: int
    avg_nodes_per_category: float
    
    class Config:
        from_attributes = True

class NodeCategoryPopular(BaseModel):
    """Schema for popular categories"""
    category: NodeCategoryRead
    node_count: int
    
    class Config:
        from_attributes = True

class NodeCategoryReorder(BaseModel):
    """Schema for reordering categories"""
    category_ids: List[UUID4] = Field(..., description="List of category IDs in new order")
    parent_id: Optional[UUID4] = Field(None, description="Parent category ID")
    
    class Config:
        from_attributes = True

class NodeCategoryDelete(BaseModel):
    """Schema for deleting category with cleanup options"""
    move_nodes_to: Optional[UUID4] = Field(None, description="Category to move nodes to")
    move_children_to: Optional[UUID4] = Field(None, description="Category to move child categories to")
    
    class Config:
        from_attributes = True

# Enable forward references
NodeCategoryTree.model_rebuild()

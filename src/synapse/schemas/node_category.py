"""
Schemas for NodeCategory - a model for organizing and categorizing nodes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID # Use uuid.UUID instead of pydantic.UUID4


class NodeCategoryBase(BaseModel):
    """Base schema for NodeCategory attributes."""
    model_config = ConfigDict(from_attributes=True) # Removed use_enum_values as no enums are directly in base

    name: str = Field(..., max_length=100, description="The unique name of the node category.")
    description: Optional[str] = Field(None, description="A detailed description of the category.")
    icon: Optional[str] = Field(None, max_length=10, description="An icon identifier or emoji for UI representation.")
    color: Optional[str] = Field(None, max_length=7, description="A hex color code for UI representation (e.g., #FF0000).")
    parent_id: Optional[UUID] = Field(None, description="The ID of the parent category, if this is a subcategory.")
    sort_order: Optional[int] = Field(None, description="The order in which categories should be displayed within their parent.")
    is_active: bool = Field(default=True, description="Indicates if the category is active and can be used.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this category belongs.")

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


class NodeCategoryCreate(NodeCategoryBase):
    """Schema for creating a new NodeCategory."""
    pass


class NodeCategoryUpdate(BaseModel):
    """Schema for updating an existing NodeCategory. All fields are optional."""
    name: Optional[str] = Field(None, max_length=100, description="New name for the category.")
    description: Optional[str] = Field(None, description="New description.")
    icon: Optional[str] = Field(None, max_length=10, description="New icon.")
    color: Optional[str] = Field(None, max_length=7, description="New hex color code.")
    parent_id: Optional[UUID] = Field(None, description="New parent category ID.")
    sort_order: Optional[int] = Field(None, description="New sort order.")
    is_active: Optional[bool] = Field(None, description="New active status.")

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


class NodeCategoryResponse(NodeCategoryBase):
    """Response schema for a NodeCategory, including database-generated fields and computed properties."""
    id: UUID = Field(..., description="Unique identifier for the category.")
    created_at: datetime = Field(..., description="Timestamp of when the category was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    
    # Computed fields (assuming these are derived in the service layer or model)
    full_path: Optional[str] = Field(None, description="The full hierarchical path of the category (e.g., 'Root > Parent > Category').")
    depth_level: Optional[int] = Field(None, description="The depth level of the category in the hierarchy (0 for root).")
    is_root_category: Optional[bool] = Field(None, description="Indicates if this is a root category (has no parent).")
    is_leaf_category: Optional[bool] = Field(None, description="Indicates if this is a leaf category (has no children).")
    has_nodes: Optional[bool] = Field(None, description="Indicates if this category has any associated nodes.")
    node_count: Optional[int] = Field(None, description="The number of directly associated nodes.")
    total_node_count: Optional[int] = Field(None, description="The total number of nodes in this category and its subcategories.")


class NodeCategoryListResponse(BaseModel):
    """Paginated list of NodeCategories."""
    items: List[NodeCategoryResponse] = Field(..., description="List of node categories for the current page.")
    total: int = Field(..., description="Total number of node categories.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class NodeCategoryTree(BaseModel):
    """Schema for hierarchical category tree representation."""
    id: UUID = Field(..., description="Unique identifier for the category.")
    name: str = Field(..., description="Name of the category.")
    description: Optional[str] = Field(None, description="Description of the category.")
    icon: Optional[str] = Field(None, description="Icon for the category.")
    color: Optional[str] = Field(None, description="Color for the category.")
    node_count: int = Field(..., description="Number of nodes directly associated with this category.")
    children: List['NodeCategoryTree'] = Field([], description="List of child categories.")

    model_config = ConfigDict(from_attributes=True)


class NodeCategoryBreadcrumb(BaseModel):
    """Schema for a single item in a category breadcrumb trail."""
    id: UUID = Field(..., description="Unique identifier for the category.")
    name: str = Field(..., description="Name of the category.")

    model_config = ConfigDict(from_attributes=True)


class NodeCategoryStats(BaseModel):
    """Schema for aggregated statistics about node categories."""
    total_categories: int = Field(..., description="Total number of categories.")
    root_categories: int = Field(..., description="Number of root categories.")
    leaf_categories: int = Field(..., description="Number of leaf categories.")
    max_depth: int = Field(..., description="Maximum depth of the category hierarchy.")
    categories_with_nodes: int = Field(..., description="Number of categories that have associated nodes.")
    total_nodes: int = Field(..., description="Total number of nodes across all categories.")
    avg_nodes_per_category: float = Field(..., description="Average number of nodes per category.")

    model_config = ConfigDict(from_attributes=True)


class NodeCategoryPopular(BaseModel):
    """Schema for representing a popular node category."""
    category: NodeCategoryResponse = Field(..., description="The popular category details.")
    node_count: int = Field(..., description="The number of nodes associated with this category.")

    model_config = ConfigDict(from_attributes=True)


class NodeCategoryReorder(BaseModel):
    """Schema for reordering categories within a parent or at the root level."""
    category_ids: List[UUID] = Field(..., description="Ordered list of category IDs to reorder.")
    parent_id: Optional[UUID] = Field(None, description="The parent category ID if reordering within a subcategory, or None for root.")

    model_config = ConfigDict(from_attributes=True)


class NodeCategoryDelete(BaseModel):
    """Schema for deleting a category with options for handling associated nodes and children."""
    move_nodes_to: Optional[UUID] = Field(None, description="The ID of the category to move associated nodes to before deletion.")
    move_children_to: Optional[UUID] = Field(None, description="The ID of the category to move child categories to before deletion.")

    model_config = ConfigDict(from_attributes=True)

# Enable forward references for recursive schemas
NodeCategoryTree.model_rebuild()

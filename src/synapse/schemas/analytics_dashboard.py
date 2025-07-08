from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class DashboardStatus(str, Enum):
    """Enum for dashboard status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class WidgetType(str, Enum):
    """Enum for widget types"""
    CHART = "chart"
    TABLE = "table"
    METRIC = "metric"
    TEXT = "text"
    IMAGE = "image"
    IFRAME = "iframe"


class ChartType(str, Enum):
    """Enum for chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"


class DashboardWidget(BaseModel):
    """Schema for dashboard widget"""
    id: str = Field(..., description="Widget ID")
    type: WidgetType = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    description: Optional[str] = Field(None, description="Widget description")
    position: Dict[str, int] = Field(..., description="Widget position (x, y, width, height)")
    config: Dict[str, Any] = Field(..., description="Widget configuration")
    data_source: Optional[str] = Field(None, description="Data source")
    refresh_interval: Optional[int] = Field(None, description="Refresh interval in seconds")
    is_visible: bool = Field(default=True, description="Whether widget is visible")


class DashboardLayout(BaseModel):
    """Schema for dashboard layout"""
    columns: int = Field(default=12, description="Number of columns")
    rows: int = Field(default=24, description="Number of rows")
    breakpoints: Dict[str, int] = Field(default_factory=dict, description="Responsive breakpoints")
    margins: Dict[str, int] = Field(default_factory=dict, description="Layout margins")
    padding: Dict[str, int] = Field(default_factory=dict, description="Layout padding")


class DashboardFilter(BaseModel):
    """Schema for dashboard filter"""
    id: str = Field(..., description="Filter ID")
    name: str = Field(..., description="Filter name")
    type: str = Field(..., description="Filter type (date, select, multi-select, etc.)")
    value: Any = Field(..., description="Filter value")
    options: Optional[List[Any]] = Field(None, description="Filter options")
    is_global: bool = Field(default=False, description="Whether filter applies globally")


class AnalyticsDashboardBase(BaseModel):
    """Base schema for AnalyticsDashboard"""
    name: str = Field(..., description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    icon: Optional[str] = Field(None, description="Dashboard icon")
    color: Optional[str] = Field(None, description="Dashboard color (hex)")
    layout: DashboardLayout = Field(..., description="Dashboard layout configuration")
    widgets: List[DashboardWidget] = Field(..., description="Dashboard widgets")
    filters: Optional[List[DashboardFilter]] = Field(default_factory=list, description="Dashboard filters")
    auto_refresh: bool = Field(default=False, description="Whether to auto-refresh")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    is_public: bool = Field(default=False, description="Whether dashboard is public")
    shared_with: Optional[List[UUID]] = Field(default_factory=list, description="Users dashboard is shared with")
    is_default: bool = Field(default=False, description="Whether this is the default dashboard")
    status: DashboardStatus = Field(default=DashboardStatus.ACTIVE, description="Dashboard status")
    workspace_id: Optional[UUID] = Field(None, description="Workspace ID")


class AnalyticsDashboardCreate(AnalyticsDashboardBase):
    """Schema for creating a new analytics dashboard"""
    pass


class AnalyticsDashboardUpdate(BaseModel):
    """Schema for updating an existing analytics dashboard"""
    name: Optional[str] = Field(None, description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    icon: Optional[str] = Field(None, description="Dashboard icon")
    color: Optional[str] = Field(None, description="Dashboard color (hex)")
    layout: Optional[DashboardLayout] = Field(None, description="Dashboard layout configuration")
    widgets: Optional[List[DashboardWidget]] = Field(None, description="Dashboard widgets")
    filters: Optional[List[DashboardFilter]] = Field(None, description="Dashboard filters")
    auto_refresh: Optional[bool] = Field(None, description="Whether to auto-refresh")
    refresh_interval: Optional[int] = Field(None, description="Refresh interval in seconds")
    is_public: Optional[bool] = Field(None, description="Whether dashboard is public")
    shared_with: Optional[List[UUID]] = Field(None, description="Users dashboard is shared with")
    is_default: Optional[bool] = Field(None, description="Whether this is the default dashboard")
    status: Optional[DashboardStatus] = Field(None, description="Dashboard status")


class AnalyticsDashboardInDB(AnalyticsDashboardBase):
    """Schema for analytics dashboard in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Dashboard ID")
    user_id: UUID = Field(..., description="User ID")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_viewed_at: Optional[datetime] = Field(None, description="Last viewed timestamp")


class AnalyticsDashboardResponse(AnalyticsDashboardInDB):
    """Schema for analytics dashboard response"""
    pass


class AnalyticsDashboardListResponse(BaseModel):
    """Schema for analytics dashboard list response"""
    model_config = ConfigDict(from_attributes=True)
    
    dashboards: List[AnalyticsDashboardResponse] = Field(..., description="List of dashboards")
    total: int = Field(..., description="Total number of dashboards")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of dashboards per page")
    pages: int = Field(..., description="Total number of pages")


class DashboardCloneRequest(BaseModel):
    """Schema for cloning a dashboard"""
    name: str = Field(..., description="New dashboard name")
    description: Optional[str] = Field(None, description="New dashboard description")
    is_public: bool = Field(default=False, description="Whether cloned dashboard is public")


class DashboardShareRequest(BaseModel):
    """Schema for sharing a dashboard"""
    user_ids: List[UUID] = Field(..., description="List of user IDs to share with")
    permissions: Dict[str, bool] = Field(..., description="Permissions for shared users")


class DashboardExportRequest(BaseModel):
    """Schema for exporting a dashboard"""
    format: str = Field(..., description="Export format (pdf, png, json)")
    include_data: bool = Field(default=False, description="Whether to include data")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for data")


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_views: int = Field(..., description="Total number of views")
    unique_viewers: int = Field(..., description="Number of unique viewers")
    avg_session_duration: float = Field(..., description="Average session duration")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    most_viewed_widget: Optional[str] = Field(None, description="Most viewed widget ID")


class DashboardWithStats(AnalyticsDashboardResponse):
    """Schema for dashboard with statistics"""
    stats: DashboardStats = Field(..., description="Dashboard statistics")

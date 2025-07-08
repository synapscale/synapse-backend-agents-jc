from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ReportStatus(str, Enum):
    """Enum for report status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    ERROR = "error"


class ReportCategory(str, Enum):
    """Enum for report categories"""
    ANALYTICS = "analytics"
    PERFORMANCE = "performance"
    USAGE = "usage"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CUSTOM = "custom"
    DASHBOARD = "dashboard"
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPLIANCE = "compliance"


class VisualizationType(str, Enum):
    """Enum for visualization types"""
    TABLE = "table"
    CHART = "chart"
    GRAPH = "graph"
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    METRIC = "metric"


class ScheduleFrequency(str, Enum):
    """Enum for schedule frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class QueryConfig(BaseModel):
    """Schema for query configuration"""
    data_source: str = Field(..., description="Data source")
    query: str = Field(..., description="SQL query or query definition")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters")
    timeout_seconds: Optional[int] = Field(None, description="Query timeout in seconds")
    max_rows: Optional[int] = Field(None, description="Maximum rows to return")


class VisualizationConfig(BaseModel):
    """Schema for visualization configuration"""
    type: VisualizationType = Field(..., description="Visualization type")
    title: Optional[str] = Field(None, description="Visualization title")
    x_axis: Optional[str] = Field(None, description="X-axis field")
    y_axis: Optional[str] = Field(None, description="Y-axis field")
    color_scheme: Optional[str] = Field(None, description="Color scheme")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Visualization options")


class ScheduleConfig(BaseModel):
    """Schema for schedule configuration"""
    frequency: ScheduleFrequency = Field(..., description="Schedule frequency")
    time_of_day: Optional[str] = Field(None, description="Time of day (HH:MM format)")
    day_of_week: Optional[int] = Field(None, description="Day of week (0-6)")
    day_of_month: Optional[int] = Field(None, description="Day of month (1-31)")
    timezone: Optional[str] = Field(None, description="Timezone")
    enabled: bool = Field(default=True, description="Whether schedule is enabled")


class CustomReportBase(BaseModel):
    """Base schema for CustomReport"""
    name: str = Field(..., max_length=255, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    category: ReportCategory = Field(..., description="Report category")
    query_config: QueryConfig = Field(..., description="Query configuration")
    visualization_config: VisualizationConfig = Field(..., description="Visualization configuration")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Report filters")
    is_scheduled: bool = Field(default=False, description="Whether report is scheduled")
    schedule_config: Optional[ScheduleConfig] = Field(None, description="Schedule configuration")
    is_public: bool = Field(default=False, description="Whether report is public")
    shared_with: Optional[List[UUID]] = Field(default_factory=list, description="Users report is shared with")
    status: ReportStatus = Field(default=ReportStatus.DRAFT, description="Report status")
    workspace_id: Optional[UUID] = Field(None, description="Workspace ID")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class CustomReportCreate(CustomReportBase):
    """Schema for creating a new custom report"""
    user_id: UUID = Field(..., description="User ID")


class CustomReportUpdate(BaseModel):
    """Schema for updating an existing custom report"""
    name: Optional[str] = Field(None, max_length=255, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    category: Optional[ReportCategory] = Field(None, description="Report category")
    query_config: Optional[QueryConfig] = Field(None, description="Query configuration")
    visualization_config: Optional[VisualizationConfig] = Field(None, description="Visualization configuration")
    filters: Optional[Dict[str, Any]] = Field(None, description="Report filters")
    is_scheduled: Optional[bool] = Field(None, description="Whether report is scheduled")
    schedule_config: Optional[ScheduleConfig] = Field(None, description="Schedule configuration")
    is_public: Optional[bool] = Field(None, description="Whether report is public")
    shared_with: Optional[List[UUID]] = Field(None, description="Users report is shared with")
    status: Optional[ReportStatus] = Field(None, description="Report status")


class CustomReportInDB(CustomReportBase):
    """Schema for custom report in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Report ID")
    user_id: UUID = Field(..., description="User ID")
    last_run_at: Optional[datetime] = Field(None, description="Last run timestamp")
    next_run_at: Optional[datetime] = Field(None, description="Next run timestamp")
    cached_data: Optional[Dict[str, Any]] = Field(None, description="Cached report data")
    cache_expires_at: Optional[datetime] = Field(None, description="Cache expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CustomReportResponse(CustomReportInDB):
    """Schema for custom report response"""
    pass


class CustomReportListResponse(BaseModel):
    """Schema for custom report list response"""
    model_config = ConfigDict(from_attributes=True)
    
    reports: List[CustomReportResponse] = Field(..., description="List of custom reports")
    total: int = Field(..., description="Total number of reports")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of reports per page")
    pages: int = Field(..., description="Total number of pages")


class CustomReportExecution(BaseModel):
    """Schema for report execution request"""
    report_id: UUID = Field(..., description="Report ID")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Execution parameters")
    force_refresh: bool = Field(default=False, description="Force refresh cached data")
    async_execution: bool = Field(default=False, description="Execute asynchronously")


class CustomReportExecutionResponse(BaseModel):
    """Schema for report execution response"""
    execution_id: UUID = Field(..., description="Execution ID")
    report_id: UUID = Field(..., description="Report ID")
    status: str = Field(..., description="Execution status")
    data: Optional[Dict[str, Any]] = Field(None, description="Report data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    rows_count: Optional[int] = Field(None, description="Number of rows returned")
    cached: bool = Field(default=False, description="Whether data was cached")


class CustomReportShare(BaseModel):
    """Schema for sharing a report"""
    report_id: UUID = Field(..., description="Report ID")
    user_ids: List[UUID] = Field(..., description="User IDs to share with")
    permissions: Dict[str, bool] = Field(..., description="Permissions for shared users")
    message: Optional[str] = Field(None, description="Share message")


class CustomReportClone(BaseModel):
    """Schema for cloning a report"""
    report_id: UUID = Field(..., description="Report ID to clone")
    new_name: str = Field(..., description="New report name")
    new_description: Optional[str] = Field(None, description="New report description")
    copy_schedule: bool = Field(default=False, description="Copy schedule configuration")
    copy_shares: bool = Field(default=False, description="Copy share settings")


class CustomReportSchedule(BaseModel):
    """Schema for scheduling a report"""
    report_id: UUID = Field(..., description="Report ID")
    schedule_config: ScheduleConfig = Field(..., description="Schedule configuration")
    recipients: Optional[List[str]] = Field(None, description="Email recipients")
    delivery_format: str = Field(default="pdf", description="Delivery format")


class CustomReportStatistics(BaseModel):
    """Schema for report statistics"""
    report_id: UUID = Field(..., description="Report ID")
    total_executions: int = Field(..., description="Total number of executions")
    successful_executions: int = Field(..., description="Successful executions")
    failed_executions: int = Field(..., description="Failed executions")
    average_execution_time: float = Field(..., description="Average execution time")
    last_execution: Optional[datetime] = Field(None, description="Last execution timestamp")
    cache_hit_rate: float = Field(..., description="Cache hit rate")
    unique_users: int = Field(..., description="Number of unique users")
    recent_executions: List[Dict[str, Any]] = Field(..., description="Recent executions")


class CustomReportFilter(BaseModel):
    """Schema for report filtering"""
    category: Optional[ReportCategory] = Field(None, description="Filter by category")
    status: Optional[ReportStatus] = Field(None, description="Filter by status")
    is_scheduled: Optional[bool] = Field(None, description="Filter by scheduled reports")
    is_public: Optional[bool] = Field(None, description="Filter by public reports")
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    workspace_id: Optional[UUID] = Field(None, description="Filter by workspace")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    has_cached_data: Optional[bool] = Field(None, description="Filter by cached data availability")


class CustomReportExport(BaseModel):
    """Schema for report export"""
    report_id: UUID = Field(..., description="Report ID")
    format: str = Field(default="csv", description="Export format")
    include_config: bool = Field(default=False, description="Include configuration")
    include_data: bool = Field(default=True, description="Include data")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for data")

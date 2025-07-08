from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ActivityAction(str, Enum):
    """Enum for activity actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    SHARE = "share"
    INVITE = "invite"
    JOIN = "join"
    LEAVE = "leave"
    ARCHIVE = "archive"
    RESTORE = "restore"
    EXPORT = "export"
    IMPORT = "import"
    COMMENT = "comment"
    EDIT = "edit"
    EXECUTE = "execute"
    UPLOAD = "upload"
    DOWNLOAD = "download"


class ResourceType(str, Enum):
    """Enum for resource types"""
    WORKSPACE = "workspace"
    PROJECT = "project"
    WORKFLOW = "workflow"
    AGENT = "agent"
    NODE = "node"
    FILE = "file"
    COMMENT = "comment"
    INVITATION = "invitation"
    MEMBER = "member"
    SETTINGS = "settings"
    TEMPLATE = "template"
    REPORT = "report"
    DASHBOARD = "dashboard"
    INTEGRATION = "integration"


class WorkspaceActivityBase(BaseModel):
    """Base schema for WorkspaceActivity"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    user_id: UUID = Field(..., description="User ID")
    action: ActivityAction = Field(..., description="Activity action")
    resource_type: ResourceType = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    description: str = Field(..., description="Activity description")
    activity_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Activity metadata")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class WorkspaceActivityCreate(WorkspaceActivityBase):
    """Schema for creating a new workspace activity"""
    pass


class WorkspaceActivityUpdate(BaseModel):
    """Schema for updating an existing workspace activity"""
    description: Optional[str] = Field(None, description="Activity description")
    activity_metadata: Optional[Dict[str, Any]] = Field(None, description="Activity metadata")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkspaceActivityInDB(WorkspaceActivityBase):
    """Schema for workspace activity in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Activity ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class WorkspaceActivityResponse(WorkspaceActivityInDB):
    """Schema for workspace activity response"""
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")
    user_avatar: Optional[str] = Field(None, description="User avatar URL")
    workspace_name: Optional[str] = Field(None, description="Workspace name")
    formatted_description: str = Field(..., description="Formatted description")
    time_ago: str = Field(..., description="Time ago string")
    activity_icon: str = Field(..., description="Activity icon")
    activity_color: str = Field(..., description="Activity color")


class WorkspaceActivityListResponse(BaseModel):
    """Schema for workspace activity list response"""
    model_config = ConfigDict(from_attributes=True)
    
    activities: List[WorkspaceActivityResponse] = Field(..., description="List of activities")
    total: int = Field(..., description="Total number of activities")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of activities per page")
    pages: int = Field(..., description="Total number of pages")


class WorkspaceActivityTimeline(BaseModel):
    """Schema for workspace activity timeline"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    activities: List[WorkspaceActivityResponse] = Field(..., description="Activities for this date")
    activity_count: int = Field(..., description="Number of activities")
    unique_users: int = Field(..., description="Number of unique users")


class WorkspaceActivityTimelineResponse(BaseModel):
    """Schema for workspace activity timeline response"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    date_range: Dict[str, datetime] = Field(..., description="Date range")
    timeline: List[WorkspaceActivityTimeline] = Field(..., description="Timeline data")
    total_activities: int = Field(..., description="Total activities in range")
    unique_users: int = Field(..., description="Unique users in range")
    most_active_day: Optional[str] = Field(None, description="Most active day")
    most_common_action: Optional[str] = Field(None, description="Most common action")


class WorkspaceActivityStatistics(BaseModel):
    """Schema for workspace activity statistics"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    total_activities: int = Field(..., description="Total activities")
    activities_today: int = Field(..., description="Activities today")
    activities_this_week: int = Field(..., description="Activities this week")
    activities_this_month: int = Field(..., description="Activities this month")
    unique_users: int = Field(..., description="Unique active users")
    top_actions: Dict[str, int] = Field(..., description="Top actions by count")
    top_resources: Dict[str, int] = Field(..., description="Top resources by activity")
    hourly_distribution: Dict[str, int] = Field(..., description="Hourly activity distribution")
    daily_trend: List[Dict[str, Any]] = Field(..., description="Daily activity trend")
    user_activity: List[Dict[str, Any]] = Field(..., description="User activity breakdown")


class WorkspaceActivityFilter(BaseModel):
    """Schema for activity filtering"""
    workspace_id: Optional[UUID] = Field(None, description="Filter by workspace")
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    action: Optional[ActivityAction] = Field(None, description="Filter by action")
    resource_type: Optional[ResourceType] = Field(None, description="Filter by resource type")
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    search_term: Optional[str] = Field(None, description="Search in description")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")


class WorkspaceActivityExport(BaseModel):
    """Schema for activity export"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    filters: Optional[WorkspaceActivityFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_metadata: bool = Field(default=False, description="Include metadata")
    include_user_info: bool = Field(default=True, description="Include user information")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for export")
    max_records: Optional[int] = Field(None, description="Maximum records to export")


class WorkspaceActivityBatch(BaseModel):
    """Schema for batch activity operations"""
    activity_ids: List[UUID] = Field(..., description="List of activity IDs")
    action: str = Field(..., description="Batch action (archive, delete, etc.)")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action-specific data")


class WorkspaceActivityAlert(BaseModel):
    """Schema for activity alerts"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    alert_type: str = Field(..., description="Alert type")
    threshold: int = Field(..., description="Alert threshold")
    time_window_hours: int = Field(..., description="Time window in hours")
    actions: List[ActivityAction] = Field(..., description="Actions to monitor")
    resource_types: List[ResourceType] = Field(..., description="Resource types to monitor")
    enabled: bool = Field(default=True, description="Whether alert is enabled")


class WorkspaceActivityInsight(BaseModel):
    """Schema for activity insights"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    insight_type: str = Field(..., description="Insight type")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    metrics: Dict[str, Any] = Field(..., description="Insight metrics")
    recommendations: List[str] = Field(..., description="Recommendations")
    confidence_score: float = Field(..., description="Confidence score")
    generated_at: datetime = Field(..., description="Generation timestamp")


class WorkspaceActivitySummary(BaseModel):
    """Schema for activity summary"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    period: str = Field(..., description="Summary period")
    total_activities: int = Field(..., description="Total activities")
    unique_users: int = Field(..., description="Unique users")
    most_active_user: Optional[str] = Field(None, description="Most active user")
    most_common_action: Optional[str] = Field(None, description="Most common action")
    peak_hour: Optional[str] = Field(None, description="Peak activity hour")
    activity_growth: Optional[float] = Field(None, description="Activity growth percentage")
    key_events: List[str] = Field(..., description="Key events during period")

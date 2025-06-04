"""
Schemas Pydantic para Analytics
Criado por José - O melhor Full Stack do mundo
Validação e serialização para analytics e insights
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    FORM_SUBMIT = "form_submit"
    WORKFLOW_CREATE = "workflow_create"
    WORKFLOW_EXECUTE = "workflow_execute"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    FEATURE_USE = "feature_use"
    ERROR = "error"
    CUSTOM = "custom"

class MetricType(str, Enum):
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS = "business"

class InsightType(str, Enum):
    USAGE_PATTERNS = "usage_patterns"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    CONVERSION = "conversion"
    RETENTION = "retention"
    FEATURE_ADOPTION = "feature_adoption"

class ReportType(str, Enum):
    DASHBOARD = "dashboard"
    EXPORT = "export"
    SCHEDULED = "scheduled"
    CUSTOM_QUERY = "custom_query"

class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"

# ==================== EVENT SCHEMAS ====================

class EventBase(BaseModel):
    session_id: Optional[str] = Field(None, max_length=100)
    event_type: EventType
    event_name: str = Field(..., min_length=1, max_length=100)
    event_category: Optional[str] = Field(None, max_length=50)
    event_action: Optional[str] = Field(None, max_length=50)
    event_label: Optional[str] = Field(None, max_length=100)
    event_value: Optional[float] = None
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    page_url: Optional[str] = Field(None, max_length=500)
    page_title: Optional[str] = Field(None, max_length=200)
    referrer: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    country: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    device_type: Optional[str] = Field(None, max_length=20)
    browser: Optional[str] = Field(None, max_length=50)
    os: Optional[str] = Field(None, max_length=50)
    screen_resolution: Optional[str] = Field(None, max_length=20)
    duration_ms: Optional[int] = Field(None, ge=0)

    @validator('properties')
    def validate_properties(cls, v):
        if v and len(str(v)) > 10000:  # Limite de tamanho para JSON
            raise ValueError('Properties muito grandes')
        return v

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== METRIC SCHEMAS ====================

class MetricBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=20)
    dimensions: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MetricCreate(MetricBase):
    metric_type: MetricType
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UserBehaviorMetricResponse(MetricBase):
    id: int
    user_id: Optional[int] = None
    context: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class SystemPerformanceMetricResponse(MetricBase):
    id: int
    component: Optional[str] = None
    server_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BusinessMetricResponse(MetricBase):
    id: int
    category: Optional[str] = None
    subcategory: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== QUERY SCHEMAS ====================

class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    event_type: Optional[EventType] = None
    event_category: Optional[str] = None
    event_name: Optional[str] = None
    metric_name: Optional[str] = None
    group_by: Optional[List[str]] = Field(default_factory=list)
    aggregation: Optional[str] = Field("count", pattern="^(count|sum|avg|min|max)$")
    order_by: Optional[str] = None
    order_direction: Optional[str] = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(100, ge=1, le=10000)
    offset: int = Field(0, ge=0)

    @validator('group_by')
    def validate_group_by(cls, v):
        if v and len(v) > 5:
            raise ValueError('Máximo de 5 campos para agrupamento')
        return v

class QueryResponse(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    aggregations: Optional[Dict[str, Any]] = None
    execution_time_ms: int
    query_hash: str

# ==================== DASHBOARD SCHEMAS ====================

class WidgetConfig(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., pattern="^(metric_chart|event_timeline|user_funnel|kpi_card|heatmap|table)$")
    title: str = Field(..., min_length=1, max_length=100)
    config: Dict[str, Any]
    position: Dict[str, int] = Field(..., description="x, y, width, height")

class DashboardLayout(BaseModel):
    columns: int = Field(12, ge=1, le=24)
    row_height: int = Field(100, ge=50, le=500)
    margin: List[int] = Field([10, 10], min_items=2, max_items=2)

class DashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    layout: DashboardLayout
    widgets: List[WidgetConfig] = Field(..., min_items=1, max_items=50)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    refresh_interval: int = Field(300, ge=30, le=3600)  # segundos
    is_public: bool = False
    tags: Optional[List[str]] = Field(default_factory=list)

    @validator('widgets')
    def validate_widgets(cls, v):
        widget_ids = [w.id for w in v]
        if len(widget_ids) != len(set(widget_ids)):
            raise ValueError('IDs de widgets devem ser únicos')
        return v

class DashboardCreate(DashboardBase):
    pass

class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    layout: Optional[DashboardLayout] = None
    widgets: Optional[List[WidgetConfig]] = None
    filters: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None

class DashboardResponse(DashboardBase):
    id: int
    user_id: int
    user_name: str
    view_count: int = 0
    last_viewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DashboardData(BaseModel):
    dashboard: DashboardResponse
    data: Dict[str, Any]
    last_updated: datetime

# ==================== REPORT SCHEMAS ====================

class QueryConfig(BaseModel):
    type: str = Field(..., pattern="^(events|metrics|custom_sql)$")
    filters: Dict[str, Any] = Field(default_factory=dict)
    aggregations: Optional[List[Dict[str, Any]]] = None
    group_by: Optional[List[str]] = None
    order_by: Optional[List[Dict[str, str]]] = None
    limit: Optional[int] = Field(None, ge=1, le=100000)

class VisualizationConfig(BaseModel):
    chart_type: str = Field(..., pattern="^(line|bar|pie|table|scatter|heatmap)$")
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ScheduleConfig(BaseModel):
    frequency: str = Field(..., pattern="^(daily|weekly|monthly|quarterly)$")
    time: str = Field(..., pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    timezone: str = Field("UTC", max_length=50)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=Sunday
    day_of_month: Optional[int] = Field(None, ge=1, le=31)

class ReportBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    report_type: ReportType
    query_config: QueryConfig
    visualization_config: Optional[VisualizationConfig] = None
    schedule_config: Optional[ScheduleConfig] = None
    recipients: Optional[List[str]] = Field(default_factory=list)
    is_scheduled: bool = False
    format: ReportFormat = ReportFormat.JSON

    @validator('recipients')
    def validate_recipients(cls, v):
        if v:
            for email in v:
                if '@' not in email:
                    raise ValueError(f'Email inválido: {email}')
        return v

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    query_config: Optional[QueryConfig] = None
    visualization_config: Optional[VisualizationConfig] = None
    schedule_config: Optional[ScheduleConfig] = None
    recipients: Optional[List[str]] = None
    is_scheduled: Optional[bool] = None
    format: Optional[ReportFormat] = None

class ReportResponse(ReportBase):
    id: int
    user_id: int
    user_name: str
    execution_count: int = 0
    last_executed_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReportExecutionResponse(BaseModel):
    id: int
    report_id: int
    user_id: int
    execution_id: str
    status: str = Field(..., pattern="^(running|completed|failed|cancelled)$")
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    row_count: Optional[int] = None
    file_url: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== INSIGHT SCHEMAS ====================

class InsightRequest(BaseModel):
    primary_type: InsightType
    insight_types: List[InsightType] = Field(..., min_items=1, max_items=10)
    date_range: Dict[str, str] = Field(..., description="start and end dates in ISO format")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    include_recommendations: bool = True
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)

    @validator('date_range')
    def validate_date_range(cls, v):
        if 'start' not in v or 'end' not in v:
            raise ValueError('Date range deve conter start e end')
        try:
            start = datetime.fromisoformat(v['start'])
            end = datetime.fromisoformat(v['end'])
            if start >= end:
                raise ValueError('Data de início deve ser anterior à data de fim')
        except ValueError as e:
            raise ValueError(f'Formato de data inválido: {e}')
        return v

class InsightResponse(BaseModel):
    id: int
    user_id: int
    insight_type: InsightType
    title: str
    summary: str
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    confidence_score: float
    data_points: int
    date_range_start: datetime
    date_range_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== SYSTEM INSIGHTS ====================

class SystemInsights(BaseModel):
    period: Dict[str, datetime]
    user_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    business_metrics: Dict[str, Any]
    trends: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    generated_at: datetime

# ==================== FUNNEL SCHEMAS ====================

class FunnelStep(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    event_name: str = Field(..., min_length=1, max_length=100)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FunnelAnalysis(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    steps: List[FunnelStep] = Field(..., min_items=2, max_items=10)
    time_window_hours: int = Field(24, ge=1, le=8760)  # máximo 1 ano
    date_range: Dict[str, str]

class FunnelResult(BaseModel):
    funnel_data: List[Dict[str, Any]]
    total_users: int
    conversion_rate: float
    time_range: str
    generated_at: datetime

# ==================== COHORT SCHEMAS ====================

class CohortAnalysis(BaseModel):
    cohort_type: str = Field(..., pattern="^(registration|first_purchase|first_workflow)$")
    period_type: str = Field(..., pattern="^(day|week|month)$")
    periods: int = Field(12, ge=1, le=52)
    date_range: Dict[str, str]

class CohortResult(BaseModel):
    cohort_data: List[List[Optional[float]]]
    cohort_labels: List[str]
    period_labels: List[str]
    total_cohorts: int
    generated_at: datetime

# ==================== A/B TEST SCHEMAS ====================

class ABTestConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    variants: List[Dict[str, Any]] = Field(..., min_items=2, max_items=10)
    success_metric: str = Field(..., min_length=1, max_length=100)
    traffic_allocation: Dict[str, float]
    start_date: datetime
    end_date: datetime
    minimum_sample_size: int = Field(100, ge=10)

class ABTestResult(BaseModel):
    test_id: int
    variant_results: Dict[str, Dict[str, Any]]
    statistical_significance: bool
    confidence_level: float
    winner: Optional[str] = None
    recommendation: str
    generated_at: datetime

# ==================== EXPORT SCHEMAS ====================

class ExportRequest(BaseModel):
    data_type: str = Field(..., pattern="^(events|metrics|users|workflows)$")
    format: ReportFormat = ReportFormat.CSV
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    date_range: Optional[Dict[str, str]] = None
    columns: Optional[List[str]] = None
    limit: Optional[int] = Field(None, ge=1, le=1000000)

class ExportResponse(BaseModel):
    export_id: str
    status: str = Field(..., pattern="^(processing|completed|failed)$")
    file_url: Optional[str] = None
    file_size_bytes: Optional[int] = None
    row_count: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

# ==================== REAL-TIME SCHEMAS ====================

class RealTimeMetric(BaseModel):
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    trend: str = Field(..., pattern="^(up|down|stable)$")
    timestamp: datetime

class RealTimeStats(BaseModel):
    active_users: int
    events_per_minute: float
    error_rate: float
    response_time_ms: float
    system_load: float
    timestamp: datetime

# ==================== ALERT SCHEMAS ====================

class AlertRule(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metric_name: str = Field(..., min_length=1, max_length=100)
    condition: str = Field(..., pattern="^(greater_than|less_than|equals|not_equals)$")
    threshold: float
    time_window_minutes: int = Field(5, ge=1, le=1440)
    notification_channels: List[str] = Field(..., min_items=1)
    is_active: bool = True

class AlertResponse(BaseModel):
    id: int
    rule: AlertRule
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    current_value: float
    message: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")

    class Config:
        from_attributes = True


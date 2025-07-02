from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime, uuid
from enum import Enum


class AgentConfigurationResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    config_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    params: dict = Field(...)
    created_at: datetime.datetime = Field(...)


class AgentResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    is_active: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    status: Optional[str] = Field(...)
    priority: Optional[int] = Field(...)
    version: Optional[str] = Field(...)
    environment: Optional[str] = Field(...)
    current_config: Optional[uuid.UUID] = Field(...)


class FeatureResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    key: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    category: Optional[str] = Field(...)
    is_active: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class KnowledgeBaseResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    kb_id: uuid.UUID = Field(...)
    title: str = Field(...)
    content: dict = Field(...)
    updated_at: datetime.datetime = Field(...)


class PlanResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    description: Optional[str] = Field(...)
    price_monthly: float = Field(...)
    price_yearly: float = Field(...)
    max_workspaces: int = Field(...)
    max_members_per_workspace: int = Field(...)
    max_projects_per_workspace: int = Field(...)
    max_storage_mb: int = Field(...)
    max_executions_per_month: int = Field(...)
    allow_collaborative_workspaces: bool = Field(...)
    allow_custom_domains: bool = Field(...)
    allow_api_access: bool = Field(...)
    allow_advanced_analytics: bool = Field(...)
    allow_priority_support: bool = Field(...)
    is_active: bool = Field(...)
    is_public: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    status: Optional[str] = Field(...)
    version: Optional[str] = Field(...)
    sort_order: Optional[int] = Field(...)


class ToolResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    tool_id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: Optional[str] = Field(...)
    base_config: dict = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class AgentErrorLogResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    error_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    occurred_at: datetime.datetime = Field(...)
    error_code: Optional[str] = Field(...)
    payload: Optional[dict] = Field(...)


class AgentHierarchyResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    ancestor: uuid.UUID = Field(...)
    descendant: uuid.UUID = Field(...)
    depth: int = Field(...)


class AgentKbResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    agent_id: uuid.UUID = Field(...)
    kb_id: uuid.UUID = Field(...)
    config: dict = Field(...)


class AgentToolResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    agent_id: uuid.UUID = Field(...)
    tool_id: uuid.UUID = Field(...)
    config: dict = Field(...)


class AgentTriggerResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    trigger_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    trigger_type: str = Field(...)
    cron_expr: Optional[str] = Field(...)
    event_name: Optional[str] = Field(...)
    active: bool = Field(...)
    last_run_at: Optional[datetime.datetime] = Field(...)


class AgentUsageMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    metric_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    period_start: datetime.datetime = Field(...)
    period_end: datetime.datetime = Field(...)
    calls_count: int = Field(...)
    tokens_used: int = Field(...)
    cost_est: float = Field(...)
    created_at: datetime.datetime = Field(...)


class PlanFeatureResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(...)
    config: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TenantResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    domain: Optional[str] = Field(...)
    status: str = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)
    plan_id: uuid.UUID = Field(...)
    theme: Optional[str] = Field(...)
    default_language: Optional[str] = Field(...)
    timezone: Optional[str] = Field(...)
    mfa_required: Optional[bool] = Field(...)
    session_timeout: Optional[int] = Field(...)
    ip_whitelist: Optional[dict] = Field(...)
    max_storage_mb: Optional[int] = Field(...)
    max_workspaces: Optional[int] = Field(...)
    max_api_calls_per_day: Optional[int] = Field(...)
    max_members_per_workspace: Optional[int] = Field(...)
    enabled_features: Optional[str] = Field(...)


class AgentQuotaResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    quota_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    max_calls: int = Field(...)
    max_tokens: int = Field(...)
    period: str = Field(...)
    created_at: datetime.datetime = Field(...)


class AnalyticsMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    metric_name: str = Field(...)
    metric_value: float = Field(...)
    dimensions: dict = Field(...)
    timestamp: datetime.datetime = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class BusinessMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    date: datetime.datetime = Field(...)
    period_type: str = Field(...)
    total_users: int = Field(...)
    new_users: int = Field(...)
    active_users: int = Field(...)
    churned_users: int = Field(...)
    total_sessions: int = Field(...)
    avg_session_duration: float = Field(...)
    total_page_views: int = Field(...)
    bounce_rate: float = Field(...)
    workflows_created: int = Field(...)
    workflows_executed: int = Field(...)
    components_published: int = Field(...)
    components_downloaded: int = Field(...)
    workspaces_created: int = Field(...)
    teams_formed: int = Field(...)
    collaborative_sessions: int = Field(...)
    total_revenue: float = Field(...)
    recurring_revenue: float = Field(...)
    marketplace_revenue: float = Field(...)
    avg_revenue_per_user: float = Field(...)
    error_rate: float = Field(...)
    avg_response_time: float = Field(...)
    uptime_percentage: float = Field(...)
    customer_satisfaction: float = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class ContactListResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    type: Optional[str] = Field(...)
    filters: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactSourceResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    integration_type: Optional[str] = Field(...)
    config: Optional[dict] = Field(...)
    is_active: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactTagResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    color: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class LlmResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    provider: str = Field(...)
    model_version: Optional[str] = Field(...)
    cost_per_token_input: float = Field(...)
    cost_per_token_output: float = Field(...)
    max_tokens_supported: Optional[int] = Field(...)
    supports_function_calling: Optional[bool] = Field(...)
    supports_vision: Optional[bool] = Field(...)
    supports_streaming: Optional[bool] = Field(...)
    context_window: Optional[int] = Field(...)
    is_active: Optional[bool] = Field(...)
    llm_metadata: Optional[dict] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    status: Optional[str] = Field(...)
    health_status: Optional[str] = Field(...)
    response_time_avg_ms: Optional[int] = Field(...)
    availability_percentage: Optional[float] = Field(...)


class NodeCategorieResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    icon: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    parent_id: Optional[uuid.UUID] = Field(...)
    sort_order: Optional[int] = Field(...)
    is_active: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class NodeTemplateResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    category: Optional[str] = Field(...)
    code_template: str = Field(...)
    input_schema: dict = Field(...)
    output_schema: dict = Field(...)
    parameters_schema: Optional[dict] = Field(...)
    icon: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    documentation: Optional[str] = Field(...)
    examples: Optional[dict] = Field(...)
    is_system: Optional[bool] = Field(...)
    is_active: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class PaymentProviderResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    display_name: str = Field(...)
    is_active: Optional[bool] = Field(...)
    config: Optional[dict] = Field(...)
    api_version: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class PlanEntitlementResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    limit_value: Optional[int] = Field(...)
    is_unlimited: Optional[bool] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class RbacPermissionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    key: str = Field(...)
    description: Optional[str] = Field(...)
    category: Optional[str] = Field(...)
    resource: Optional[str] = Field(...)
    action: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class RbacRoleResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    is_system: Optional[bool] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class SystemPerformanceMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    metric_name: str = Field(...)
    metric_type: str = Field(...)
    service: str = Field(...)
    environment: str = Field(...)
    value: float = Field(...)
    unit: Optional[str] = Field(...)
    tags: Optional[dict] = Field(...)
    timestamp: datetime.datetime = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TenantFeatureResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(...)
    usage_count: Optional[int] = Field(...)
    limit_value: Optional[int] = Field(...)
    config: Optional[dict] = Field(...)
    expires_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class UserResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    email: str = Field(...)
    username: str = Field(...)
    full_name: str = Field(...)
    is_active: Optional[bool] = Field(...)
    is_verified: Optional[bool] = Field(...)
    is_superuser: Optional[bool] = Field(...)
    profile_image_url: Optional[str] = Field(...)
    bio: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)
    status: Optional[str] = Field(...)
    metadata: Optional[dict] = Field(...)
    last_login_at: Optional[datetime.datetime] = Field(...)
    login_count: Optional[int] = Field(...)
    failed_login_attempts: Optional[int] = Field(...)
    account_locked_until: Optional[datetime.datetime] = Field(...)


class WorkflowExecutionMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    workflow_execution_id: uuid.UUID = Field(...)
    node_execution_id: Optional[int] = Field(...)
    metric_type: str = Field(...)
    metric_name: str = Field(...)
    value_numeric: Optional[int] = Field(...)
    value_float: Optional[str] = Field(...)
    value_text: Optional[str] = Field(...)
    value_json: Optional[dict] = Field(...)
    context: Optional[str] = Field(...)
    tags: Optional[dict] = Field(...)
    measured_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class AgentAclResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    agent_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    can_read: bool = Field(...)
    can_write: bool = Field(...)


class AgentModelResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    agent_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    override: dict = Field(...)


class AnalyticsAlertResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    condition: dict = Field(...)
    notification_config: dict = Field(...)
    is_active: bool = Field(...)
    owner_id: uuid.UUID = Field(...)
    last_triggered_at: Optional[datetime.datetime] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class AnalyticsDashboardResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    icon: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    user_id: uuid.UUID = Field(...)
    layout: dict = Field(...)
    widgets: dict = Field(...)
    filters: Optional[dict] = Field(...)
    auto_refresh: bool = Field(...)
    refresh_interval: Optional[int] = Field(...)
    is_public: bool = Field(...)
    shared_with: Optional[dict] = Field(...)
    is_default: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    last_viewed_at: Optional[datetime.datetime] = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)


class AnalyticsExportResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    export_type: str = Field(...)
    query: dict = Field(...)
    file_path: Optional[str] = Field(...)
    status: str = Field(...)
    owner_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class AnalyticsReportResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    query: dict = Field(...)
    schedule: Optional[str] = Field(...)
    owner_id: uuid.UUID = Field(...)
    is_active: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class AuditLogResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    audit_id: uuid.UUID = Field(...)
    table_name: str = Field(...)
    record_id: uuid.UUID = Field(...)
    changed_by: Optional[uuid.UUID] = Field(...)
    changed_at: datetime.datetime = Field(...)
    operation: str = Field(...)
    diffs: Optional[dict] = Field(...)


class CampaignResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    type: str = Field(...)
    status: Optional[str] = Field(...)
    subject: Optional[str] = Field(...)
    content: Optional[str] = Field(...)
    template_id: Optional[uuid.UUID] = Field(...)
    scheduled_at: Optional[datetime.datetime] = Field(...)
    sent_at: Optional[datetime.datetime] = Field(...)
    stats: Optional[dict] = Field(...)
    settings: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    email: str = Field(...)
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    phone: Optional[str] = Field(...)
    company: Optional[str] = Field(...)
    job_title: Optional[str] = Field(...)
    status: Optional[str] = Field(...)
    lead_score: Optional[int] = Field(...)
    source_id: Optional[uuid.UUID] = Field(...)
    custom_fields: Optional[dict] = Field(...)
    tags: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class CouponResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    code: str = Field(...)
    name: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    type: str = Field(...)
    value: float = Field(...)
    currency: Optional[str] = Field(...)
    max_uses: Optional[int] = Field(...)
    used_count: Optional[int] = Field(...)
    min_amount: Optional[float] = Field(...)
    max_discount: Optional[float] = Field(...)
    valid_from: Optional[datetime.datetime] = Field(...)
    valid_until: Optional[datetime.datetime] = Field(...)
    is_active: Optional[bool] = Field(...)
    is_stackable: Optional[bool] = Field(...)
    applicable_plans: Optional[dict] = Field(...)
    restrictions: Optional[dict] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class EmailVerificationTokenResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_used: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class FileResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    filename: str = Field(...)
    original_name: str = Field(...)
    file_path: str = Field(...)
    file_size: int = Field(...)
    mime_type: str = Field(...)
    category: str = Field(...)
    is_public: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tags: Optional[dict] = Field(...)
    description: Optional[str] = Field(...)
    status: Optional[str] = Field(...)
    scan_status: Optional[str] = Field(...)
    access_count: Optional[int] = Field(...)
    last_accessed_at: Optional[datetime.datetime] = Field(...)


class MarketplaceComponentResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    category: str = Field(...)
    component_type: str = Field(...)
    tags: Optional[str] = Field(...)
    price: float = Field(...)
    is_free: bool = Field(...)
    author_id: uuid.UUID = Field(...)
    version: str = Field(...)
    content: Optional[str] = Field(...)
    component_metadata: Optional[str] = Field(...)
    downloads_count: int = Field(...)
    rating_average: float = Field(...)
    rating_count: int = Field(...)
    is_featured: bool = Field(...)
    is_approved: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    title: str = Field(...)
    short_description: Optional[str] = Field(...)
    subcategory: Optional[str] = Field(...)
    organization: Optional[str] = Field(...)
    configuration_schema: Optional[dict] = Field(...)
    dependencies: Optional[dict] = Field(...)
    compatibility: Optional[dict] = Field(...)
    documentation: Optional[str] = Field(...)
    readme: Optional[str] = Field(...)
    changelog: Optional[str] = Field(...)
    examples: Optional[dict] = Field(...)
    icon_url: Optional[str] = Field(...)
    screenshots: Optional[dict] = Field(...)
    demo_url: Optional[str] = Field(...)
    video_url: Optional[str] = Field(...)
    currency: Optional[str] = Field(...)
    license_type: Optional[str] = Field(...)
    install_count: int = Field(...)
    view_count: int = Field(...)
    like_count: int = Field(...)
    is_verified: bool = Field(...)
    moderation_notes: Optional[str] = Field(...)
    keywords: Optional[dict] = Field(...)
    search_vector: Optional[str] = Field(...)
    popularity_score: float = Field(...)
    published_at: Optional[datetime.datetime] = Field(...)
    last_download_at: Optional[datetime.datetime] = Field(...)


class PasswordResetTokenResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_used: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class PaymentCustomerResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    external_customer_id: str = Field(...)
    customer_data: Optional[dict] = Field(...)
    is_active: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class PlanProviderMappingResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    external_plan_id: str = Field(...)
    external_price_id: Optional[str] = Field(...)
    is_active: Optional[bool] = Field(...)
    config: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ProjectCollaboratorResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    can_edit: bool = Field(...)
    can_comment: bool = Field(...)
    can_share: bool = Field(...)
    can_delete: bool = Field(...)
    is_online: bool = Field(...)
    current_cursor_position: Optional[dict] = Field(...)
    last_edit_at: Optional[datetime.datetime] = Field(...)
    added_at: datetime.datetime = Field(...)
    last_seen_at: datetime.datetime = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ProjectCommentResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    parent_id: Optional[uuid.UUID] = Field(...)
    content: str = Field(...)
    content_type: str = Field(...)
    node_id: Optional[str] = Field(...)
    position_x: Optional[float] = Field(...)
    position_y: Optional[float] = Field(...)
    is_resolved: bool = Field(...)
    is_edited: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    resolved_at: Optional[datetime.datetime] = Field(...)


class RbacRolePermissionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    role_id: uuid.UUID = Field(...)
    permission_id: uuid.UUID = Field(...)
    granted: Optional[bool] = Field(...)
    conditions: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class RefreshTokenResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_revoked: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TagResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    target_type: str = Field(...)
    target_id: uuid.UUID = Field(...)
    tag_name: str = Field(...)
    tag_value: Optional[str] = Field(...)
    tag_category: Optional[str] = Field(...)
    is_system_tag: Optional[bool] = Field(...)
    created_by_user_id: Optional[uuid.UUID] = Field(...)
    auto_generated: Optional[bool] = Field(...)
    confidence_score: Optional[float] = Field(...)
    tag_metadata: Optional[dict] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TemplateCollectionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    collection_id: Optional[str] = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    creator_id: uuid.UUID = Field(...)
    is_public: Optional[bool] = Field(...)
    is_featured: Optional[bool] = Field(...)
    template_ids: dict = Field(...)
    tags: Optional[dict] = Field(...)
    thumbnail_url: Optional[str] = Field(...)
    view_count: Optional[int] = Field(...)
    follow_count: Optional[int] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class UserBehaviorMetricResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    date: datetime.datetime = Field(...)
    period_type: str = Field(...)
    session_count: int = Field(...)
    total_session_duration: int = Field(...)
    avg_session_duration: float = Field(...)
    page_views: int = Field(...)
    unique_pages_visited: int = Field(...)
    workflows_created: int = Field(...)
    workflows_executed: int = Field(...)
    components_used: int = Field(...)
    collaborations_initiated: int = Field(...)
    marketplace_purchases: int = Field(...)
    revenue_generated: float = Field(...)
    components_published: int = Field(...)
    error_count: int = Field(...)
    support_tickets: int = Field(...)
    feature_requests: int = Field(...)
    engagement_score: float = Field(...)
    satisfaction_score: float = Field(...)
    value_score: float = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class UserInsightResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    insight_type: str = Field(...)
    category: str = Field(...)
    priority: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    recommendation: Optional[str] = Field(...)
    supporting_data: Optional[dict] = Field(...)
    confidence_score: float = Field(...)
    suggested_action: Optional[str] = Field(...)
    action_url: Optional[str] = Field(...)
    action_data: Optional[dict] = Field(...)
    is_read: bool = Field(...)
    is_dismissed: bool = Field(...)
    is_acted_upon: bool = Field(...)
    user_feedback: Optional[str] = Field(...)
    expires_at: Optional[datetime.datetime] = Field(...)
    is_evergreen: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    read_at: Optional[datetime.datetime] = Field(...)
    acted_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class UserSubscriptionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    started_at: datetime.datetime = Field(...)
    expires_at: Optional[datetime.datetime] = Field(...)
    cancelled_at: Optional[datetime.datetime] = Field(...)
    payment_method: Optional[str] = Field(...)
    payment_provider: Optional[str] = Field(...)
    external_subscription_id: Optional[str] = Field(...)
    billing_cycle: Optional[str] = Field(...)
    current_period_start: Optional[datetime.datetime] = Field(...)
    current_period_end: Optional[datetime.datetime] = Field(...)
    current_workspaces: int = Field(...)
    current_storage_mb: float = Field(...)
    current_executions_this_month: int = Field(...)
    subscription_metadata: Optional[dict] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    status: Optional[str] = Field(...)


class UserTenantRoleResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    role_id: uuid.UUID = Field(...)
    granted_by: Optional[uuid.UUID] = Field(...)
    granted_at: Optional[datetime.datetime] = Field(...)
    expires_at: Optional[datetime.datetime] = Field(...)
    is_active: Optional[bool] = Field(...)
    conditions: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class UserVariableResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    key: str = Field(...)
    value: str = Field(...)
    is_secret: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    category: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    is_encrypted: bool = Field(...)
    is_active: bool = Field(...)


class WebhookLogResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    event_type: str = Field(...)
    event_id: Optional[str] = Field(...)
    payload: dict = Field(...)
    headers: Optional[dict] = Field(...)
    status: Optional[str] = Field(...)
    processed_at: Optional[datetime.datetime] = Field(...)
    error_message: Optional[str] = Field(...)
    retry_count: Optional[int] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkspaceResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    description: Optional[str] = Field(...)
    avatar_url: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    owner_id: uuid.UUID = Field(...)
    is_public: bool = Field(...)
    is_template: bool = Field(...)
    allow_guest_access: bool = Field(...)
    require_approval: bool = Field(...)
    max_members: Optional[int] = Field(...)
    max_projects: Optional[int] = Field(...)
    max_storage_mb: Optional[int] = Field(...)
    enable_real_time_editing: bool = Field(...)
    enable_comments: bool = Field(...)
    enable_chat: bool = Field(...)
    enable_video_calls: bool = Field(...)
    member_count: int = Field(...)
    project_count: int = Field(...)
    activity_count: int = Field(...)
    storage_used_mb: float = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    last_activity_at: datetime.datetime = Field(...)
    email_notifications: Optional[bool] = Field(...)
    push_notifications: Optional[bool] = Field(...)
    api_calls_today: Optional[int] = Field(...)
    api_calls_this_month: Optional[int] = Field(...)
    last_api_reset_daily: Optional[datetime.datetime] = Field(...)
    last_api_reset_monthly: Optional[datetime.datetime] = Field(...)
    feature_usage_count: Optional[dict] = Field(...)
    type: str = Field(...)


class CampaignContactResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    campaign_id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    status: Optional[str] = Field(...)
    sent_at: Optional[datetime.datetime] = Field(...)
    opened_at: Optional[datetime.datetime] = Field(...)
    clicked_at: Optional[datetime.datetime] = Field(...)
    bounced_at: Optional[datetime.datetime] = Field(...)
    unsubscribed_at: Optional[datetime.datetime] = Field(...)
    error_message: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ComponentDownloadResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    version: str = Field(...)
    download_type: str = Field(...)
    ip_address: Optional[str] = Field(...)
    user_agent: Optional[str] = Field(...)
    referrer: Optional[str] = Field(...)
    status: str = Field(...)
    file_size: Optional[int] = Field(...)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ComponentPurchaseResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    amount: float = Field(...)
    currency: str = Field(...)
    payment_method: Optional[str] = Field(...)
    transaction_id: str = Field(...)
    payment_provider: Optional[str] = Field(...)
    provider_transaction_id: Optional[str] = Field(...)
    status: str = Field(...)
    license_key: Optional[str] = Field(...)
    license_expires_at: Optional[datetime.datetime] = Field(...)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    refunded_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ComponentRatingResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    title: Optional[str] = Field(...)
    review: Optional[str] = Field(...)
    ease_of_use: Optional[int] = Field(...)
    documentation_quality: Optional[int] = Field(...)
    performance: Optional[int] = Field(...)
    reliability: Optional[int] = Field(...)
    support_quality: Optional[int] = Field(...)
    version_used: Optional[str] = Field(...)
    use_case: Optional[str] = Field(...)
    experience_level: Optional[str] = Field(...)
    helpful_count: int = Field(...)
    reported_count: int = Field(...)
    is_verified_purchase: bool = Field(...)
    is_featured: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class ComponentVersionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    version: str = Field(...)
    is_latest: bool = Field(...)
    is_stable: bool = Field(...)
    changelog: Optional[str] = Field(...)
    breaking_changes: Optional[str] = Field(...)
    migration_guide: Optional[str] = Field(...)
    component_data: dict = Field(...)
    file_size: Optional[int] = Field(...)
    min_platform_version: Optional[str] = Field(...)
    max_platform_version: Optional[str] = Field(...)
    dependencies: Optional[dict] = Field(...)
    download_count: int = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    deprecated_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactEventResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    event_type: str = Field(...)
    event_data: Optional[dict] = Field(...)
    occurred_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactInteractionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    user_id: Optional[uuid.UUID] = Field(...)
    type: str = Field(...)
    channel: Optional[str] = Field(...)
    subject: Optional[str] = Field(...)
    content: Optional[str] = Field(...)
    direction: Optional[str] = Field(...)
    status: Optional[str] = Field(...)
    scheduled_at: Optional[datetime.datetime] = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactListMembershipResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    list_id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    added_by: Optional[uuid.UUID] = Field(...)
    added_at: Optional[datetime.datetime] = Field(...)
    status: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ContactNoteResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    content: str = Field(...)
    type: Optional[str] = Field(...)
    is_private: Optional[bool] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ConversionJourneyResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    journey_name: Optional[str] = Field(...)
    current_stage: Optional[str] = Field(...)
    stages_completed: Optional[dict] = Field(...)
    conversion_probability: Optional[float] = Field(...)
    last_interaction_at: Optional[datetime.datetime] = Field(...)
    converted_at: Optional[datetime.datetime] = Field(...)
    conversion_value: Optional[float] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class CustomReportResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    category: Optional[str] = Field(...)
    query_config: dict = Field(...)
    visualization_config: Optional[dict] = Field(...)
    filters: Optional[dict] = Field(...)
    is_scheduled: bool = Field(...)
    schedule_config: Optional[dict] = Field(...)
    last_run_at: Optional[datetime.datetime] = Field(...)
    next_run_at: Optional[datetime.datetime] = Field(...)
    is_public: bool = Field(...)
    shared_with: Optional[dict] = Field(...)
    cached_data: Optional[dict] = Field(...)
    cache_expires_at: Optional[datetime.datetime] = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class LlmsConversationResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    agent_id: Optional[uuid.UUID] = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    title: Optional[str] = Field(...)
    status: Optional[str] = Field(...)
    message_count: Optional[int] = Field(...)
    total_tokens_used: Optional[int] = Field(...)
    context: Optional[dict] = Field(...)
    settings: Optional[dict] = Field(...)
    last_message_at: Optional[datetime.datetime] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class NodeResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: str = Field(...)
    description: Optional[str] = Field(...)
    version: str = Field(...)
    definition: dict = Field(...)
    is_public: bool = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)
    code_template: str = Field(...)
    input_schema: dict = Field(...)
    output_schema: dict = Field(...)
    parameters_schema: Optional[dict] = Field(...)
    icon: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    documentation: Optional[str] = Field(...)
    examples: Optional[dict] = Field(...)
    downloads_count: Optional[int] = Field(...)
    usage_count: Optional[int] = Field(...)
    rating_average: Optional[int] = Field(...)
    rating_count: Optional[int] = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    status: Optional[str] = Field(...)
    timeout_seconds: Optional[int] = Field(...)
    retry_count: Optional[int] = Field(...)


class PaymentMethodResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    customer_id: uuid.UUID = Field(...)
    external_method_id: str = Field(...)
    type: str = Field(...)
    last4: Optional[str] = Field(...)
    brand: Optional[str] = Field(...)
    exp_month: Optional[int] = Field(...)
    exp_year: Optional[int] = Field(...)
    is_default: Optional[bool] = Field(...)
    is_active: Optional[bool] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    definition: dict = Field(...)
    is_active: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    is_public: Optional[bool] = Field(...)
    category: Optional[str] = Field(...)
    tags: Optional[dict] = Field(...)
    version: Optional[str] = Field(...)
    thumbnail_url: Optional[str] = Field(...)
    downloads_count: Optional[int] = Field(...)
    rating_average: Optional[int] = Field(...)
    rating_count: Optional[int] = Field(...)
    execution_count: Optional[int] = Field(...)
    last_executed_at: Optional[datetime.datetime] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    status: Optional[str] = Field(...)
    priority: Optional[int] = Field(...)
    timeout_seconds: Optional[int] = Field(...)
    retry_count: Optional[int] = Field(...)


class WorkspaceActivitieResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    action: str = Field(...)
    resource_type: str = Field(...)
    resource_id: Optional[str] = Field(...)
    description: str = Field(...)
    metadata: Optional[dict] = Field(...)
    ip_address: Optional[str] = Field(...)
    user_agent: Optional[str] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)
    meta_data: Optional[dict] = Field(...)


class WorkspaceFeatureResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(...)
    config: Optional[dict] = Field(...)
    usage_count: Optional[int] = Field(...)
    limit_value: Optional[int] = Field(...)
    expires_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkspaceInvitationResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    inviter_id: uuid.UUID = Field(...)
    invited_user_id: Optional[uuid.UUID] = Field(...)
    email: str = Field(...)
    message: Optional[str] = Field(...)
    token: str = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    expires_at: datetime.datetime = Field(...)
    responded_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkspaceMemberResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    workspace_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    custom_permissions: Optional[dict] = Field(...)
    status: str = Field(...)
    is_favorite: bool = Field(...)
    notification_preferences: Optional[dict] = Field(...)
    last_seen_at: datetime.datetime = Field(...)
    joined_at: datetime.datetime = Field(...)
    left_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)
    role: str = Field(...)


class LlmsConversationsTurnResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    first_used_at: datetime.datetime = Field(...)
    last_used_at: datetime.datetime = Field(...)
    message_count: Optional[int] = Field(...)
    total_input_tokens: Optional[int] = Field(...)
    total_output_tokens: Optional[int] = Field(...)
    total_cost_usd: Optional[float] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class LlmsMessageResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    role: str = Field(...)
    content: str = Field(...)
    attachments: Optional[dict] = Field(...)
    model_used: Optional[str] = Field(...)
    model_provider: Optional[str] = Field(...)
    tokens_used: Optional[int] = Field(...)
    processing_time_ms: Optional[int] = Field(...)
    temperature: Optional[float] = Field(...)
    max_tokens: Optional[int] = Field(...)
    status: Optional[str] = Field(...)
    error_message: Optional[str] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class NodeRatingResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ReportExecutionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    report_id: uuid.UUID = Field(...)
    user_id: Optional[uuid.UUID] = Field(...)
    execution_type: str = Field(...)
    parameters: Optional[dict] = Field(...)
    status: str = Field(...)
    result_data: Optional[dict] = Field(...)
    error_message: Optional[str] = Field(...)
    execution_time_ms: Optional[int] = Field(...)
    rows_processed: Optional[int] = Field(...)
    data_size_bytes: Optional[int] = Field(...)
    started_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class SubscriptionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    provider_id: Optional[uuid.UUID] = Field(...)
    external_subscription_id: Optional[str] = Field(...)
    status: str = Field(...)
    current_period_start: Optional[datetime.datetime] = Field(...)
    current_period_end: Optional[datetime.datetime] = Field(...)
    trial_start: Optional[datetime.datetime] = Field(...)
    trial_end: Optional[datetime.datetime] = Field(...)
    cancel_at_period_end: Optional[bool] = Field(...)
    canceled_at: Optional[datetime.datetime] = Field(...)
    ended_at: Optional[datetime.datetime] = Field(...)
    payment_method_id: Optional[uuid.UUID] = Field(...)
    coupon_id: Optional[uuid.UUID] = Field(...)
    quantity: Optional[int] = Field(...)
    discount_amount: Optional[float] = Field(...)
    tax_percent: Optional[float] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowExecutionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    execution_id: Optional[str] = Field(...)
    workflow_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    status: str = Field(...)
    priority: Optional[int] = Field(...)
    input_data: Optional[dict] = Field(...)
    output_data: Optional[dict] = Field(...)
    context_data: Optional[dict] = Field(...)
    variables: Optional[dict] = Field(...)
    total_nodes: Optional[int] = Field(...)
    completed_nodes: Optional[int] = Field(...)
    failed_nodes: Optional[int] = Field(...)
    progress_percentage: Optional[int] = Field(...)
    started_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    timeout_at: Optional[datetime.datetime] = Field(...)
    estimated_duration: Optional[int] = Field(...)
    actual_duration: Optional[int] = Field(...)
    execution_log: Optional[str] = Field(...)
    error_message: Optional[str] = Field(...)
    error_details: Optional[dict] = Field(...)
    debug_info: Optional[dict] = Field(...)
    retry_count: Optional[int] = Field(...)
    max_retries: Optional[int] = Field(...)
    auto_retry: Optional[bool] = Field(...)
    notify_on_completion: Optional[bool] = Field(...)
    notify_on_failure: Optional[bool] = Field(...)
    tags: Optional[dict] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowNodeResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    instance_name: Optional[str] = Field(...)
    position_x: int = Field(...)
    position_y: int = Field(...)
    configuration: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowTemplateResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    category: str = Field(...)
    tags: Optional[dict] = Field(...)
    workflow_definition: dict = Field(...)
    preview_image: Optional[str] = Field(...)
    author_id: uuid.UUID = Field(...)
    version: str = Field(...)
    is_public: bool = Field(...)
    is_featured: bool = Field(...)
    downloads_count: int = Field(...)
    rating_average: float = Field(...)
    rating_count: int = Field(...)
    price: float = Field(...)
    is_free: bool = Field(...)
    license: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    title: str = Field(...)
    short_description: Optional[str] = Field(...)
    original_workflow_id: Optional[uuid.UUID] = Field(...)
    status: Optional[str] = Field(...)
    is_verified: Optional[bool] = Field(...)
    license_type: Optional[str] = Field(...)
    workflow_data: dict = Field(...)
    nodes_data: dict = Field(...)
    connections_data: Optional[dict] = Field(...)
    required_variables: Optional[dict] = Field(...)
    optional_variables: Optional[dict] = Field(...)
    default_config: Optional[dict] = Field(...)
    compatibility_version: Optional[str] = Field(...)
    estimated_duration: Optional[int] = Field(...)
    complexity_level: Optional[int] = Field(...)
    download_count: Optional[int] = Field(...)
    usage_count: Optional[int] = Field(...)
    view_count: Optional[int] = Field(...)
    keywords: Optional[dict] = Field(...)
    use_cases: Optional[dict] = Field(...)
    industries: Optional[dict] = Field(...)
    thumbnail_url: Optional[str] = Field(...)
    preview_images: Optional[dict] = Field(...)
    demo_video_url: Optional[str] = Field(...)
    documentation: Optional[str] = Field(...)
    setup_instructions: Optional[str] = Field(...)
    changelog: Optional[dict] = Field(...)
    support_email: Optional[str] = Field(...)
    repository_url: Optional[str] = Field(...)
    documentation_url: Optional[str] = Field(...)
    published_at: Optional[datetime.datetime] = Field(...)
    last_used_at: Optional[datetime.datetime] = Field(...)


class WorkspaceProjectResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(...)
    color: Optional[str] = Field(...)
    allow_concurrent_editing: bool = Field(...)
    auto_save_interval: Optional[int] = Field(...)
    version_control_enabled: bool = Field(...)
    status: str = Field(...)
    is_template: bool = Field(...)
    is_public: bool = Field(...)
    collaborator_count: int = Field(...)
    edit_count: int = Field(...)
    comment_count: int = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    last_edited_at: datetime.datetime = Field(...)


class AnalyticsEventResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    event_id: str = Field(...)
    event_type: str = Field(...)
    category: str = Field(...)
    action: str = Field(...)
    label: Optional[str] = Field(...)
    user_id: Optional[uuid.UUID] = Field(...)
    session_id: Optional[str] = Field(...)
    anonymous_id: Optional[str] = Field(...)
    ip_address: Optional[str] = Field(...)
    user_agent: Optional[str] = Field(...)
    referrer: Optional[str] = Field(...)
    page_url: Optional[str] = Field(...)
    properties: dict = Field(...)
    value: Optional[float] = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    project_id: uuid.UUID = Field(...)
    workflow_id: Optional[uuid.UUID] = Field(...)
    country: Optional[str] = Field(...)
    region: Optional[str] = Field(...)
    city: Optional[str] = Field(...)
    timezone: Optional[str] = Field(...)
    device_type: Optional[str] = Field(...)
    os: Optional[str] = Field(...)
    browser: Optional[str] = Field(...)
    screen_resolution: Optional[str] = Field(...)
    timestamp: datetime.datetime = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class InvoiceResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    subscription_id: Optional[uuid.UUID] = Field(...)
    invoice_number: str = Field(...)
    status: str = Field(...)
    currency: str = Field(...)
    subtotal: float = Field(...)
    tax_amount: float = Field(...)
    discount_amount: float = Field(...)
    total_amount: float = Field(...)
    due_date: Optional[str] = Field(...)
    paid_at: Optional[datetime.datetime] = Field(...)
    items: Optional[dict] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class LlmsUsageLogResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    message_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    input_tokens: int = Field(...)
    output_tokens: int = Field(...)
    total_tokens: int = Field(...)
    cost_usd: float = Field(...)
    latency_ms: Optional[int] = Field(...)
    api_status_code: Optional[int] = Field(...)
    api_request_payload: Optional[dict] = Field(...)
    api_response_metadata: Optional[dict] = Field(...)
    user_api_key_used: Optional[bool] = Field(...)
    model_settings: Optional[dict] = Field(...)
    error_message: Optional[str] = Field(...)
    status: Optional[str] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class MessageFeedbackResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    message_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating_type: str = Field(...)
    rating_value: Optional[int] = Field(...)
    feedback_text: Optional[str] = Field(...)
    feedback_category: Optional[str] = Field(...)
    improvement_suggestions: Optional[str] = Field(...)
    is_public: Optional[bool] = Field(...)
    feedback_metadata: Optional[dict] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class NodeExecutionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    execution_id: Optional[str] = Field(...)
    workflow_execution_id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    node_key: str = Field(...)
    node_type: str = Field(...)
    node_name: Optional[str] = Field(...)
    execution_order: int = Field(...)
    input_data: Optional[dict] = Field(...)
    output_data: Optional[dict] = Field(...)
    config_data: Optional[dict] = Field(...)
    started_at: Optional[datetime.datetime] = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    timeout_at: Optional[datetime.datetime] = Field(...)
    duration_ms: Optional[int] = Field(...)
    execution_log: Optional[str] = Field(...)
    error_message: Optional[str] = Field(...)
    error_details: Optional[dict] = Field(...)
    debug_info: Optional[dict] = Field(...)
    retry_count: Optional[int] = Field(...)
    max_retries: Optional[int] = Field(...)
    retry_delay: Optional[int] = Field(...)
    dependencies: Optional[dict] = Field(...)
    dependents: Optional[dict] = Field(...)
    metadata: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class ProjectVersionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    version_number: int = Field(...)
    version_name: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    workflow_data: dict = Field(...)
    changes_summary: Optional[dict] = Field(...)
    file_size: Optional[int] = Field(...)
    checksum: Optional[str] = Field(...)
    is_major: bool = Field(...)
    is_auto_save: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TemplateDownloadResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    download_type: Optional[str] = Field(...)
    ip_address: Optional[str] = Field(...)
    user_agent: Optional[str] = Field(...)
    template_version: Optional[str] = Field(...)
    downloaded_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TemplateFavoriteResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    notes: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TemplateReviewResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    title: Optional[str] = Field(...)
    comment: Optional[str] = Field(...)
    ease_of_use: Optional[int] = Field(...)
    documentation_quality: Optional[int] = Field(...)
    performance: Optional[int] = Field(...)
    value_for_money: Optional[int] = Field(...)
    is_verified_purchase: Optional[bool] = Field(...)
    is_helpful_count: Optional[int] = Field(...)
    is_reported: Optional[bool] = Field(...)
    version_reviewed: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class TemplateUsageResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workflow_id: Optional[uuid.UUID] = Field(...)
    usage_type: str = Field(...)
    success: Optional[bool] = Field(...)
    template_version: Optional[str] = Field(...)
    modifications_made: Optional[dict] = Field(...)
    execution_time: Optional[int] = Field(...)
    ip_address: Optional[str] = Field(...)
    user_agent: Optional[str] = Field(...)
    used_at: Optional[datetime.datetime] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowConnectionResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    source_node_id: uuid.UUID = Field(...)
    target_node_id: uuid.UUID = Field(...)
    source_port: Optional[str] = Field(...)
    target_port: Optional[str] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class WorkflowExecutionQueueResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: int = Field(...)
    queue_id: Optional[str] = Field(...)
    workflow_execution_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    priority: Optional[int] = Field(...)
    scheduled_at: Optional[datetime.datetime] = Field(...)
    started_at: Optional[datetime.datetime] = Field(...)
    completed_at: Optional[datetime.datetime] = Field(...)
    status: Optional[str] = Field(...)
    worker_id: Optional[str] = Field(...)
    max_execution_time: Optional[int] = Field(...)
    retry_count: Optional[int] = Field(...)
    max_retries: Optional[int] = Field(...)
    meta_data: Optional[dict] = Field(...)
    created_at: Optional[datetime.datetime] = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


class BillingEventResponse(BaseModel):
    """Modelo de resposta gerado automaticamente do banco de dados"""

    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(...)
    event_type: str = Field(...)
    amount_usd: float = Field(...)
    description: Optional[str] = Field(...)
    related_usage_log_id: Optional[uuid.UUID] = Field(...)
    related_message_id: Optional[uuid.UUID] = Field(...)
    invoice_id: Optional[str] = Field(...)
    payment_provider: Optional[str] = Field(...)
    payment_transaction_id: Optional[str] = Field(...)
    billing_metadata: Optional[dict] = Field(...)
    status: Optional[str] = Field(...)
    processed_at: Optional[datetime.datetime] = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(...)


# Modelos de lista padrão
class PaginatedResponse(BaseModel):
    """Resposta paginada padrão"""

    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Itens por página")

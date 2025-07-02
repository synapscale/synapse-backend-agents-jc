from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Union
import datetime, uuid
from enum import Enum
from pydantic import field_validator, ConfigDict


class AgentConfigurations(BaseModel):
    config_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    version_num: int = Field(...)
    params: dict = Field(...)
    created_by: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)


class Agents(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    is_active: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    tenant_id: uuid.UUID = Field(...)
    status: Optional[str] = Field(None)
    priority: Optional[int] = Field(None)
    version: Optional[str] = Field(None)
    environment: Optional[str] = Field(None)
    current_config: Optional[uuid.UUID] = Field(None)


class AlembicVersion(BaseModel):
    version_num: str = Field(...)


class Features(BaseModel):
    id: uuid.UUID = Field(...)
    key: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class KnowledgeBases(BaseModel):
    kb_id: uuid.UUID = Field(...)
    title: str = Field(...)
    content: dict = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: datetime.datetime = Field(...)


class Plans(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    description: Optional[str] = Field(None)
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
    status: Optional[str] = Field(None)
    version: Optional[str] = Field(None)
    sort_order: Optional[int] = Field(None)


class Tools(BaseModel):
    tool_id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: Optional[str] = Field(None)
    base_config: dict = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)


class AgentErrorLogs(BaseModel):
    error_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    occurred_at: datetime.datetime = Field(...)
    error_code: Optional[str] = Field(None)
    payload: Optional[dict] = Field(None)


class AgentHierarchy(BaseModel):
    ancestor: uuid.UUID = Field(...)
    descendant: uuid.UUID = Field(...)
    depth: int = Field(...)


class AgentKbs(BaseModel):
    agent_id: uuid.UUID = Field(...)
    kb_id: uuid.UUID = Field(...)
    config: dict = Field(...)


class AgentTools(BaseModel):
    agent_id: uuid.UUID = Field(...)
    tool_id: uuid.UUID = Field(...)
    config: dict = Field(...)


class AgentTriggers(BaseModel):
    trigger_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    trigger_type: str = Field(...)
    cron_expr: Optional[str] = Field(None)
    event_name: Optional[str] = Field(None)
    active: bool = Field(...)
    last_run_at: Optional[datetime.datetime] = Field(None)


class AgentUsageMetrics(BaseModel):
    metric_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    period_start: datetime.datetime = Field(...)
    period_end: datetime.datetime = Field(...)
    calls_count: int = Field(...)
    tokens_used: int = Field(...)
    cost_est: float = Field(...)
    created_at: datetime.datetime = Field(...)


class PlanFeatures(BaseModel):
    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(None)
    config: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Tenants(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    domain: Optional[str] = Field(None)
    status: str = Field(...)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    plan_id: uuid.UUID = Field(...)
    theme: Optional[str] = Field(None)
    default_language: Optional[str] = Field(None)
    timezone: Optional[str] = Field(None)
    mfa_required: Optional[bool] = Field(None)
    session_timeout: Optional[int] = Field(None)
    ip_whitelist: Optional[dict] = Field(None)
    max_storage_mb: Optional[int] = Field(None)
    max_workspaces: Optional[int] = Field(None)
    max_api_calls_per_day: Optional[int] = Field(None)
    max_members_per_workspace: Optional[int] = Field(None)
    enabled_features: Optional[str] = Field(None)


class AgentQuotas(BaseModel):
    quota_id: uuid.UUID = Field(...)
    agent_id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    max_calls: int = Field(...)
    max_tokens: int = Field(...)
    period: str = Field(...)
    created_at: datetime.datetime = Field(...)


class AnalyticsMetrics(BaseModel):
    id: uuid.UUID = Field(...)
    metric_name: str = Field(...)
    metric_value: float = Field(...)
    dimensions: dict = Field(...)
    timestamp: datetime.datetime = Field(...)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class BusinessMetrics(BaseModel):
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
    tenant_id: Optional[uuid.UUID] = Field(None)


class ContactLists(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    filters: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ContactSources(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    integration_type: Optional[str] = Field(None)
    config: Optional[dict] = Field(None)
    is_active: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ContactTags(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    name: str = Field(...)
    color: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Llms(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    provider: str = Field(...)
    model_version: Optional[str] = Field(None)
    cost_per_token_input: float = Field(...)
    cost_per_token_output: float = Field(...)
    max_tokens_supported: Optional[int] = Field(None)
    supports_function_calling: Optional[bool] = Field(None)
    supports_vision: Optional[bool] = Field(None)
    supports_streaming: Optional[bool] = Field(None)
    context_window: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)
    llm_metadata: Optional[dict] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    status: Optional[str] = Field(None)
    health_status: Optional[str] = Field(None)
    response_time_avg_ms: Optional[int] = Field(None)
    availability_percentage: Optional[float] = Field(None)


class NodeCategories(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    parent_id: Optional[uuid.UUID] = Field(None)
    sort_order: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class NodeTemplates(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    code_template: str = Field(...)
    input_schema: dict = Field(...)
    output_schema: dict = Field(...)
    parameters_schema: Optional[dict] = Field(None)
    icon: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    documentation: Optional[str] = Field(None)
    examples: Optional[dict] = Field(None)
    is_system: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class PaymentProviders(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    display_name: str = Field(...)
    is_active: Optional[bool] = Field(None)
    config: Optional[dict] = Field(None)
    webhook_secret: Optional[str] = Field(None)
    api_version: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class PlanEntitlements(BaseModel):
    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    limit_value: Optional[int] = Field(None)
    is_unlimited: Optional[bool] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class RbacPermissions(BaseModel):
    id: uuid.UUID = Field(...)
    key: str = Field(...)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    resource: Optional[str] = Field(None)
    action: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class RbacRoles(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    is_system: Optional[bool] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class SystemPerformanceMetrics(BaseModel):
    id: int = Field(...)
    metric_name: str = Field(...)
    metric_type: str = Field(...)
    service: str = Field(...)
    environment: str = Field(...)
    value: float = Field(...)
    unit: Optional[str] = Field(None)
    tags: Optional[dict] = Field(None)
    timestamp: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class TenantFeatures(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(None)
    usage_count: Optional[int] = Field(None)
    limit_value: Optional[int] = Field(None)
    config: Optional[dict] = Field(None)
    expires_at: Optional[datetime.datetime] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class Users(BaseModel):
    id: uuid.UUID = Field(...)
    email: str = Field(...)
    username: str = Field(...)
    hashed_password: str = Field(...)
    full_name: str = Field(...)
    is_active: Optional[bool] = Field(None)
    is_verified: Optional[bool] = Field(None)
    is_superuser: Optional[bool] = Field(None)
    profile_image_url: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    status: Optional[str] = Field(None)
    metadata: Optional[dict] = Field(None)
    last_login_at: Optional[datetime.datetime] = Field(None)
    login_count: Optional[int] = Field(None)
    failed_login_attempts: Optional[int] = Field(None)
    account_locked_until: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class WorkflowExecutionMetrics(BaseModel):
    id: int = Field(...)
    workflow_execution_id: uuid.UUID = Field(...)
    node_execution_id: Optional[int] = Field(None)
    metric_type: str = Field(...)
    metric_name: str = Field(...)
    value_numeric: Optional[int] = Field(None)
    value_float: Optional[str] = Field(None)
    value_text: Optional[str] = Field(None)
    value_json: Optional[dict] = Field(None)
    context: Optional[str] = Field(None)
    tags: Optional[dict] = Field(None)
    measured_at: Optional[datetime.datetime] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class AgentAcl(BaseModel):
    agent_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    can_read: bool = Field(...)
    can_write: bool = Field(...)


class AgentModels(BaseModel):
    agent_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    override: dict = Field(...)


class AnalyticsAlerts(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    condition: dict = Field(...)
    notification_config: dict = Field(...)
    is_active: bool = Field(...)
    owner_id: uuid.UUID = Field(...)
    last_triggered_at: Optional[datetime.datetime] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class AnalyticsDashboards(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    user_id: uuid.UUID = Field(...)
    layout: dict = Field(...)
    widgets: dict = Field(...)
    filters: Optional[dict] = Field(None)
    auto_refresh: bool = Field(...)
    refresh_interval: Optional[int] = Field(None)
    is_public: bool = Field(...)
    shared_with: Optional[dict] = Field(None)
    is_default: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    last_viewed_at: Optional[datetime.datetime] = Field(None)
    workspace_id: Optional[uuid.UUID] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class AnalyticsExports(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    export_type: str = Field(...)
    query: dict = Field(...)
    file_path: Optional[str] = Field(None)
    status: str = Field(...)
    owner_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class AnalyticsReports(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    query: dict = Field(...)
    schedule: Optional[str] = Field(None)
    owner_id: uuid.UUID = Field(...)
    is_active: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class AuditLog(BaseModel):
    audit_id: uuid.UUID = Field(...)
    table_name: str = Field(...)
    record_id: uuid.UUID = Field(...)
    changed_by: Optional[uuid.UUID] = Field(None)
    changed_at: datetime.datetime = Field(...)
    operation: str = Field(...)
    diffs: Optional[dict] = Field(None)


class Campaigns(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    type: str = Field(...)
    status: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    template_id: Optional[uuid.UUID] = Field(None)
    scheduled_at: Optional[datetime.datetime] = Field(None)
    sent_at: Optional[datetime.datetime] = Field(None)
    stats: Optional[dict] = Field(None)
    settings: Optional[dict] = Field(None)
    created_by: uuid.UUID = Field(...)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Contacts(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    email: str = Field(...)
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    company: Optional[str] = Field(None)
    job_title: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    lead_score: Optional[int] = Field(None)
    source_id: Optional[uuid.UUID] = Field(None)
    custom_fields: Optional[dict] = Field(None)
    tags: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Coupons(BaseModel):
    id: uuid.UUID = Field(...)
    code: str = Field(...)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    type: str = Field(...)
    value: float = Field(...)
    currency: Optional[str] = Field(None)
    max_uses: Optional[int] = Field(None)
    used_count: Optional[int] = Field(None)
    min_amount: Optional[float] = Field(None)
    max_discount: Optional[float] = Field(None)
    valid_from: Optional[datetime.datetime] = Field(None)
    valid_until: Optional[datetime.datetime] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_stackable: Optional[bool] = Field(None)
    applicable_plans: Optional[dict] = Field(None)
    restrictions: Optional[dict] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_by: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class EmailVerificationTokens(BaseModel):
    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_used: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Files(BaseModel):
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
    tags: Optional[dict] = Field(None)
    description: Optional[str] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    status: Optional[str] = Field(None)
    scan_status: Optional[str] = Field(None)
    access_count: Optional[int] = Field(None)
    last_accessed_at: Optional[datetime.datetime] = Field(None)


class MarketplaceComponents(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    category: str = Field(...)
    component_type: str = Field(...)
    tags: Optional[str] = Field(None)
    price: float = Field(...)
    is_free: bool = Field(...)
    author_id: uuid.UUID = Field(...)
    version: str = Field(...)
    content: Optional[str] = Field(None)
    component_metadata: Optional[str] = Field(None)
    downloads_count: int = Field(...)
    rating_average: float = Field(...)
    rating_count: int = Field(...)
    is_featured: bool = Field(...)
    is_approved: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    title: str = Field(...)
    short_description: Optional[str] = Field(None)
    subcategory: Optional[str] = Field(None)
    organization: Optional[str] = Field(None)
    configuration_schema: Optional[dict] = Field(None)
    dependencies: Optional[dict] = Field(None)
    compatibility: Optional[dict] = Field(None)
    documentation: Optional[str] = Field(None)
    readme: Optional[str] = Field(None)
    changelog: Optional[str] = Field(None)
    examples: Optional[dict] = Field(None)
    icon_url: Optional[str] = Field(None)
    screenshots: Optional[dict] = Field(None)
    demo_url: Optional[str] = Field(None)
    video_url: Optional[str] = Field(None)
    currency: Optional[str] = Field(None)
    license_type: Optional[str] = Field(None)
    install_count: int = Field(...)
    view_count: int = Field(...)
    like_count: int = Field(...)
    is_verified: bool = Field(...)
    moderation_notes: Optional[str] = Field(None)
    keywords: Optional[dict] = Field(None)
    search_vector: Optional[str] = Field(None)
    popularity_score: float = Field(...)
    published_at: Optional[datetime.datetime] = Field(None)
    last_download_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class PasswordResetTokens(BaseModel):
    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_used: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class PaymentCustomers(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    external_customer_id: str = Field(...)
    customer_data: Optional[dict] = Field(None)
    is_active: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class PlanProviderMappings(BaseModel):
    id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    external_plan_id: str = Field(...)
    external_price_id: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    config: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ProjectCollaborators(BaseModel):
    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    can_edit: bool = Field(...)
    can_comment: bool = Field(...)
    can_share: bool = Field(...)
    can_delete: bool = Field(...)
    is_online: bool = Field(...)
    current_cursor_position: Optional[dict] = Field(None)
    last_edit_at: Optional[datetime.datetime] = Field(None)
    added_at: datetime.datetime = Field(...)
    last_seen_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ProjectComments(BaseModel):
    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    parent_id: Optional[uuid.UUID] = Field(None)
    content: str = Field(...)
    content_type: str = Field(...)
    node_id: Optional[str] = Field(None)
    position_x: Optional[float] = Field(None)
    position_y: Optional[float] = Field(None)
    is_resolved: bool = Field(...)
    is_edited: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    resolved_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class RbacRolePermissions(BaseModel):
    id: uuid.UUID = Field(...)
    role_id: uuid.UUID = Field(...)
    permission_id: uuid.UUID = Field(...)
    granted: Optional[bool] = Field(None)
    conditions: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class RefreshTokens(BaseModel):
    id: uuid.UUID = Field(...)
    token: str = Field(...)
    user_id: uuid.UUID = Field(...)
    expires_at: datetime.datetime = Field(...)
    is_revoked: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Tags(BaseModel):
    id: uuid.UUID = Field(...)
    target_type: str = Field(...)
    target_id: uuid.UUID = Field(...)
    tag_name: str = Field(...)
    tag_value: Optional[str] = Field(None)
    tag_category: Optional[str] = Field(None)
    is_system_tag: Optional[bool] = Field(None)
    created_by_user_id: Optional[uuid.UUID] = Field(None)
    auto_generated: Optional[bool] = Field(None)
    confidence_score: Optional[float] = Field(None)
    tag_metadata: Optional[dict] = Field(None)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class TemplateCollections(BaseModel):
    id: int = Field(...)
    collection_id: Optional[str] = Field(None)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    creator_id: uuid.UUID = Field(...)
    is_public: Optional[bool] = Field(None)
    is_featured: Optional[bool] = Field(None)
    template_ids: dict = Field(...)
    tags: Optional[dict] = Field(None)
    thumbnail_url: Optional[str] = Field(None)
    view_count: Optional[int] = Field(None)
    follow_count: Optional[int] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class UserBehaviorMetrics(BaseModel):
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
    tenant_id: Optional[uuid.UUID] = Field(None)


class UserInsights(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    insight_type: str = Field(...)
    category: str = Field(...)
    priority: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    recommendation: Optional[str] = Field(None)
    supporting_data: Optional[dict] = Field(None)
    confidence_score: float = Field(...)
    suggested_action: Optional[str] = Field(None)
    action_url: Optional[str] = Field(None)
    action_data: Optional[dict] = Field(None)
    is_read: bool = Field(...)
    is_dismissed: bool = Field(...)
    is_acted_upon: bool = Field(...)
    user_feedback: Optional[str] = Field(None)
    expires_at: Optional[datetime.datetime] = Field(None)
    is_evergreen: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    read_at: Optional[datetime.datetime] = Field(None)
    acted_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class UserSubscriptions(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    started_at: datetime.datetime = Field(...)
    expires_at: Optional[datetime.datetime] = Field(None)
    cancelled_at: Optional[datetime.datetime] = Field(None)
    payment_method: Optional[str] = Field(None)
    payment_provider: Optional[str] = Field(None)
    external_subscription_id: Optional[str] = Field(None)
    billing_cycle: Optional[str] = Field(None)
    current_period_start: Optional[datetime.datetime] = Field(None)
    current_period_end: Optional[datetime.datetime] = Field(None)
    current_workspaces: int = Field(...)
    current_storage_mb: float = Field(...)
    current_executions_this_month: int = Field(...)
    subscription_metadata: Optional[dict] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    status: Optional[str] = Field(None)


class UserTenantRoles(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    role_id: uuid.UUID = Field(...)
    granted_by: Optional[uuid.UUID] = Field(None)
    granted_at: Optional[datetime.datetime] = Field(None)
    expires_at: Optional[datetime.datetime] = Field(None)
    is_active: Optional[bool] = Field(None)
    conditions: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class UserVariables(BaseModel):
    id: uuid.UUID = Field(...)
    key: str = Field(...)
    value: str = Field(...)
    is_secret: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    category: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    is_encrypted: bool = Field(...)
    is_active: bool = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class WebhookLogs(BaseModel):
    id: uuid.UUID = Field(...)
    provider_id: uuid.UUID = Field(...)
    event_type: str = Field(...)
    event_id: Optional[str] = Field(None)
    payload: dict = Field(...)
    headers: Optional[dict] = Field(None)
    status: Optional[str] = Field(None)
    processed_at: Optional[datetime.datetime] = Field(None)
    error_message: Optional[str] = Field(None)
    retry_count: Optional[int] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class Workspaces(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    slug: str = Field(...)
    description: Optional[str] = Field(None)
    avatar_url: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    owner_id: uuid.UUID = Field(...)
    is_public: bool = Field(...)
    is_template: bool = Field(...)
    allow_guest_access: bool = Field(...)
    require_approval: bool = Field(...)
    max_members: Optional[int] = Field(None)
    max_projects: Optional[int] = Field(None)
    max_storage_mb: Optional[int] = Field(None)
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
    tenant_id: uuid.UUID = Field(...)
    email_notifications: Optional[bool] = Field(None)
    push_notifications: Optional[bool] = Field(None)
    api_calls_today: Optional[int] = Field(None)
    api_calls_this_month: Optional[int] = Field(None)
    last_api_reset_daily: Optional[datetime.datetime] = Field(None)
    last_api_reset_monthly: Optional[datetime.datetime] = Field(None)
    feature_usage_count: Optional[dict] = Field(None)
    type: str = Field(...)


class CampaignContacts(BaseModel):
    id: uuid.UUID = Field(...)
    campaign_id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    status: Optional[str] = Field(None)
    sent_at: Optional[datetime.datetime] = Field(None)
    opened_at: Optional[datetime.datetime] = Field(None)
    clicked_at: Optional[datetime.datetime] = Field(None)
    bounced_at: Optional[datetime.datetime] = Field(None)
    unsubscribed_at: Optional[datetime.datetime] = Field(None)
    error_message: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ComponentDownloads(BaseModel):
    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    version: str = Field(...)
    download_type: str = Field(...)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    referrer: Optional[str] = Field(None)
    status: str = Field(...)
    file_size: Optional[int] = Field(None)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ComponentPurchases(BaseModel):
    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    amount: float = Field(...)
    currency: str = Field(...)
    payment_method: Optional[str] = Field(None)
    transaction_id: str = Field(...)
    payment_provider: Optional[str] = Field(None)
    provider_transaction_id: Optional[str] = Field(None)
    status: str = Field(...)
    license_key: Optional[str] = Field(None)
    license_expires_at: Optional[datetime.datetime] = Field(None)
    created_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(None)
    refunded_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ComponentRatings(BaseModel):
    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    title: Optional[str] = Field(None)
    review: Optional[str] = Field(None)
    ease_of_use: Optional[int] = Field(None)
    documentation_quality: Optional[int] = Field(None)
    performance: Optional[int] = Field(None)
    reliability: Optional[int] = Field(None)
    support_quality: Optional[int] = Field(None)
    version_used: Optional[str] = Field(None)
    use_case: Optional[str] = Field(None)
    experience_level: Optional[str] = Field(None)
    helpful_count: int = Field(...)
    reported_count: int = Field(...)
    is_verified_purchase: bool = Field(...)
    is_featured: bool = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ComponentVersions(BaseModel):
    id: uuid.UUID = Field(...)
    component_id: uuid.UUID = Field(...)
    version: str = Field(...)
    is_latest: bool = Field(...)
    is_stable: bool = Field(...)
    changelog: Optional[str] = Field(None)
    breaking_changes: Optional[str] = Field(None)
    migration_guide: Optional[str] = Field(None)
    component_data: dict = Field(...)
    file_size: Optional[int] = Field(None)
    min_platform_version: Optional[str] = Field(None)
    max_platform_version: Optional[str] = Field(None)
    dependencies: Optional[dict] = Field(None)
    download_count: int = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    deprecated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ContactEvents(BaseModel):
    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    event_type: str = Field(...)
    event_data: Optional[dict] = Field(None)
    occurred_at: Optional[datetime.datetime] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ContactInteractions(BaseModel):
    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    user_id: Optional[uuid.UUID] = Field(None)
    type: str = Field(...)
    channel: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    direction: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    scheduled_at: Optional[datetime.datetime] = Field(None)
    completed_at: Optional[datetime.datetime] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ContactListMemberships(BaseModel):
    id: uuid.UUID = Field(...)
    list_id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    added_by: Optional[uuid.UUID] = Field(None)
    added_at: Optional[datetime.datetime] = Field(None)
    status: Optional[str] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class ContactNotes(BaseModel):
    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    content: str = Field(...)
    type: Optional[str] = Field(None)
    is_private: Optional[bool] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ConversionJourneys(BaseModel):
    id: uuid.UUID = Field(...)
    contact_id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    journey_name: Optional[str] = Field(None)
    current_stage: Optional[str] = Field(None)
    stages_completed: Optional[dict] = Field(None)
    conversion_probability: Optional[float] = Field(None)
    last_interaction_at: Optional[datetime.datetime] = Field(None)
    converted_at: Optional[datetime.datetime] = Field(None)
    conversion_value: Optional[float] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class CustomReports(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    query_config: dict = Field(...)
    visualization_config: Optional[dict] = Field(None)
    filters: Optional[dict] = Field(None)
    is_scheduled: bool = Field(...)
    schedule_config: Optional[dict] = Field(None)
    last_run_at: Optional[datetime.datetime] = Field(None)
    next_run_at: Optional[datetime.datetime] = Field(None)
    is_public: bool = Field(...)
    shared_with: Optional[dict] = Field(None)
    cached_data: Optional[dict] = Field(None)
    cache_expires_at: Optional[datetime.datetime] = Field(None)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class LlmsConversations(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    agent_id: Optional[uuid.UUID] = Field(None)
    workspace_id: Optional[uuid.UUID] = Field(None)
    title: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    message_count: Optional[int] = Field(None)
    total_tokens_used: Optional[int] = Field(None)
    context: Optional[dict] = Field(None)
    settings: Optional[dict] = Field(None)
    last_message_at: Optional[datetime.datetime] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: uuid.UUID = Field(...)


class Nodes(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: str = Field(...)
    description: Optional[str] = Field(None)
    version: str = Field(...)
    definition: dict = Field(...)
    is_public: bool = Field(...)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    code_template: str = Field(...)
    input_schema: dict = Field(...)
    output_schema: dict = Field(...)
    parameters_schema: Optional[dict] = Field(None)
    icon: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    documentation: Optional[str] = Field(None)
    examples: Optional[dict] = Field(None)
    downloads_count: Optional[int] = Field(None)
    usage_count: Optional[int] = Field(None)
    rating_average: Optional[int] = Field(None)
    rating_count: Optional[int] = Field(None)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    status: Optional[str] = Field(None)
    timeout_seconds: Optional[int] = Field(None)
    retry_count: Optional[int] = Field(None)


class PaymentMethods(BaseModel):
    id: uuid.UUID = Field(...)
    customer_id: uuid.UUID = Field(...)
    external_method_id: str = Field(...)
    type: str = Field(...)
    last4: Optional[str] = Field(None)
    brand: Optional[str] = Field(None)
    exp_month: Optional[int] = Field(None)
    exp_year: Optional[int] = Field(None)
    is_default: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class Workflows(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    definition: dict = Field(...)
    is_active: bool = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    is_public: Optional[bool] = Field(None)
    category: Optional[str] = Field(None)
    tags: Optional[dict] = Field(None)
    version: Optional[str] = Field(None)
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    downloads_count: Optional[int] = Field(None, description="Contagem de downloads")
    rating_average: Optional[int] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Contagem de avaliações")
    execution_count: Optional[int] = Field(None, description="Contagem de execuções")
    last_executed_at: Optional[datetime.datetime] = Field(
        None, description="Última execução"
    )
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Data de atualização")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, description="Prioridade")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Número de tentativas")


class WorkspaceActivities(BaseModel):
    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    action: str = Field(...)
    resource_type: str = Field(...)
    resource_id: Optional[str] = Field(None)
    description: str = Field(...)
    metadata: Optional[dict] = Field(None)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    meta_data: Optional[dict] = Field(None)


class WorkspaceFeatures(BaseModel):
    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    feature_id: uuid.UUID = Field(...)
    is_enabled: Optional[bool] = Field(None)
    config: Optional[dict] = Field(None)
    usage_count: Optional[int] = Field(None)
    limit_value: Optional[int] = Field(None)
    expires_at: Optional[datetime.datetime] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class WorkspaceInvitations(BaseModel):
    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    inviter_id: uuid.UUID = Field(...)
    invited_user_id: Optional[uuid.UUID] = Field(None)
    email: str = Field(...)
    message: Optional[str] = Field(None)
    token: str = Field(...)
    status: str = Field(...)
    created_at: datetime.datetime = Field(...)
    expires_at: datetime.datetime = Field(...)
    responded_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class WorkspaceMembers(BaseModel):
    id: int = Field(...)
    workspace_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    custom_permissions: Optional[dict] = Field(None)
    status: str = Field(...)
    is_favorite: bool = Field(...)
    notification_preferences: Optional[dict] = Field(None)
    last_seen_at: datetime.datetime = Field(...)
    joined_at: datetime.datetime = Field(...)
    left_at: Optional[datetime.datetime] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: uuid.UUID = Field(...)
    role: str = Field(...)


class LlmsConversationsTurns(BaseModel):
    id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    first_used_at: datetime.datetime = Field(...)
    last_used_at: datetime.datetime = Field(...)
    message_count: Optional[int] = Field(None)
    total_input_tokens: Optional[int] = Field(None)
    total_output_tokens: Optional[int] = Field(None)
    total_cost_usd: Optional[float] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class LlmsMessages(BaseModel):
    id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    role: str = Field(...)
    content: str = Field(...)
    attachments: Optional[dict] = Field(None)
    model_used: Optional[str] = Field(None)
    model_provider: Optional[str] = Field(None)
    tokens_used: Optional[int] = Field(None)
    processing_time_ms: Optional[int] = Field(None)
    temperature: Optional[float] = Field(None)
    max_tokens: Optional[int] = Field(None)
    status: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class NodeRatings(BaseModel):
    id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ReportExecutions(BaseModel):
    id: uuid.UUID = Field(...)
    report_id: uuid.UUID = Field(...)
    user_id: Optional[uuid.UUID] = Field(None)
    execution_type: str = Field(...)
    parameters: Optional[dict] = Field(None)
    status: str = Field(...)
    result_data: Optional[dict] = Field(None)
    error_message: Optional[str] = Field(None)
    execution_time_ms: Optional[int] = Field(None)
    rows_processed: Optional[int] = Field(None)
    data_size_bytes: Optional[int] = Field(None)
    started_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Subscriptions(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    plan_id: uuid.UUID = Field(...)
    provider_id: Optional[uuid.UUID] = Field(None)
    external_subscription_id: Optional[str] = Field(None)
    status: str = Field(...)
    current_period_start: Optional[datetime.datetime] = Field(None)
    current_period_end: Optional[datetime.datetime] = Field(None)
    trial_start: Optional[datetime.datetime] = Field(None)
    trial_end: Optional[datetime.datetime] = Field(None)
    cancel_at_period_end: Optional[bool] = Field(None)
    canceled_at: Optional[datetime.datetime] = Field(None)
    ended_at: Optional[datetime.datetime] = Field(None)
    payment_method_id: Optional[uuid.UUID] = Field(None)
    coupon_id: Optional[uuid.UUID] = Field(None)
    quantity: Optional[int] = Field(None)
    discount_amount: Optional[float] = Field(None)
    tax_percent: Optional[float] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class WorkflowExecutions(BaseModel):
    id: uuid.UUID = Field(...)
    execution_id: Optional[str] = Field(None)
    workflow_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    status: str = Field(...)
    priority: Optional[int] = Field(None)
    input_data: Optional[dict] = Field(None)
    output_data: Optional[dict] = Field(None)
    context_data: Optional[dict] = Field(None)
    variables: Optional[dict] = Field(None)
    total_nodes: Optional[int] = Field(None)
    completed_nodes: Optional[int] = Field(None)
    failed_nodes: Optional[int] = Field(None)
    progress_percentage: Optional[int] = Field(None)
    started_at: datetime.datetime = Field(...)
    completed_at: Optional[datetime.datetime] = Field(None)
    timeout_at: Optional[datetime.datetime] = Field(None)
    estimated_duration: Optional[int] = Field(None)
    actual_duration: Optional[int] = Field(None)
    execution_log: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    error_details: Optional[dict] = Field(None)
    debug_info: Optional[dict] = Field(None)
    retry_count: Optional[int] = Field(None)
    max_retries: Optional[int] = Field(None)
    auto_retry: Optional[bool] = Field(None)
    notify_on_completion: Optional[bool] = Field(None)
    notify_on_failure: Optional[bool] = Field(None)
    tags: Optional[dict] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class WorkflowNodes(BaseModel):
    id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    instance_name: Optional[str] = Field(None)
    position_x: int = Field(...)
    position_y: int = Field(...)
    configuration: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class WorkflowTemplates(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    category: str = Field(...)
    tags: Optional[dict] = Field(None)
    workflow_definition: dict = Field(...)
    preview_image: Optional[str] = Field(None)
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
    short_description: Optional[str] = Field(None)
    original_workflow_id: Optional[uuid.UUID] = Field(None)
    status: Optional[str] = Field(None)
    is_verified: Optional[bool] = Field(None)
    license_type: Optional[str] = Field(None)
    workflow_data: dict = Field(...)
    nodes_data: dict = Field(...)
    connections_data: Optional[dict] = Field(None)
    required_variables: Optional[dict] = Field(None)
    optional_variables: Optional[dict] = Field(None)
    default_config: Optional[dict] = Field(None)
    compatibility_version: Optional[str] = Field(None)
    estimated_duration: Optional[int] = Field(None)
    complexity_level: Optional[int] = Field(None)
    download_count: Optional[int] = Field(None)
    usage_count: Optional[int] = Field(None)
    view_count: Optional[int] = Field(None)
    keywords: Optional[dict] = Field(None)
    use_cases: Optional[dict] = Field(None)
    industries: Optional[dict] = Field(None)
    thumbnail_url: Optional[str] = Field(None)
    preview_images: Optional[dict] = Field(None)
    demo_video_url: Optional[str] = Field(None)
    documentation: Optional[str] = Field(None)
    setup_instructions: Optional[str] = Field(None)
    changelog: Optional[dict] = Field(None)
    support_email: Optional[str] = Field(None)
    repository_url: Optional[str] = Field(None)
    documentation_url: Optional[str] = Field(None)
    published_at: Optional[datetime.datetime] = Field(None)
    last_used_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class WorkspaceProjects(BaseModel):
    id: uuid.UUID = Field(...)
    workspace_id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    allow_concurrent_editing: bool = Field(...)
    auto_save_interval: Optional[int] = Field(None)
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
    tenant_id: uuid.UUID = Field(...)


class AnalyticsEvents(BaseModel):
    id: uuid.UUID = Field(...)
    event_id: str = Field(...)
    event_type: str = Field(...)
    category: str = Field(...)
    action: str = Field(...)
    label: Optional[str] = Field(None)
    user_id: Optional[uuid.UUID] = Field(None)
    session_id: Optional[str] = Field(None)
    anonymous_id: Optional[str] = Field(None)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    referrer: Optional[str] = Field(None)
    page_url: Optional[str] = Field(None)
    properties: dict = Field(...)
    value: Optional[float] = Field(None)
    workspace_id: Optional[uuid.UUID] = Field(None)
    project_id: uuid.UUID = Field(...)
    workflow_id: Optional[uuid.UUID] = Field(None)
    country: Optional[str] = Field(None)
    region: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    timezone: Optional[str] = Field(None)
    device_type: Optional[str] = Field(None)
    os: Optional[str] = Field(None)
    browser: Optional[str] = Field(None)
    screen_resolution: Optional[str] = Field(None)
    timestamp: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class Invoices(BaseModel):
    id: uuid.UUID = Field(...)
    tenant_id: uuid.UUID = Field(...)
    subscription_id: Optional[uuid.UUID] = Field(None)
    invoice_number: str = Field(...)
    status: str = Field(...)
    currency: str = Field(...)
    subtotal: float = Field(...)
    tax_amount: float = Field(...)
    discount_amount: float = Field(...)
    total_amount: float = Field(...)
    due_date: Optional[str] = Field(None)
    paid_at: Optional[datetime.datetime] = Field(None)
    items: Optional[dict] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class LlmsUsageLogs(BaseModel):
    id: uuid.UUID = Field(...)
    message_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    conversation_id: uuid.UUID = Field(...)
    llm_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    input_tokens: int = Field(...)
    output_tokens: int = Field(...)
    total_tokens: int = Field(...)
    cost_usd: float = Field(...)
    latency_ms: Optional[int] = Field(None)
    api_status_code: Optional[int] = Field(None)
    api_request_payload: Optional[dict] = Field(None)
    api_response_metadata: Optional[dict] = Field(None)
    user_api_key_used: Optional[bool] = Field(None)
    model_settings: Optional[dict] = Field(None)
    error_message: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class MessageFeedbacks(BaseModel):
    id: uuid.UUID = Field(...)
    message_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating_type: str = Field(...)
    rating_value: Optional[int] = Field(None)
    feedback_text: Optional[str] = Field(None)
    feedback_category: Optional[str] = Field(None)
    improvement_suggestions: Optional[str] = Field(None)
    is_public: Optional[bool] = Field(None)
    feedback_metadata: Optional[dict] = Field(None)
    created_at: datetime.datetime = Field(...)
    updated_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)


class NodeExecutions(BaseModel):
    id: int = Field(...)
    execution_id: Optional[str] = Field(None)
    workflow_execution_id: uuid.UUID = Field(...)
    node_id: uuid.UUID = Field(...)
    node_key: str = Field(...)
    node_type: str = Field(...)
    node_name: Optional[str] = Field(None)
    execution_order: int = Field(...)
    input_data: Optional[dict] = Field(None)
    output_data: Optional[dict] = Field(None)
    config_data: Optional[dict] = Field(None)
    started_at: Optional[datetime.datetime] = Field(None)
    completed_at: Optional[datetime.datetime] = Field(None)
    timeout_at: Optional[datetime.datetime] = Field(None)
    duration_ms: Optional[int] = Field(None)
    execution_log: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    error_details: Optional[dict] = Field(None)
    debug_info: Optional[dict] = Field(None)
    retry_count: Optional[int] = Field(None)
    max_retries: Optional[int] = Field(None)
    retry_delay: Optional[int] = Field(None)
    dependencies: Optional[dict] = Field(None)
    dependents: Optional[dict] = Field(None)
    metadata: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class ProjectVersions(BaseModel):
    id: uuid.UUID = Field(...)
    project_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    version_number: int = Field(...)
    version_name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    workflow_data: dict = Field(...)
    changes_summary: Optional[dict] = Field(None)
    file_size: Optional[int] = Field(None)
    checksum: Optional[str] = Field(None)
    is_major: bool = Field(...)
    is_auto_save: bool = Field(...)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class TemplateDownloads(BaseModel):
    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    download_type: Optional[str] = Field(None)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    template_version: Optional[str] = Field(None)
    downloaded_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class TemplateFavorites(BaseModel):
    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    notes: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class TemplateReviews(BaseModel):
    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    rating: int = Field(...)
    title: Optional[str] = Field(None)
    comment: Optional[str] = Field(None)
    ease_of_use: Optional[int] = Field(None)
    documentation_quality: Optional[int] = Field(None)
    performance: Optional[int] = Field(None)
    value_for_money: Optional[int] = Field(None)
    is_verified_purchase: Optional[bool] = Field(None)
    is_helpful_count: Optional[int] = Field(None)
    is_reported: Optional[bool] = Field(None)
    version_reviewed: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class TemplateUsage(BaseModel):
    id: int = Field(...)
    template_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workflow_id: Optional[uuid.UUID] = Field(None)
    usage_type: str = Field(...)
    success: Optional[bool] = Field(None)
    template_version: Optional[str] = Field(None)
    modifications_made: Optional[dict] = Field(None)
    execution_time: Optional[int] = Field(None)
    ip_address: Optional[str] = Field(None)
    user_agent: Optional[str] = Field(None)
    used_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class WorkflowConnections(BaseModel):
    id: uuid.UUID = Field(...)
    workflow_id: uuid.UUID = Field(...)
    source_node_id: uuid.UUID = Field(...)
    target_node_id: uuid.UUID = Field(...)
    source_port: Optional[str] = Field(None)
    target_port: Optional[str] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


class WorkflowExecutionQueue(BaseModel):
    id: int = Field(...)
    queue_id: Optional[str] = Field(None)
    workflow_execution_id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    priority: Optional[int] = Field(None)
    scheduled_at: Optional[datetime.datetime] = Field(None)
    started_at: Optional[datetime.datetime] = Field(None)
    completed_at: Optional[datetime.datetime] = Field(None)
    status: Optional[str] = Field(None)
    worker_id: Optional[str] = Field(None)
    max_execution_time: Optional[int] = Field(None)
    retry_count: Optional[int] = Field(None)
    max_retries: Optional[int] = Field(None)
    meta_data: Optional[dict] = Field(None)
    created_at: Optional[datetime.datetime] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)
    tenant_id: Optional[uuid.UUID] = Field(None)


class BillingEvents(BaseModel):
    id: uuid.UUID = Field(...)
    user_id: uuid.UUID = Field(...)
    workspace_id: Optional[uuid.UUID] = Field(None)
    event_type: str = Field(...)
    amount_usd: float = Field(...)
    description: Optional[str] = Field(None)
    related_usage_log_id: Optional[uuid.UUID] = Field(None)
    related_message_id: Optional[uuid.UUID] = Field(None)
    invoice_id: Optional[str] = Field(None)
    payment_provider: Optional[str] = Field(None)
    payment_transaction_id: Optional[str] = Field(None)
    billing_metadata: Optional[dict] = Field(None)
    status: Optional[str] = Field(None)
    processed_at: Optional[datetime.datetime] = Field(None)
    created_at: datetime.datetime = Field(...)
    tenant_id: Optional[uuid.UUID] = Field(None)
    updated_at: Optional[datetime.datetime] = Field(None)


# ===== TENANT API SCHEMAS =====
# Added to provide request/response models for tenant endpoints


class TenantStatus(str, Enum):
    """Status do tenant - deve corresponder aos valores no banco"""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class TenantTheme(str, Enum):
    """Temas disponíveis para interface"""

    LIGHT = "light"
    DARK = "dark"


class TenantType(str, Enum):
    """Tipo do tenant (campo legacy, mantido para compatibilidade)"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


# ===== SCHEMAS DE CRIAÇÃO =====


class TenantCreate(BaseModel):
    """Schema para criação de novo tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Campos obrigatórios
    name: str = Field(..., min_length=1, max_length=255, description="Nome do tenant")
    slug: str = Field(
        ..., min_length=1, max_length=120, description="Slug único do tenant"
    )
    plan_id: uuid.UUID = Field(..., description="ID do plano selecionado")

    # Campos opcionais do banco
    domain: Optional[str] = Field(
        None, max_length=255, description="Domínio personalizado"
    )
    status: TenantStatus = Field(
        TenantStatus.ACTIVE, description="Status inicial do tenant"
    )
    theme: Optional[TenantTheme] = Field(
        TenantTheme.LIGHT, description="Tema da interface"
    )
    default_language: Optional[str] = Field(
        "en", min_length=2, max_length=10, description="Idioma padrão"
    )
    timezone: Optional[str] = Field("UTC", max_length=50, description="Timezone padrão")

    # Configurações de segurança
    mfa_required: Optional[bool] = Field(False, description="MFA obrigatório")
    session_timeout: Optional[int] = Field(
        3600, ge=300, le=86400, description="Timeout da sessão em segundos"
    )
    ip_whitelist: Optional[List[str]] = Field(
        default_factory=list, description="Lista de IPs permitidos"
    )

    # Limites (opcional, se não definido usa os do plano)
    max_storage_mb: Optional[int] = Field(
        None, ge=0, description="Limite de storage em MB"
    )
    max_workspaces: Optional[int] = Field(
        None, ge=1, description="Máximo de workspaces"
    )
    max_api_calls_per_day: Optional[int] = Field(
        None, ge=0, description="Limite de chamadas API por dia"
    )
    max_members_per_workspace: Optional[int] = Field(
        None, ge=1, description="Máximo de membros por workspace"
    )

    # Features habilitadas
    enabled_features: Optional[List[str]] = Field(
        default_factory=list, description="Features habilitadas"
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validar formato do slug"""
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug deve conter apenas letras minúsculas, números e hífens"
            )
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug não pode começar ou terminar com hífen")
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        """Validar formato do domínio"""
        if v is None:
            return v
        import re

        domain_pattern = (
            r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Formato de domínio inválido")
        return v.lower()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validar timezone"""
        if v is None:
            return v
        try:
            import pytz

            pytz.timezone(v)
        except Exception:
            raise ValueError(f"Timezone inválida: {v}")
        return v

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validar lista de IPs"""
        if not v:
            return v
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v

    @field_validator("enabled_features")
    @classmethod
    def validate_enabled_features(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validar features habilitadas"""
        if not v:
            return v

        valid_features = [
            "analytics",
            "api_access",
            "advanced_workflows",
            "priority_support",
            "custom_integrations",
            "sso",
            "audit_logs",
            "data_export",
            "white_labeling",
            "custom_domains",
            "unlimited_storage",
        ]

        for feature in v:
            if feature not in valid_features:
                raise ValueError(
                    f"Feature inválida: {feature}. Features válidas: {valid_features}"
                )

        return list(set(v))  # Remove duplicatas


# ===== SCHEMAS DE ATUALIZAÇÃO =====


class TenantUpdate(BaseModel):
    """Schema para atualização de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Campos básicos
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    status: Optional[TenantStatus] = None
    theme: Optional[TenantTheme] = None
    default_language: Optional[str] = Field(None, min_length=2, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)

    # Configurações de segurança
    mfa_required: Optional[bool] = None
    session_timeout: Optional[int] = Field(None, ge=300, le=86400)
    ip_whitelist: Optional[List[str]] = None

    # Plano e limites
    plan_id: Optional[uuid.UUID] = None
    max_storage_mb: Optional[int] = Field(None, ge=0)
    max_workspaces: Optional[int] = Field(None, ge=1)
    max_api_calls_per_day: Optional[int] = Field(None, ge=0)
    max_members_per_workspace: Optional[int] = Field(None, ge=1)

    # Features
    enabled_features: Optional[List[str]] = None

    # Aplicar as mesmas validações do TenantCreate
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re

        domain_pattern = (
            r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Formato de domínio inválido")
        return v.lower()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            import pytz

            pytz.timezone(v)
        except Exception:
            raise ValueError(f"Timezone inválida: {v}")
        return v

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v

    @field_validator("enabled_features")
    @classmethod
    def validate_enabled_features(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if not v:
            return v

        valid_features = [
            "analytics",
            "api_access",
            "advanced_workflows",
            "priority_support",
            "custom_integrations",
            "sso",
            "audit_logs",
            "data_export",
            "white_labeling",
            "custom_domains",
            "unlimited_storage",
        ]

        for feature in v:
            if feature not in valid_features:
                raise ValueError(
                    f"Feature inválida: {feature}. Features válidas: {valid_features}"
                )

        return list(set(v))


# ===== SCHEMAS DE RESPOSTA =====


class TenantResponse(BaseModel):
    """Schema completo de resposta do tenant com todos os campos"""

    model_config = ConfigDict(from_attributes=True)

    # Campos do banco de dados
    id: uuid.UUID
    name: str
    slug: str
    domain: Optional[str] = None
    status: str
    theme: Optional[str] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    mfa_required: Optional[bool] = None
    session_timeout: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    plan_id: Optional[uuid.UUID] = None
    max_storage_mb: Optional[int] = None
    max_workspaces: Optional[int] = None
    max_api_calls_per_day: Optional[int] = None
    max_members_per_workspace: Optional[int] = None
    enabled_features: Optional[List[str]] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class TenantPublic(BaseModel):
    """Schema público do tenant (informações não sensíveis)"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    domain: Optional[str] = None
    theme: Optional[str] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime.datetime


class TenantSummary(BaseModel):
    """Schema resumido do tenant para listagens"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str
    plan_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime


class TenantStats(BaseModel):
    """Schema para estatísticas do tenant"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: uuid.UUID
    tenant_name: str
    workspace_count: int = 0
    user_count: int = 0
    conversation_count: int = 0
    message_count: int = 0
    status: str
    storage_used_gb: int = 0
    max_storage_gb: int = 10
    storage_usage_percent: float = 0.0
    last_activity_at: Optional[datetime.datetime] = None
    subscription_status: str = "trial"
    trial_ends_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    # Limites atuais baseados no plano
    api_calls_today: int = 0
    api_calls_this_month: int = 0
    max_api_calls_per_day: Optional[int] = None

    # Usage insights
    features_usage: Dict[str, int] = Field(default_factory=dict)
    most_active_workspace: Optional[Dict[str, Any]] = None


class TenantSecuritySettings(BaseModel):
    """Schema para configurações de segurança"""

    model_config = ConfigDict(str_strip_whitespace=True)

    mfa_required: bool = False
    session_timeout: int = Field(3600, ge=300, le=86400)
    ip_whitelist: List[str] = Field(default_factory=list)
    password_policy: Dict[str, Any] = Field(default_factory=dict)
    login_attempts_limit: int = Field(5, ge=3, le=10)

    @field_validator("ip_whitelist")
    @classmethod
    def validate_ip_whitelist(cls, v: List[str]) -> List[str]:
        if not v:
            return v
        import ipaddress

        for ip in v:
            try:
                ipaddress.ip_network(ip, strict=False)
            except ValueError:
                raise ValueError(f"IP ou CIDR inválido: {ip}")
        return v


class TenantNotificationSettings(BaseModel):
    """Schema para configurações de notificação"""

    model_config = ConfigDict(from_attributes=True)

    email_notifications: bool = True
    push_notifications: bool = True
    webhook_url: Optional[str] = None
    notification_types: List[str] = Field(default_factory=list)
    quiet_hours_start: Optional[str] = None  # formato HH:MM
    quiet_hours_end: Optional[str] = None  # formato HH:MM


class TenantWithPlan(TenantResponse):
    """Tenant com informações detalhadas do plano"""

    plan: Dict[str, Any]  # Detalhes completos do plano


class TenantWithWorkspaces(TenantResponse):
    """Tenant com lista de workspaces"""

    workspaces: List[Dict[str, Any]] = Field(default_factory=list)


class TenantWithUsers(TenantResponse):
    """Tenant com lista de usuários"""

    users: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================
# USER API SCHEMAS - Imported from legacy/user.py
# =============================================


class UserStatus(str, Enum):
    """Status do usuário - deve corresponder aos valores no banco"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class UserRole(str, Enum):
    """Roles baseados no campo is_superuser"""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# ===== SCHEMAS DE CRIAÇÃO E ATUALIZAÇÃO =====


class UserCreate(BaseModel):
    """Schema para criação de usuários (admin)"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Campos obrigatórios
    email: EmailStr = Field(..., description="Email único do usuário")
    username: str = Field(
        ..., min_length=3, max_length=255, description="Nome de usuário único"
    )
    full_name: str = Field(
        ..., min_length=2, max_length=200, description="Nome completo"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Senha (opcional, será gerada automaticamente se não fornecida)",
    )

    # Campos opcionais do banco
    is_active: bool = Field(True, description="Se o usuário está ativo")
    is_verified: bool = Field(False, description="Se o email foi verificado")
    is_superuser: bool = Field(False, description="Se é administrador")
    status: UserStatus = Field(UserStatus.ACTIVE, description="Status do usuário")
    bio: Optional[str] = Field(None, max_length=1000, description="Biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem de perfil"
    )
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


class UserUpdate(BaseModel):
    """Schema para atualização de usuários"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Campos opcionais para atualização
    email: Optional[EmailStr] = Field(None, description="Email único do usuário")
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Nome de usuário único"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Nome completo"
    )
    is_active: Optional[bool] = Field(None, description="Se o usuário está ativo")
    is_verified: Optional[bool] = Field(None, description="Se o email foi verificado")
    is_superuser: Optional[bool] = Field(None, description="Se é administrador")
    status: Optional[UserStatus] = Field(None, description="Status do usuário")
    bio: Optional[str] = Field(None, max_length=1000, description="Biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="URL da imagem de perfil"
    )


# ===== WORKSPACE SCHEMAS (ALINHADO COM O BANCO REAL) =====


class WorkspaceCreate(BaseModel):
    """Schema para criação de workspace - ALINHADO COM BANCO"""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Nome do workspace"
    )
    slug: str = Field(..., min_length=1, max_length=120, description="Slug único")
    description: Optional[str] = Field(None, description="Descrição")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    color: Optional[str] = Field(None, description="Cor hex")
    is_public: bool = Field(False, description="Workspace público")
    is_template: bool = Field(False, description="É template")
    allow_guest_access: bool = Field(False, description="Permite acesso de convidados")
    require_approval: bool = Field(True, description="Requer aprovação")
    max_members: Optional[int] = Field(None, description="Máximo de membros")
    max_projects: Optional[int] = Field(None, description="Máximo de projetos")
    max_storage_mb: Optional[int] = Field(None, description="Máximo de storage em MB")
    enable_real_time_editing: bool = Field(True, description="Edição em tempo real")
    enable_comments: bool = Field(True, description="Comentários habilitados")
    enable_chat: bool = Field(True, description="Chat habilitado")
    enable_video_calls: bool = Field(False, description="Video calls habilitadas")
    email_notifications: Optional[bool] = Field(
        True, description="Notificações por email"
    )
    push_notifications: Optional[bool] = Field(False, description="Notificações push")
    type: str = Field("individual", description="Tipo do workspace")


class WorkspaceUpdate(BaseModel):
    """Schema para atualização de workspace - ALINHADO COM BANCO"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome")
    description: Optional[str] = Field(None, description="Descrição")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    color: Optional[str] = Field(None, description="Cor hex")
    is_public: Optional[bool] = Field(None, description="Workspace público")
    is_template: Optional[bool] = Field(None, description="É template")
    allow_guest_access: Optional[bool] = Field(
        None, description="Permite acesso de convidados"
    )
    require_approval: Optional[bool] = Field(None, description="Requer aprovação")
    max_members: Optional[int] = Field(None, description="Máximo de membros")
    max_projects: Optional[int] = Field(None, description="Máximo de projetos")
    max_storage_mb: Optional[int] = Field(None, description="Máximo de storage")
    enable_real_time_editing: Optional[bool] = Field(
        None, description="Edição em tempo real"
    )
    enable_comments: Optional[bool] = Field(None, description="Comentários")
    enable_chat: Optional[bool] = Field(None, description="Chat")
    enable_video_calls: Optional[bool] = Field(None, description="Video calls")
    email_notifications: Optional[bool] = Field(None, description="Notificações email")
    push_notifications: Optional[bool] = Field(None, description="Notificações push")


class WorkspaceResponse(BaseModel):
    """Schema de resposta para workspace - ALINHADO COM BANCO"""

    id: uuid.UUID = Field(..., description="ID do workspace")
    name: str = Field(..., description="Nome do workspace")
    slug: str = Field(..., description="Slug único")
    description: Optional[str] = Field(None, description="Descrição")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    color: Optional[str] = Field(None, description="Cor hex")
    owner_id: uuid.UUID = Field(..., description="ID do proprietário")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    is_public: bool = Field(..., description="Workspace público")
    is_template: bool = Field(..., description="É template")
    allow_guest_access: bool = Field(..., description="Permite acesso de convidados")
    require_approval: bool = Field(..., description="Requer aprovação")
    max_members: Optional[int] = Field(None, description="Máximo de membros")
    max_projects: Optional[int] = Field(None, description="Máximo de projetos")
    max_storage_mb: Optional[int] = Field(None, description="Máximo de storage em MB")
    enable_real_time_editing: bool = Field(..., description="Edição em tempo real")
    enable_comments: bool = Field(..., description="Comentários habilitados")
    enable_chat: bool = Field(..., description="Chat habilitado")
    enable_video_calls: bool = Field(..., description="Video calls habilitadas")
    member_count: int = Field(..., description="Número de membros")
    project_count: int = Field(..., description="Número de projetos")
    activity_count: int = Field(..., description="Número de atividades")
    storage_used_mb: float = Field(..., description="Storage usado em MB")
    status: str = Field(..., description="Status do workspace")
    type: str = Field(..., description="Tipo do workspace")
    email_notifications: Optional[bool] = Field(
        None, description="Notificações por email"
    )
    push_notifications: Optional[bool] = Field(None, description="Notificações push")
    api_calls_today: Optional[int] = Field(None, description="Calls API hoje")
    api_calls_this_month: Optional[int] = Field(None, description="Calls API este mês")
    last_api_reset_daily: Optional[datetime.datetime] = Field(
        None, description="Último reset diário"
    )
    last_api_reset_monthly: Optional[datetime.datetime] = Field(
        None, description="Último reset mensal"
    )
    feature_usage_count: Optional[dict] = Field(None, description="Contadores de uso")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Data de atualização")
    last_activity_at: Optional[datetime.datetime] = Field(
        None, description="Última atividade"
    )


# ===== AGENT SCHEMAS (ALINHADO COM O BANCO REAL) =====


class AgentCreate(BaseModel):
    """Schema para criação de agente - ALINHADO COM BANCO"""

    name: str = Field(..., min_length=1, max_length=255, description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição")
    is_active: bool = Field(True, description="Agente ativo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    status: Optional[str] = Field("active", description="Status do agente")
    priority: Optional[int] = Field(1, description="Prioridade")
    version: Optional[str] = Field("1.0.0", description="Versão")
    environment: Optional[str] = Field("development", description="Ambiente")


class AgentUpdate(BaseModel):
    """Schema para atualização de agente - ALINHADO COM BANCO"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Nome do agente"
    )
    description: Optional[str] = Field(None, description="Descrição")
    is_active: Optional[bool] = Field(None, description="Agente ativo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    status: Optional[str] = Field(None, description="Status do agente")
    priority: Optional[int] = Field(None, description="Prioridade")
    version: Optional[str] = Field(None, description="Versão")
    environment: Optional[str] = Field(None, description="Ambiente")


# ===== FILE SCHEMAS (ALINHADO COM O BANCO REAL) =====


class FileCreate(BaseModel):
    """Schema para criação de arquivo - ALINHADO COM BANCO"""

    filename: str = Field(..., description="Nome do arquivo")
    original_name: str = Field(..., description="Nome original")
    file_path: str = Field(..., description="Caminho do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo")
    mime_type: str = Field(..., description="Tipo MIME")
    category: str = Field(..., description="Categoria")
    is_public: bool = Field(False, description="Arquivo público")
    tags: Optional[dict] = Field(None, description="Tags do arquivo")
    description: Optional[str] = Field(None, description="Descrição")
    status: Optional[str] = Field("active", description="Status")
    scan_status: Optional[str] = Field("pending", description="Status do scan")


class FileUpdate(BaseModel):
    """Schema para atualização de arquivo - ALINHADO COM BANCO"""

    filename: Optional[str] = Field(None, description="Nome do arquivo")
    category: Optional[str] = Field(None, description="Categoria")
    is_public: Optional[bool] = Field(None, description="Arquivo público")
    description: Optional[str] = Field(None, description="Descrição")
    tags: Optional[dict] = Field(None, description="Tags do arquivo")
    status: Optional[str] = Field(None, description="Status")
    scan_status: Optional[str] = Field(None, description="Status do scan")


class FileResponse(BaseModel):
    """Schema de resposta para arquivo - ALINHADO COM BANCO"""

    id: uuid.UUID = Field(..., description="ID do arquivo")
    filename: str = Field(..., description="Nome do arquivo")
    original_name: str = Field(..., description="Nome original")
    file_path: str = Field(..., description="Caminho do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo")
    mime_type: str = Field(..., description="Tipo MIME")
    category: str = Field(..., description="Categoria")
    is_public: bool = Field(..., description="Arquivo público")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    tags: Optional[dict] = Field(None, description="Tags do arquivo")
    description: Optional[str] = Field(None, description="Descrição")
    status: Optional[str] = Field(None, description="Status")
    scan_status: Optional[str] = Field(None, description="Status do scan")
    access_count: Optional[int] = Field(None, description="Contagem de acessos")
    last_accessed_at: Optional[datetime.datetime] = Field(
        None, description="Último acesso"
    )
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Data de atualização")


# ===== NODE SCHEMAS (ALINHADO COM O BANCO REAL) =====


class NodeCreate(BaseModel):
    """Schema para criação de nó - ALINHADO COM BANCO"""

    name: str = Field(..., description="Nome do nó")
    category: str = Field(..., description="Categoria")
    description: Optional[str] = Field(None, description="Descrição")
    version: Optional[str] = Field("1.0.0", description="Versão")
    definition: dict = Field(..., description="Definição do nó")
    is_public: bool = Field(False, description="Nó público")
    code_template: str = Field(..., description="Template de código")
    input_schema: dict = Field(..., description="Schema de entrada")
    output_schema: dict = Field(..., description="Schema de saída")
    parameters_schema: Optional[dict] = Field(None, description="Schema de parâmetros")
    icon: Optional[str] = Field(None, description="Ícone")
    color: Optional[str] = Field(None, description="Cor")
    documentation: Optional[str] = Field(None, description="Documentação")
    examples: Optional[dict] = Field(None, description="Exemplos")
    status: Optional[str] = Field("active", description="Status")
    timeout_seconds: Optional[int] = Field(300, description="Timeout em segundos")
    retry_count: Optional[int] = Field(3, description="Número de tentativas")


class NodeUpdate(BaseModel):
    """Schema para atualização de nó - ALINHADO COM BANCO"""

    name: Optional[str] = Field(None, description="Nome do nó")
    category: Optional[str] = Field(None, description="Categoria")
    description: Optional[str] = Field(None, description="Descrição")
    version: Optional[str] = Field(None, description="Versão")
    definition: Optional[dict] = Field(None, description="Definição do nó")
    is_public: Optional[bool] = Field(None, description="Nó público")
    code_template: Optional[str] = Field(None, description="Template de código")
    input_schema: Optional[dict] = Field(None, description="Schema de entrada")
    output_schema: Optional[dict] = Field(None, description="Schema de saída")
    parameters_schema: Optional[dict] = Field(None, description="Schema de parâmetros")
    icon: Optional[str] = Field(None, description="Ícone")
    color: Optional[str] = Field(None, description="Cor")
    documentation: Optional[str] = Field(None, description="Documentação")
    examples: Optional[dict] = Field(None, description="Exemplos")
    status: Optional[str] = Field(None, description="Status")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Número de tentativas")


class NodeResponse(BaseModel):
    """Schema de resposta para nó - ALINHADO COM BANCO"""

    id: uuid.UUID = Field(..., description="ID do nó")
    name: str = Field(..., description="Nome do nó")
    category: str = Field(..., description="Categoria")
    description: Optional[str] = Field(None, description="Descrição")
    version: str = Field(..., description="Versão")
    definition: dict = Field(..., description="Definição do nó")
    is_public: bool = Field(..., description="Nó público")
    code_template: str = Field(..., description="Template de código")
    input_schema: dict = Field(..., description="Schema de entrada")
    output_schema: dict = Field(..., description="Schema de saída")
    parameters_schema: Optional[dict] = Field(None, description="Schema de parâmetros")
    icon: Optional[str] = Field(None, description="Ícone")
    color: Optional[str] = Field(None, description="Cor")
    documentation: Optional[str] = Field(None, description="Documentação")
    examples: Optional[dict] = Field(None, description="Exemplos")
    downloads_count: Optional[int] = Field(None, description="Downloads")
    usage_count: Optional[int] = Field(None, description="Contagem de uso")
    rating_average: Optional[int] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Contagem de avaliações")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    status: Optional[str] = Field(None, description="Status")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Número de tentativas")
    created_at: Optional[datetime.datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Data de atualização"
    )


# ===== WORKFLOW SCHEMAS (ALINHADO COM O BANCO REAL) =====


class WorkflowCreate(BaseModel):
    """Schema para criação de workflow - ALINHADO COM BANCO"""

    name: str = Field(..., description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
    definition: dict = Field(..., description="Definição do workflow em JSON")
    is_active: bool = Field(True, description="Workflow ativo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    is_public: Optional[bool] = Field(False, description="Workflow público")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")
    version: Optional[str] = Field(None, description="Versão")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    status: Optional[str] = Field("draft", description="Status")
    priority: Optional[int] = Field(1, description="Prioridade")
    timeout_seconds: Optional[int] = Field(3600, description="Timeout em segundos")
    retry_count: Optional[int] = Field(3, description="Número de tentativas")


class WorkflowUpdate(BaseModel):
    """Schema para atualização de workflow - ALINHADO COM BANCO"""

    name: Optional[str] = Field(None, description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
    definition: Optional[dict] = Field(None, description="Definição do workflow")
    is_active: Optional[bool] = Field(None, description="Workflow ativo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    is_public: Optional[bool] = Field(None, description="Workflow público")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")
    version: Optional[str] = Field(None, description="Versão")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, description="Prioridade")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Número de tentativas")


class WorkflowResponse(BaseModel):
    """Schema de resposta para workflow - ALINHADO COM BANCO"""

    id: uuid.UUID = Field(..., description="ID do workflow")
    name: str = Field(..., description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
    definition: dict = Field(..., description="Definição do workflow")
    is_active: bool = Field(..., description="Workflow ativo")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    is_public: Optional[bool] = Field(None, description="Workflow público")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")
    version: Optional[str] = Field(None, description="Versão")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    downloads_count: Optional[int] = Field(None, description="Contagem de downloads")
    rating_average: Optional[int] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Contagem de avaliações")
    execution_count: Optional[int] = Field(None, description="Contagem de execuções")
    last_executed_at: Optional[datetime.datetime] = Field(
        None, description="Última execução"
    )
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, description="Prioridade")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Número de tentativas")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Data de atualização")

    # Todos os campos são opcionais para atualização
    email: Optional[EmailStr] = Field(None, description="Novo email")
    username: Optional[str] = Field(
        None, min_length=3, max_length=255, description="Novo username"
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=200, description="Novo nome completo"
    )
    bio: Optional[str] = Field(None, max_length=1000, description="Nova biografia")
    profile_image_url: Optional[str] = Field(
        None, max_length=500, description="Nova URL da imagem"
    )
    is_active: Optional[bool] = Field(None, description="Novo status ativo")
    is_verified: Optional[bool] = Field(None, description="Novo status verificado")
    status: Optional[UserStatus] = Field(None, description="Novo status")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Novos metadados")


class UserResponse(BaseModel):
    """Schema completo de resposta do usuário"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    # Campos principais
    id: uuid.UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")

    # Status e permissões
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    is_superuser: bool = Field(..., description="Se é administrador")
    status: UserStatus = Field(..., description="Status atual")

    # Informações de perfil
    bio: Optional[str] = Field(None, description="Biografia do usuário")
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    user_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )

    # Timestamps
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


# =============================================
# AUTH API SCHEMAS - For authentication endpoints
# =============================================


class Token(BaseModel):
    """Token de autenticação"""

    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Expira em segundos")


class RefreshTokenRequest(BaseModel):
    """Solicitação de refresh token"""

    refresh_token: str = Field(..., description="Token de refresh")


class PasswordResetRequest(BaseModel):
    """Solicitação de reset de senha"""

    email: EmailStr = Field(..., description="Email para reset")


class PasswordResetConfirm(BaseModel):
    """Confirmação de reset de senha"""

    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nova senha")


class EmailVerificationRequest(BaseModel):
    """Solicitação de verificação de email"""

    email: EmailStr = Field(..., description="Email para verificação")


class UserRegister(BaseModel):
    """Registro de usuário"""

    email: EmailStr = Field(..., description="Email único")
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    password: str = Field(..., min_length=8, description="Senha")
    full_name: str = Field(..., min_length=2, description="Nome completo")
    bio: Optional[str] = Field(None, description="Biografia")


# Response models for API endpoints
class UsersResponse(BaseModel):
    """Response model for users endpoint"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")
    is_active: Optional[bool] = Field(None, description="Se o usuário está ativo")
    is_verified: Optional[bool] = Field(None, description="Se o email foi verificado")
    is_superuser: Optional[bool] = Field(None, description="Se é administrador")
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    bio: Optional[str] = Field(None, description="Biografia")
    created_at: Optional[datetime.datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Última atualização"
    )
    status: Optional[str] = Field(None, description="Status do usuário")
    metadata: Optional[dict] = Field(None, description="Metadados")
    last_login_at: Optional[datetime.datetime] = Field(None, description="Último login")
    login_count: Optional[int] = Field(None, description="Contagem de logins")
    failed_login_attempts: Optional[int] = Field(
        None, description="Tentativas de login falhadas"
    )
    account_locked_until: Optional[datetime.datetime] = Field(
        None, description="Conta bloqueada até"
    )


class AgentsResponse(BaseModel):
    """Response model for agents endpoint"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do agente")
    name: str = Field(..., description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição")
    is_active: bool = Field(..., description="Se o agente está ativo")
    user_id: uuid.UUID = Field(..., description="ID do usuário proprietário")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, description="Prioridade")
    version: Optional[str] = Field(None, description="Versão")
    environment: Optional[str] = Field(None, description="Ambiente")
    current_config: Optional[uuid.UUID] = Field(None, description="Configuração atual")


class NodesResponse(BaseModel):
    """Response model for nodes endpoint"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do nó")
    name: str = Field(..., description="Nome do nó")
    category: str = Field(..., description="Categoria")
    description: Optional[str] = Field(None, description="Descrição")
    version: str = Field(..., description="Versão")
    definition: dict = Field(..., description="Definição")
    is_public: bool = Field(..., description="Se é público")
    created_at: Optional[datetime.datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Última atualização"
    )
    code_template: str = Field(..., description="Template de código")
    input_schema: dict = Field(..., description="Schema de entrada")
    output_schema: dict = Field(..., description="Schema de saída")
    parameters_schema: Optional[dict] = Field(None, description="Schema de parâmetros")
    icon: Optional[str] = Field(None, description="Ícone")
    color: Optional[str] = Field(None, description="Cor")
    documentation: Optional[str] = Field(None, description="Documentação")
    examples: Optional[dict] = Field(None, description="Exemplos")
    downloads_count: Optional[int] = Field(None, description="Contagem de downloads")
    usage_count: Optional[int] = Field(None, description="Contagem de uso")
    rating_average: Optional[int] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Contagem de avaliações")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    status: Optional[str] = Field(None, description="Status")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Contagem de tentativas")


class WorkflowsResponse(BaseModel):
    """Response model for workflows endpoint"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do workflow")
    name: str = Field(..., description="Nome do workflow")
    description: Optional[str] = Field(None, description="Descrição")
    definition: dict = Field(..., description="Definição")
    is_active: bool = Field(..., description="Se está ativo")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    is_public: Optional[bool] = Field(None, description="Se é público")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[dict] = Field(None, description="Tags")
    version: Optional[str] = Field(None, description="Versão")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    downloads_count: Optional[int] = Field(None, description="Contagem de downloads")
    rating_average: Optional[int] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Contagem de avaliações")
    execution_count: Optional[int] = Field(None, description="Contagem de execuções")
    last_executed_at: Optional[datetime.datetime] = Field(
        None, description="Última execução"
    )
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    status: Optional[str] = Field(None, description="Status")
    priority: Optional[int] = Field(None, description="Prioridade")
    timeout_seconds: Optional[int] = Field(None, description="Timeout em segundos")
    retry_count: Optional[int] = Field(None, description="Contagem de tentativas")


class FilesResponse(BaseModel):
    """Response model for files endpoint"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome do arquivo")
    original_name: str = Field(..., description="Nome original")
    file_path: str = Field(..., description="Caminho do arquivo")
    file_size: int = Field(..., description="Tamanho do arquivo")
    mime_type: str = Field(..., description="Tipo MIME")
    category: str = Field(..., description="Categoria")
    is_public: bool = Field(..., description="Se é público")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    tags: Optional[dict] = Field(None, description="Tags")
    description: Optional[str] = Field(None, description="Descrição")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    status: Optional[str] = Field(None, description="Status")
    scan_status: Optional[str] = Field(None, description="Status do scan")
    access_count: Optional[int] = Field(None, description="Contagem de acessos")
    last_accessed_at: Optional[datetime.datetime] = Field(
        None, description="Último acesso"
    )


# Additional schemas needed for user service
class UserProfileResponse(BaseModel):
    """Response model for user profile"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., description="Nome de usuário")
    full_name: str = Field(..., description="Nome completo")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    profile_image_url: Optional[str] = Field(
        None, description="URL da imagem de perfil"
    )
    bio: Optional[str] = Field(None, description="Biografia")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    status: UserStatus = Field(..., description="Status atual")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


# Token data schema
class TokenData(BaseModel):
    """Token payload data"""

    user_id: Optional[str] = None
    username: Optional[str] = None
    tenant_id: Optional[str] = None
    exp: Optional[int] = None


# ===== USER PROFILE UPDATE SCHEMA =====


class UserProfileUpdate(BaseModel):
    """Schema para atualização de perfil do usuário"""

    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Primeiro nome"
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Último nome"
    )
    company: Optional[str] = Field(None, max_length=200, description="Empresa")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    bio: Optional[str] = Field(None, max_length=500, description="Biografia")
    location: Optional[str] = Field(None, max_length=100, description="Localização")
    website: Optional[str] = Field(None, max_length=200, description="Website")
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Preferências do usuário"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


# ===== USER LIST RESPONSE =====


class UserListResponse(BaseModel):
    """Schema de resposta para listagem paginada de usuários"""

    model_config = ConfigDict(from_attributes=True)

    items: List[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# ===== WORKSPACE RELATED SCHEMAS =====


class MemberInvite(BaseModel):
    """Schema para convite de membro para workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(..., description="Email do usuário a ser convidado")
    role: str = Field("member", description="Role do membro")
    message: Optional[str] = Field(
        None, max_length=500, description="Mensagem personalizada"
    )


class ProjectCreate(BaseModel):
    """Schema para criação de projeto"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do projeto")
    description: Optional[str] = Field(
        None, max_length=1000, description="Descrição do projeto"
    )
    is_public: bool = Field(False, description="Se o projeto é público")
    tags: Optional[List[str]] = Field(
        default_factory=list, description="Tags do projeto"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados do projeto"
    )


class ProjectUpdate(BaseModel):
    """Schema para atualização de projeto"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Nova descrição"
    )
    is_public: Optional[bool] = Field(None, description="Novo status público")
    tags: Optional[List[str]] = Field(None, description="Novas tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Novos metadados")


class CommentCreate(BaseModel):
    """Schema para criação de comentário"""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Conteúdo do comentário"
    )
    parent_id: Optional[int] = Field(
        None, description="ID do comentário pai (para respostas)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados do comentário"
    )


# Workspace related schemas
class WorkspaceStatus(str, Enum):
    """Status do workspace"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    DRAFT = "draft"


class WorkspaceType(str, Enum):
    """Tipo do workspace"""

    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"


class WorkspaceCreate(BaseModel):
    """Schema para criação de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ..., min_length=1, max_length=255, description="Nome do workspace"
    )
    slug: Optional[str] = Field(None, max_length=100, description="Slug único")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição")
    type: WorkspaceType = Field(WorkspaceType.PERSONAL, description="Tipo do workspace")
    is_public: bool = Field(False, description="Se é público")
    color: Optional[str] = Field(None, description="Cor do workspace")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")


class WorkspaceUpdate(BaseModel):
    """Schema para atualização de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Novo nome"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Nova descrição"
    )
    color: Optional[str] = Field(None, description="Nova cor")
    avatar_url: Optional[str] = Field(None, description="Nova URL do avatar")
    is_public: Optional[bool] = Field(None, description="Novo status público")


class WorkspaceResponse(BaseModel):
    """Schema de resposta para workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID do workspace")
    name: str = Field(..., description="Nome")
    slug: str = Field(..., description="Slug")
    type: str = Field(..., description="Tipo")
    description: Optional[str] = Field(None, description="Descrição")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    color: Optional[str] = Field(None, description="Cor")
    owner_id: uuid.UUID = Field(..., description="ID do proprietário")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    is_public: bool = Field(..., description="Se é público")
    is_template: Optional[bool] = Field(None, description="Se é template")
    allow_guest_access: Optional[bool] = Field(
        None, description="Permitir acesso de convidados"
    )
    require_approval: Optional[bool] = Field(None, description="Requer aprovação")
    max_members: Optional[int] = Field(None, description="Máximo de membros")
    max_projects: Optional[int] = Field(None, description="Máximo de projetos")
    max_storage_mb: Optional[int] = Field(
        None, description="Máximo de armazenamento em MB"
    )
    enable_real_time_editing: Optional[bool] = Field(
        None, description="Edição em tempo real"
    )
    enable_comments: Optional[bool] = Field(None, description="Comentários habilitados")
    enable_chat: Optional[bool] = Field(None, description="Chat habilitado")
    enable_video_calls: Optional[bool] = Field(
        None, description="Videochamadas habilitadas"
    )
    email_notifications: Optional[bool] = Field(
        None, description="Notificações por email"
    )
    push_notifications: Optional[bool] = Field(None, description="Notificações push")
    member_count: Optional[int] = Field(None, description="Quantidade de membros")
    project_count: Optional[int] = Field(None, description="Quantidade de projetos")
    activity_count: Optional[int] = Field(None, description="Quantidade de atividades")
    storage_used_mb: Optional[float] = Field(
        None, description="Armazenamento usado em MB"
    )
    api_calls_today: Optional[int] = Field(None, description="Chamadas de API hoje")
    api_calls_this_month: Optional[int] = Field(
        None, description="Chamadas de API este mês"
    )
    feature_usage_count: Optional[Dict[str, Any]] = Field(
        None, description="Contagem de uso de features"
    )
    status: str = Field(..., description="Status")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    last_activity_at: Optional[datetime.datetime] = Field(
        None, description="Última atividade"
    )
    owner_name: Optional[str] = Field(None, description="Nome do proprietário")
    tenant_name: Optional[str] = Field(None, description="Nome do tenant")


class WorkspaceListResponse(BaseModel):
    """Schema de resposta para listagem paginada de workspaces"""

    model_config = ConfigDict(from_attributes=True)

    items: List[WorkspaceResponse] = Field(..., description="Lista de workspaces")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# Workspace Member schemas
class WorkspaceMemberCreate(BaseModel):
    """Schema para criação de membro de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: Optional[uuid.UUID] = Field(None, description="ID do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    role: str = Field("member", description="Role do membro")
    permissions: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Permissões específicas"
    )


class WorkspaceMemberResponse(BaseModel):
    """Schema de resposta para membro de workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID do membro")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    workspace_id: uuid.UUID = Field(..., description="ID do workspace")
    role: str = Field(..., description="Role")
    permissions: Dict[str, Any] = Field(..., description="Permissões")
    joined_at: datetime.datetime = Field(..., description="Data de ingresso")
    last_seen_at: Optional[datetime.datetime] = Field(
        None, description="Última visualização"
    )
    is_active: bool = Field(..., description="Se está ativo")


class WorkspaceMemberListResponse(BaseModel):
    """Schema de resposta para listagem de membros"""

    model_config = ConfigDict(from_attributes=True)

    items: List[WorkspaceMemberResponse] = Field(..., description="Lista de membros")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# Workspace Feature schemas (CORREÇÃO TASK 1.1)
class WorkspaceFeatureCreate(BaseModel):
    """Schema para criação de feature de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se a feature está habilitada")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração da feature"
    )
    usage_limit: Optional[int] = Field(None, description="Limite de uso")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


class WorkspaceFeatureResponse(BaseModel):
    """Schema de resposta para feature de workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da workspace feature")
    workspace_id: uuid.UUID = Field(..., description="ID do workspace")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    config: Dict[str, Any] = Field(..., description="Configuração")
    usage_limit: Optional[int] = Field(None, description="Limite de uso")
    current_usage: Optional[int] = Field(None, description="Uso atual")
    last_used_at: Optional[datetime.datetime] = Field(None, description="Último uso")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    metadata: Dict[str, Any] = Field(..., description="Metadados")

    # Campos do relacionamento com Feature
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")
    feature_description: Optional[str] = Field(None, description="Descrição da feature")


class WorkspaceFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do workspace"""

    model_config = ConfigDict(from_attributes=True)

    items: List[WorkspaceFeatureResponse] = Field(
        ..., description="Lista de features do workspace"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# Feature schemas (CORREÇÃO TASK 1.1 - Adicionar schemas principais)
class FeatureCreate(BaseModel):
    """Schema para criação de feature"""

    model_config = ConfigDict(str_strip_whitespace=True)

    key: str = Field(..., max_length=100, description="Chave única da feature")
    name: str = Field(..., max_length=200, description="Nome da feature")
    description: Optional[str] = Field(None, description="Descrição da feature")
    category: Optional[str] = Field(None, max_length=100, description="Categoria")
    is_active: bool = Field(True, description="Se a feature está ativa")


class FeatureUpdate(BaseModel):
    """Schema para atualização de feature"""

    model_config = ConfigDict(str_strip_whitespace=True)

    key: Optional[str] = Field(None, max_length=100, description="Nova chave")
    name: Optional[str] = Field(None, max_length=200, description="Novo nome")
    description: Optional[str] = Field(None, description="Nova descrição")
    category: Optional[str] = Field(None, max_length=100, description="Nova categoria")
    is_active: Optional[bool] = Field(None, description="Novo status")


class FeatureResponse(BaseModel):
    """Schema de resposta para feature"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da feature")
    key: str = Field(..., description="Chave da feature")
    name: str = Field(..., description="Nome da feature")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    is_active: bool = Field(..., description="Se está ativa")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class FeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features"""

    model_config = ConfigDict(from_attributes=True)

    features: List[FeatureResponse] = Field(..., description="Lista de features")
    total_count: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Tamanho da página")
    has_next: bool = Field(..., description="Se há próxima página")


# PlanFeature schemas
class PlanFeatureCreate(BaseModel):
    """Schema para criação de feature de plano"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se está habilitada")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração"
    )


class PlanFeatureResponse(BaseModel):
    """Schema de resposta para feature de plano"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da plan feature")
    plan_id: uuid.UUID = Field(..., description="ID do plano")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    config: Dict[str, Any] = Field(..., description="Configuração")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")

    # Campos do relacionamento
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")


class PlanFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do plano"""

    model_config = ConfigDict(from_attributes=True)

    items: List[PlanFeatureResponse] = Field(
        ..., description="Lista de features do plano"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# TenantFeature schemas
class TenantFeatureCreate(BaseModel):
    """Schema para criação de feature de tenant"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se está habilitada")
    usage_count: Optional[int] = Field(0, description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração"
    )
    expires_at: Optional[datetime.datetime] = Field(
        None, description="Data de expiração"
    )


class TenantFeatureResponse(BaseModel):
    """Schema de resposta para feature de tenant"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da tenant feature")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    usage_count: int = Field(..., description="Contagem de uso")
    limit_value: Optional[int] = Field(None, description="Limite de valor")
    config: Dict[str, Any] = Field(..., description="Configuração")
    expires_at: Optional[datetime.datetime] = Field(
        None, description="Data de expiração"
    )
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")

    # Campos do relacionamento
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")


class TenantFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do tenant"""

    model_config = ConfigDict(from_attributes=True)

    items: List[TenantFeatureResponse] = Field(
        ..., description="Lista de features do tenant"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# Workspace Feature schemas (CORREÇÃO TASK 1.1)
class WorkspaceFeatureCreate(BaseModel):
    """Schema para criação de feature de workspace"""

    model_config = ConfigDict(str_strip_whitespace=True)

    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(True, description="Se a feature está habilitada")
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Configuração da feature"
    )
    usage_limit: Optional[int] = Field(None, description="Limite de uso")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadados adicionais"
    )


class WorkspaceFeatureResponse(BaseModel):
    """Schema de resposta para feature de workspace"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="ID da workspace feature")
    workspace_id: uuid.UUID = Field(..., description="ID do workspace")
    feature_id: uuid.UUID = Field(..., description="ID da feature")
    is_enabled: bool = Field(..., description="Se está habilitada")
    config: Dict[str, Any] = Field(..., description="Configuração")
    usage_limit: Optional[int] = Field(None, description="Limite de uso")
    current_usage: Optional[int] = Field(None, description="Uso atual")
    last_used_at: Optional[datetime.datetime] = Field(None, description="Último uso")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    metadata: Dict[str, Any] = Field(..., description="Metadados")

    # Campos do relacionamento com Feature
    feature_name: Optional[str] = Field(None, description="Nome da feature")
    feature_key: Optional[str] = Field(None, description="Chave da feature")
    feature_description: Optional[str] = Field(None, description="Descrição da feature")


class WorkspaceFeatureListResponse(BaseModel):
    """Schema de resposta para listagem de features do workspace"""

    model_config = ConfigDict(from_attributes=True)

    items: List[WorkspaceFeatureResponse] = Field(
        ..., description="Lista de features do workspace"
    )
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# Adicionar os schemas de Agent que estão faltando

class AgentResponse(BaseModel):
    """Schema de resposta para agente - ALINHADO COM BANCO"""

    id: uuid.UUID = Field(..., description="ID do agente")
    name: str = Field(..., description="Nome do agente")
    description: Optional[str] = Field(None, description="Descrição")
    is_active: bool = Field(..., description="Agente ativo")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    status: Optional[str] = Field(None, description="Status do agente")
    priority: Optional[int] = Field(None, description="Prioridade")
    version: Optional[str] = Field(None, description="Versão")
    environment: Optional[str] = Field(None, description="Ambiente")
    current_config: Optional[uuid.UUID] = Field(None, description="Configuração atual")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Data de atualização")
    
    # Campos adicionais para compatibilidade com endpoints
    scope: Optional[str] = Field(None, description="Escopo do agente")
    configuration: Optional[dict] = Field(None, description="Configuração")
    metadata: Optional[dict] = Field(None, description="Metadados")
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    workspace_name: Optional[str] = Field(None, description="Nome do workspace")


class AgentStatus(str, Enum):
    """Status do agente"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    ERROR = "error"


class AgentEnvironment(str, Enum):
    """Ambiente do agente"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class AgentScope(str, Enum):
    """Escopo do agente"""
    PRIVATE = "private"
    WORKSPACE = "workspace"
    TENANT = "tenant"
    PUBLIC = "public"


class AgentCreate(BaseModel):
    """Schema para criação de agente"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255, description="Nome do agente")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição")
    version: Optional[str] = Field("1.0.0", description="Versão")
    environment: AgentEnvironment = Field(AgentEnvironment.DEVELOPMENT, description="Ambiente")
    scope: AgentScope = Field(AgentScope.PRIVATE, description="Escopo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    configuration: Optional[dict] = Field(default_factory=dict, description="Configuração")
    metadata: Optional[dict] = Field(default_factory=dict, description="Metadados")
    is_active: bool = Field(True, description="Agente ativo")


class AgentUpdate(BaseModel):
    """Schema para atualização de agente"""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição")
    version: Optional[str] = Field(None, description="Versão")
    environment: Optional[AgentEnvironment] = Field(None, description="Ambiente")
    scope: Optional[AgentScope] = Field(None, description="Escopo")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    configuration: Optional[dict] = Field(None, description="Configuração")
    metadata: Optional[dict] = Field(None, description="Metadados")
    is_active: Optional[bool] = Field(None, description="Agente ativo")


class AgentListResponse(BaseModel):
    """Schema de resposta para listagem paginada de agentes"""

    model_config = ConfigDict(from_attributes=True)

    items: List[AgentResponse] = Field(..., description="Lista de agentes")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# ===== SCHEMAS FALTANTES PARA ENDPOINTS =====

# Payment schemas
class PaymentProviderCreate(BaseModel):
    """Schema para criação de provedor de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="Nome do provedor")
    display_name: str = Field(..., description="Nome de exibição")
    is_active: bool = Field(True, description="Se está ativo")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuração")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    api_version: Optional[str] = Field(None, description="Versão da API")


class PaymentProviderResponse(BaseModel):
    """Schema de resposta para provedor de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do provedor")
    name: str = Field(..., description="Nome")
    display_name: str = Field(..., description="Nome de exibição")
    is_active: bool = Field(..., description="Se está ativo")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuração")
    webhook_secret: Optional[str] = Field(None, description="Segredo do webhook")
    api_version: Optional[str] = Field(None, description="Versão da API")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class PaymentCustomerCreate(BaseModel):
    """Schema para criação de customer de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    provider_id: uuid.UUID = Field(..., description="ID do provedor")
    external_customer_id: str = Field(..., description="ID externo do customer")
    customer_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados do customer")
    is_active: bool = Field(True, description="Se está ativo")


class PaymentCustomerResponse(BaseModel):
    """Schema de resposta para customer de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do customer")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    provider_id: uuid.UUID = Field(..., description="ID do provedor")
    external_customer_id: str = Field(..., description="ID externo")
    customer_data: Optional[Dict[str, Any]] = Field(None, description="Dados do customer")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class PaymentMethodCreate(BaseModel):
    """Schema para criação de método de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: str = Field(..., description="Tipo do método")
    external_method_id: str = Field(..., description="ID externo do método")
    provider_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados do provedor")
    is_default: bool = Field(False, description="Se é padrão")
    is_active: bool = Field(True, description="Se está ativo")


class PaymentMethodUpdate(BaseModel):
    """Schema para atualização de método de pagamento"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    type: Optional[str] = Field(None, description="Tipo do método")
    external_method_id: Optional[str] = Field(None, description="ID externo")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Dados do provedor")
    is_default: Optional[bool] = Field(None, description="Se é padrão")
    is_active: Optional[bool] = Field(None, description="Se está ativo")


class PaymentMethodResponse(BaseModel):
    """Schema de resposta para método de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do método")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    type: str = Field(..., description="Tipo")
    external_method_id: str = Field(..., description="ID externo")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Dados do provedor")
    is_default: bool = Field(..., description="Se é padrão")
    is_active: bool = Field(..., description="Se está ativo")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class PaymentMethodListResponse(BaseModel):
    """Schema de resposta para listagem de métodos de pagamento"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[PaymentMethodResponse] = Field(..., description="Lista de métodos")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


class InvoiceCreate(BaseModel):
    """Schema para criação de invoice"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    amount: float = Field(..., description="Valor")
    currency: str = Field("USD", description="Moeda")
    status: str = Field("pending", description="Status")
    due_date: Optional[datetime.datetime] = Field(None, description="Data de vencimento")
    items: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Itens")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")


class InvoiceUpdate(BaseModel):
    """Schema para atualização de invoice"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    amount: Optional[float] = Field(None, description="Valor")
    currency: Optional[str] = Field(None, description="Moeda")
    status: Optional[str] = Field(None, description="Status")
    due_date: Optional[datetime.datetime] = Field(None, description="Data de vencimento")
    items: Optional[List[Dict[str, Any]]] = Field(None, description="Itens")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados")


class InvoiceResponse(BaseModel):
    """Schema de resposta para invoice"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID da invoice")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    amount: float = Field(..., description="Valor")
    currency: str = Field(..., description="Moeda")
    status: str = Field(..., description="Status")
    due_date: Optional[datetime.datetime] = Field(None, description="Data de vencimento")
    paid_at: Optional[datetime.datetime] = Field(None, description="Data de pagamento")
    items: List[Dict[str, Any]] = Field(..., description="Itens")
    metadata: Dict[str, Any] = Field(..., description="Metadados")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class InvoiceListResponse(BaseModel):
    """Schema de resposta para listagem de invoices"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[InvoiceResponse] = Field(..., description="Lista de invoices")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# LLM schemas
class LLMCreate(BaseModel):
    """Schema para criação de LLM"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="Nome do LLM")
    provider: str = Field(..., description="Provedor")
    model_id: str = Field(..., description="ID do modelo")
    description: Optional[str] = Field(None, description="Descrição")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    temperature: Optional[float] = Field(None, description="Temperatura")
    top_p: Optional[float] = Field(None, description="Top P")
    frequency_penalty: Optional[float] = Field(None, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, description="Penalidade de presença")
    cost_per_1k_input_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de entrada")
    cost_per_1k_output_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de saída")
    is_active: bool = Field(True, description="Se está ativo")
    is_public: bool = Field(False, description="Se é público")


class LLMUpdate(BaseModel):
    """Schema para atualização de LLM"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: Optional[str] = Field(None, description="Nome")
    provider: Optional[str] = Field(None, description="Provedor")
    model_id: Optional[str] = Field(None, description="ID do modelo")
    description: Optional[str] = Field(None, description="Descrição")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    temperature: Optional[float] = Field(None, description="Temperatura")
    top_p: Optional[float] = Field(None, description="Top P")
    frequency_penalty: Optional[float] = Field(None, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, description="Penalidade de presença")
    cost_per_1k_input_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de entrada")
    cost_per_1k_output_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de saída")
    is_active: Optional[bool] = Field(None, description="Se está ativo")
    is_public: Optional[bool] = Field(None, description="Se é público")


class LLMResponse(BaseModel):
    """Schema de resposta para LLM"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do LLM")
    name: str = Field(..., description="Nome")
    provider: str = Field(..., description="Provedor")
    model_id: str = Field(..., description="ID do modelo")
    description: Optional[str] = Field(None, description="Descrição")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    temperature: Optional[float] = Field(None, description="Temperatura")
    top_p: Optional[float] = Field(None, description="Top P")
    frequency_penalty: Optional[float] = Field(None, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, description="Penalidade de presença")
    cost_per_1k_input_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de entrada")
    cost_per_1k_output_tokens: Optional[float] = Field(None, description="Custo por 1k tokens de saída")
    is_active: bool = Field(..., description="Se está ativo")
    is_public: bool = Field(..., description="Se é público")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class LLMListResponse(BaseModel):
    """Schema de resposta para listagem de LLMs"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[LLMResponse] = Field(..., description="Lista de LLMs")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# LLM Conversation schemas
class LLMConversationCreate(BaseModel):
    """Schema para criação de conversa LLM"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    title: Optional[str] = Field(None, description="Título da conversa")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")


class LLMConversationResponse(BaseModel):
    """Schema de resposta para conversa LLM"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID da conversa")
    llm_id: uuid.UUID = Field(..., description="ID do LLM")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    title: Optional[str] = Field(None, description="Título")
    workspace_id: Optional[uuid.UUID] = Field(None, description="ID do workspace")
    metadata: Dict[str, Any] = Field(..., description="Metadados")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


class LLMConversationListResponse(BaseModel):
    """Schema de resposta para listagem de conversas LLM"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[LLMConversationResponse] = Field(..., description="Lista de conversas")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# LLM Message schemas
class LLMMessageCreate(BaseModel):
    """Schema para criação de mensagem LLM"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    role: str = Field(..., description="Role da mensagem (user, assistant, system)")
    content: str = Field(..., description="Conteúdo da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")


class LLMMessageResponse(BaseModel):
    """Schema de resposta para mensagem LLM"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID da mensagem")
    conversation_id: uuid.UUID = Field(..., description="ID da conversa")
    role: str = Field(..., description="Role")
    content: str = Field(..., description="Conteúdo")
    metadata: Dict[str, Any] = Field(..., description="Metadados")
    created_at: datetime.datetime = Field(..., description="Data de criação")


class LLMMessageListResponse(BaseModel):
    """Schema de resposta para listagem de mensagens LLM"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[LLMMessageResponse] = Field(..., description="Lista de mensagens")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


# RBAC schemas
class RBACRoleCreate(BaseModel):
    """Schema para criação de role RBAC"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., description="Nome do role")
    description: Optional[str] = Field(None, description="Descrição")
    is_system: bool = Field(False, description="Se é um role do sistema")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadados")


class RBACRoleUpdate(BaseModel):
    """Schema para atualização de role RBAC"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: Optional[str] = Field(None, description="Nome")
    description: Optional[str] = Field(None, description="Descrição")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados")


class RBACRoleResponse(BaseModel):
    """Schema de resposta para role RBAC"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do role")
    name: str = Field(..., description="Nome")
    description: Optional[str] = Field(None, description="Descrição")
    is_system: bool = Field(..., description="Se é do sistema")
    metadata: Dict[str, Any] = Field(..., description="Metadados")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class RBACRoleListResponse(BaseModel):
    """Schema de resposta para listagem de roles RBAC"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[RBACRoleResponse] = Field(..., description="Lista de roles")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


class RBACPermissionCreate(BaseModel):
    """Schema para criação de permission RBAC"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    key: str = Field(..., description="Chave da permissão")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    resource: Optional[str] = Field(None, description="Recurso")
    action: Optional[str] = Field(None, description="Ação")


class RBACPermissionResponse(BaseModel):
    """Schema de resposta para permission RBAC"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID da permissão")
    key: str = Field(..., description="Chave")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    resource: Optional[str] = Field(None, description="Recurso")
    action: Optional[str] = Field(None, description="Ação")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class RBACPermissionListResponse(BaseModel):
    """Schema de resposta para listagem de permissions RBAC"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[RBACPermissionResponse] = Field(..., description="Lista de permissões")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")


class UserTenantRoleCreate(BaseModel):
    """Schema para criação de role de usuário no tenant"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    role_id: uuid.UUID = Field(..., description="ID do role")
    granted: bool = Field(True, description="Se está concedido")
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Condições")


class UserTenantRoleResponse(BaseModel):
    """Schema de resposta para role de usuário no tenant"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(..., description="ID do user tenant role")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    role_id: uuid.UUID = Field(..., description="ID do role")
    tenant_id: uuid.UUID = Field(..., description="ID do tenant")
    granted: bool = Field(..., description="Se está concedido")
    conditions: Dict[str, Any] = Field(..., description="Condições")
    created_at: datetime.datetime = Field(..., description="Data de criação")
    updated_at: datetime.datetime = Field(..., description="Última atualização")


# Classe utilitária
class PaginatedResponse(BaseModel):
    """Schema base para respostas paginadas"""
    
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")

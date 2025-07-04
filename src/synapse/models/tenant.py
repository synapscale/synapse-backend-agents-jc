from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, ARRAY, and_
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from synapse.database import Base
import uuid
from enum import Enum as PyEnum


class TenantStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Estrutura EXATA do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    domain = Column(String)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.plans.id"), nullable=False
    )
    theme = Column(String, default="light")
    default_language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    mfa_required = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=3600)
    ip_whitelist = Column(JSONB, default=list)
    max_storage_mb = Column(Integer)
    max_workspaces = Column(Integer)
    max_api_calls_per_day = Column(Integer)
    max_members_per_workspace = Column(Integer)
    enabled_features = Column(ARRAY(String))

    # Relationships
    users = relationship("synapse.models.user.User", back_populates="tenant")
    files = relationship("synapse.models.file.File", back_populates="tenant")
    tenant_features = relationship("synapse.models.tenant_feature.TenantFeature", back_populates="tenant")
    plan = relationship("synapse.models.plan.Plan", back_populates="tenants")
    workspaces = relationship("synapse.models.workspace.Workspace", back_populates="tenant")
    plan_entitlements = relationship("synapse.models.plan_entitlement.PlanEntitlement", back_populates="tenant", cascade="all, delete-orphan")
    workspace_activities = relationship("synapse.models.workspace_activity.WorkspaceActivity", back_populates="tenant", cascade="all, delete-orphan")
    workspace_invitations = relationship("synapse.models.workspace_invitation.WorkspaceInvitation", back_populates="tenant", cascade="all, delete-orphan")
    workspace_projects = relationship("synapse.models.workspace_project.WorkspaceProject", back_populates="tenant", cascade="all, delete-orphan")

    # Relacionamentos RBAC
    rbac_roles = relationship("synapse.models.rbac_role.RBACRole", back_populates="tenant", cascade="all, delete-orphan")
    rbac_permissions = relationship("synapse.models.rbac_permission.RBACPermission", back_populates="tenant", cascade="all, delete-orphan")
    rbac_role_permissions = relationship("synapse.models.rbac_role_permission.RBACRolePermission", back_populates="tenant", cascade="all, delete-orphan")
    user_roles = relationship("synapse.models.user_tenant_role.UserTenantRole", back_populates="tenant", cascade="all, delete-orphan")

    # Relacionamentos Analytics
    user_behavior_metrics = relationship("synapse.models.user_behavior_metric.UserBehaviorMetric", back_populates="tenant", cascade="all, delete-orphan")
    user_insights = relationship("synapse.models.user_insight.UserInsight", back_populates="tenant", cascade="all, delete-orphan")
    user_subscriptions = relationship("synapse.models.user_subscription.UserSubscription", back_populates="tenant", cascade="all, delete-orphan")

    # Relacionamentos de Pagamento
    payment_customers = relationship("synapse.models.payment_customer.PaymentCustomer", back_populates="tenant", cascade="all, delete-orphan")
    payment_providers = relationship("synapse.models.payment_provider.PaymentProvider", back_populates="tenant", cascade="all, delete-orphan")
    invoices = relationship("synapse.models.invoice.Invoice", back_populates="tenant", cascade="all, delete-orphan")
    coupons = relationship("synapse.models.coupon.Coupon", back_populates="tenant", cascade="all, delete-orphan")
    workspace_members = relationship("synapse.models.workspace_member.WorkspaceMember", back_populates="tenant", cascade="all, delete-orphan")
    project_versions = relationship("synapse.models.project_version.ProjectVersion", back_populates="tenant", cascade="all, delete-orphan")
    subscriptions = relationship("synapse.models.subscription.Subscription", back_populates="tenant", cascade="all, delete-orphan")
    user_variables = relationship("synapse.models.user_variable.UserVariable", back_populates="tenant", cascade="all, delete-orphan")

    # Analytics Relationships
    analytics_alerts = relationship("synapse.models.analytics_alert.AnalyticsAlert", back_populates="tenant", cascade="all, delete-orphan")
    analytics_dashboards = relationship("synapse.models.analytics_dashboard.AnalyticsDashboard", back_populates="tenant", cascade="all, delete-orphan")
    analytics_events = relationship("synapse.models.analytics_event.AnalyticsEvent", back_populates="tenant", cascade="all, delete-orphan")
    analytics_exports = relationship("synapse.models.analytics_export.AnalyticsExport", back_populates="tenant", cascade="all, delete-orphan")
    analytics_metrics = relationship("synapse.models.analytics_metric.AnalyticsMetric", back_populates="tenant", cascade="all, delete-orphan")
    analytics_reports = relationship("synapse.models.analytics_report.AnalyticsReport", back_populates="tenant", cascade="all, delete-orphan")
    business_metrics = relationship("synapse.models.business_metric.BusinessMetric", back_populates="tenant", cascade="all, delete-orphan")
    custom_reports = relationship("synapse.models.custom_report.CustomReport", back_populates="tenant", cascade="all, delete-orphan")
    report_executions = relationship("synapse.models.report_execution.ReportExecution", back_populates="tenant", cascade="all, delete-orphan")

    # Contact and Campaign Relationships
    campaigns = relationship("synapse.models.campaign.Campaign", back_populates="tenant", cascade="all, delete-orphan")
    contact_lists = relationship("synapse.models.contact_list.ContactList", back_populates="tenant", cascade="all, delete-orphan")
    contacts = relationship("synapse.models.contact.Contact", back_populates="tenant", cascade="all, delete-orphan")

    # Knowledge and Node Relationships
    knowledge_bases = relationship("synapse.models.knowledge_base.KnowledgeBase", back_populates="tenant", cascade="all, delete-orphan")
    node_categories = relationship("synapse.models.node_category.NodeCategory", back_populates="tenant", cascade="all, delete-orphan")
    node_executions = relationship("synapse.models.node_execution.NodeExecution", back_populates="tenant", cascade="all, delete-orphan")
    node_ratings = relationship("synapse.models.node_rating.NodeRating", back_populates="tenant", cascade="all, delete-orphan")

    # Workflow Relationships
    workflow_connections = relationship("synapse.models.workflow_connection.WorkflowConnection", back_populates="tenant", cascade="all, delete-orphan")
    workflow_execution_metrics = relationship("synapse.models.workflow_execution_metric.WorkflowExecutionMetric", back_populates="tenant", cascade="all, delete-orphan")
    workflow_execution_queue = relationship("synapse.models.workflow_execution_queue.WorkflowExecutionQueue", back_populates="tenant", cascade="all, delete-orphan")
    workflow_nodes = relationship("synapse.models.workflow_node.WorkflowNode", back_populates="tenant", cascade="all, delete-orphan")
    workflow_templates = relationship("synapse.models.workflow_template.WorkflowTemplate", back_populates="tenant", cascade="all, delete-orphan")

    # Message Relationships
    message_feedbacks = relationship("synapse.models.message_feedback.MessageFeedback", back_populates="tenant", cascade="all, delete-orphan")
    
    # Plan Provider Mappings
    plan_provider_mappings = relationship("synapse.models.plan_provider_mapping.PlanProviderMapping", back_populates="tenant", cascade="all, delete-orphan")

    # LLM Relationships
    llms = relationship("synapse.models.llm.LLM", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("synapse.models.conversation.Conversation", back_populates="tenant", cascade="all, delete-orphan")
    conversation_llms = relationship("synapse.models.conversation_llm.ConversationLLM", back_populates="tenant", cascade="all, delete-orphan")

    # Agent Relationships  
    agents = relationship("synapse.models.agent.Agent", back_populates="tenant", cascade="all, delete-orphan")
    agent_quotas = relationship("synapse.models.agent_quota.AgentQuota", back_populates="tenant", cascade="all, delete-orphan")

    # Billing Relationships
    billing_events = relationship("synapse.models.billing_event.BillingEvent", back_populates="tenant", cascade="all, delete-orphan")

    # Component and Marketplace Relationships  
    component_downloads = relationship("synapse.models.marketplace.ComponentDownload", back_populates="tenant", cascade="all, delete-orphan")
    component_purchases = relationship("synapse.models.marketplace.ComponentPurchase", back_populates="tenant", cascade="all, delete-orphan")
    component_ratings = relationship("synapse.models.marketplace.ComponentRating", back_populates="tenant", cascade="all, delete-orphan")
    component_versions = relationship("synapse.models.component_version.ComponentVersion", back_populates="tenant", cascade="all, delete-orphan")
    marketplace_components = relationship("synapse.models.marketplace.MarketplaceComponent", back_populates="tenant", cascade="all, delete-orphan")

    # Contact Event and Interaction Relationships
    contact_events = relationship("synapse.models.contact_event.ContactEvent", back_populates="tenant", cascade="all, delete-orphan")
    contact_interactions = relationship("synapse.models.contact_interaction.ContactInteraction", back_populates="tenant", cascade="all, delete-orphan")
    contact_list_memberships = relationship("synapse.models.contact_list_membership.ContactListMembership", back_populates="tenant", cascade="all, delete-orphan")
    contact_notes = relationship("synapse.models.contact_note.ContactNote", back_populates="tenant", cascade="all, delete-orphan")
    contact_sources = relationship("synapse.models.contact_source.ContactSource", back_populates="tenant", cascade="all, delete-orphan")
    contact_tags = relationship("synapse.models.contact_tag.ContactTag", back_populates="tenant", cascade="all, delete-orphan")
    conversion_journeys = relationship("synapse.models.conversion_journey.ConversionJourney", back_populates="tenant", cascade="all, delete-orphan")

    # Node and Workflow Template Relationships
    node_templates = relationship("synapse.models.node_template.NodeTemplate", back_populates="tenant", cascade="all, delete-orphan")
    nodes = relationship("synapse.models.node.Node", back_populates="tenant", cascade="all, delete-orphan")

    # Payment Method Relationships
    payment_methods = relationship("synapse.models.payment_method.PaymentMethod", back_populates="tenant", cascade="all, delete-orphan")

    # Project Collaboration Relationships
    project_collaborators = relationship("synapse.models.project_collaborator.ProjectCollaborator", back_populates="tenant", cascade="all, delete-orphan")
    project_comments = relationship("synapse.models.project_comment.ProjectComment", back_populates="tenant", cascade="all, delete-orphan")

    # System Performance Relationships
    system_performance_metrics = relationship("synapse.models.analytics.SystemPerformanceMetric", back_populates="tenant", cascade="all, delete-orphan")

    # Tags Relationships
    tags = relationship(
        "synapse.models.tag.Tag",
        primaryjoin="and_(foreign(synapse.models.tag.Tag.target_id) == synapse.models.tenant.Tenant.id, synapse.models.tag.Tag.target_type == 'tenant')",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )

    # Template Relationships
    template_collections = relationship("synapse.models.template.TemplateCollection", back_populates="tenant", cascade="all, delete-orphan")
    template_downloads = relationship("synapse.models.template.TemplateDownload", back_populates="tenant", cascade="all, delete-orphan")
    template_favorites = relationship("synapse.models.template.TemplateFavorite", back_populates="tenant", cascade="all, delete-orphan")
    template_reviews = relationship("synapse.models.template.TemplateReview", back_populates="tenant", cascade="all, delete-orphan")
    template_usage = relationship("synapse.models.template.TemplateUsage", back_populates="tenant", cascade="all, delete-orphan")

    # Webhook Relationships
    webhook_logs = relationship("synapse.models.webhook_log.WebhookLog", back_populates="tenant", cascade="all, delete-orphan")

    # Workflow Execution Relationships
    workflow_executions = relationship("synapse.models.workflow_execution.WorkflowExecution", back_populates="tenant", cascade="all, delete-orphan")
    workflows = relationship("synapse.models.workflow.Workflow", back_populates="tenant", cascade="all, delete-orphan")

    # Workspace Feature Relationships
    workspace_features = relationship("synapse.models.feature.WorkspaceFeature", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', status={self.status})>"

    @property
    def is_active(self):
        return self.status == "active"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "domain": self.domain,
            "status": self.status,
            "theme": self.theme,
            "default_language": self.default_language,
            "timezone": self.timezone,
            "mfa_required": self.mfa_required,
            "session_timeout": self.session_timeout,
            "plan_id": str(self.plan_id) if self.plan_id else None,
            "max_storage_mb": self.max_storage_mb,
            "max_workspaces": self.max_workspaces,
            "max_api_calls_per_day": self.max_api_calls_per_day,
            "max_members_per_workspace": self.max_members_per_workspace,
            "enabled_features": self.enabled_features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }

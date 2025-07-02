from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
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
    __table_args__ = {"schema": "synapscale_db"}

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
    users = relationship("User", back_populates="tenant")
    files = relationship("File", back_populates="tenant")
    tenant_features = relationship("TenantFeature", back_populates="tenant")
    plan = relationship("Plan", back_populates="tenants")
    workspaces = relationship("Workspace", back_populates="tenant")
    plan_entitlements = relationship("PlanEntitlement", back_populates="tenant", cascade="all, delete-orphan")
    workspace_activities = relationship("WorkspaceActivity", back_populates="tenant", cascade="all, delete-orphan")
    workspace_invitations = relationship("WorkspaceInvitation", back_populates="tenant", cascade="all, delete-orphan")
    workspace_projects = relationship("WorkspaceProject", back_populates="tenant", cascade="all, delete-orphan")

    # Relacionamentos RBAC - NOVOS MODELS
    rbac_roles = relationship(
        "RBACRole", back_populates="tenant", cascade="all, delete-orphan"
    )
    rbac_permissions = relationship(
        "RBACPermission", back_populates="tenant", cascade="all, delete-orphan"
    )
    rbac_role_permissions = relationship(
        "RBACRolePermission", back_populates="tenant", cascade="all, delete-orphan"
    )
    user_roles = relationship(
        "UserTenantRole", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Relacionamentos Analytics - NOVOS MODELS
    user_behavior_metrics = relationship(
        "UserBehaviorMetric", back_populates="tenant", cascade="all, delete-orphan"
    )
    user_insights = relationship(
        "UserInsight", back_populates="tenant", cascade="all, delete-orphan"
    )
    user_subscriptions = relationship(
        "UserSubscription", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Relacionamentos de Pagamento - NOVOS MODELS  
    payment_customers = relationship(
        "PaymentCustomer", back_populates="tenant", cascade="all, delete-orphan"
    )
    payment_providers = relationship(
        "PaymentProvider", back_populates="tenant", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="tenant", cascade="all, delete-orphan"
    )
    coupons = relationship(
        "Coupon", back_populates="tenant", cascade="all, delete-orphan"
    )
    workspace_members = relationship(
        "WorkspaceMember", back_populates="tenant", cascade="all, delete-orphan"
    )
    project_versions = relationship(
        "ProjectVersion", back_populates="tenant", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "Subscription", back_populates="tenant", cascade="all, delete-orphan"
    )
    user_variables = relationship(
        "UserVariable", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Analytics Relationships
    analytics_alerts = relationship(
        "AnalyticsAlert", back_populates="tenant", cascade="all, delete-orphan"
    )
    analytics_events = relationship(
        "AnalyticsEvent", back_populates="tenant", cascade="all, delete-orphan"
    )
    analytics_metrics = relationship(
        "AnalyticsMetric", back_populates="tenant", cascade="all, delete-orphan"
    )
    analytics_reports = relationship(
        "AnalyticsReport", back_populates="tenant", cascade="all, delete-orphan"
    )
    business_metrics = relationship(
        "BusinessMetric", back_populates="tenant", cascade="all, delete-orphan"
    )
    custom_reports = relationship(
        "CustomReport", back_populates="tenant", cascade="all, delete-orphan"
    )
    report_executions = relationship(
        "ReportExecution", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Contact and Campaign Relationships
    campaigns = relationship(
        "Campaign", back_populates="tenant", cascade="all, delete-orphan"
    )
    contact_lists = relationship(
        "ContactList", back_populates="tenant", cascade="all, delete-orphan"
    )
    contacts = relationship(
        "Contact", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Knowledge and Node Relationships
    knowledge_bases = relationship(
        "KnowledgeBase", back_populates="tenant", cascade="all, delete-orphan"
    )
    node_categories = relationship(
        "NodeCategory", back_populates="tenant", cascade="all, delete-orphan"
    )
    node_executions = relationship(
        "synapse.models.node_execution.NodeExecution", back_populates="tenant", cascade="all, delete-orphan"
    )
    node_ratings = relationship(
        "NodeRating", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Workflow Relationships
    workflow_connections = relationship(
        "WorkflowConnection", back_populates="tenant", cascade="all, delete-orphan"
    )
    workflow_execution_metrics = relationship(
        "WorkflowExecutionMetric", back_populates="tenant", cascade="all, delete-orphan"
    )
    workflow_execution_queue = relationship(
        "WorkflowExecutionQueue", back_populates="tenant", cascade="all, delete-orphan"
    )
    workflow_nodes = relationship(
        "WorkflowNode", back_populates="tenant", cascade="all, delete-orphan"
    )
    workflow_templates = relationship(
        "WorkflowTemplate", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Message Relationships
    message_feedbacks = relationship(
        "MessageFeedback", back_populates="tenant", cascade="all, delete-orphan"
    )

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

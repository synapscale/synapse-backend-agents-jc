"""
Modelo de usuário completo com autenticação e autorização
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from passlib.context import CryptContext
from synapse.database import Base
from enum import Enum as PyEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # Campo real do banco
    full_name = Column(String(200), nullable=False)  # Campo real do banco
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)  # Campo real do banco
    profile_image_url = Column(String(500))  # Campo real do banco
    bio = Column(String(1000))  # Campo real do banco
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    status = Column(String(20), default="active")
    user_metadata = Column("metadata", JSONB, default=dict)
    last_login_at = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True
    )

    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")
    nodes = relationship("Node", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    workflow_executions = relationship("WorkflowExecution", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    variables = relationship("UserVariable", back_populates="user", cascade="all, delete-orphan")

    # Relacionamentos de autenticação - NOVOS MODELS
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    email_verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    tenant_roles = relationship(
        "UserTenantRole",
        foreign_keys="UserTenantRole.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relacionamentos de auditoria e analytics - NOVOS MODELS
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("UserInsight", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan", overlaps="subscription")

    # Relacionamentos de templates
    created_templates = relationship("WorkflowTemplate", back_populates="author", cascade="all, delete-orphan")
    template_reviews = relationship("synapse.models.template.TemplateReview", back_populates="user", cascade="all, delete-orphan")
    template_downloads = relationship("synapse.models.template.TemplateDownload", back_populates="user", cascade="all, delete-orphan")
    favorite_templates = relationship("synapse.models.template.TemplateFavorite", back_populates="user", cascade="all, delete-orphan")
    template_collections = relationship("synapse.models.template.TemplateCollection", back_populates="creator", cascade="all, delete-orphan")
    template_usage = relationship("synapse.models.template.TemplateUsage", back_populates="user", cascade="all, delete-orphan")

    # Relacionamentos de marketplace
    marketplace_components = relationship("synapse.models.marketplace.MarketplaceComponent", back_populates="author", cascade="all, delete-orphan")
    component_ratings = relationship("synapse.models.marketplace.ComponentRating", back_populates="user", cascade="all, delete-orphan")
    component_downloads = relationship("synapse.models.marketplace.ComponentDownload", back_populates="user", cascade="all, delete-orphan")
    component_purchases = relationship("synapse.models.marketplace.ComponentPurchase", back_populates="user", cascade="all, delete-orphan")

    # Relacionamentos de workspaces
    owned_workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    workspace_invitations_sent = relationship(
        "WorkspaceInvitation",
        foreign_keys="WorkspaceInvitation.inviter_id",
        back_populates="inviter",
    )
    workspace_invitations_received = relationship(
        "WorkspaceInvitation",
        foreign_keys="WorkspaceInvitation.invited_user_id",
        back_populates="invited_user",
    )
    workspace_activities = relationship("WorkspaceActivity", back_populates="user", cascade="all, delete-orphan")

    # Relacionamentos de analytics
    analytics_events = relationship("AnalyticsEvent", back_populates="user", cascade="all, delete-orphan")
    behavior_metrics = relationship("UserBehaviorMetric", back_populates="user", cascade="all, delete-orphan")
    analytics_dashboards = relationship(
        "AnalyticsDashboard",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="AnalyticsDashboard.user_id",
    )
    
    # Relacionamento para alertas de analytics
    analytics_alerts = relationship("AnalyticsAlert", back_populates="owner", cascade="all, delete-orphan")
    
    # Relacionamento para exports de analytics
    analytics_exports = relationship("AnalyticsExport", back_populates="owner", cascade="all, delete-orphan")
    
    # Relacionamento para reports de analytics
    analytics_reports = relationship("AnalyticsReport", back_populates="owner", cascade="all, delete-orphan")
    
    # Relacionamento para execuções de reports
    report_executions = relationship("ReportExecution", back_populates="user", cascade="all, delete-orphan")

    # Relacionamento de assinatura (uma para um)
    subscription = relationship(
        "UserSubscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        overlaps="subscriptions"
    )

    # Project relationships
    project_versions = relationship("ProjectVersion", back_populates="user", cascade="all, delete-orphan")

    # Novos relacionamentos LLM
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    billing_events = relationship("BillingEvent", back_populates="user", cascade="all, delete-orphan")
    message_feedbacks = relationship("MessageFeedback", back_populates="user", cascade="all, delete-orphan")
    created_tags = relationship("Tag", back_populates="created_by_user", cascade="all, delete-orphan")

    # Relacionamentos de Pagamento - NOVOS MODELS
    payment_customers = relationship("PaymentCustomer", back_populates="user", cascade="all, delete-orphan")
    created_coupons = relationship(
        "Coupon", 
        foreign_keys="Coupon.created_by",
        back_populates="creator",
        cascade="all, delete-orphan"
    )

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="users")
    files = relationship("File", back_populates="user")

    # Relacionamento para ratings de nodes
    node_ratings = relationship("NodeRating", back_populates="user", cascade="all, delete-orphan")
    
    # Relacionamento para fila de execução de workflows
    workflow_queue_entries = relationship("WorkflowExecutionQueue", back_populates="user", cascade="all, delete-orphan")

    # Relacionamento para campanhas criadas
    created_campaigns = relationship("Campaign", back_populates="creator", cascade="all, delete-orphan")
    
    # Relacionamento para notas de contatos
    contact_notes = relationship("ContactNote", back_populates="user", cascade="all, delete-orphan")
    
    # Relacionamento para memberships de listas de contatos adicionadas
    added_contact_memberships = relationship("ContactListMembership", back_populates="added_by_user", cascade="all, delete-orphan")
    
    # Relacionamento para relatórios customizados
    custom_reports = relationship("CustomReport", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """Verifica se a senha fornecida está correta"""
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        """Define uma nova senha para o usuário"""
        self.hashed_password = pwd_context.hash(password)

    @property
    def first_name(self) -> str:
        """Compatibilidade: extrai primeiro nome do full_name"""
        if self.full_name:
            return self.full_name.split(" ")[0]
        return ""

    @property
    def last_name(self) -> str:
        """Compatibilidade: extrai sobrenome do full_name"""
        if self.full_name and " " in self.full_name:
            return " ".join(self.full_name.split(" ")[1:])
        return ""

    @property
    def role(self) -> str:
        """Compatibilidade: mapeia is_superuser para role"""
        return "admin" if self.is_superuser else "user"

    @property
    def avatar_url(self) -> str:
        """Compatibilidade: mapeia profile_image_url"""
        return self.profile_image_url or ""

    def get_full_name(self) -> str:
        """Retorna o nome completo do usuário"""
        return self.full_name or self.email

    def has_permission(self, permission: str) -> bool:
        """Verifica se o usuário tem uma permissão específica"""
        role_permissions = {
            "admin": ["*"],
            "user": ["read", "write", "execute"],
            "viewer": ["read"],
        }
        user_permissions = role_permissions.get(self.role, [])
        return "*" in user_permissions or permission in user_permissions

    def to_dict(self) -> dict:
        """Converte o usuário para dicionário (sem dados sensíveis)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,  # property
            "last_name": self.last_name,  # property
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,  # property
            "profile_image_url": self.profile_image_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "role": self.role,  # property
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

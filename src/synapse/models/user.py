"""
Modelo de usuário completo com autenticação e autorização
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from passlib.context import CryptContext
from src.synapse.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")
    subscription_plan = Column(String(50), default="free")
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")
    nodes = relationship("Node", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    # executions = relationship("Execution", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    variables = relationship("UserVariable", back_populates="user", cascade="all, delete-orphan")
    workflow_executions = relationship("WorkflowExecution", back_populates="user", cascade="all, delete-orphan")
    
    # Relacionamentos de templates
    created_templates = relationship("WorkflowTemplate", back_populates="author", cascade="all, delete-orphan")
    template_reviews = relationship("TemplateReview", back_populates="user", cascade="all, delete-orphan")
    template_downloads = relationship("TemplateDownload", back_populates="user", cascade="all, delete-orphan")
    favorite_templates = relationship("TemplateFavorite", back_populates="user", cascade="all, delete-orphan")
    template_collections = relationship("TemplateCollection", back_populates="creator", cascade="all, delete-orphan")
    template_usage = relationship("TemplateUsage", back_populates="user", cascade="all, delete-orphan")
    
    # Relacionamentos de marketplace
    marketplace_components = relationship("MarketplaceComponent", back_populates="author", cascade="all, delete-orphan")
    component_ratings = relationship("ComponentRating", back_populates="user", cascade="all, delete-orphan")
    component_downloads = relationship("ComponentDownload", back_populates="user", cascade="all, delete-orphan")
    component_purchases = relationship("ComponentPurchase", back_populates="user", cascade="all, delete-orphan")
    
    # Relacionamentos de workspaces
    owned_workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    workspace_invitations_sent = relationship("WorkspaceInvitation", foreign_keys="WorkspaceInvitation.inviter_id", back_populates="inviter")
    workspace_invitations_received = relationship("WorkspaceInvitation", foreign_keys="WorkspaceInvitation.invited_user_id", back_populates="invited_user")
    
    # Relacionamentos de analytics
    analytics_events = relationship("AnalyticsEvent", back_populates="user", cascade="all, delete-orphan")
    behavior_metrics = relationship("UserBehaviorMetric", back_populates="user", cascade="all, delete-orphan")
    custom_reports = relationship("CustomReport", back_populates="user", cascade="all, delete-orphan")
    user_insights = relationship("UserInsight", back_populates="user", cascade="all, delete-orphan")
    analytics_dashboards = relationship("AnalyticsDashboard", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        """Verifica se a senha fornecida está correta"""
        return pwd_context.verify(password, self.password_hash)

    def set_password(self, password: str):
        """Define uma nova senha para o usuário"""
        self.password_hash = pwd_context.hash(password)

    @property
    def full_name(self) -> str:
        """Retorna o nome completo do usuário"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

    def has_permission(self, permission: str) -> bool:
        """Verifica se o usuário tem uma permissão específica"""
        role_permissions = {
            "admin": ["*"],
            "user": ["read", "write", "execute"],
            "viewer": ["read"]
        }
        user_permissions = role_permissions.get(self.role, [])
        return "*" in user_permissions or permission in user_permissions

    def to_dict(self) -> dict:
        """Converte o usuário para dicionário (sem dados sensíveis)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "subscription_plan": self.subscription_plan,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    user = relationship("User", back_populates="refresh_tokens")

    def is_expired(self) -> bool:
        """Verifica se o token está expirado"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """Verifica se o token é válido (não expirado e não revogado)"""
        return not self.is_expired() and not self.is_revoked

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def is_expired(self) -> bool:
        """Verifica se o token está expirado"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """Verifica se o token é válido (não expirado e não usado)"""
        return not self.is_expired() and not self.is_used

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def is_expired(self) -> bool:
        """Verifica se o token está expirado"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """Verifica se o token é válido (não expirado e não usado)"""
        return not self.is_expired() and not self.is_used


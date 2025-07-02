"""
Modelos Workspace para Colaboração
Criado por José - um desenvolvedor Full Stack
Sistema avançado de workspaces colaborativos
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Enum,
    text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from synapse.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Import WorkspaceRole and WorkspaceActivity from dedicated modules to avoid conflicts
from synapse.models.workspace_member import WorkspaceRole


class WorkspaceType(PyEnum):
    """Tipos de workspace"""

    INDIVIDUAL = "individual"
    COLLABORATIVE = "collaborative"


class PermissionLevel(PyEnum):
    """Níveis de permissão"""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class Workspace(Base):
    """
    Modelo para workspaces colaborativos
    """

    __tablename__ = "workspaces"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)

    # Tipo do workspace (NOVO CAMPO)
    type = Column(Enum(WorkspaceType), nullable=False, default=WorkspaceType.INDIVIDUAL)

    # Informações básicas
    description = Column(Text)
    avatar_url = Column(String(500))
    color = Column(String(7), default="#3B82F6")  # Cor hex

    # Proprietário
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )



    # Configurações
    is_public = Column(Boolean, nullable=False, server_default=text("false"))
    is_template = Column(Boolean, default=False, nullable=False)
    allow_guest_access = Column(Boolean, default=False, nullable=False)
    require_approval = Column(Boolean, default=True, nullable=False)

    # Limites
    max_members = Column(Integer, default=10)
    max_projects = Column(Integer, default=50)
    max_storage_mb = Column(Integer, default=1000)

    # Configurações de colaboração
    enable_real_time_editing = Column(Boolean, default=True, nullable=False)
    enable_comments = Column(Boolean, default=True, nullable=False)
    enable_chat = Column(Boolean, default=True, nullable=False)
    enable_video_calls = Column(Boolean, default=False, nullable=False)



    # Estatísticas
    member_count = Column(Integer, default=1, nullable=False)
    project_count = Column(Integer, default=0, nullable=False)
    activity_count = Column(Integer, default=0, nullable=False)
    storage_used_mb = Column(Float, default=0.0, nullable=False)

    # Status
    status = Column(
        String(20), default="active", nullable=False
    )  # active, suspended, deleted

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Tenant (required field that was missing!)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    # Notification settings (from real database)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)

    # API usage tracking (from real database)
    api_calls_today = Column(Integer, default=0)
    api_calls_this_month = Column(Integer, default=0)
    last_api_reset_daily = Column(DateTime(timezone=True), server_default=func.now())
    last_api_reset_monthly = Column(DateTime(timezone=True), server_default=func.now())

    # Feature usage tracking (from real database)
    feature_usage_count = Column(JSONB, default=dict)

    # Relacionamentos
    owner = relationship("User", back_populates="owned_workspaces")
    tenant = relationship("Tenant", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("WorkspaceActivity", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("WorkspaceProject", back_populates="workspace", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="workspace", cascade="all, delete-orphan")
    nodes = relationship("Node", back_populates="workspace", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="workspace", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="workspace", cascade="all, delete-orphan")

    # Novos relacionamentos LLM
    usage_logs = relationship("UsageLog", back_populates="workspace", cascade="all, delete-orphan")
    billing_events = relationship("BillingEvent", back_populates="workspace", cascade="all, delete-orphan")
    workspace_features = relationship("WorkspaceFeature", back_populates="workspace", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="workspace", cascade="all, delete-orphan")
    custom_reports = relationship("CustomReport", back_populates="workspace", cascade="all, delete-orphan")
    
    # Relacionamento para dashboards de analytics
    analytics_dashboards = relationship("AnalyticsDashboard", back_populates="workspace", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Workspace(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
        )

    @property
    def is_over_member_limit(self):
        """Verifica se excedeu o limite de membros"""
        return self.member_count > self.max_members

    @property
    def is_over_storage_limit(self):
        """Verifica se excedeu o limite de armazenamento"""
        return self.storage_used_mb > self.max_storage_mb

    def get_member_role(self, user_id):
        """Obtém o papel de um usuário no workspace"""
        # Converter para UUID se necessário
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        if self.owner_id == user_id:
            return WorkspaceRole.OWNER

        member = next((m for m in self.members if m.user_id == user_id), None)
        return WorkspaceRole(member.role) if member else None

    def can_add_member(self) -> bool:
        """Verifica se pode adicionar mais membros baseado nos limites"""
        return self.member_count < (self.max_members or 10)

    def can_create_project(self) -> bool:
        """Verifica se pode criar mais projetos baseado nos limites"""
        return self.project_count < (self.max_projects or 50)

    def can_use_storage(self, additional_mb: float) -> bool:
        """Verifica se pode usar mais armazenamento baseado nos limites"""
        max_storage = self.max_storage_mb or 1000
        return (self.storage_used_mb + additional_mb) <= max_storage

    def get_workspace_limits(self) -> dict:
        """Retorna os limites do workspace"""
        return {
            "max_members": self.max_members,
            "max_projects": self.max_projects,
            "max_storage_mb": self.max_storage_mb,
            "current_members": self.member_count,
            "current_projects": self.project_count,
            "current_storage_mb": self.storage_used_mb,
            "can_add_member": self.can_add_member(),
            "can_create_project": self.can_create_project(),
        }

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "slug": self.slug,
            "type": self.type.value if self.type else WorkspaceType.INDIVIDUAL.value,
            "description": self.description,
            "avatar_url": self.avatar_url,
            "color": self.color,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "owner_name": (
                self.owner.full_name
                if self.owner and hasattr(self.owner, "full_name")
                else None
            ),

            "is_public": self.is_public,
            "allow_guest_access": self.allow_guest_access,
            "require_approval": self.require_approval,
            "max_members": self.max_members,
            "max_projects": self.max_projects,
            "max_storage_mb": self.max_storage_mb,
            "enable_real_time_editing": self.enable_real_time_editing,
            "enable_comments": self.enable_comments,
            "enable_chat": self.enable_chat,
            "enable_video_calls": self.enable_video_calls,
            "member_count": self.member_count,
            "project_count": self.project_count,
            "activity_count": self.activity_count,
            "storage_used_mb": self.storage_used_mb,
            "status": self.status,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "api_calls_today": self.api_calls_today,
            "api_calls_this_month": self.api_calls_this_month,
            "feature_usage_count": self.feature_usage_count,
            "last_activity_at": self.last_activity_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# WorkspaceMember model moved to workspace_member.py to avoid conflicts


# NOTE: WorkspaceProject and related models (ProjectCollaborator, ProjectComment, ProjectVersion) 
# have been moved to separate modules with proper schema configuration to avoid 
# SQLAlchemy registry conflicts and ensure correct database table references.
# 
# Import these models from their respective modules:
# - WorkspaceProject from synapse.models.workspace_project
# - ProjectCollaborator from synapse.models.project_collaborator  
# - ProjectComment from synapse.models.project_comment
# - ProjectVersion from synapse.models.project_version

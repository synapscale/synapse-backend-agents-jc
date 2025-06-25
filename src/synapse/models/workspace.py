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
    __table_args__ = {"schema": "synapscale_db"}

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
    owner_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Plano do workspace (NOVO CAMPO)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

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

    # Configurações de notificação
    notification_settings = Column(JSON, default=dict)

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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    owner = relationship("User", back_populates="owned_workspaces")
    plan = relationship("Plan")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("WorkspaceActivity", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship(
        "WorkspaceProject", back_populates="workspace", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan"
    )
    activities = relationship(
        "WorkspaceActivity", back_populates="workspace", cascade="all, delete-orphan"
    )
    workflows = relationship(
        "Workflow", back_populates="workspace", cascade="all, delete-orphan"
    )
    nodes = relationship(
        "Node", back_populates="workspace", cascade="all, delete-orphan"
    )
    agents = relationship(
        "Agent", back_populates="workspace", cascade="all, delete-orphan"
    )
    conversations = relationship(
        "Conversation", back_populates="workspace", cascade="all, delete-orphan"
    )
    
    # Novos relacionamentos LLM
    usage_logs = relationship("UsageLog", back_populates="workspace", cascade="all, delete-orphan")
    billing_events = relationship("BillingEvent", back_populates="workspace", cascade="all, delete-orphan")

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
        """Verifica se pode adicionar mais membros baseado no plano"""
        if not self.plan:
            return False
        return self.member_count < self.plan.max_members_per_workspace

    def can_create_project(self) -> bool:
        """Verifica se pode criar mais projetos baseado no plano"""
        if not self.plan:
            return False
        return self.project_count < self.plan.max_projects_per_workspace

    def can_use_storage(self, additional_mb: float) -> bool:
        """Verifica se pode usar mais armazenamento baseado no plano"""
        if not self.plan:
            return False
        return (self.storage_used_mb + additional_mb) <= self.plan.max_storage_mb

    def get_plan_limits(self) -> dict:
        """Retorna os limites do plano atual"""
        if not self.plan:
            return {}
        
        return {
            "max_members": self.plan.max_members_per_workspace,
            "max_projects": self.plan.max_projects_per_workspace,
            "max_storage_mb": self.plan.max_storage_mb,
            "current_members": self.member_count,
            "current_projects": self.project_count,
            "current_storage_mb": self.storage_used_mb,
            "can_add_member": self.can_add_member(),
            "can_create_project": self.can_create_project(),
            "features": self.plan.features if self.plan.features else {},
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
            "owner_name": self.owner.full_name if self.owner and hasattr(self.owner, 'full_name') else None,
            "plan_id": str(self.plan_id) if self.plan_id else None,
            "plan_name": self.plan.name if self.plan and hasattr(self.plan, 'name') else None,
            "plan_type": self.plan.type.value if self.plan and hasattr(self.plan, 'type') else None,
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
            "notification_settings": self.notification_settings,
            "member_count": self.member_count,
            "project_count": self.project_count,
            "activity_count": self.activity_count,
            "storage_used_mb": self.storage_used_mb,
            "status": self.status,
            "last_activity_at": self.last_activity_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# WorkspaceMember model moved to workspace_member.py to avoid conflicts


class WorkspaceProject(Base):
    """
    Modelo para projetos dentro de workspaces
    """

    __tablename__ = "workspace_projects"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=False, index=True)

    # Informações do projeto
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7), default="#10B981")

    # Configurações de colaboração
    allow_concurrent_editing = Column(Boolean, default=True, nullable=False)
    auto_save_interval = Column(Integer, default=30)  # segundos
    version_control_enabled = Column(Boolean, default=True, nullable=False)

    # Status
    status = Column(
        String(20), default="active", nullable=False
    )  # active, archived, deleted
    is_template = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # Estatísticas
    collaborator_count = Column(Integer, default=0, nullable=False)
    edit_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_edited_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    workspace = relationship("Workspace", back_populates="projects")
    workflow = relationship("Workflow")
    collaborators = relationship(
        "ProjectCollaborator", back_populates="project", cascade="all, delete-orphan"
    )
    comments = relationship(
        "ProjectComment", back_populates="project", cascade="all, delete-orphan"
    )
    versions = relationship(
        "ProjectVersion", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<WorkspaceProject(id={self.id}, name='{self.name}', workspace_id={self.workspace_id})>"


class ProjectCollaborator(Base):
    """
    Modelo para colaboradores de projeto
    """

    __tablename__ = "project_collaborators"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False, index=True)

    # Permissões específicas do projeto
    can_edit = Column(Boolean, default=True, nullable=False)
    can_comment = Column(Boolean, default=True, nullable=False)
    can_share = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    # Estado de colaboração
    is_online = Column(Boolean, default=False, nullable=False)
    current_cursor_position = Column(JSON)  # Posição do cursor para edição colaborativa
    last_edit_at = Column(DateTime)

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    project = relationship("WorkspaceProject", back_populates="collaborators")
    user = relationship("User")

    def __repr__(self):
        return f"<ProjectCollaborator(project_id={self.project_id}, user_id={self.user_id})>"


class ProjectComment(Base):
    """
    Modelo para comentários em projetos
    """

    __tablename__ = "project_comments"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False, index=True)
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.project_comments.id"), index=True
    )  # Para threads

    # Conteúdo
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text", nullable=False)  # text, markdown

    # Posicionamento (para comentários contextuais)
    node_id = Column(String(36))  # ID do nó comentado
    position_x = Column(Float)
    position_y = Column(Float)

    # Status
    is_resolved = Column(Boolean, default=False, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    resolved_at = Column(DateTime)

    # Relacionamentos
    project = relationship("WorkspaceProject", back_populates="comments")
    user = relationship("User")
    parent = relationship("ProjectComment", remote_side=[id])
    replies = relationship("ProjectComment", back_populates="parent")

    def __repr__(self):
        return f"<ProjectComment(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"


class ProjectVersion(Base):
    """
    Modelo para controle de versão de projetos
    """

    __tablename__ = "project_versions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("synapscale_db.users.id"), nullable=False, index=True)

    # Versão
    version_number = Column(Integer, nullable=False)
    version_name = Column(String(100))
    description = Column(Text)

    # Dados
    workflow_data = Column(JSON, nullable=False)  # Snapshot do workflow
    changes_summary = Column(JSON, default=dict)  # Resumo das mudanças

    # Metadata
    file_size = Column(Integer)
    checksum = Column(String(64))  # SHA-256

    # Status
    is_major = Column(Boolean, default=False, nullable=False)
    is_auto_save = Column(Boolean, default=False, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    project = relationship("WorkspaceProject", back_populates="versions")
    user = relationship("User")

    def __repr__(self):
        return f"<ProjectVersion(id={self.id}, project_id={self.project_id}, version={self.version_number})>"

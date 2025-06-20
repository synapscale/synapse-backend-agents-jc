"""
Modelo de membros de workspace
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from synapse.database import Base
from datetime import datetime, timezone
from enum import Enum
import uuid

class WorkspaceRole(Enum):
    """Roles de membro no workspace"""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class WorkspaceMember(Base):
    """
    Modelo de membro de workspace com relacionamentos e funcionalidades completas
    """
    __tablename__ = "workspace_members"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Role e Status
    role = Column(SQLEnum(WorkspaceRole), nullable=False, default=WorkspaceRole.MEMBER)
    status = Column(String(20), nullable=False, default="active")  # active, inactive, pending
    
    # Configurações pessoais
    is_favorite = Column(Boolean, default=False)
    notification_preferences = Column(JSON, default=dict)  # Preferências de notificação
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")

    def __repr__(self):
        return f"<WorkspaceMember(id={self.id}, workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role.value})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": self.id,
            "workspace_id": str(self.workspace_id),
            "user_id": str(self.user_id),
            "role": self.role.value,
            "status": self.status,
            "is_favorite": self.is_favorite,
            "notification_preferences": self.notification_preferences,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def has_permission(self, permission: str) -> bool:
        """Verifica se o membro tem uma permissão específica"""
        permissions = {
            WorkspaceRole.OWNER: [
                "workspace.delete", "workspace.update", "workspace.invite",
                "member.add", "member.remove", "member.update_role",
                "project.create", "project.delete", "project.update",
                "settings.update", "billing.manage"
            ],
            WorkspaceRole.ADMIN: [
                "workspace.update", "workspace.invite",
                "member.add", "member.remove",
                "project.create", "project.delete", "project.update",
                "settings.update"
            ],
            WorkspaceRole.MEMBER: [
                "workspace.view", "project.create", "project.update",
                "comment.create", "comment.update"
            ],
            WorkspaceRole.VIEWER: [
                "workspace.view", "project.view", "comment.view"
            ]
        }
        
        role_permissions = permissions.get(self.role, [])
        return permission in role_permissions

    def can_manage_member(self, target_member_role: WorkspaceRole) -> bool:
        """Verifica se pode gerenciar um membro com o role especificado"""
        hierarchy = {
            WorkspaceRole.OWNER: 4,
            WorkspaceRole.ADMIN: 3,
            WorkspaceRole.MEMBER: 2,
            WorkspaceRole.VIEWER: 1
        }
        
        current_level = hierarchy.get(self.role, 0)
        target_level = hierarchy.get(target_member_role, 0)
        
        return current_level > target_level

    def update_last_seen(self):
        """Atualiza o timestamp de última visualização"""
        self.last_seen_at = datetime.now(timezone.utc)

    @classmethod
    def create_owner_membership(cls, workspace_id: str, user_id: str):
        """Cria membership de owner"""
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            role=WorkspaceRole.OWNER,
            status="active",
            is_favorite=True,
            notification_preferences={
                "email_notifications": True,
                "push_notifications": True,
                "activity_digest": "daily"
            }
        )

    @classmethod
    def create_member_membership(cls, workspace_id: str, user_id: str, role: WorkspaceRole = WorkspaceRole.MEMBER):
        """Cria membership de membro regular"""
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            status="active",
            is_favorite=False,
            notification_preferences={
                "email_notifications": True,
                "push_notifications": False,
                "activity_digest": "weekly"
            }
        ) 
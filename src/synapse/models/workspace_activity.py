"""
Modelo de atividades de workspace
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from synapse.database import Base
from datetime import datetime, timezone
import uuid

class WorkspaceActivity(Base):
    """
    Modelo de atividade do workspace para auditoria e timeline
    """
    __tablename__ = "workspace_activities"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Dados da atividade
    action = Column(String(100), nullable=False, index=True)  # workspace_created, member_added, etc.
    resource_type = Column(String(50), nullable=False)  # workspace, member, project, etc.
    resource_id = Column(String(255), nullable=True)  # ID do recurso afetado
    description = Column(Text, nullable=False)  # Descrição legível da atividade
    meta_data = Column(JSON, default=dict)  # Dados adicionais da atividade
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relacionamentos
    workspace = relationship("Workspace", back_populates="activities")
    user = relationship("User")

    def __repr__(self):
        return f"<WorkspaceActivity(id={self.id}, action={self.action}, workspace_id={self.workspace_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "description": self.description,
            "meta_data": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create_workspace_activity(
        cls,
        workspace_id: str,
        user_id: str,
        action: str,
        description: str,
        resource_type: str = "workspace",
        resource_id: str = None,
        meta_data: dict = None
    ):
        """Cria uma nova atividade de workspace"""
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id or workspace_id,
            description=description,
            meta_data=meta_data or {}
        )

    @classmethod
    def create_member_activity(
        cls,
        workspace_id: str,
        user_id: str,
        action: str,
        description: str,
        member_id: str,
        meta_data: dict = None
    ):
        """Cria uma atividade relacionada a membros"""
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type="member",
            resource_id=member_id,
            description=description,
            meta_data=meta_data or {}
        )

    @classmethod
    def create_project_activity(
        cls,
        workspace_id: str,
        user_id: str,
        action: str,
        description: str,
        project_id: str,
        meta_data: dict = None
    ):
        """Cria uma atividade relacionada a projetos"""
        return cls(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type="project",
            resource_id=project_id,
            description=description,
            meta_data=meta_data or {}
        ) 
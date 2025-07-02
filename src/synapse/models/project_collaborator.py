"""
Model para Project Collaborators
ALINHADO PERFEITAMENTE COM A TABELA project_collaborators
"""

from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class ProjectCollaborator(Base):
    """Model para colaboradores de projeto - ALINHADO COM project_collaborators TABLE"""
    
    __tablename__ = "project_collaborators"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    can_edit = Column(Boolean, nullable=False)
    can_comment = Column(Boolean, nullable=False)
    can_share = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)
    is_online = Column(Boolean, nullable=False)
    current_cursor_position = Column(JSONB, nullable=True)
    last_edit_at = Column(DateTime(timezone=True), nullable=True)
    added_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relacionamentos
    project = relationship("WorkspaceProject", back_populates="collaborators")
    user = relationship("User")
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<ProjectCollaborator(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": str(self.user_id),
            "can_edit": self.can_edit,
            "can_comment": self.can_comment,
            "can_share": self.can_share,
            "can_delete": self.can_delete,
            "is_online": self.is_online,
            "current_cursor_position": self.current_cursor_position,
            "last_edit_at": self.last_edit_at.isoformat() if self.last_edit_at else None,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def has_edit_permission(self) -> bool:
        """Verifica se tem permissão de edição"""
        return self.can_edit

    def has_comment_permission(self) -> bool:
        """Verifica se tem permissão de comentário"""
        return self.can_comment

    def has_share_permission(self) -> bool:
        """Verifica se tem permissão de compartilhamento"""
        return self.can_share

    def has_delete_permission(self) -> bool:
        """Verifica se tem permissão de exclusão"""
        return self.can_delete

    def is_active_collaborator(self) -> bool:
        """Verifica se é um colaborador ativo (online)"""
        return self.is_online

    def get_permission_level(self):
        """Retorna o nível de permissão"""
        if self.can_delete:
            return "admin"
        elif self.can_edit and self.can_share:
            return "editor"
        elif self.can_edit:
            return "contributor"
        elif self.can_comment:
            return "commenter"
        else:
            return "viewer"

    def set_permission_level(self, level: str):
        """Define o nível de permissão"""
        if level == "admin":
            self.can_edit = True
            self.can_comment = True
            self.can_share = True
            self.can_delete = True
        elif level == "editor":
            self.can_edit = True
            self.can_comment = True
            self.can_share = True
            self.can_delete = False
        elif level == "contributor":
            self.can_edit = True
            self.can_comment = True
            self.can_share = False
            self.can_delete = False
        elif level == "commenter":
            self.can_edit = False
            self.can_comment = True
            self.can_share = False
            self.can_delete = False
        elif level == "viewer":
            self.can_edit = False
            self.can_comment = False
            self.can_share = False
            self.can_delete = False

    def update_cursor_position(self, position: dict):
        """Atualiza a posição do cursor"""
        self.current_cursor_position = position

    def set_online(self):
        """Marca como online"""
        from datetime import datetime, timezone
        self.is_online = True
        self.last_seen_at = datetime.now(timezone.utc)

    def set_offline(self):
        """Marca como offline"""
        from datetime import datetime, timezone
        self.is_online = False
        self.last_seen_at = datetime.now(timezone.utc)

    def record_edit(self):
        """Registra uma edição"""
        from datetime import datetime, timezone
        self.last_edit_at = datetime.now(timezone.utc)
        self.last_seen_at = datetime.now(timezone.utc)

    def get_cursor_coordinates(self):
        """Retorna as coordenadas do cursor"""
        if self.current_cursor_position:
            return {
                "x": self.current_cursor_position.get("x"),
                "y": self.current_cursor_position.get("y"),
                "node_id": self.current_cursor_position.get("node_id")
            }
        return None

    def has_been_active_recently(self, minutes: int = 30) -> bool:
        """Verifica se esteve ativo recentemente"""
        if not self.last_seen_at:
            return False
        
        from datetime import datetime, timedelta, timezone
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return self.last_seen_at >= cutoff_time

    def get_time_since_last_edit(self):
        """Retorna o tempo desde a última edição"""
        if not self.last_edit_at:
            return None
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) - self.last_edit_at

    def get_time_since_last_seen(self):
        """Retorna o tempo desde a última visualização"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) - self.last_seen_at

    @classmethod
    def create_collaborator(
        cls,
        project_id: str,
        user_id: str,
        permission_level: str = "contributor",
        tenant_id: str = None
    ):
        """Cria um novo colaborador"""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        collaborator = cls(
            project_id=project_id,
            user_id=user_id,
            is_online=False,
            added_at=now,
            last_seen_at=now,
            tenant_id=tenant_id
        )
        
        collaborator.set_permission_level(permission_level)
        return collaborator

    def grant_edit_permission(self):
        """Concede permissão de edição"""
        self.can_edit = True

    def revoke_edit_permission(self):
        """Revoga permissão de edição"""
        self.can_edit = False

    def grant_comment_permission(self):
        """Concede permissão de comentário"""
        self.can_comment = True

    def revoke_comment_permission(self):
        """Revoga permissão de comentário"""
        self.can_comment = False

    def grant_share_permission(self):
        """Concede permissão de compartilhamento"""
        self.can_share = True

    def revoke_share_permission(self):
        """Revoga permissão de compartilhamento"""
        self.can_share = False

    def grant_delete_permission(self):
        """Concede permissão de exclusão"""
        self.can_delete = True

    def revoke_delete_permission(self):
        """Revoga permissão de exclusão"""
        self.can_delete = False

    def get_activity_status(self):
        """Retorna o status de atividade"""
        if self.is_online:
            return "online"
        elif self.has_been_active_recently(5):
            return "recently_active"
        elif self.has_been_active_recently(60):
            return "away"
        else:
            return "offline"

    def get_collaboration_stats(self):
        """Retorna estatísticas de colaboração"""
        time_since_added = None
        time_since_last_edit = self.get_time_since_last_edit()
        time_since_last_seen = self.get_time_since_last_seen()
        
        if self.added_at:
            from datetime import datetime, timezone
            time_since_added = datetime.now(timezone.utc) - self.added_at
        
        return {
            "permission_level": self.get_permission_level(),
            "activity_status": self.get_activity_status(),
            "time_since_added": time_since_added,
            "time_since_last_edit": time_since_last_edit,
            "time_since_last_seen": time_since_last_seen,
            "has_cursor_position": self.current_cursor_position is not None
        }

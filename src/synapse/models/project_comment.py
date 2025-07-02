"""
Model para Project Comments
ALINHADO PERFEITAMENTE COM A TABELA project_comments
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class ProjectComment(Base):
    """Model para comentários de projeto - ALINHADO COM project_comments TABLE"""
    
    __tablename__ = "project_comments"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.project_comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False)
    node_id = Column(String(36), nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    is_resolved = Column(Boolean, nullable=False)
    is_edited = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    project = relationship("WorkspaceProject", back_populates="comments")
    user = relationship("User")
    tenant = relationship("Tenant")
    parent_comment = relationship("ProjectComment", remote_side=[id], back_populates="replies")
    replies = relationship("ProjectComment", back_populates="parent_comment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProjectComment(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": str(self.user_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "content": self.content,
            "content_type": self.content_type,
            "node_id": self.node_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "is_resolved": self.is_resolved,
            "is_edited": self.is_edited,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
        }

    def is_top_level_comment(self) -> bool:
        """Verifica se é um comentário de nível superior"""
        return self.parent_id is None

    def is_reply(self) -> bool:
        """Verifica se é uma resposta a outro comentário"""
        return self.parent_id is not None

    def is_comment_resolved(self) -> bool:
        """Verifica se o comentário está resolvido"""
        return self.is_resolved

    def is_comment_edited(self) -> bool:
        """Verifica se o comentário foi editado"""
        return self.is_edited

    def has_position(self) -> bool:
        """Verifica se o comentário tem posição definida"""
        return self.position_x is not None and self.position_y is not None

    def is_node_comment(self) -> bool:
        """Verifica se é um comentário de node específico"""
        return self.node_id is not None

    def is_text_comment(self) -> bool:
        """Verifica se é um comentário de texto"""
        return self.content_type == "text"

    def is_markdown_comment(self) -> bool:
        """Verifica se é um comentário em markdown"""
        return self.content_type == "markdown"

    def resolve_comment(self, user_id: str = None):
        """Resolve o comentário"""
        from datetime import datetime, timezone
        self.is_resolved = True
        self.resolved_at = datetime.now(timezone.utc)

    def unresolve_comment(self):
        """Desfaz a resolução do comentário"""
        self.is_resolved = False
        self.resolved_at = None

    def edit_content(self, new_content: str):
        """Edita o conteúdo do comentário"""
        from datetime import datetime, timezone
        self.content = new_content
        self.is_edited = True
        self.updated_at = datetime.now(timezone.utc)

    def set_position(self, x: float, y: float):
        """Define a posição do comentário"""
        self.position_x = x
        self.position_y = y

    def get_position(self):
        """Retorna a posição do comentário"""
        if self.has_position():
            return {"x": self.position_x, "y": self.position_y}
        return None

    def add_reply(self, user_id: str, content: str, content_type: str = "text", tenant_id: str = None):
        """Adiciona uma resposta ao comentário"""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        reply = ProjectComment(
            project_id=self.project_id,
            user_id=user_id,
            parent_id=self.id,
            content=content,
            content_type=content_type,
            is_resolved=False,
            is_edited=False,
            created_at=now,
            updated_at=now,
            tenant_id=tenant_id
        )
        
        return reply

    def get_reply_count(self):
        """Retorna o número de respostas"""
        return len(self.replies)

    def get_thread_depth(self):
        """Retorna a profundidade do thread"""
        depth = 0
        current = self
        while current.parent_comment:
            depth += 1
            current = current.parent_comment
        return depth

    def get_root_comment(self):
        """Retorna o comentário raiz do thread"""
        current = self
        while current.parent_comment:
            current = current.parent_comment
        return current

    @classmethod
    def create_comment(
        cls,
        project_id: str,
        user_id: str,
        content: str,
        content_type: str = "text",
        node_id: str = None,
        position_x: float = None,
        position_y: float = None,
        parent_id: str = None,
        tenant_id: str = None
    ):
        """Cria um novo comentário"""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        return cls(
            project_id=project_id,
            user_id=user_id,
            content=content,
            content_type=content_type,
            node_id=node_id,
            position_x=position_x,
            position_y=position_y,
            parent_id=parent_id,
            is_resolved=False,
            is_edited=False,
            created_at=now,
            updated_at=now,
            tenant_id=tenant_id
        )

    def get_mentions(self):
        """Extrai menções (@username) do conteúdo"""
        import re
        mentions = re.findall(r'@(\w+)', self.content)
        return mentions

    def get_content_preview(self, max_length: int = 100):
        """Retorna preview do conteúdo"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."

    def get_time_since_creation(self):
        """Retorna tempo desde a criação"""
        if not self.created_at:
            return None
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) - self.created_at

    def get_time_since_resolution(self):
        """Retorna tempo desde a resolução"""
        if not self.resolved_at:
            return None
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) - self.resolved_at

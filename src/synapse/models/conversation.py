"""
Modelo de conversação para chat com agentes
"""

from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, text, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class Conversation(Base):
    __tablename__ = "llms_conversations"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.agents.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workspaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
    )

    # Informações básicas
    title = Column(String(255))
    status = Column(String(50), default="active")  # active, archived, deleted

    # Estatísticas
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    # Contexto e configurações
    context = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)

    # Timestamps
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamentos existentes
    user = relationship("User", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    workspace = relationship("Workspace", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    # Novos relacionamentos LLM
    llms_conversations_turns = relationship(
        "ConversationLLM", back_populates="conversation", cascade="all, delete-orphan"
    )
    usage_logs = relationship(
        "UsageLog", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Conversation(id={self.id}, title={self.title}, user_id={self.user_id})>"
        )

    @property
    def display_title(self):
        """Título para exibição"""
        if self.title:
            return self.title
        elif self.messages:
            # Usar início da primeira mensagem como título
            first_message = self.messages[0].content[:50]
            return f"{first_message}..." if len(first_message) == 50 else first_message
        else:
            return "Nova Conversa"

    def to_dict(self):
        """Converter para dicionário"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "title": self.title,
            "display_title": self.display_title,
            "status": self.status,
            "message_count": self.message_count,
            "total_tokens_used": self.total_tokens_used,
            "context": self.context,
            "settings": self.settings,
            "last_message_at": (
                self.last_message_at.isoformat() if self.last_message_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

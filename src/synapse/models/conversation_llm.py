"""
Modelo ConversationLLM para relacionamento entre conversas e LLMs
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class ConversationLLM(Base):
    __tablename__ = "llms_conversations_turns"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    llm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamps de uso
    first_used_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_used_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Métricas de uso
    message_count = Column(Integer, server_default=text("0"))
    total_input_tokens = Column(Integer, server_default=text("0"))
    total_output_tokens = Column(Integer, server_default=text("0"))
    total_cost_usd = Column(Float, server_default=text("0.0"))

    # Relacionamentos
    conversation = relationship(
        "Conversation", back_populates="llms_conversations_turns"
    )
    llm = relationship("LLM", back_populates="llms_conversations_turns")

    def __repr__(self):
        return f"<ConversationLLM(conversation_id={self.conversation_id}, llm_id={self.llm_id})>"

    @property
    def total_tokens(self):
        """Total de tokens usados"""
        return self.total_input_tokens + self.total_output_tokens

    @property
    def average_cost_per_message(self):
        """Custo médio por mensagem"""
        if self.message_count > 0:
            return self.total_cost_usd / self.message_count
        return 0.0

    @property
    def average_tokens_per_message(self):
        """Tokens médios por mensagem"""
        if self.message_count > 0:
            return self.total_tokens / self.message_count
        return 0.0

    def update_usage(self, input_tokens: int, output_tokens: int, cost: float):
        """Atualiza métricas de uso"""
        self.message_count += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost
        self.last_used_at = func.now()

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "llm_id": str(self.llm_id),
            "first_used_at": (
                self.first_used_at.isoformat() if self.first_used_at else None
            ),
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
            "message_count": self.message_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "average_cost_per_message": self.average_cost_per_message,
            "average_tokens_per_message": self.average_tokens_per_message,
        }

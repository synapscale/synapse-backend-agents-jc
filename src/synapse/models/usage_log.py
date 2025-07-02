"""
Modelo UsageLog para tracking detalhado de uso de LLMs
"""

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    JSON,
    UUID,
    Text,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from synapse.database import Base


class UsageLog(Base):
    __tablename__ = "llms_usage_logs"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    llm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workspaces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Métricas de uso
    input_tokens = Column(Integer, nullable=False, server_default="0")
    output_tokens = Column(Integer, nullable=False, server_default="0")
    total_tokens = Column(Integer, nullable=False, server_default="0")
    cost_usd = Column(Float, nullable=False, server_default="0.0")
    latency_ms = Column(Integer, nullable=True)

    # Dados da API
    api_status_code = Column(Integer, nullable=True)
    api_request_payload = Column(JSON, nullable=True)
    api_response_metadata = Column("metadata", JSON, nullable=True)
    user_api_key_used = Column(Boolean, server_default="false")
    model_settings = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    status = Column(String(20), server_default="success")

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relacionamentos
    message = relationship("Message", back_populates="usage_logs")
    user = relationship("User", back_populates="usage_logs")
    conversation = relationship("Conversation", back_populates="usage_logs")
    llm = relationship("LLM", back_populates="usage_logs")
    workspace = relationship("Workspace", back_populates="usage_logs")
    billing_events = relationship("BillingEvent", back_populates="related_usage_log")

    def __repr__(self):
        return f"<UsageLog(user_id={self.user_id}, llm_id={self.llm_id}, tokens={self.total_tokens})>"

    @property
    def cost_per_token(self):
        """Custo por token"""
        if self.total_tokens > 0:
            return self.cost_usd / self.total_tokens
        return 0.0

    @property
    def efficiency_score(self):
        """Score de eficiência (output/input ratio)"""
        if self.input_tokens > 0:
            return self.output_tokens / self.input_tokens
        return 0.0

    @property
    def was_successful(self):
        """Indica se a operação foi bem-sucedida"""
        return self.status == "success" and self.api_status_code in [200, 201]

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "message_id": str(self.message_id),
            "user_id": str(self.user_id),
            "conversation_id": str(self.conversation_id),
            "llm_id": str(self.llm_id),
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "cost_per_token": self.cost_per_token,
            "efficiency_score": self.efficiency_score,
            "latency_ms": self.latency_ms,
            "api_status_code": self.api_status_code,
            "user_api_key_used": self.user_api_key_used,
            "model_settings": self.model_settings,
            "error_message": self.error_message,
            "status": self.status,
            "was_successful": self.was_successful,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def get_user_usage_stats(cls, db_session, user_id, start_date=None, end_date=None):
        """Obtém estatísticas de uso de um usuário"""
        query = db_session.query(cls).filter(cls.user_id == user_id)

        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)

        logs = query.all()

        return {
            "total_requests": len(logs),
            "total_tokens": sum(log.total_tokens for log in logs),
            "total_cost_usd": sum(log.cost_usd for log in logs),
            "success_rate": (
                len([log for log in logs if log.was_successful]) / len(logs)
                if logs
                else 0
            ),
            "avg_latency_ms": (
                sum(log.latency_ms for log in logs if log.latency_ms)
                / len([log for log in logs if log.latency_ms])
                if logs
                else 0
            ),
        }

    @classmethod
    def get_workspace_usage_stats(
        cls, db_session, workspace_id, start_date=None, end_date=None
    ):
        """Obtém estatísticas de uso de um workspace"""
        query = db_session.query(cls).filter(cls.workspace_id == workspace_id)

        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)

        logs = query.all()

        return {
            "total_requests": len(logs),
            "total_tokens": sum(log.total_tokens for log in logs),
            "total_cost_usd": sum(log.cost_usd for log in logs),
            "unique_users": len(set(log.user_id for log in logs)),
            "success_rate": (
                len([log for log in logs if log.was_successful]) / len(logs)
                if logs
                else 0
            ),
        }

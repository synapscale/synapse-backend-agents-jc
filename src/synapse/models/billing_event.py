"""
Modelo BillingEvent para rastreamento de eventos de cobrança
"""

from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class BillingEvent(Base):
    __tablename__ = "billing_events"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workspaces.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Tipo e valor do evento
    event_type = Column(
        String(50), nullable=False, index=True
    )  # usage, subscription, credit, refund
    amount_usd = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    # Relacionamentos com outras entidades
    related_usage_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms_usage_logs.id", ondelete="SET NULL"),
        nullable=True,
    )
    related_message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.llms_messages.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Dados de pagamento
    invoice_id = Column(String(100), nullable=True)
    payment_provider = Column(String(50), nullable=True)  # stripe, paypal, etc
    payment_transaction_id = Column(String(100), nullable=True)

    # Metadata adicional
    billing_metadata = Column("metadata", JSON, nullable=True)

    # Status do evento
    status = Column(
        String(20), server_default="pending", index=True
    )  # pending, completed, failed, refunded
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relacionamentos
    user = relationship("User", back_populates="billing_events")
    workspace = relationship("Workspace", back_populates="billing_events")
    related_usage_log = relationship("UsageLog", back_populates="billing_events")
    message = relationship("Message", back_populates="billing_events")

    def __repr__(self):
        return f"<BillingEvent(user_id={self.user_id}, event_type={self.event_type}, amount={self.amount_usd})>"

    @property
    def is_completed(self):
        """Verifica se o evento foi completado"""
        return self.status == "completed"

    @property
    def is_pending(self):
        """Verifica se o evento está pendente"""
        return self.status == "pending"

    @property
    def is_failed(self):
        """Verifica se o evento falhou"""
        return self.status == "failed"

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "event_type": self.event_type,
            "amount_usd": self.amount_usd,
            "description": self.description,
            "related_usage_log_id": (
                str(self.related_usage_log_id) if self.related_usage_log_id else None
            ),
            "related_message_id": (
                str(self.related_message_id) if self.related_message_id else None
            ),
            "invoice_id": self.invoice_id,
            "payment_provider": self.payment_provider,
            "payment_transaction_id": self.payment_transaction_id,
            "billing_metadata": self.billing_metadata,
            "status": self.status,
            "is_completed": self.is_completed,
            "is_pending": self.is_pending,
            "is_failed": self.is_failed,
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

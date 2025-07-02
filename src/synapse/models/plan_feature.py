from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid


class PlanFeature(Base):
    __tablename__ = "plan_features"
    __table_args__ = {"schema": "synapscale_db"}

    # Estrutura EXATA do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.features.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_enabled = Column(Boolean, default=True)
    config = Column(JSONB, default={})  # Campo real do banco
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    plan = relationship("Plan", back_populates="plan_features")
    feature = relationship("Feature", back_populates="plan_features")

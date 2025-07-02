from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid


class PlanEntitlement(Base):
    __tablename__ = "plan_entitlements"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

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
    limit_value = Column(Integer)
    is_unlimited = Column(Boolean, default=False)
    entitlement_metadata = Column("metadata", JSONB, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE")
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    plan = relationship("Plan", back_populates="plan_entitlements")
    feature = relationship("Feature", back_populates="plan_entitlements")
    tenant = relationship("Tenant", back_populates="plan_entitlements")

"""Plan Provider Mapping Model"""

from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class PlanProviderMapping(Base):
    """Mapping between plans and payment providers"""
    
    __tablename__ = "plan_provider_mappings"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    plan_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.plans.id"), primary_key=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.payment_providers.id"), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    plan = relationship("synapse.models.plan.Plan", back_populates="provider_mappings")
    provider = relationship("synapse.models.payment_provider.PaymentProvider", back_populates="plan_mappings")
    tenant = relationship("synapse.models.tenant.Tenant", back_populates="plan_provider_mappings")

    def __str__(self):
        return f"PlanProviderMapping(plan_id={self.plan_id}, provider_id={self.provider_id})"

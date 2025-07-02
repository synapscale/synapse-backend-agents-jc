"""User Subscription Model"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class UserSubscription(Base):
    """User subscription management"""
    
    __tablename__ = "user_subscriptions"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.plans.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(50), nullable=True)
    payment_provider = Column(String(50), nullable=True)
    external_subscription_id = Column(String(255), nullable=True)
    billing_cycle = Column(String(20), nullable=True, server_default="monthly")
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    current_workspaces = Column(Integer, nullable=False, server_default="0")
    current_storage_mb = Column(Float, nullable=False, server_default="0.0")
    current_executions_this_month = Column(Integer, nullable=False, server_default="0")
    subscription_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    status = Column(String(50), nullable=True, server_default="active")

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="user_subscriptions")
    tenant = relationship("Tenant", back_populates="user_subscriptions")

    def __str__(self):
        return f"UserSubscription(user_id={self.user_id}, plan_id={self.plan_id}, status={self.status})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == "active" and (self.expires_at is None or self.expires_at > func.now())

    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        return self.billing_cycle == "trial" or (
            self.current_period_start and 
            self.current_period_end and
            (self.current_period_end - self.current_period_start).days <= 30
        )

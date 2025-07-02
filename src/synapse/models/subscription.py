"""Subscription Model"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class Subscription(Base):
    """Tenant subscriptions to plans"""
    
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.plans.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.payment_providers.id"), nullable=True)
    external_subscription_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, server_default="active")
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=True, server_default="false")
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.payment_methods.id"), nullable=True)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.coupons.id"), nullable=True)
    quantity = Column(Integer, nullable=True, server_default="1")
    discount_amount = Column(Numeric, nullable=True, server_default="0")
    tax_percent = Column(Numeric, nullable=True, server_default="0")
    subscription_metadata = Column("metadata", JSONB, nullable=True, server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    provider = relationship("PaymentProvider", back_populates="subscriptions")
    payment_method = relationship("PaymentMethod", back_populates="subscriptions")
    coupon = relationship("Coupon", back_populates="subscriptions")

    def __str__(self):
        return f"Subscription(tenant_id={self.tenant_id}, plan_id={self.plan_id}, status={self.status})"

    @property
    def meta_data(self):
        """Alias for subscription_metadata for API compatibility"""
        return self.subscription_metadata

    @meta_data.setter
    def meta_data(self, value):
        """Setter for meta_data that updates subscription_metadata"""
        self.subscription_metadata = value

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == "active" and not self.is_canceled

    @property
    def is_canceled(self):
        """Check if subscription is canceled"""
        return self.canceled_at is not None or self.ended_at is not None

    @property
    def is_in_trial(self):
        """Check if subscription is in trial period"""
        if not self.trial_start or not self.trial_end:
            return False
        now = func.now()
        return self.trial_start <= now <= self.trial_end

    @property
    def days_until_renewal(self):
        """Get days until next renewal"""
        if not self.current_period_end:
            return None
        
        from datetime import datetime
        if isinstance(self.current_period_end, datetime):
            return (self.current_period_end - datetime.now()).days
        return None

    @property
    def total_amount(self):
        """Calculate total amount including discounts and taxes"""
        if not hasattr(self, 'plan') or not self.plan:
            return 0
        
        base_amount = float(self.plan.price or 0) * (self.quantity or 1)
        discount = float(self.discount_amount or 0)
        tax_rate = float(self.tax_percent or 0) / 100
        
        subtotal = base_amount - discount
        tax_amount = subtotal * tax_rate
        
        return subtotal + tax_amount

    def cancel(self, immediate=False):
        """Cancel subscription"""
        if immediate:
            self.status = "canceled"
            self.canceled_at = func.current_timestamp()
            self.ended_at = func.current_timestamp()
        else:
            self.cancel_at_period_end = True
            self.canceled_at = func.current_timestamp()

    def reactivate(self):
        """Reactivate a canceled subscription"""
        self.status = "active"
        self.cancel_at_period_end = False
        self.canceled_at = None
        self.ended_at = None
        self.updated_at = func.current_timestamp()

    @classmethod
    def get_active_subscription(cls, session, tenant_id):
        """Get active subscription for tenant"""
        return session.query(cls).filter(
            cls.tenant_id == tenant_id,
            cls.status == "active"
        ).first()

    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "plan_id": str(self.plan_id),
            "provider_id": str(self.provider_id) if self.provider_id else None,
            "external_subscription_id": self.external_subscription_id,
            "status": self.status,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "trial_start": self.trial_start.isoformat() if self.trial_start else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "cancel_at_period_end": self.cancel_at_period_end,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "payment_method_id": str(self.payment_method_id) if self.payment_method_id else None,
            "coupon_id": str(self.coupon_id) if self.coupon_id else None,
            "quantity": self.quantity,
            "discount_amount": float(self.discount_amount) if self.discount_amount else 0,
            "tax_percent": float(self.tax_percent) if self.tax_percent else 0,
            "metadata": self.subscription_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

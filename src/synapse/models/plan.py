from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = {"schema": "synapscale_db"}

    # Estrutura EXATA do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    description = Column(Text)
    price_monthly = Column(Float, nullable=False, default=0.0)
    price_yearly = Column(Float, nullable=False, default=0.0)
    max_workspaces = Column(Integer, nullable=False, default=1)
    max_members_per_workspace = Column(Integer, nullable=False, default=1)
    max_projects_per_workspace = Column(Integer, nullable=False, default=10)
    max_storage_mb = Column(Integer, nullable=False, default=100)
    max_executions_per_month = Column(Integer, nullable=False, default=100)
    allow_collaborative_workspaces = Column(Boolean, nullable=False, default=False)
    allow_custom_domains = Column(Boolean, nullable=False, default=False)
    allow_api_access = Column(Boolean, nullable=False, default=False)
    allow_advanced_analytics = Column(Boolean, nullable=False, default=False)
    allow_priority_support = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_public = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    status = Column(String, default="active")
    version = Column(String, default="1.0.0")
    sort_order = Column(Integer, default=0)

    # Relationships
    tenants = relationship("Tenant", back_populates="plan")
    user_subscriptions = relationship("UserSubscription", back_populates="plan", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="plan", cascade="all, delete-orphan")
    plan_features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    plan_entitlements = relationship("PlanEntitlement", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "price_monthly": self.price_monthly,
            "price_yearly": self.price_yearly,
            "max_workspaces": self.max_workspaces,
            "max_members_per_workspace": self.max_members_per_workspace,
            "max_projects_per_workspace": self.max_projects_per_workspace,
            "max_storage_mb": self.max_storage_mb,
            "max_executions_per_month": self.max_executions_per_month,
            "allow_collaborative_workspaces": self.allow_collaborative_workspaces,
            "allow_custom_domains": self.allow_custom_domains,
            "allow_api_access": self.allow_api_access,
            "allow_advanced_analytics": self.allow_advanced_analytics,
            "allow_priority_support": self.allow_priority_support,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "status": self.status,
            "version": self.version,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

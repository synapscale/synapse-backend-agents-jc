"""
Modelos de Planos e Assinaturas
Sistema de planos para controle de permissões multi-workspace
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Enum,
    text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from synapse.database import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid


class PlanType(PyEnum):
    """Tipos de plano"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(PyEnum):
    """Status de assinatura"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class Plan(Base):
    """
    Modelo para planos de assinatura
    """
    __tablename__ = "plans"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    type = Column(Enum(PlanType), nullable=False)

    # Informações básicas
    description = Column(Text)
    price_monthly = Column(Float, default=0.0, nullable=False)
    price_yearly = Column(Float, default=0.0, nullable=False)

    # Limites e permissões
    max_workspaces = Column(Integer, default=1, nullable=False)
    max_members_per_workspace = Column(Integer, default=1, nullable=False)
    max_projects_per_workspace = Column(Integer, default=10, nullable=False)
    max_storage_mb = Column(Integer, default=100, nullable=False)
    max_executions_per_month = Column(Integer, default=100, nullable=False)
    
    # Recursos
    allow_collaborative_workspaces = Column(Boolean, default=False, nullable=False)
    allow_custom_domains = Column(Boolean, default=False, nullable=False)
    allow_api_access = Column(Boolean, default=False, nullable=False)
    allow_advanced_analytics = Column(Boolean, default=False, nullable=False)
    allow_priority_support = Column(Boolean, default=False, nullable=False)
    
    # Configurações avançadas
    features = Column(JSON, default=dict)  # Features específicas do plano
    restrictions = Column(JSON, default=dict)  # Restrições específicas

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)  # Visível para novos usuários

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', type={self.type})>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "slug": self.slug,
            "type": self.type.value if self.type else None,
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
            "features": self.features,
            "restrictions": self.restrictions,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class UserSubscription(Base):
    """
    Modelo para assinaturas de usuários
    """
    __tablename__ = "user_subscriptions"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    # Status da assinatura
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Datas importantes
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Informações de pagamento
    payment_method = Column(String(50))  # credit_card, paypal, bank_transfer, etc.
    payment_provider = Column(String(50))  # stripe, paypal, etc.
    external_subscription_id = Column(String(255))  # ID da assinatura no provedor
    
    # Billing
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    
    # Uso atual (para controle de limites)
    current_workspaces = Column(Integer, default=0, nullable=False)
    current_storage_mb = Column(Float, default=0.0, nullable=False)
    current_executions_this_month = Column(Integer, default=0, nullable=False)
    
    # Metadata
    subscription_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")

    def __repr__(self):
        return f"<UserSubscription(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Verifica se a assinatura está ativa"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        
        if self.expires_at and self.expires_at < datetime.now():
            return False
            
        return True

    @property
    def days_until_expiry(self) -> int:
        """Dias até a expiração"""
        if not self.expires_at:
            return -1
        
        delta = self.expires_at - datetime.now()
        return delta.days

    def can_create_workspace(self) -> bool:
        """Verifica se pode criar mais workspaces"""
        return self.current_workspaces < self.plan.max_workspaces

    def can_use_storage(self, additional_mb: float) -> bool:
        """Verifica se pode usar mais armazenamento"""
        return (self.current_storage_mb + additional_mb) <= self.plan.max_storage_mb

    def can_execute_workflow(self) -> bool:
        """Verifica se pode executar mais workflows este mês"""
        return self.current_executions_this_month < self.plan.max_executions_per_month

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "plan_id": str(self.plan_id) if self.plan_id else None,
            "plan": self.plan.to_dict() if self.plan else None,
            "status": self.status.value if self.status else None,
            "started_at": self.started_at,
            "expires_at": self.expires_at,
            "cancelled_at": self.cancelled_at,
            "payment_method": self.payment_method,
            "payment_provider": self.payment_provider,
            "billing_cycle": self.billing_cycle,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end,
            "current_workspaces": self.current_workspaces,
            "current_storage_mb": self.current_storage_mb,
            "current_executions_this_month": self.current_executions_this_month,
            "is_active": self.is_active,
            "days_until_expiry": self.days_until_expiry,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        } 
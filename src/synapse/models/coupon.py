"""
Model para Coupons
ALINHADO PERFEITAMENTE COM A TABELA coupons
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from synapse.database import Base


class Coupon(Base):
    """Model para cupons de desconto - ALINHADO COM coupons TABLE"""
    
    __tablename__ = "coupons"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, server_default="'percentage'::character varying")
    value = Column(Numeric, nullable=False)
    currency = Column(String(3), nullable=True, server_default="'USD'::character varying")
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, nullable=True, server_default="0")
    min_amount = Column(Numeric, nullable=True)
    max_discount = Column(Numeric, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=True, server_default=func.true())
    is_stackable = Column(Boolean, nullable=True, server_default=func.false())
    applicable_plans = Column(JSONB, nullable=True, server_default=func.text("'[]'::jsonb"))
    restrictions = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    coupon_metadata = Column("metadata", JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    creator = relationship("User")
    tenant = relationship("Tenant")
    subscriptions = relationship("Subscription", back_populates="coupon", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Coupon(id={self.id}, code='{self.code}', type='{self.type}', value={self.value})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "value": float(self.value),
            "currency": self.currency,
            "max_uses": self.max_uses,
            "used_count": self.used_count,
            "min_amount": float(self.min_amount) if self.min_amount else None,
            "max_discount": float(self.max_discount) if self.max_discount else None,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_active": self.is_active,
            "is_stackable": self.is_stackable,
            "applicable_plans": self.applicable_plans,
            "restrictions": self.restrictions,
            "metadata": self.coupon_metadata,
            "created_by": str(self.created_by) if self.created_by else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_percentage_discount(self) -> bool:
        """Verifica se é desconto percentual"""
        return self.type == "percentage"

    def is_fixed_discount(self) -> bool:
        """Verifica se é desconto fixo"""
        return self.type == "fixed"

    def is_valid(self) -> bool:
        """Verifica se o cupom está válido"""
        if not self.is_active:
            return False
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        return True

    def is_expired(self) -> bool:
        """Verifica se o cupom está expirado"""
        if not self.valid_until:
            return False
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.valid_until

    def calculate_discount(self, amount: float) -> float:
        """Calcula o desconto para um valor"""
        if not self.is_valid():
            return 0.0
        
        if self.min_amount and amount < float(self.min_amount):
            return 0.0
        
        if self.is_percentage_discount():
            discount = amount * (float(self.value) / 100)
        else:
            discount = float(self.value)
        
        if self.max_discount:
            discount = min(discount, float(self.max_discount))
        
        return discount

    def can_be_applied_to_plan(self, plan_id: str) -> bool:
        """Verifica se pode ser aplicado a um plano específico"""
        if not self.applicable_plans:
            return True  # Se vazio, aplica a todos
        
        return plan_id in self.applicable_plans

    def increment_usage(self):
        """Incrementa o contador de uso"""
        self.used_count = (self.used_count or 0) + 1

    def get_remaining_uses(self):
        """Retorna o número de usos restantes"""
        if not self.max_uses:
            return None  # Ilimitado
        
        return max(0, self.max_uses - (self.used_count or 0))

    def get_usage_percentage(self):
        """Retorna a porcentagem de uso"""
        if not self.max_uses:
            return 0  # Ilimitado
        
        return min(100, ((self.used_count or 0) / self.max_uses) * 100)

    @classmethod
    def create_percentage_coupon(
        cls,
        code: str,
        percentage: float,
        name: str = None,
        max_uses: int = None,
        valid_until = None,
        tenant_id: str = None
    ):
        """Cria um cupom de desconto percentual"""
        return cls(
            code=code,
            name=name,
            type="percentage",
            value=percentage,
            max_uses=max_uses,
            valid_until=valid_until,
            tenant_id=tenant_id
        )

    @classmethod
    def create_fixed_coupon(
        cls,
        code: str,
        amount: float,
        currency: str = "USD",
        name: str = None,
        max_uses: int = None,
        valid_until = None,
        tenant_id: str = None
    ):
        """Cria um cupom de desconto fixo"""
        return cls(
            code=code,
            name=name,
            type="fixed",
            value=amount,
            currency=currency,
            max_uses=max_uses,
            valid_until=valid_until,
            tenant_id=tenant_id
        )

    def deactivate(self):
        """Desativa o cupom"""
        self.is_active = False

    def activate(self):
        """Ativa o cupom"""
        self.is_active = True

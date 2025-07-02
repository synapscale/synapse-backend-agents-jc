"""
Model para Payment Methods
ALINHADO PERFEITAMENTE COM A TABELA payment_methods
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class PaymentMethod(Base):
    """Model para métodos de pagamento - ALINHADO COM payment_methods TABLE"""
    
    __tablename__ = "payment_methods"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    customer_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.payment_customers.id"), nullable=False)
    external_method_id = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    last4 = Column(String(4), nullable=True)
    brand = Column(String(50), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    is_default = Column(Boolean, nullable=True, server_default=func.false())
    is_active = Column(Boolean, nullable=True, server_default=func.true())
    payment_metadata = Column("metadata", JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    customer = relationship("PaymentCustomer", back_populates="payment_methods")
    tenant = relationship("Tenant")
    subscriptions = relationship("Subscription", back_populates="payment_method", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type='{self.type}', last4='{self.last4}', customer_id={self.customer_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "external_method_id": self.external_method_id,
            "type": self.type,
            "last4": self.last4,
            "brand": self.brand,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "metadata": self.payment_metadata,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_card(self) -> bool:
        """Verifica se é método de cartão"""
        return self.type in ["card", "credit_card", "debit_card"]

    def is_bank_account(self) -> bool:
        """Verifica se é conta bancária"""
        return self.type in ["bank_account", "ach", "sepa_debit"]

    def is_digital_wallet(self) -> bool:
        """Verifica se é carteira digital"""
        return self.type in ["paypal", "apple_pay", "google_pay", "amazon_pay"]

    def is_expired(self) -> bool:
        """Verifica se o método de pagamento está expirado"""
        if not self.exp_month or not self.exp_year:
            return False
        
        from datetime import date
        today = date.today()
        
        # Considerar expirado se estamos no mês de expiração ou depois
        if self.exp_year < today.year:
            return True
        elif self.exp_year == today.year and self.exp_month < today.month:
            return True
        
        return False

    def is_valid(self) -> bool:
        """Verifica se o método de pagamento é válido"""
        return self.is_active and not self.is_expired()

    def get_display_name(self):
        """Retorna nome para exibição"""
        if self.is_card():
            brand_name = self.brand.title() if self.brand else "Card"
            return f"{brand_name} ****{self.last4}"
        elif self.is_bank_account():
            return f"Bank Account ****{self.last4}"
        elif self.is_digital_wallet():
            return self.type.replace("_", " ").title()
        else:
            return self.type.title()

    def get_card_brand_display(self):
        """Retorna a marca do cartão de forma legível"""
        brand_map = {
            "visa": "Visa",
            "mastercard": "Mastercard",
            "amex": "American Express",
            "discover": "Discover",
            "diners": "Diners Club",
            "jcb": "JCB",
            "unionpay": "UnionPay"
        }
        return brand_map.get(self.brand.lower() if self.brand else "", self.brand or "Unknown")

    def set_as_default(self, session):
        """Define este método como padrão"""
        # Remover default de outros métodos do mesmo cliente
        other_methods = session.query(PaymentMethod).filter(
            PaymentMethod.customer_id == self.customer_id,
            PaymentMethod.id != self.id
        ).all()
        
        for method in other_methods:
            method.is_default = False
        
        self.is_default = True

    def deactivate(self):
        """Desativa o método de pagamento"""
        self.is_active = False
        if self.is_default:
            self.is_default = False

    def activate(self):
        """Ativa o método de pagamento"""
        self.is_active = True

    def update_expiration(self, exp_month: int, exp_year: int):
        """Atualiza a data de expiração"""
        self.exp_month = exp_month
        self.exp_year = exp_year

    def get_expiration_display(self):
        """Retorna a expiração formatada"""
        if self.exp_month and self.exp_year:
            return f"{self.exp_month:02d}/{self.exp_year}"
        return ""

    @classmethod
    def create_card_method(
        cls,
        customer_id: str,
        external_method_id: str,
        last4: str,
        brand: str,
        exp_month: int,
        exp_year: int,
        is_default: bool = False,
        tenant_id: str = None
    ):
        """Cria um método de pagamento de cartão"""
        return cls(
            customer_id=customer_id,
            external_method_id=external_method_id,
            type="card",
            last4=last4,
            brand=brand.lower(),
            exp_month=exp_month,
            exp_year=exp_year,
            is_default=is_default,
            tenant_id=tenant_id
        )

    @classmethod
    def create_bank_account_method(
        cls,
        customer_id: str,
        external_method_id: str,
        last4: str,
        is_default: bool = False,
        tenant_id: str = None
    ):
        """Cria um método de pagamento de conta bancária"""
        return cls(
            customer_id=customer_id,
            external_method_id=external_method_id,
            type="bank_account",
            last4=last4,
            is_default=is_default,
            tenant_id=tenant_id
        )

    @classmethod
    def create_digital_wallet_method(
        cls,
        customer_id: str,
        external_method_id: str,
        wallet_type: str,
        email: str = None,
        is_default: bool = False,
        tenant_id: str = None
    ):
        """Cria um método de pagamento de carteira digital"""
        metadata = {"email": email} if email else {}
        
        return cls(
            customer_id=customer_id,
            external_method_id=external_method_id,
            type=wallet_type,
            is_default=is_default,
            payment_metadata=metadata,
            tenant_id=tenant_id
        )

    def get_months_until_expiration(self):
        """Retorna quantos meses até a expiração"""
        if not self.exp_month or not self.exp_year:
            return None
        
        from datetime import date
        today = date.today()
        
        months = (self.exp_year - today.year) * 12 + (self.exp_month - today.month)
        return max(0, months)

    def is_expiring_soon(self, months_threshold: int = 2) -> bool:
        """Verifica se vai expirar em breve"""
        months_left = self.get_months_until_expiration()
        return months_left is not None and months_left <= months_threshold

"""
Model para Payment Customers
ALINHADO PERFEITAMENTE COM A TABELA payment_customers
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class PaymentCustomer(Base):
    """Model para clientes de pagamento - ALINHADO COM payment_customers TABLE"""
    
    __tablename__ = "payment_customers"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.payment_providers.id"), nullable=False)
    external_customer_id = Column(String(255), nullable=False, index=True)
    customer_data = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    is_active = Column(Boolean, nullable=True, server_default=func.true())
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Campo opcional para associação direta com usuário
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("synapscale_db.users.id"), 
        nullable=True,
        comment="Link opcional para usuário específico"
    )

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="payment_customers")
    provider = relationship("PaymentProvider", back_populates="customers")
    payment_methods = relationship("PaymentMethod", back_populates="customer", cascade="all, delete-orphan")
    
    # Relacionamento opcional com usuário
    user = relationship("User", back_populates="payment_customers")

    def __repr__(self):
        return f"<PaymentCustomer(id={self.id}, tenant_id={self.tenant_id}, external_id='{self.external_customer_id}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "provider_id": str(self.provider_id),
            "external_customer_id": self.external_customer_id,
            "customer_data": self.customer_data,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_active_customer(self) -> bool:
        """Verifica se o cliente está ativo"""
        return self.is_active

    def get_customer_email(self):
        """Retorna o email do cliente dos dados"""
        if self.customer_data:
            return self.customer_data.get("email")
        return None

    def get_customer_name(self):
        """Retorna o nome do cliente dos dados"""
        if self.customer_data:
            return self.customer_data.get("name") or self.customer_data.get("full_name")
        return None

    def get_customer_phone(self):
        """Retorna o telefone do cliente dos dados"""
        if self.customer_data:
            return self.customer_data.get("phone")
        return None

    def get_default_payment_method(self):
        """Retorna o método de pagamento padrão"""
        for method in self.payment_methods:
            if method.is_default and method.is_active:
                return method
        return None

    def get_active_payment_methods(self):
        """Retorna todos os métodos de pagamento ativos"""
        return [method for method in self.payment_methods if method.is_active]

    def update_customer_data(self, new_data: dict):
        """Atualiza os dados do cliente"""
        if self.customer_data:
            self.customer_data.update(new_data)
        else:
            self.customer_data = new_data

    def deactivate(self):
        """Desativa o cliente"""
        self.is_active = False

    def activate(self):
        """Ativa o cliente"""
        self.is_active = True

    @classmethod
    def create_customer(
        cls,
        tenant_id: str,
        provider_id: str,
        external_customer_id: str,
        customer_data: dict = None
    ):
        """Cria um novo cliente de pagamento"""
        return cls(
            tenant_id=tenant_id,
            provider_id=provider_id,
            external_customer_id=external_customer_id,
            customer_data=customer_data or {}
        )

    @classmethod
    def find_by_external_id(cls, session, external_customer_id: str, provider_id: str):
        """Busca cliente pelo ID externo e provider"""
        return session.query(cls).filter(
            cls.external_customer_id == external_customer_id,
            cls.provider_id == provider_id
        ).first()

    def has_valid_payment_method(self) -> bool:
        """Verifica se tem pelo menos um método de pagamento válido"""
        return any(method.is_active for method in self.payment_methods)

    def get_subscription_count(self, session):
        """Retorna o número de assinaturas ativas"""
        # Implementação dependeria do model de subscriptions
        return 0

    def get_total_spent(self, session):
        """Retorna o total gasto pelo cliente"""
        # Implementação dependeria do model de invoices/payments
        return 0.0

"""
Model para Payment Providers
ALINHADO PERFEITAMENTE COM A TABELA payment_providers
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class PaymentProvider(Base):
    """Model para provedores de pagamento - ALINHADO COM payment_providers TABLE"""
    
    __tablename__ = "payment_providers"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=True, server_default=func.true())
    config = Column(JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    webhook_secret = Column(String(255), nullable=True)
    api_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="payment_providers")
    customers = relationship("PaymentCustomer", back_populates="provider", cascade="all, delete-orphan")
    plan_mappings = relationship("PlanProviderMapping", back_populates="provider", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="provider", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PaymentProvider(id={self.id}, name='{self.name}', display_name='{self.display_name}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "config": self.config,
            "webhook_secret": self.webhook_secret,
            "api_version": self.api_version,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_active_provider(self) -> bool:
        """Verifica se o provedor está ativo"""
        return self.is_active

    def get_api_key(self):
        """Retorna a chave da API"""
        if self.config:
            return self.config.get("api_key")
        return None

    def get_secret_key(self):
        """Retorna a chave secreta"""
        if self.config:
            return self.config.get("secret_key")
        return None

    def get_public_key(self):
        """Retorna a chave pública"""
        if self.config:
            return self.config.get("public_key")
        return None

    def get_webhook_url(self):
        """Retorna a URL do webhook"""
        if self.config:
            return self.config.get("webhook_url")
        return None

    def get_api_base_url(self):
        """Retorna a URL base da API"""
        if self.config:
            return self.config.get("api_base_url")
        return None

    def is_stripe(self) -> bool:
        """Verifica se é o provedor Stripe"""
        return self.name.lower() == "stripe"

    def is_paypal(self) -> bool:
        """Verifica se é o provedor PayPal"""
        return self.name.lower() == "paypal"

    def is_square(self) -> bool:
        """Verifica se é o provedor Square"""
        return self.name.lower() == "square"

    def supports_subscriptions(self) -> bool:
        """Verifica se suporta assinaturas"""
        if self.config:
            return self.config.get("supports_subscriptions", True)
        return True

    def supports_webhooks(self) -> bool:
        """Verifica se suporta webhooks"""
        return self.webhook_secret is not None

    def update_config(self, new_config: dict):
        """Atualiza a configuração"""
        if self.config:
            self.config.update(new_config)
        else:
            self.config = new_config

    def set_webhook_secret(self, secret: str):
        """Define o segredo do webhook"""
        self.webhook_secret = secret

    def activate(self):
        """Ativa o provedor"""
        self.is_active = True

    def deactivate(self):
        """Desativa o provedor"""
        self.is_active = False

    @classmethod
    def create_stripe_provider(
        cls,
        display_name: str = "Stripe",
        api_key: str = None,
        secret_key: str = None,
        webhook_secret: str = None,
        tenant_id: str = None
    ):
        """Cria um provedor Stripe"""
        config = {
            "api_key": api_key,
            "secret_key": secret_key,
            "supports_subscriptions": True,
            "supports_webhooks": True,
            "api_base_url": "https://api.stripe.com"
        }
        
        return cls(
            name="stripe",
            display_name=display_name,
            config=config,
            webhook_secret=webhook_secret,
            api_version="2023-10-16",
            tenant_id=tenant_id
        )

    @classmethod
    def create_paypal_provider(
        cls,
        display_name: str = "PayPal",
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None
    ):
        """Cria um provedor PayPal"""
        config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "supports_subscriptions": True,
            "supports_webhooks": True,
            "api_base_url": "https://api.paypal.com"
        }
        
        return cls(
            name="paypal",
            display_name=display_name,
            config=config,
            tenant_id=tenant_id
        )

    def get_customer_count(self, session):
        """Retorna o número de clientes ativos"""
        return session.query(PaymentCustomer).filter(
            PaymentCustomer.provider_id == self.id,
            PaymentCustomer.is_active == True
        ).count()

    def get_transaction_volume(self, session, start_date=None, end_date=None):
        """Retorna o volume de transações"""
        # Implementação dependeria do model de transactions
        return 0.0

    @classmethod
    def get_active_providers(cls, session, tenant_id: str = None):
        """Retorna todos os provedores ativos"""
        query = session.query(cls).filter(cls.is_active == True)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        return query.all()

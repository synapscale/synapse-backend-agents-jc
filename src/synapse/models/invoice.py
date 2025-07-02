"""
Model para Invoices
ALINHADO PERFEITAMENTE COM A TABELA invoices
"""

from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from decimal import Decimal
from synapse.database import Base


class Invoice(Base):
    """Model para faturas - ALINHADO COM invoices TABLE"""
    
    __tablename__ = "invoices"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.subscriptions.id"), nullable=True)
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, server_default="'draft'::character varying")
    currency = Column(String(3), nullable=False, server_default="'USD'::character varying")
    subtotal = Column(Numeric, nullable=False, server_default="0")
    tax_amount = Column(Numeric, nullable=False, server_default="0")
    discount_amount = Column(Numeric, nullable=False, server_default="0")
    total_amount = Column(Numeric, nullable=False, server_default="0")
    due_date = Column(Date, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    items = Column(JSONB, nullable=True, server_default=func.text("'[]'::jsonb"))
    invoice_metadata = Column("metadata", JSONB, nullable=True, server_default=func.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Campo opcional para integração com sistema de pagamento
    payment_customer_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("synapscale_db.payment_customers.id"), 
        nullable=True,
        comment="Link opcional para customer de pagamento"
    )

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="invoices")
    subscription = relationship("Subscription")
    
    # Relacionamento opcional com sistema de pagamento
    payment_customer = relationship("PaymentCustomer", backref="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}', total={self.total_amount})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "subscription_id": str(self.subscription_id) if self.subscription_id else None,
            "invoice_number": self.invoice_number,
            "status": self.status,
            "currency": self.currency,
            "subtotal": float(self.subtotal),
            "tax_amount": float(self.tax_amount),
            "discount_amount": float(self.discount_amount),
            "total_amount": float(self.total_amount),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "items": self.items,
            "metadata": self.invoice_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_draft(self) -> bool:
        """Verifica se a fatura está em rascunho"""
        return self.status == "draft"

    def is_sent(self) -> bool:
        """Verifica se a fatura foi enviada"""
        return self.status == "sent"

    def is_paid(self) -> bool:
        """Verifica se a fatura está paga"""
        return self.status == "paid"

    def is_overdue(self) -> bool:
        """Verifica se a fatura está vencida"""
        if self.status == "paid":
            return False
        
        if not self.due_date:
            return False
        
        from datetime import date
        return date.today() > self.due_date

    def is_cancelled(self) -> bool:
        """Verifica se a fatura foi cancelada"""
        return self.status == "cancelled"

    def calculate_total(self):
        """Calcula o total da fatura"""
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount

    def add_item(self, description: str, quantity: int, unit_price: float, tax_rate: float = 0.0):
        """Adiciona um item à fatura"""
        if not self.items:
            self.items = []
        
        item = {
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "tax_rate": tax_rate,
            "total": quantity * unit_price
        }
        
        self.items.append(item)
        self._recalculate_totals()

    def _recalculate_totals(self):
        """Recalcula os totais baseado nos itens"""
        if not self.items:
            self.subtotal = 0
            self.tax_amount = 0
            self.calculate_total()
            return
        
        subtotal = 0
        tax_amount = 0
        
        for item in self.items:
            item_total = item["quantity"] * item["unit_price"]
            subtotal += item_total
            tax_amount += item_total * (item.get("tax_rate", 0) / 100)
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.calculate_total()

    def mark_as_sent(self):
        """Marca a fatura como enviada"""
        self.status = "sent"

    def mark_as_paid(self):
        """Marca a fatura como paga"""
        from datetime import datetime, timezone
        self.status = "paid"
        self.paid_at = datetime.now(timezone.utc)

    def mark_as_cancelled(self):
        """Marca a fatura como cancelada"""
        self.status = "cancelled"

    def apply_discount(self, amount: float):
        """Aplica desconto à fatura"""
        self.discount_amount += amount
        self.calculate_total()

    def get_status_display(self):
        """Retorna o status de forma legível"""
        status_map = {
            "draft": "Rascunho",
            "sent": "Enviada",
            "paid": "Paga",
            "overdue": "Vencida",
            "cancelled": "Cancelada"
        }
        return status_map.get(self.status, self.status)

    def get_days_until_due(self):
        """Retorna o número de dias até o vencimento"""
        if not self.due_date:
            return None
        
        from datetime import date
        delta = self.due_date - date.today()
        return delta.days

    def get_days_overdue(self):
        """Retorna o número de dias em atraso"""
        if not self.is_overdue():
            return 0
        
        from datetime import date
        delta = date.today() - self.due_date
        return delta.days

    @classmethod
    def generate_invoice_number(cls, session, tenant_id: str):
        """Gera um número único de fatura"""
        from datetime import datetime
        
        # Buscar a última fatura do tenant
        last_invoice = session.query(cls).filter(
            cls.tenant_id == tenant_id
        ).order_by(cls.created_at.desc()).first()
        
        if last_invoice:
            # Extrair número sequencial
            try:
                parts = last_invoice.invoice_number.split("-")
                if len(parts) >= 2:
                    last_num = int(parts[-1])
                    next_num = last_num + 1
                else:
                    next_num = 1
            except:
                next_num = 1
        else:
            next_num = 1
        
        # Formato: INV-YYYYMM-0001
        current_date = datetime.now()
        return f"INV-{current_date.strftime('%Y%m')}-{next_num:04d}"

    @classmethod
    def create_invoice(
        cls,
        tenant_id: str,
        subscription_id: str = None,
        due_days: int = 30,
        currency: str = "USD"
    ):
        """Cria uma nova fatura"""
        from datetime import date, timedelta
        
        return cls(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            due_date=date.today() + timedelta(days=due_days),
            currency=currency
        )

"""
Payment models aggregator - importa todos os modelos relacionados a pagamento
"""

from .payment_provider import PaymentProvider
from .payment_customer import PaymentCustomer
from .payment_method import PaymentMethod

# Exportar para que possam ser importados com from synapse.models.payment import ...
__all__ = [
    'PaymentProvider',
    'PaymentCustomer', 
    'PaymentMethod',
]

# Alias para compatibilidade se houver Invoice em outro lugar
try:
    from .invoice import Invoice
    __all__.append('Invoice')
except ImportError:
    # Se não houver modelo Invoice, criar um placeholder básico
    from sqlalchemy import Column, String, Float, DateTime, Text, UUID, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
    from datetime import datetime
    import uuid

    from synapse.models.base import Base

    class Invoice(Base):
        """Modelo básico de Invoice para compatibilidade"""
        __tablename__ = "invoices"
        
        id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        tenant_id = Column(PostgresUUID(as_uuid=True), nullable=False)
        amount = Column(Float, nullable=False)
        currency = Column(String(3), default="USD")
        status = Column(String(50), default="pending")
        due_date = Column(DateTime, nullable=True)
        paid_at = Column(DateTime, nullable=True)
        items = Column(Text, nullable=True)  # JSON serializado
        metadata = Column(Text, nullable=True)  # JSON serializado
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __all__.append('Invoice') 
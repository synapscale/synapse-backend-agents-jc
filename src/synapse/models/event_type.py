"""
Modelo EventType para tipos de eventos
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class EventType(Base):
    __tablename__ = "event_types"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    category = Column(String(100), nullable=True)  # user, system, business, error, etc.
    severity = Column(String(50), nullable=True)  # info, warning, error, critical
    
    # Schema do evento
    payload_schema = Column(JSON, nullable=True)  # JSON Schema para validação
    required_fields = Column(JSON, nullable=True)  # Lista de campos obrigatórios
    
    # Processamento
    should_alert = Column(Boolean, default=False)  # Se deve gerar alertas
    should_log = Column(Boolean, default=True)  # Se deve fazer log
    retention_days = Column(String(10), nullable=True)  # Tempo de retenção
    
    # Métricas
    generates_metrics = Column(Boolean, default=False)  # Se gera métricas
    metric_config = Column(JSON, nullable=True)  # Configuração de métricas
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Se é um evento do sistema
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EventType(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "payload_schema": self.payload_schema,
            "required_fields": self.required_fields,
            "should_alert": self.should_alert,
            "should_log": self.should_log,
            "retention_days": self.retention_days,
            "generates_metrics": self.generates_metrics,
            "metric_config": self.metric_config,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

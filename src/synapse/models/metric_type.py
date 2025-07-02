"""
Modelo MetricType para tipos de métricas
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class MetricType(Base):
    __tablename__ = "metric_types"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    category = Column(String(100), nullable=True)  # performance, usage, business, etc.
    unit = Column(String(50), nullable=True)  # count, percentage, seconds, etc.
    data_type = Column(String(50), nullable=False, default="number")  # number, boolean, string
    
    # Agregação
    aggregation_method = Column(String(50), nullable=True)  # sum, avg, max, min, count
    aggregation_window = Column(String(50), nullable=True)  # hour, day, week, month
    
    # Configuração de coleta
    collection_config = Column(JSON, nullable=True)
    validation_rules = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Se é uma métrica do sistema
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MetricType(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "unit": self.unit,
            "data_type": self.data_type,
            "aggregation_method": self.aggregation_method,
            "aggregation_window": self.aggregation_window,
            "collection_config": self.collection_config,
            "validation_rules": self.validation_rules,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

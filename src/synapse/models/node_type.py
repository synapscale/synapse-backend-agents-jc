"""
Modelo NodeType para tipos de nós
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class NodeType(Base):
    __tablename__ = "node_types"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    category = Column(String(100), nullable=True)  # input, output, processing, etc.
    config_schema = Column(JSON, nullable=True)
    default_config = Column(JSON, nullable=True)
    
    # UI
    icon = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    
    # Capacidades
    can_have_inputs = Column(Boolean, default=True)
    can_have_outputs = Column(Boolean, default=True)
    max_inputs = Column(String(10), nullable=True)  # "1", "many", etc.
    max_outputs = Column(String(10), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NodeType(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "icon": self.icon,
            "color": self.color,
            "can_have_inputs": self.can_have_inputs,
            "can_have_outputs": self.can_have_outputs,
            "max_inputs": self.max_inputs,
            "max_outputs": self.max_outputs,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

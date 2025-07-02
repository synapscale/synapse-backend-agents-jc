"""
Modelo NodeTemplate para templates de nós de workflow
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class NodeTemplate(Base):
    __tablename__ = "node_templates"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    node_type = Column(String(100), nullable=False)  # api, webhook, condition, etc.
    config_schema = Column(JSON, nullable=True)
    default_config = Column(JSON, nullable=True)
    
    # Metadados
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    icon = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NodeTemplate(name='{self.name}', type='{self.node_type}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "node_type": self.node_type,
            "config_schema": self.config_schema,
            "default_config": self.default_config,
            "category": self.category,
            "tags": self.tags,
            "icon": self.icon,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

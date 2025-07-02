"""
Modelo AgentType para tipos de agentes
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class AgentType(Base):
    __tablename__ = "agent_types"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    category = Column(String(100), nullable=True)  # chatbot, automation, analytics, etc.
    capabilities = Column(JSON, nullable=True)  # Lista de capacidades
    default_config = Column(JSON, nullable=True)
    
    # UI
    icon = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    
    # Recursos
    requires_training = Column(Boolean, default=False)
    supports_knowledge_base = Column(Boolean, default=True)
    supports_tools = Column(Boolean, default=True)
    supports_webhooks = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AgentType(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "capabilities": self.capabilities,
            "default_config": self.default_config,
            "icon": self.icon,
            "color": self.color,
            "requires_training": self.requires_training,
            "supports_knowledge_base": self.supports_knowledge_base,
            "supports_tools": self.supports_tools,
            "supports_webhooks": self.supports_webhooks,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

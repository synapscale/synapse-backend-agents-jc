"""
Modelo NodeTemplate para templates de nós de workflow
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class NodeTemplate(Base):
    __tablename__ = "node_templates"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    category = Column(String(100), nullable=True)
    code_template = Column(Text, nullable=False)
    input_schema = Column(JSON, nullable=False)
    output_schema = Column(JSON, nullable=False)
    parameters_schema = Column(JSON, nullable=True)
    
    # Metadados
    icon = Column(String(255), nullable=True)
    color = Column(String(255), nullable=True)
    documentation = Column(Text, nullable=True)
    examples = Column(JSON, nullable=True)
    
    # Status
    is_system = Column(Boolean, nullable=True)
    is_active = Column(Boolean, nullable=True)
    
    # Foreign key
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="node_templates")
    
    def __repr__(self):
        return f"<NodeTemplate(name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "code_template": self.code_template,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "parameters_schema": self.parameters_schema,
            "icon": self.icon,
            "color": self.color,
            "documentation": self.documentation,
            "examples": self.examples,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

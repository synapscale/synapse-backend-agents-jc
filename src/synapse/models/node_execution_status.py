"""
Modelo NodeExecutionStatus para status de execução de nós
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class NodeExecutionStatus(Base):
    __tablename__ = "node_execution_statuses"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuração
    color = Column(String(7), nullable=True)  # Hex color
    is_final = Column(Boolean, default=False)  # Se é um status final
    is_error = Column(Boolean, default=False)  # Se indica erro
    is_success = Column(Boolean, default=False)  # Se indica sucesso
    can_retry = Column(Boolean, default=True)  # Se permite retry
    blocks_workflow = Column(Boolean, default=False)  # Se bloqueia o workflow
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NodeExecutionStatus(name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "color": self.color,
            "is_final": self.is_final,
            "is_error": self.is_error,
            "is_success": self.is_success,
            "can_retry": self.can_retry,
            "blocks_workflow": self.blocks_workflow,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

"""
Modelo de Workflow - SINCRONIZADO COM BANCO DE DADOS REAL
Estrutura baseada na tabela synapscale_db.workflows
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base
from enum import Enum as PyEnum


class WorkflowStatus(PyEnum):
    """Status do workflow"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class Workflow(Base):
    __tablename__ = "workflows"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Colunas exatamente como no banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # character varying - no length specified in DB
    description = Column(Text, nullable=True)
    definition = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    workspace_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("synapscale_db.workspaces.id", ondelete="CASCADE"), 
        nullable=True
    )
    is_public = Column(Boolean, nullable=True, server_default=text("false"))
    category = Column(String, nullable=True)  # character varying
    tags = Column(JSONB, nullable=True)  # jsonb in DB, not json
    version = Column(String, nullable=True)  # character varying
    thumbnail_url = Column(String, nullable=True)  # character varying
    downloads_count = Column(Integer, nullable=True)
    rating_average = Column(Integer, nullable=True)
    rating_count = Column(Integer, nullable=True)
    execution_count = Column(Integer, nullable=True)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String, nullable=True, server_default=text("'draft'::character varying"))
    priority = Column(Integer, nullable=True, server_default=text("1"))
    timeout_seconds = Column(Integer, nullable=True, server_default=text("3600"))
    retry_count = Column(Integer, nullable=True, server_default=text("3"))

    # Relacionamentos
    user = relationship("User", back_populates="workflows")
    workspace = relationship("Workspace", back_populates="workflows")
    workflow_nodes = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan"
    )
    connections = relationship(
        "WorkflowConnection", back_populates="workflow", cascade="all, delete-orphan"
    )
    executions = relationship(
        "WorkflowExecution",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
    projects = relationship("WorkspaceProject", back_populates="workflow", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="workflow", cascade="all, delete-orphan")
    templates = relationship("WorkflowTemplate", back_populates="original_workflow", cascade="all, delete-orphan")

    def to_dict(self, include_definition: bool = True) -> dict:
        """Converte workflow para dicionário"""
        data = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "user_id": str(self.user_id) if self.user_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "is_public": self.is_public,
            "category": self.category,
            "tags": self.tags,
            "version": self.version,
            "status": self.status.value,
            "thumbnail_url": self.thumbnail_url,
            "downloads_count": self.downloads_count,
            "rating_average": self.rating_average,
            "rating_count": self.rating_count,
            "execution_count": self.execution_count,
            "last_executed_at": (
                self.last_executed_at.isoformat() if self.last_executed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_definition:
            data["definition"] = self.definition

        return data

    def validate_definition(self) -> bool:
        """Valida a estrutura da definição do workflow"""
        if not isinstance(self.definition, dict):
            return False

        required_keys = ["nodes", "connections"]
        if not all(key in self.definition for key in required_keys):
            return False

        # Validar nodes
        nodes = self.definition.get("nodes", [])
        if not isinstance(nodes, list):
            return False

        # Validar connections
        connections = self.definition.get("connections", [])
        if not isinstance(connections, list):
            return False

        return True

    def get_node_count(self) -> int:
        """Retorna o número de nodes no workflow"""
        return len(self.definition.get("nodes", []))

    def get_connection_count(self) -> int:
        """Retorna o número de conexões no workflow"""
        return len(self.definition.get("connections", []))

    def increment_downloads(self):
        """Incrementa contador de downloads"""
        self.downloads_count += 1

    def increment_executions(self):
        """Incrementa contador de execuções"""
        self.execution_count += 1
        self.last_executed_at = func.now()

    def update_rating(self, new_rating: int):
        """Atualiza rating médio com nova avaliação"""
        total_points = self.rating_average * self.rating_count
        total_points += new_rating
        self.rating_count += 1
        self.rating_average = total_points / self.rating_count

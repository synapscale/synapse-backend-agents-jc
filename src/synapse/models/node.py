"""
Modelo completo de Node com todas as funcionalidades
"""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from synapse.database import Base


class NodeType(enum.Enum):
    """Tipos de nodes disponíveis no sistema."""
    LLM = "llm"
    TRANSFORM = "transform"
    API = "api"
    CONDITION = "condition"
    TRIGGER = "trigger"
    OPERATION = "operation"
    FLOW = "flow"
    INPUT = "input"
    OUTPUT = "output"
    FILE_PROCESSOR = "file_processor"


class NodeStatus(enum.Enum):
    """Status possíveis para um node."""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    PRIVATE = "private"


class Node(Base):
    """Modelo principal para nodes do sistema."""

    __tablename__ = "nodes"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(50), nullable=False, server_default=text("'1.0.0'"))

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workspaces.id"),
        nullable=True,
        index=True,
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=True,
        index=True,
    )

    downloads_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    rating_average = Column(Integer, default=0)

    # Campos adicionais do Node
    type: Column[str] = Column(
        Enum(NodeType, values_callable=lambda x: [e.value for e in x], name="nodetype"),
        nullable=False,
        server_default="operation",
    )
    status: Column[str] = Column(
        Enum(
            NodeStatus,
            values_callable=lambda x: [e.value for e in x],
            name="nodestatus",
        ),
        nullable=False,
        server_default="draft",
    )
    is_public = Column(Boolean, default=False)
    code_template = Column(Text)
    input_schema = Column(JSON, default=dict)
    output_schema = Column(JSON, default=dict)
    parameters_schema = Column(JSON, default=dict)
    icon = Column(String(10), default="🔧")
    color = Column(String(7), default="#6366f1")
    documentation = Column(Text)
    examples = Column(JSON, default=list)
    definition = Column(JSON, nullable=False, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()")
    )

    # Relacionamento com User
    user = relationship("User", back_populates="nodes")

    # Relacionamento com WorkflowNode - REMOVIDO (não há FK no banco real)

    # Relacionamento com Workspace
    workspace = relationship("Workspace", back_populates="nodes")

    # Relacionamento com NodeRating
    ratings = relationship("NodeRating", back_populates="node")

    # Relacionamento com NodeExecution
    executions = relationship("NodeExecution", back_populates="node", cascade="all, delete-orphan")

    # Relacionamento com Tenant
    tenant = relationship("synapse.models.tenant.Tenant", back_populates="nodes")

    def to_dict(self, include_code: bool | None = False) -> dict:
        """Converte node para dicionário"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "category": self.category,
            "user_id": str(self.user_id),
            "workspace_id": (
                str(self.workspace_id) if self.workspace_id is not None else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at is not None else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at is not None else None
            ),
        }

        if include_code:
            data.update(
                {
                    "code_template": self.code_template,
                    "input_schema": self.input_schema,
                    "output_schema": self.output_schema,
                    "parameters_schema": self.parameters_schema,
                }
            )

        return data

    def is_compatible_with(self, other_node: "Node") -> bool:
        """Verifica compatibilidade entre nodes"""
        try:
            # Verificar compatibilidade entre output e input
            my_output = self.output_schema.get("properties", {})
            other_input = other_node.input_schema.get("properties", {})

            # Lista de chaves obrigatórias que devem estar presentes
            required_inputs = other_node.input_schema.get("required", [])

            for required_field in required_inputs:
                if required_field not in my_output:
                    return False

            return True
        except Exception:
            return False

    def update_rating(self, new_rating: int) -> None:
        """Atualiza a avaliação média do node"""
        if not 1 <= new_rating <= 5:
            raise ValueError("Rating deve estar entre 1 e 5")

        current_total = self.rating_average * self.rating_count
        new_total = current_total + new_rating
        self.rating_count += 1
        self.rating_average = new_total / self.rating_count


class NodeTemplate(Base):
    """Template para criação de nodes baseados em padrões predefinidos."""

    __tablename__ = "node_templates"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type: Column[str] = Column(
        Enum(NodeType, values_callable=lambda x: [e.value for e in x], name="nodetype"),
        nullable=False,
    )
    category = Column(String(100))

    # Template de código
    code_template = Column(Text, nullable=False)
    input_schema = Column(JSON, nullable=False)
    output_schema = Column(JSON, nullable=False)
    parameters_schema = Column(JSON, default=dict)

    # Metadados
    icon = Column(String(10), default="🔧")
    color = Column(String(7), default="#6366f1")
    documentation = Column(Text)
    examples = Column(JSON, default=list)

    # Sistema
    is_system = Column(Boolean, default=False)  # Templates do sistema vs usuário
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    rating_count = Column(Integer, default=0)
    rating_average = Column(Integer, default=0)

    def to_dict(self) -> dict:
        """Converte template para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
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
            "rating_count": self.rating_count,
            "rating_average": self.rating_average,
            "created_at": (
                self.created_at.isoformat() if self.created_at is not None else None
            ),
        }

    def create_node_from_template(self, user_id: str, name: str | None = None) -> dict:
        """Cria um novo node baseado neste template"""
        return {
            "name": name or self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "code_template": self.code_template,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "parameters_schema": self.parameters_schema,
            "icon": self.icon,
            "color": self.color,
            "documentation": self.documentation,
            "examples": self.examples,
            "user_id": user_id,
        }

"""
Modelo completo de Node com todas as funcionalidades
"""

from typing import Optional

# Ajuste na ordem dos imports
import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    Integer,
    ForeignKey,
    Enum,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.synapse.database import Base


class NodeType(enum.Enum):
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
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    PRIVATE = "private"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(
        String(50), nullable=False, server_default=text("'1.0.0'")
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        index=True,
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=True,
        index=True,
    )

    downloads_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    rating_average = Column(Integer, default=0)

    def to_dict(self, include_code: Optional[bool] = False) -> dict:
        """Converte node para dicionário"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "category": self.category,
            "user_id": str(self.user_id),
            "workspace_id": (
                str(self.workspace_id)
                if self.workspace_id is not None
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at is not None
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at is not None
                else None
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

            for output_key, output_config in my_output.items():
                if output_key in other_input:
                    output_type = output_config.get("type")
                    input_type = other_input[output_key].get("type")
                    if output_type != input_type:
                        return False

            return True
        except KeyError:
            return False

    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )

    def update_rating(self, new_rating: int):
        """Atualiza rating médio com nova avaliação"""
        if not 1 <= new_rating <= 5:
            raise ValueError("Rating deve estar entre 1 e 5")

        total_points = self.rating_average * self.rating_count
        total_points += new_rating
        self.rating_count += 1
        self.rating_average = total_points / self.rating_count


class NodeTemplate(Base):
    __tablename__ = "node_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(NodeType), nullable=False)
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
    is_system = Column(
        Boolean, default=False  # Templates do sistema vs usuário
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )

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
            "created_at": (
                self.created_at.isoformat()
                if self.created_at is not None
                else None
            ),
        }

    def create_node_from_template(
        self, user_id: str, name: Optional[str] = None
    ) -> dict:
        """Cria um novo node baseado neste template"""
        return {
            "name": name or self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "user_id": user_id,
            "code_template": self.code_template,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "parameters_schema": self.parameters_schema,
            "icon": self.icon,
            "color": self.color,
            "documentation": self.documentation,
            "examples": self.examples,
        }

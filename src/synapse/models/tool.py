"""
Model para Tools
ALINHADO PERFEITAMENTE COM A TABELA tools
"""

from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class Tool(Base):
    """Model para Tools - ALINHADO COM tools TABLE"""

    __tablename__ = "tools"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    tool_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=True)
    base_config = Column(JSONB, nullable=False, server_default=func.text("'{}'::jsonb"))
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamentos
    tenant = relationship("Tenant")
    agent_tools = relationship(
        "AgentTool", back_populates="tool", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tool(tool_id={self.tool_id}, name='{self.name}', category='{self.category}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "tool_id": str(self.tool_id),
            "name": self.name,
            "category": self.category,
            "base_config": self.base_config,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_config_schema(self):
        """Retorna o schema de configuração da ferramenta"""
        return self.base_config.get("schema", {})

    def validate_config(self, config: dict) -> bool:
        """Valida uma configuração contra o schema base"""
        # Implementação básica - pode ser expandida com jsonschema
        required_fields = self.base_config.get("required_fields", [])
        return all(field in config for field in required_fields)

    def get_category_display(self):
        """Retorna a categoria de forma legível"""
        category_map = {
            "search": "Busca",
            "data": "Dados",
            "communication": "Comunicação",
            "analysis": "Análise",
            "automation": "Automação",
            "integration": "Integração",
            "utility": "Utilitários",
            "ai": "Inteligência Artificial",
        }
        return category_map.get(self.category, self.category)

    @classmethod
    def create_tool(
        cls,
        name: str,
        category: str = None,
        base_config: dict = None,
        tenant_id: str = None,
    ):
        """Cria uma nova ferramenta"""
        return cls(
            name=name,
            category=category,
            base_config=base_config or {},
            tenant_id=tenant_id,
        )

    def is_global(self) -> bool:
        """Verifica se é uma ferramenta global"""
        return self.tenant_id is None

    def update_config(self, new_config: dict):
        """Atualiza a configuração base da ferramenta"""
        self.base_config = new_config
        self.updated_at = func.now()

    def get_version(self):
        """Retorna a versão da ferramenta"""
        return self.base_config.get("version", "1.0")

    def is_deprecated(self) -> bool:
        """Verifica se a ferramenta está deprecated"""
        return self.base_config.get("deprecated", False)

    def get_description(self):
        """Retorna a descrição da ferramenta"""
        return self.base_config.get("description", "")

    def get_usage_examples(self):
        """Retorna exemplos de uso da ferramenta"""
        return self.base_config.get("examples", [])

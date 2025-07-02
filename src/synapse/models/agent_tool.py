"""
Model para Agent Tools (relacionamento)
ALINHADO PERFEITAMENTE COM A TABELA agent_tools
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentTool(Base):
    """Model para relacionamento Agent-Tool - ALINHADO COM agent_tools TABLE"""
    
    __tablename__ = "agent_tools"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela (chave composta)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), primary_key=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tools.tool_id"), primary_key=True)
    config = Column(JSONB, nullable=False, server_default=func.text("'{}'::jsonb"))

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")

    def __repr__(self):
        return f"<AgentTool(agent_id={self.agent_id}, tool_id={self.tool_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "agent_id": str(self.agent_id),
            "tool_id": str(self.tool_id),
            "config": self.config,
        }

    def is_enabled(self) -> bool:
        """Verifica se a ferramenta está habilitada para o agente"""
        return self.config.get("enabled", True)

    def get_timeout(self):
        """Retorna o timeout configurado para a ferramenta"""
        return self.config.get("timeout", 30)

    def get_rate_limit(self):
        """Retorna o rate limit configurado"""
        return self.config.get("rate_limit", None)

    def get_priority(self):
        """Retorna a prioridade da ferramenta"""
        return self.config.get("priority", 5)

    def get_permissions(self):
        """Retorna as permissões configuradas"""
        return self.config.get("permissions", [])

    def has_permission(self, permission: str) -> bool:
        """Verifica se tem uma permissão específica"""
        permissions = self.get_permissions()
        return permission in permissions or "*" in permissions

    def update_config(self, new_config: dict):
        """Atualiza a configuração"""
        self.config = {**self.config, **new_config}

    @classmethod
    def create_assignment(
        cls,
        agent_id: str,
        tool_id: str,
        config: dict = None
    ):
        """Cria uma nova atribuição de ferramenta para agente"""
        return cls(
            agent_id=agent_id,
            tool_id=tool_id,
            config=config or {}
        )

    def get_custom_params(self):
        """Retorna parâmetros customizados"""
        return self.config.get("custom_params", {})

    def is_required(self) -> bool:
        """Verifica se a ferramenta é obrigatória para o agente"""
        return self.config.get("required", False)

    def get_usage_limit(self):
        """Retorna o limite de uso configurado"""
        return self.config.get("usage_limit", None)

    def can_use(self, current_usage: int = 0) -> bool:
        """Verifica se a ferramenta pode ser usada"""
        if not self.is_enabled():
            return False
        
        usage_limit = self.get_usage_limit()
        if usage_limit and current_usage >= usage_limit:
            return False
        
        return True

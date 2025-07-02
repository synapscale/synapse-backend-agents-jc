"""
Model para Agent Models (relacionamento)
ALINHADO PERFEITAMENTE COM A TABELA agent_models
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentModel(Base):
    """Model para relacionamento Agent-LLM - ALINHADO COM agent_models TABLE"""
    
    __tablename__ = "agent_models"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela (chave composta)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), primary_key=True)
    llm_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.llms.id"), primary_key=True)
    override = Column(JSONB, nullable=False, server_default=func.text("'{}'::jsonb"))

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_models")
    llm = relationship("LLM", back_populates="agent_models")

    def __repr__(self):
        return f"<AgentModel(agent_id={self.agent_id}, llm_id={self.llm_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "agent_id": str(self.agent_id),
            "llm_id": str(self.llm_id),
            "override": self.override,
        }

    def get_temperature(self):
        """Retorna a temperatura override ou None"""
        return self.override.get("temperature")

    def get_max_tokens(self):
        """Retorna o max_tokens override ou None"""
        return self.override.get("max_tokens")

    def get_top_p(self):
        """Retorna o top_p override ou None"""
        return self.override.get("top_p")

    def get_frequency_penalty(self):
        """Retorna o frequency_penalty override ou None"""
        return self.override.get("frequency_penalty")

    def get_presence_penalty(self):
        """Retorna o presence_penalty override ou None"""
        return self.override.get("presence_penalty")

    def get_stop_sequences(self):
        """Retorna as sequências de parada override"""
        return self.override.get("stop_sequences", [])

    def get_system_prompt_override(self):
        """Retorna o override do system prompt"""
        return self.override.get("system_prompt")

    def is_primary(self) -> bool:
        """Verifica se este é o modelo primário para o agente"""
        return self.override.get("is_primary", False)

    def get_priority(self):
        """Retorna a prioridade do modelo"""
        return self.override.get("priority", 5)

    def get_cost_multiplier(self):
        """Retorna o multiplicador de custo"""
        return self.override.get("cost_multiplier", 1.0)

    def update_override(self, new_override: dict):
        """Atualiza os overrides"""
        self.override = {**self.override, **new_override}

    @classmethod
    def create_assignment(
        cls,
        agent_id: str,
        llm_id: str,
        override: dict = None
    ):
        """Cria uma nova atribuição de modelo para agente"""
        return cls(
            agent_id=agent_id,
            llm_id=llm_id,
            override=override or {}
        )

    def set_as_primary(self):
        """Define este modelo como primário"""
        self.override["is_primary"] = True

    def set_temperature(self, temperature: float):
        """Define a temperatura override"""
        self.override["temperature"] = temperature

    def set_max_tokens(self, max_tokens: int):
        """Define o max_tokens override"""
        self.override["max_tokens"] = max_tokens

    def get_context_window_override(self):
        """Retorna o override da janela de contexto"""
        return self.override.get("context_window")

    def is_enabled_for_function_calling(self) -> bool:
        """Verifica se está habilitado para function calling"""
        return self.override.get("function_calling_enabled", True)

    def get_custom_headers(self):
        """Retorna headers customizados para requisições"""
        return self.override.get("custom_headers", {})

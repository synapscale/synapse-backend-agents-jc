"""
Model para Agent Knowledge Bases (relacionamento)
ALINHADO PERFEITAMENTE COM A TABELA agent_kbs
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentKnowledgeBase(Base):
    """Model para relacionamento Agent-KnowledgeBase - ALINHADO COM agent_kbs TABLE"""

    __tablename__ = "agent_kbs"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela (chave composta)
    agent_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), primary_key=True
    )
    kb_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.knowledge_bases.kb_id"),
        primary_key=True,
    )
    config = Column(JSONB, nullable=False, server_default=func.text("'{}'::jsonb"))

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_knowledge_bases")
    knowledge_base = relationship("KnowledgeBase", back_populates="agent_kbs")

    def __repr__(self):
        return f"<AgentKnowledgeBase(agent_id={self.agent_id}, kb_id={self.kb_id})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "agent_id": str(self.agent_id),
            "kb_id": str(self.kb_id),
            "config": self.config,
        }

    def get_search_weight(self):
        """Retorna o peso de busca configurado"""
        return self.config.get("search_weight", 1.0)

    def get_chunk_size(self):
        """Retorna o tamanho do chunk configurado"""
        return self.config.get("chunk_size", 1000)

    def get_overlap(self):
        """Retorna o overlap configurado"""
        return self.config.get("overlap", 200)

    def is_enabled(self) -> bool:
        """Verifica se a knowledge base está habilitada para o agente"""
        return self.config.get("enabled", True)

    def get_search_strategy(self):
        """Retorna a estratégia de busca configurada"""
        return self.config.get("search_strategy", "semantic")

    def update_config(self, new_config: dict):
        """Atualiza a configuração"""
        self.config = {**self.config, **new_config}

    @classmethod
    def create_assignment(cls, agent_id: str, kb_id: str, config: dict = None):
        """Cria uma nova atribuição de knowledge base para agente"""
        return cls(agent_id=agent_id, kb_id=kb_id, config=config or {})

    def get_priority(self):
        """Retorna a prioridade da knowledge base"""
        return self.config.get("priority", 5)

    def get_max_results(self):
        """Retorna o número máximo de resultados"""
        return self.config.get("max_results", 10)

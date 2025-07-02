"""
Model para Agent Configurations
ALINHADO PERFEITAMENTE COM A TABELA agent_configurations
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentConfiguration(Base):
    """Model para configurações de agentes - ALINHADO COM agent_configurations TABLE"""
    
    __tablename__ = "agent_configurations"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    config_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    version_num = Column(Integer, nullable=False)
    params = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_configurations")
    creator = relationship("User")

    def __repr__(self):
        return f"<AgentConfiguration(config_id={self.config_id}, agent_id={self.agent_id}, version={self.version_num})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "config_id": str(self.config_id),
            "agent_id": str(self.agent_id),
            "version_num": self.version_num,
            "params": self.params,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_param(self, key: str, default=None):
        """Retorna um parâmetro específico"""
        return self.params.get(key, default)

    def set_param(self, key: str, value):
        """Define um parâmetro específico"""
        self.params[key] = value

    def remove_param(self, key: str):
        """Remove um parâmetro"""
        if key in self.params:
            del self.params[key]

    def get_system_prompt(self):
        """Retorna o system prompt"""
        return self.params.get("system_prompt", "")

    def get_temperature(self):
        """Retorna a temperatura"""
        return self.params.get("temperature", 0.7)

    def get_max_tokens(self):
        """Retorna o max_tokens"""
        return self.params.get("max_tokens", 2000)

    def get_tools_config(self):
        """Retorna a configuração de ferramentas"""
        return self.params.get("tools", [])

    def get_knowledge_bases_config(self):
        """Retorna a configuração de knowledge bases"""
        return self.params.get("knowledge_bases", [])

    def is_active(self) -> bool:
        """Verifica se esta configuração está ativa"""
        return self.params.get("active", False)

    def set_as_active(self):
        """Define esta configuração como ativa"""
        self.params["active"] = True

    def set_as_inactive(self):
        """Define esta configuração como inativa"""
        self.params["active"] = False

    @classmethod
    def create_configuration(
        cls,
        agent_id: str,
        version_num: int,
        params: dict,
        created_by: str
    ):
        """Cria uma nova configuração"""
        return cls(
            agent_id=agent_id,
            version_num=version_num,
            params=params,
            created_by=created_by
        )

    def clone_configuration(self, new_version: int, created_by: str):
        """Clona esta configuração para uma nova versão"""
        return self.__class__.create_configuration(
            agent_id=self.agent_id,
            version_num=new_version,
            params=self.params.copy(),
            created_by=created_by
        )

    def get_config_hash(self):
        """Retorna um hash da configuração para comparação"""
        import json
        import hashlib
        config_str = json.dumps(self.params, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    def compare_with(self, other_config):
        """Compara com outra configuração"""
        return self.get_config_hash() == other_config.get_config_hash()

    def get_memory_settings(self):
        """Retorna configurações de memória"""
        return self.params.get("memory", {})

    def get_personality_settings(self):
        """Retorna configurações de personalidade"""
        return self.params.get("personality", {})

    def get_safety_settings(self):
        """Retorna configurações de segurança"""
        return self.params.get("safety", {})

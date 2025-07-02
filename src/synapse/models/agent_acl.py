"""
Model para Agent ACL (Access Control List)
ALINHADO PERFEITAMENTE COM A TABELA agent_acl
"""

from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentACL(Base):
    """Model para controle de acesso de agentes - ALINHADO COM agent_acl TABLE"""
    
    __tablename__ = "agent_acl"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela (chave composta)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), primary_key=True)
    can_read = Column(Boolean, nullable=False, default=True)
    can_write = Column(Boolean, nullable=False, default=False)

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_acl")
    user = relationship("User")

    def __repr__(self):
        return f"<AgentACL(agent_id={self.agent_id}, user_id={self.user_id}, read={self.can_read}, write={self.can_write})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "agent_id": str(self.agent_id),
            "user_id": str(self.user_id),
            "can_read": self.can_read,
            "can_write": self.can_write,
        }

    def has_read_permission(self) -> bool:
        """Verifica se tem permissão de leitura"""
        return self.can_read

    def has_write_permission(self) -> bool:
        """Verifica se tem permissão de escrita"""
        return self.can_write

    def has_full_permission(self) -> bool:
        """Verifica se tem permissão completa"""
        return self.can_read and self.can_write

    def grant_read(self):
        """Concede permissão de leitura"""
        self.can_read = True

    def revoke_read(self):
        """Revoga permissão de leitura"""
        self.can_read = False

    def grant_write(self):
        """Concede permissão de escrita"""
        self.can_write = True

    def revoke_write(self):
        """Revoga permissão de escrita"""
        self.can_write = False

    def grant_full_access(self):
        """Concede acesso completo"""
        self.can_read = True
        self.can_write = True

    def revoke_all_access(self):
        """Revoga todo acesso"""
        self.can_read = False
        self.can_write = False

    @classmethod
    def create_acl(
        cls,
        agent_id: str,
        user_id: str,
        can_read: bool = True,
        can_write: bool = False
    ):
        """Cria uma nova entrada ACL"""
        return cls(
            agent_id=agent_id,
            user_id=user_id,
            can_read=can_read,
            can_write=can_write
        )

    @classmethod
    def create_read_only(cls, agent_id: str, user_id: str):
        """Cria uma entrada ACL apenas de leitura"""
        return cls.create_acl(agent_id, user_id, can_read=True, can_write=False)

    @classmethod
    def create_full_access(cls, agent_id: str, user_id: str):
        """Cria uma entrada ACL com acesso completo"""
        return cls.create_acl(agent_id, user_id, can_read=True, can_write=True)

    def get_permission_level(self):
        """Retorna o nível de permissão como string"""
        if self.can_read and self.can_write:
            return "full"
        elif self.can_read:
            return "read"
        else:
            return "none"

    def set_permission_level(self, level: str):
        """Define o nível de permissão"""
        if level == "full":
            self.grant_full_access()
        elif level == "read":
            self.can_read = True
            self.can_write = False
        elif level == "none":
            self.revoke_all_access()
        else:
            raise ValueError(f"Invalid permission level: {level}")

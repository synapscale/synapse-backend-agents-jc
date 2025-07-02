"""
Model para Agent Triggers
ALINHADO PERFEITAMENTE COM A TABELA agent_triggers
"""

from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from synapse.database import Base


class AgentTrigger(Base):
    """Model para triggers de agentes - ALINHADO COM agent_triggers TABLE"""
    
    __tablename__ = "agent_triggers"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    trigger_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    agent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    trigger_type = Column(Text, nullable=False)  # USER-DEFINED type será tratado como Text
    cron_expr = Column(Text, nullable=True)
    event_name = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    agent = relationship("Agent", back_populates="agent_triggers")

    def __repr__(self):
        return f"<AgentTrigger(trigger_id={self.trigger_id}, agent_id={self.agent_id}, type='{self.trigger_type}')>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "trigger_id": str(self.trigger_id),
            "agent_id": str(self.agent_id),
            "trigger_type": self.trigger_type,
            "cron_expr": self.cron_expr,
            "event_name": self.event_name,
            "active": self.active,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
        }

    def is_cron_trigger(self) -> bool:
        """Verifica se é um trigger baseado em cron"""
        return self.trigger_type == "cron" and self.cron_expr is not None

    def is_event_trigger(self) -> bool:
        """Verifica se é um trigger baseado em evento"""
        return self.trigger_type == "event" and self.event_name is not None

    def is_manual_trigger(self) -> bool:
        """Verifica se é um trigger manual"""
        return self.trigger_type == "manual"

    def is_webhook_trigger(self) -> bool:
        """Verifica se é um trigger de webhook"""
        return self.trigger_type == "webhook"

    def is_active(self) -> bool:
        """Verifica se o trigger está ativo"""
        return self.active

    def activate(self):
        """Ativa o trigger"""
        self.active = True

    def deactivate(self):
        """Desativa o trigger"""
        self.active = False

    def update_last_run(self):
        """Atualiza o timestamp da última execução"""
        from datetime import datetime, timezone
        self.last_run_at = datetime.now(timezone.utc)

    def get_trigger_description(self):
        """Retorna uma descrição legível do trigger"""
        if self.is_cron_trigger():
            return f"Cron: {self.cron_expr}"
        elif self.is_event_trigger():
            return f"Event: {self.event_name}"
        elif self.is_manual_trigger():
            return "Manual"
        elif self.is_webhook_trigger():
            return "Webhook"
        else:
            return f"Type: {self.trigger_type}"

    @classmethod
    def create_cron_trigger(
        cls,
        agent_id: str,
        cron_expr: str,
        active: bool = True
    ):
        """Cria um trigger baseado em cron"""
        return cls(
            agent_id=agent_id,
            trigger_type="cron",
            cron_expr=cron_expr,
            active=active
        )

    @classmethod
    def create_event_trigger(
        cls,
        agent_id: str,
        event_name: str,
        active: bool = True
    ):
        """Cria um trigger baseado em evento"""
        return cls(
            agent_id=agent_id,
            trigger_type="event",
            event_name=event_name,
            active=active
        )

    @classmethod
    def create_manual_trigger(
        cls,
        agent_id: str,
        active: bool = True
    ):
        """Cria um trigger manual"""
        return cls(
            agent_id=agent_id,
            trigger_type="manual",
            active=active
        )

    @classmethod
    def create_webhook_trigger(
        cls,
        agent_id: str,
        active: bool = True
    ):
        """Cria um trigger de webhook"""
        return cls(
            agent_id=agent_id,
            trigger_type="webhook",
            active=active
        )

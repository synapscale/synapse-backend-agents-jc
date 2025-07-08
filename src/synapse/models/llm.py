"""
Modelo LLM para catálogo de modelos LLM disponíveis
"""

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    JSON,
    UUID,
    text,
    ForeignKey,
    Numeric,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from synapse.database import Base


class LLM(Base):
    __tablename__ = "llms"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model_version = Column(String(50), nullable=True)

    # Custos
    cost_per_token_input = Column(Float, nullable=False, server_default=text("0.0"))
    cost_per_token_output = Column(Float, nullable=False, server_default=text("0.0"))

    # Capacidades
    max_tokens_supported = Column(Integer, nullable=True)
    supports_function_calling = Column(Boolean, server_default=text("false"))
    supports_vision = Column(Boolean, server_default=text("false"))
    supports_streaming = Column(Boolean, server_default=text("true"))
    context_window = Column(Integer, nullable=True)

    # Status e metadata
    is_active = Column(Boolean, server_default=text("true"), index=True)
    llm_metadata = Column(JSON, nullable=True)
    
    status = Column(String(20), default="active")
    health_status = Column(String(20), default="healthy")
    response_time_avg_ms = Column(Integer, default=0)
    availability_percentage = Column(Numeric(5,2), default=99.9)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamentos
    llms_conversations_turns = relationship("ConversationLLM", back_populates="llm")
    usage_logs = relationship("UsageLog", back_populates="llm")
    agent_models = relationship("AgentModel", back_populates="llm", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LLM(name={self.name}, provider={self.provider})>"

    @property
    def display_name(self):
        """Nome para exibição"""
        return f"{self.provider.title()} {self.name}"

    @property
    def cost_per_1k_tokens_input(self):
        """Custo por 1000 tokens de input"""
        return self.cost_per_token_input * 1000

    @property
    def cost_per_1k_tokens_output(self):
        """Custo por 1000 tokens de output"""
        return self.cost_per_token_output * 1000

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calcula o custo total para determinado uso"""
        return (input_tokens * self.cost_per_token_input) + (
            output_tokens * self.cost_per_token_output
        )

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "provider": self.provider,
            "model_version": self.model_version,
            "display_name": self.display_name,
            "cost_per_token_input": self.cost_per_token_input,
            "cost_per_token_output": self.cost_per_token_output,
            "cost_per_1k_tokens_input": self.cost_per_1k_tokens_input,
            "cost_per_1k_tokens_output": self.cost_per_1k_tokens_output,
            "max_tokens_supported": self.max_tokens_supported,
            "supports_function_calling": self.supports_function_calling,
            "supports_vision": self.supports_vision,
            "supports_streaming": self.supports_streaming,
            "context_window": self.context_window,
            "is_active": self.is_active,
            "llm_metadata": self.llm_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_provider_and_name(cls, db_session, provider: str, name: str):
        """Busca LLM por provedor e nome"""
        return (
            db_session.query(cls)
            .filter(cls.provider == provider, cls.name == name, cls.is_active == True)
            .first()
        )

    @classmethod
    def get_active_llms(cls, db_session, provider: str = None):
        """Busca LLMs ativos, opcionalmente filtrados por provedor"""
        query = db_session.query(cls).filter(cls.is_active == True)
        if provider:
            query = query.filter(cls.provider == provider)
        return query.all()

    @classmethod
    def get_cheapest_llm(cls, db_session, provider: str = None):
        """Busca o LLM mais barato (baseado em custo de input)"""
        query = db_session.query(cls).filter(cls.is_active == True)
        if provider:
            query = query.filter(cls.provider == provider)
        return query.order_by(cls.cost_per_token_input.asc()).first()

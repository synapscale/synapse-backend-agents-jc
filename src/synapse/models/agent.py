"""
Modelo completo de Agent com todas as funcionalidades
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    JSON,
    Integer,
    ForeignKey,
    Enum,
    Float,
    Boolean,
    DECIMAL,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from synapse.database import Base


class AgentStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    MAINTENANCE = "maintenance"


class AgentType(enum.Enum):
    GENERAL = "general"
    SPECIALIST = "specialist"
    WORKFLOW = "workflow"
    ASSISTANT = "assistant"


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos que existem na estrutura real do banco
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workspaces.id"),
        nullable=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
    )
    status = Column(String, nullable=True, default='active')
    priority = Column(Integer, nullable=True, default=1)
    version = Column(String, nullable=True, default='1.0.0')
    environment = Column(String, nullable=True, default='development')
    current_config = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.agent_configurations.config_id"),
        nullable=True,
    )





    # Relacionamentos
    user = relationship("User", back_populates="agents")
    workspace = relationship("Workspace", back_populates="agents")
    tenant = relationship("Tenant", back_populates="agents")
    conversations = relationship(
        "Conversation", back_populates="agent", cascade="all, delete-orphan"
    )
    
    # Novos relacionamentos para as tabelas de agentes
    agent_acl = relationship("AgentACL", back_populates="agent", cascade="all, delete-orphan")
    agent_configurations = relationship(
        "AgentConfiguration", 
        foreign_keys="[AgentConfiguration.agent_id]",
        back_populates="agent", 
        cascade="all, delete-orphan"
    )
    
    # Relacionamento para a configuração atual
    current_configuration = relationship(
        "AgentConfiguration",
        foreign_keys="[Agent.current_config]",
        post_update=True,  # Evita referência circular
        uselist=False
    )
    error_logs = relationship("AgentErrorLog", back_populates="agent", cascade="all, delete-orphan")
    agent_knowledge_bases = relationship("AgentKnowledgeBase", back_populates="agent", cascade="all, delete-orphan")
    agent_models = relationship("AgentModel", back_populates="agent", cascade="all, delete-orphan")
    agent_quotas = relationship("AgentQuota", back_populates="agent", cascade="all, delete-orphan")
    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    agent_triggers = relationship("AgentTrigger", back_populates="agent", cascade="all, delete-orphan")
    agent_usage_metrics = relationship("AgentUsageMetric", back_populates="agent", cascade="all, delete-orphan")
    
    # Relacionamentos de hierarquia (removendo foreign_keys problemáticos)
    descendants = relationship("AgentHierarchy", back_populates="ancestor_agent", cascade="all, delete-orphan")
    ancestors = relationship("AgentHierarchy", back_populates="descendant_agent", cascade="all, delete-orphan")

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Converte agente para dicionário"""
        data = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "provider": self.provider,
            "model": self.model,
            "model_provider": self.model_provider,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "status": self.status.value,
            "avatar_url": self.avatar_url,
            "conversation_count": self.conversation_count or 0,
            "message_count": self.message_count or 0,
            "rating_average": self.rating_average or 0.0,
            "rating_count": self.rating_count or 0,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": str(self.user_id) if self.user_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "tools": self.tools if self.tools is not None else [],
        }

        if include_sensitive:
            data.update(
                {
                    "personality": self.personality,
                    "instructions": self.instructions,
                    "tools": self.tools,
                    "knowledge_base": self.knowledge_base,
                    "capabilities": self.capabilities,
                    "configuration": self.configuration,
                    "top_p": self.top_p,
                    "frequency_penalty": self.frequency_penalty,
                    "presence_penalty": self.presence_penalty,
                    "total_tokens_used": self.total_tokens_used,
                    "average_response_time": self.average_response_time,
                }
            )

        return data

    def increment_conversation(self):
        """Incrementa contador de conversações"""
        self.conversation_count += 1
        self.last_active_at = func.now()

    def increment_message(self, tokens_used: int = 0, response_time: float = 0.0):
        """Incrementa contador de mensagens e atualiza estatísticas"""
        self.message_count += 1
        self.total_tokens_used += tokens_used

        # Atualizar tempo médio de resposta
        if response_time > 0:
            if self.average_response_time == 0:
                self.average_response_time = response_time
            else:
                # Média móvel simples
                self.average_response_time = (
                    self.average_response_time + response_time
                ) / 2

        self.last_active_at = func.now()

    def update_rating(self, new_rating: float):
        """Atualiza rating médio com nova avaliação"""
        if not 1.0 <= new_rating <= 5.0:
            raise ValueError("Rating deve estar entre 1.0 e 5.0")

        total_points = self.rating_average * self.rating_count
        total_points += new_rating
        self.rating_count += 1
        self.rating_average = total_points / self.rating_count

    def get_llm_config(self) -> dict:
        """Retorna configuração para o LLM"""
        return {
            "provider": self.model_provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

    def get_system_prompt(self) -> str:
        """Gera prompt do sistema baseado na personalidade e instruções"""
        system_prompt = f"Você é {self.name}"

        if self.description:
            system_prompt += f", {self.description}"

        if self.personality:
            system_prompt += f"\n\nPersonalidade: {self.personality}"

        if self.instructions:
            system_prompt += f"\n\nInstruções específicas: {self.instructions}"

        # Adicionar informações sobre ferramentas disponíveis
        if self.tools:
            tools_list = ", ".join(self.tools)
            system_prompt += f"\n\nFerramentas disponíveis: {tools_list}"

        return system_prompt

    def has_tool(self, tool_name: str) -> bool:
        """Verifica se o agente tem uma ferramenta específica"""
        return tool_name in (self.tools or [])

    def add_tool(self, tool_name: str):
        """Adiciona uma ferramenta ao agente"""
        if not self.tools:
            self.tools = []
        if tool_name not in self.tools:
            self.tools.append(tool_name)

    def remove_tool(self, tool_name: str):
        """Remove uma ferramenta do agente"""
        if self.tools and tool_name in self.tools:
            self.tools.remove(tool_name)

    def is_available(self) -> bool:
        """Verifica se o agente está disponível para conversas"""
        return self.status == AgentStatus.ACTIVE

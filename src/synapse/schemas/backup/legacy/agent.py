"""
Schemas Pydantic para agents
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Schemas base
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    agent_type: str = Field(default="conversational")
    personality: str | None = None
    instructions: str | None = None


class AgentCreate(AgentBase):
    model_provider: str = Field(default="openai")
    model: str = Field(default="gpt-4o")
    system_prompt: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=128000)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    frequency_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    tools: list[str] = Field(default_factory=list)
    knowledge_base: dict[str, Any] | None = None
    capabilities: list[str] | None = None
    configuration: dict[str, Any] | None = None
    avatar_url: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    agent_type: str | None = None
    personality: str | None = None
    instructions: str | None = None
    model_provider: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=128000)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    frequency_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(None, ge=-2.0, le=2.0)
    tools: list[str] | None = None
    knowledge_base: dict[str, Any] | None = None
    capabilities: list[str] | None = None
    configuration: dict[str, Any] | None = None
    avatar_url: str | None = None
    status: str | None = None


class AgentResponse(AgentBase):
    id: str
    user_id: str
    tenant_id: str  # CRÍTICO: campo de multi-tenancy
    workspace_id: str | None = None
    model_provider: str
    model: str
    system_prompt: str | None = None
    temperature: float
    max_tokens: int
    status: str
    tools: list[str]
    knowledge_base: dict[str, Any] | None = None
    avatar_url: str | None = None
    conversation_count: int
    message_count: int
    rating_average: float
    rating_count: int
    # Campos adicionais do modelo
    agent_type: str = "general"
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    capabilities: list[str] | None = None
    configuration: dict[str, Any] | None = None
    total_tokens_used: int = 0
    average_response_time: float = 0.0
    last_active_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

    @validator("id", "user_id", "tenant_id", "workspace_id", pre=True)
    def convert_uuid_to_string(cls, v):
        """Converte UUID para string"""
        if v is None:
            return v
        if hasattr(v, "__str__"):
            return str(v)
        return v


class AgentListResponse(BaseModel):
    items: list[AgentResponse]
    total: int
    page: int
    size: int
    pages: int

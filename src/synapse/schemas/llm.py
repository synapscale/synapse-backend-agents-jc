"""Esquemas para integração com modelos de linguagem (LLMs)."""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LLMCapability(str, Enum):
    """Capacidades dos modelos LLM."""
    TEXT = "text"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    CODE = "code"
    REASONING = "reasoning"
    EMBEDDING = "embedding"


class LLMProvider(str, Enum):
    """Provedores de LLM disponíveis."""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"
    GROK = "grok"
    DEEPSEEK = "deepseek"
    TESS = "tess"
    OTHER = "outro"


# Base schemas
class LLMCreate(BaseModel):
    """Schema para criação de LLM."""
    name: str = Field(..., description="Nome do modelo")
    provider: str = Field(..., description="Provedor do modelo")
    model_version: str = Field(..., description="Versão do modelo no provedor")
    description: Optional[str] = Field(None, description="Descrição do modelo")
    capabilities: List[str] = Field(default_factory=list, description="Capacidades do modelo")
    context_window: int = Field(default=0, description="Tamanho do contexto em tokens")
    token_limit: int = Field(default=0, description="Limite de tokens na resposta")
    pricing: Optional[Dict[str, float]] = Field(None, description="Informações de preço")
    is_active: bool = Field(default=True, description="Se o modelo está ativo")
    cost_per_token_input: Optional[float] = Field(None, description="Custo por token de entrada")
    cost_per_token_output: Optional[float] = Field(None, description="Custo por token de saída")
    supports_function_calling: Optional[bool] = Field(None, description="Suporta function calling")
    supports_vision: Optional[bool] = Field(None, description="Suporta visão")
    supports_streaming: Optional[bool] = Field(None, description="Suporta streaming")
    status: Optional[str] = Field(None, description="Status do LLM")
    health_status: Optional[str] = Field(None, description="Status de saúde do LLM")
    response_time_avg_ms: Optional[int] = Field(None, description="Tempo médio de resposta em ms")
    availability_percentage: Optional[float] = Field(None, description="Percentual de disponibilidade")


class LLMUpdate(BaseModel):
    """Schema para atualização de LLM."""
    name: Optional[str] = Field(None, description="Nome do modelo")
    description: Optional[str] = Field(None, description="Descrição do modelo")
    capabilities: Optional[List[str]] = Field(None, description="Capacidades do modelo")
    context_window: Optional[int] = Field(None, description="Tamanho do contexto em tokens")
    token_limit: Optional[int] = Field(None, description="Limite de tokens na resposta")
    pricing: Optional[Dict[str, float]] = Field(None, description="Informações de preço")
    is_active: Optional[bool] = Field(None, description="Se o modelo está ativo")
    cost_per_token_input: Optional[float] = Field(None, description="Custo por token de entrada")
    cost_per_token_output: Optional[float] = Field(None, description="Custo por token de saída")
    supports_function_calling: Optional[bool] = Field(None, description="Suporta function calling")
    supports_vision: Optional[bool] = Field(None, description="Suporta visão")
    supports_streaming: Optional[bool] = Field(None, description="Suporta streaming")
    status: Optional[str] = Field(None, description="Status do LLM")
    health_status: Optional[str] = Field(None, description="Status de saúde do LLM")
    response_time_avg_ms: Optional[int] = Field(None, description="Tempo médio de resposta em ms")
    availability_percentage: Optional[float] = Field(None, description="Percentual de disponibilidade")


class LLMResponse(BaseModel):
    """Schema de resposta para LLM."""
    id: UUID = Field(..., description="ID único do modelo")
    name: str = Field(..., description="Nome do modelo")
    provider: str = Field(..., description="Provedor do modelo")
    model_version: str = Field(..., description="Versão do modelo no provedor")
    description: Optional[str] = Field(None, description="Descrição do modelo")
    capabilities: List[str] = Field(default_factory=list, description="Capacidades do modelo")
    context_window: int = Field(default=0, description="Tamanho do contexto em tokens")
    token_limit: int = Field(default=0, description="Limite de tokens na resposta")
    pricing: Optional[Dict[str, float]] = Field(None, description="Informações de preço")
    is_active: bool = Field(default=True, description="Se o modelo está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    cost_per_token_input: Optional[float] = Field(None, description="Custo por token de entrada")
    cost_per_token_output: Optional[float] = Field(None, description="Custo por token de saída")
    supports_function_calling: Optional[bool] = Field(None, description="Suporta function calling")
    supports_vision: Optional[bool] = Field(None, description="Suporta visão")
    supports_streaming: Optional[bool] = Field(None, description="Suporta streaming")
    status: Optional[str] = Field(None, description="Status do LLM")
    health_status: Optional[str] = Field(None, description="Status de saúde do LLM")
    response_time_avg_ms: Optional[int] = Field(None, description="Tempo médio de resposta em ms")
    availability_percentage: Optional[float] = Field(None, description="Percentual de disponibilidade")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais do LLM")


class LLMListResponse(BaseModel):
    """Schema de resposta para lista de LLMs."""
    items: List[LLMResponse] = Field(..., description="Lista de LLMs")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")
    has_next: bool = Field(..., description="Se há próxima página")
    has_prev: bool = Field(..., description="Se há página anterior")


# Conversation schemas
class LLMConversationCreate(BaseModel):
    """Schema para criação de conversa com LLM."""
    llm_id: UUID = Field(..., description="ID do LLM")
    title: Optional[str] = Field(None, description="Título da conversa")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")
    temperature: float = Field(default=0.7, description="Temperatura para geração")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens na resposta")


class LLMConversationResponse(BaseModel):
    """Schema de resposta para conversa com LLM."""
    id: UUID = Field(..., description="ID único da conversa")
    llm_id: UUID = Field(..., description="ID do LLM")
    user_id: UUID = Field(..., description="ID do usuário")
    title: Optional[str] = Field(None, description="Título da conversa")
    system_prompt: Optional[str] = Field(None, description="Prompt do sistema")
    temperature: float = Field(default=0.7, description="Temperatura para geração")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens na resposta")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")


class LLMConversationListResponse(BaseModel):
    """Schema de resposta para lista de conversas com LLM."""
    items: List[LLMConversationResponse] = Field(..., description="Lista de conversas")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")
    has_next: bool = Field(..., description="Se há próxima página")
    has_prev: bool = Field(..., description="Se há página anterior")


# Message schemas
class LLMMessageCreate(BaseModel):
    """Schema para criação de mensagem em conversa com LLM."""
    conversation_id: UUID = Field(..., description="ID da conversa")
    role: str = Field(..., description="Papel da mensagem (user/assistant)")
    content: str = Field(..., description="Conteúdo da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados da mensagem")


class LLMMessageResponse(BaseModel):
    """Schema de resposta para mensagem em conversa com LLM."""
    id: UUID = Field(..., description="ID único da mensagem")
    conversation_id: UUID = Field(..., description="ID da conversa")
    role: str = Field(..., description="Papel da mensagem (user/assistant)")
    content: str = Field(..., description="Conteúdo da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados da mensagem")
    created_at: datetime = Field(..., description="Data de criação")


class LLMMessageListResponse(BaseModel):
    """Schema de resposta para lista de mensagens em conversa com LLM."""
    items: List[LLMMessageResponse] = Field(..., description="Lista de mensagens")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")
    has_next: bool = Field(..., description="Se há próxima página")
    has_prev: bool = Field(..., description="Se há página anterior")

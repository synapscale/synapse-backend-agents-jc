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
    """Schema para criação de LLM - ALINHADO COM O BANCO."""
    name: str = Field(..., description="Nome do modelo")
    provider: str = Field(..., description="Provedor do modelo")
    model_version: Optional[str] = Field(None, description="Versão do modelo no provedor")
    cost_per_token_input: float = Field(default=0.0, description="Custo por token de entrada")
    cost_per_token_output: float = Field(default=0.0, description="Custo por token de saída")
    max_tokens_supported: Optional[int] = Field(None, description="Máximo de tokens suportados")
    supports_function_calling: bool = Field(default=False, description="Suporta function calling")
    supports_vision: bool = Field(default=False, description="Suporta visão")
    supports_streaming: bool = Field(default=True, description="Suporta streaming")
    context_window: Optional[int] = Field(None, description="Tamanho do contexto em tokens")
    is_active: bool = Field(default=True, description="Se o modelo está ativo")
    llm_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do LLM")
    status: str = Field(default="active", description="Status do LLM")
    health_status: str = Field(default="healthy", description="Status de saúde do LLM")
    response_time_avg_ms: int = Field(default=0, description="Tempo médio de resposta em ms")
    availability_percentage: float = Field(default=99.9, description="Percentual de disponibilidade")


class LLMUpdate(BaseModel):
    """Schema para atualização de LLM - ALINHADO COM O BANCO."""
    name: Optional[str] = Field(None, description="Nome do modelo")
    model_version: Optional[str] = Field(None, description="Versão do modelo no provedor")
    cost_per_token_input: Optional[float] = Field(None, description="Custo por token de entrada")
    cost_per_token_output: Optional[float] = Field(None, description="Custo por token de saída")
    max_tokens_supported: Optional[int] = Field(None, description="Máximo de tokens suportados")
    supports_function_calling: Optional[bool] = Field(None, description="Suporta function calling")
    supports_vision: Optional[bool] = Field(None, description="Suporta visão")
    supports_streaming: Optional[bool] = Field(None, description="Suporta streaming")
    context_window: Optional[int] = Field(None, description="Tamanho do contexto em tokens")
    is_active: Optional[bool] = Field(None, description="Se o modelo está ativo")
    llm_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do LLM")
    status: Optional[str] = Field(None, description="Status do LLM")
    health_status: Optional[str] = Field(None, description="Status de saúde do LLM")
    response_time_avg_ms: Optional[int] = Field(None, description="Tempo médio de resposta em ms")
    availability_percentage: Optional[float] = Field(None, description="Percentual de disponibilidade")


class LLMResponse(BaseModel):
    """Schema de resposta para LLM - ALINHADO COM O BANCO."""
    id: UUID = Field(..., description="ID único do modelo")
    name: str = Field(..., description="Nome do modelo")
    provider: str = Field(..., description="Provedor do modelo")
    model_version: Optional[str] = Field(None, description="Versão do modelo no provedor")
    cost_per_token_input: Optional[float] = Field(None, description="Custo por token de entrada")
    cost_per_token_output: Optional[float] = Field(None, description="Custo por token de saída")
    max_tokens_supported: Optional[int] = Field(None, description="Máximo de tokens suportados")
    supports_function_calling: bool = Field(..., description="Suporta function calling")
    supports_vision: bool = Field(..., description="Suporta visão")
    supports_streaming: bool = Field(..., description="Suporta streaming")
    context_window: Optional[int] = Field(None, description="Tamanho do contexto em tokens")
    is_active: bool = Field(..., description="Se o modelo está ativo")
    llm_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do LLM")
    status: str = Field(..., description="Status do LLM")
    health_status: str = Field(..., description="Status de saúde do LLM")
    response_time_avg_ms: int = Field(..., description="Tempo médio de resposta em ms")
    availability_percentage: float = Field(..., description="Percentual de disponibilidade")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")


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

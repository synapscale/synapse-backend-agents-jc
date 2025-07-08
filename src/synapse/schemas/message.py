"""
Schemas para Message - mensagens de conversas
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class MessageBase(BaseModel):
    """Schema base para Message"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    
    # Conteúdo da mensagem
    content: str = Field(..., description="Conteúdo da mensagem")
    message_type: str = Field(..., description="Tipo da mensagem")
    
    # Origem da mensagem
    sender_type: str = Field(..., description="Tipo do remetente (user, agent, system)")
    sender_id: Optional[UUID] = Field(None, description="ID do remetente")
    
    # Status da mensagem
    status: str = Field("sent", description="Status da mensagem")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Informações de processamento
    processing_time_ms: Optional[int] = Field(None, description="Tempo de processamento em ms")
    token_count: Optional[int] = Field(None, description="Contagem de tokens")
    
    # Relacionamentos
    parent_message_id: Optional[UUID] = Field(None, description="ID da mensagem pai")
    thread_id: Optional[UUID] = Field(None, description="ID da thread")


class MessageCreate(MessageBase):
    """Schema para criação de Message"""
    pass


class MessageUpdate(BaseModel):
    """Schema para atualização de Message"""
    
    content: Optional[str] = Field(None, description="Conteúdo da mensagem")
    status: Optional[str] = Field(None, description="Status da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    processing_time_ms: Optional[int] = Field(None, description="Tempo de processamento em ms")
    token_count: Optional[int] = Field(None, description="Contagem de tokens")


class MessageResponse(MessageBase):
    """Schema para resposta de Message"""
    
    id: UUID = Field(..., description="ID único da mensagem")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas (opcional)
    conversation_title: Optional[str] = Field(None, description="Título da conversa")
    sender_name: Optional[str] = Field(None, description="Nome do remetente")
    
    # Respostas/filhas
    reply_count: Optional[int] = Field(None, description="Número de respostas")
    
    model_config = ConfigDict(from_attributes=True)


class MessageList(BaseModel):
    """Schema para lista de Message"""
    
    items: list[MessageResponse] = Field(..., description="Lista de mensagens")
    total: int = Field(..., description="Total de mensagens")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class MessageWithReplies(MessageResponse):
    """Schema para Message com respostas"""
    
    replies: List[MessageResponse] = Field(..., description="Respostas à mensagem")
    
    model_config = ConfigDict(from_attributes=True)


class MessageThread(BaseModel):
    """Schema para thread de mensagens"""
    
    thread_id: UUID = Field(..., description="ID da thread")
    messages: List[MessageResponse] = Field(..., description="Mensagens da thread")
    total_messages: int = Field(..., description="Total de mensagens")
    
    model_config = ConfigDict(from_attributes=True)


class MessageStatistics(BaseModel):
    """Schema para estatísticas de mensagens"""
    
    total_messages: int = Field(..., description="Total de mensagens")
    messages_by_sender_type: Dict[str, int] = Field(..., description="Por tipo de remetente")
    messages_by_status: Dict[str, int] = Field(..., description="Por status")
    
    average_processing_time_ms: Optional[float] = Field(None, description="Tempo médio de processamento")
    total_tokens: Optional[int] = Field(None, description="Total de tokens")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)

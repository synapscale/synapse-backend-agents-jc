"""Conversation schemas aligned with database model"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = Field(None, description="Título da conversa")
    status: str = Field(default="active", description="Status da conversa")
    
class ConversationCreate(ConversationBase):
    """Schema for creating conversation"""
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    title: Optional[str] = Field(None, description="Título da conversa")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto da conversa")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configurações da conversa")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

class ConversationResponse(ConversationBase):
    """Response schema for conversation"""
    id: UUID = Field(..., description="ID da conversa")
    user_id: UUID = Field(..., description="ID do usuário")
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    tenant_id: UUID = Field(..., description="ID do tenant")
    title: Optional[str] = Field(None, description="Título da conversa")
    status: str = Field(..., description="Status da conversa")
    message_count: int = Field(default=0, description="Número de mensagens")
    total_tokens_used: int = Field(default=0, description="Total de tokens usados")
    agent_name: Optional[str] = Field(None, description="Nome do agente")
    latest_message: Optional[Dict[str, Any]] = Field(None, description="Última mensagem")
    last_message_at: Optional[datetime] = Field(None, description="Data da última mensagem")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto da conversa")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configurações da conversa")
    
    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    """Response schema for conversation list"""
    conversations: List[ConversationResponse]
    total: int
    page: int
    size: int
    
class ConversationTitleUpdate(BaseModel):
    """Schema for updating conversation title"""
    title: str = Field(..., min_length=1, max_length=255, description="Novo título")

class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., description="Conteúdo da mensagem")
    role: str = Field(..., description="Role da mensagem (user, assistant, system)")
    
class MessageCreate(MessageBase):
    """Schema for creating message"""
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados da mensagem")
    tokens_used: Optional[int] = Field(None, description="Tokens usados")
    cost: Optional[float] = Field(None, description="Custo da mensagem")

class MessageResponse(MessageBase):
    """Response schema for message"""
    id: UUID = Field(..., description="ID da mensagem")
    conversation_id: UUID = Field(..., description="ID da conversa")
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    agent_name: Optional[str] = Field(None, description="Nome do agente")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados")
    tokens_used: Optional[int] = Field(None, description="Tokens usados")
    cost: Optional[float] = Field(None, description="Custo da mensagem")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """Response schema for message list"""
    messages: List[MessageResponse]
    total: int
    page: int
    size: int

__all__ = [
    "ConversationCreate", "ConversationResponse", "ConversationListResponse", 
    "ConversationTitleUpdate", "MessageCreate", "MessageResponse", "MessageListResponse"
]

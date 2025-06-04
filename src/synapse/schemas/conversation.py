"""
Schemas Pydantic para conversations e messages
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Schemas de Conversation
class ConversationBase(BaseModel):
    title: Optional[str] = None
    agent_id: Optional[str] = None
    workspace_id: Optional[str] = None

class ConversationCreate(ConversationBase):
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    status: str
    message_count: int
    total_tokens_used: int
    context: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    last_message_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    page: int
    size: int
    pages: int

# Schemas de Message
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|assistant|system)$")

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    attachments: List[Dict[str, Any]]
    model_used: Optional[str] = None
    model_provider: Optional[str] = None
    tokens_used: int
    processing_time_ms: int
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    page: int
    size: int
    pages: int


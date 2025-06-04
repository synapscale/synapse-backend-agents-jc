"""
Schemas Pydantic para agents
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Schemas base
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: str = Field(default="conversational")
    personality: Optional[str] = None
    instructions: Optional[str] = None

class AgentCreate(AgentBase):
    model_provider: str = Field(default="openai")
    model_name: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=8000)
    tools: List[str] = Field(default_factory=list)
    knowledge_base: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: Optional[str] = None
    personality: Optional[str] = None
    instructions: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8000)
    tools: Optional[List[str]] = None
    knowledge_base: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None
    status: Optional[str] = None

class AgentResponse(AgentBase):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    model_provider: str
    model_name: str
    temperature: float
    max_tokens: int
    status: str
    tools: List[str]
    knowledge_base: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None
    conversation_count: int
    message_count: int
    rating_average: float
    rating_count: int
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    items: List[AgentResponse]
    total: int
    page: int
    size: int
    pages: int


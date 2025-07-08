from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ContactEventType(str, Enum):
    """Tipos comuns de eventos de contato."""
    page_view = "page_view"
    click = "click"
    form_submit = "form_submit"
    download = "download"
    scroll = "scroll"
    video_play = "video_play"
    video_pause = "video_pause"
    email_open = "email_open"
    email_click = "email_click"
    email_bounce = "email_bounce"
    email_unsubscribe = "email_unsubscribe"
    email_sent = "email_sent"
    purchase = "purchase"
    signup = "signup"
    login = "login"
    logout = "logout"
    subscription = "subscription"
    cancellation = "cancellation"
    # Outros tipos podem ser aceitos como string

class ContactEventBase(BaseModel):
    """Schema base para ContactEvent."""
    contact_id: UUID = Field(..., description="ID do contato")
    event_type: str = Field(..., description="Tipo do evento")
    event_name: Optional[str] = Field(None, description="Nome do evento")
    event_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dados do evento")
    description: Optional[str] = Field(None, description="Descrição do evento")
    occurred_at: Optional[datetime] = Field(None, description="Data/hora do evento")
    source: Optional[str] = Field(None, description="Fonte do evento")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    ip_address: Optional[str] = Field(None, description="IP do usuário")
    user_agent: Optional[str] = Field(None, description="User agent do navegador")
    referrer: Optional[str] = Field(None, description="Referrer do evento")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")

class ContactEventCreate(ContactEventBase):
    """Schema para criação de ContactEvent."""
    pass

class ContactEventUpdate(BaseModel):
    """Schema para atualização de ContactEvent."""
    event_name: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    source: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

class ContactEventResponse(ContactEventBase):
    """Schema para resposta de ContactEvent."""
    id: UUID = Field(..., description="ID do evento")
    created_at: Optional[datetime] = Field(None, description="Data de criação do registro")
    model_config = ConfigDict(from_attributes=True)

class ContactEventList(BaseModel):
    """Schema para lista paginada de ContactEvent."""
    items: List[ContactEventResponse] = Field(..., description="Lista de eventos")
    total: int = Field(..., description="Total de eventos")
    page: int = Field(1, ge=1, description="Página atual")
    size: int = Field(10, ge=1, le=100, description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    model_config = ConfigDict(from_attributes=True) 
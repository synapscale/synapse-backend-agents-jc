from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class CampaignType(str, Enum):
    """Tipos de campanha."""
    email = "email"
    sms = "sms"
    push = "push"
    webinar = "webinar"
    # Adicione outros tipos conforme necessário

class CampaignStatus(str, Enum):
    """Status possíveis da campanha."""
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    sent = "sent"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"

class CampaignBase(BaseModel):
    """Schema base para Campaign."""
    name: str = Field(..., min_length=1, max_length=255, description="Nome da campanha")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição da campanha")
    type: CampaignType = Field(..., description="Tipo da campanha")
    status: Optional[CampaignStatus] = Field(None, description="Status da campanha")
    subject: Optional[str] = Field(None, max_length=255, description="Assunto (para email)")
    content: Optional[str] = Field(None, description="Conteúdo da campanha")
    template_id: Optional[UUID] = Field(None, description="ID do template usado")
    scheduled_at: Optional[datetime] = Field(None, description="Data/hora agendada")
    sent_at: Optional[datetime] = Field(None, description="Data/hora de envio")
    stats: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Estatísticas da campanha")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configurações da campanha")

class CampaignCreate(CampaignBase):
    """Schema para criação de Campaign."""
    tenant_id: UUID = Field(..., description="ID do tenant")
    created_by: UUID = Field(..., description="ID do usuário criador")

class CampaignUpdate(BaseModel):
    """Schema para atualização de Campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    template_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    stats: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None

class CampaignResponse(CampaignBase):
    """Schema para resposta de Campaign."""
    id: UUID = Field(..., description="ID da campanha")
    tenant_id: UUID = Field(..., description="ID do tenant")
    created_by: UUID = Field(..., description="ID do usuário criador")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    model_config = ConfigDict(from_attributes=True)

class CampaignList(BaseModel):
    """Schema para lista paginada de Campaign."""
    items: List[CampaignResponse] = Field(..., description="Lista de campanhas")
    total: int = Field(..., description="Total de campanhas")
    page: int = Field(1, ge=1, description="Página atual")
    size: int = Field(10, ge=1, le=100, description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    model_config = ConfigDict(from_attributes=True) 
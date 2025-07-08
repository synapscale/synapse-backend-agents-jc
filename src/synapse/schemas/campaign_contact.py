from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class CampaignContactStatus(str, Enum):
    """Status possíveis do contato na campanha."""
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    opened = "opened"
    clicked = "clicked"
    bounced = "bounced"
    unsubscribed = "unsubscribed"
    failed = "failed"

class CampaignContactBase(BaseModel):
    """Schema base para CampaignContact."""
    campaign_id: UUID = Field(..., description="ID da campanha")
    contact_id: UUID = Field(..., description="ID do contato")
    status: Optional[CampaignContactStatus] = Field(None, description="Status do contato na campanha")
    sent_at: Optional[datetime] = Field(None, description="Data/hora de envio")
    opened_at: Optional[datetime] = Field(None, description="Data/hora de abertura")
    clicked_at: Optional[datetime] = Field(None, description="Data/hora de clique")
    bounced_at: Optional[datetime] = Field(None, description="Data/hora de bounce")
    unsubscribed_at: Optional[datetime] = Field(None, description="Data/hora de descadastro")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant")

class CampaignContactCreate(CampaignContactBase):
    """Schema para criação de CampaignContact."""
    pass

class CampaignContactUpdate(BaseModel):
    """Schema para atualização de CampaignContact."""
    status: Optional[CampaignContactStatus] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class CampaignContactResponse(CampaignContactBase):
    """Schema para resposta de CampaignContact."""
    id: UUID = Field(..., description="ID da relação campanha-contato")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")
    model_config = ConfigDict(from_attributes=True)

class CampaignContactList(BaseModel):
    """Schema para lista paginada de CampaignContact."""
    items: List[CampaignContactResponse] = Field(..., description="Lista de relações campanha-contato")
    total: int = Field(..., description="Total de relações")
    page: int = Field(1, ge=1, description="Página atual")
    size: int = Field(10, ge=1, le=100, description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    model_config = ConfigDict(from_attributes=True) 
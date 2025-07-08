"""
Schemas para AgentModel - associação entre agentes e modelos LLM
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AgentModelBase(BaseModel):
    """Schema base para AgentModel"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    llm_id: UUID = Field(..., description="ID do modelo LLM")
    
    # Configurações específicas do modelo para este agente
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling")
    top_k: Optional[int] = Field(None, gt=0, description="Top-k sampling")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de presença")
    
    # Status e prioridade
    is_primary: bool = Field(False, description="Modelo primário do agente")
    is_active: bool = Field(True, description="Modelo ativo")
    priority: int = Field(1, description="Prioridade (1=mais alta)")
    
    # Metadata
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração adicional")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")


class AgentModelCreate(AgentModelBase):
    """Schema para criação de AgentModel"""
    pass


class AgentModelUpdate(BaseModel):
    """Schema para atualização de AgentModel"""
    
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling")
    top_k: Optional[int] = Field(None, gt=0, description="Top-k sampling")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de presença")
    
    is_primary: Optional[bool] = Field(None, description="Modelo primário do agente")
    is_active: Optional[bool] = Field(None, description="Modelo ativo")
    priority: Optional[int] = Field(None, description="Prioridade")
    
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração adicional")


class AgentModelResponse(AgentModelBase):
    """Schema para resposta de AgentModel"""
    
    id: UUID = Field(..., description="ID único da associação")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas (opcional)
    agent_name: Optional[str] = Field(None, description="Nome do agente")
    llm_name: Optional[str] = Field(None, description="Nome do modelo LLM")
    llm_provider: Optional[str] = Field(None, description="Provedor do modelo")
    
    model_config = ConfigDict(from_attributes=True)


class AgentModelList(BaseModel):
    """Schema para lista de AgentModel"""
    
    items: list[AgentModelResponse] = Field(..., description="Lista de associações")
    total: int = Field(..., description="Total de associações")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AgentModelWithLLM(AgentModelResponse):
    """Schema para AgentModel com detalhes do LLM"""
    
    llm_details: Dict[str, Any] = Field(..., description="Detalhes do modelo LLM")
    
    model_config = ConfigDict(from_attributes=True)

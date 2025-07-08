"""
Schemas para UsageLog - rastreamento de uso do sistema
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class UsageLogBase(BaseModel):
    """Schema base para UsageLog"""
    
    # Identificação do usuário e tenant
    user_id: UUID = Field(..., description="ID do usuário")
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Contexto da operação
    operation_type: str = Field(..., description="Tipo da operação")
    resource_type: str = Field(..., description="Tipo do recurso")
    resource_id: Optional[UUID] = Field(None, description="ID do recurso")
    
    # Métricas de uso
    tokens_used: int = Field(0, description="Tokens utilizados")
    cost_usd: float = Field(0.0, description="Custo em USD")
    
    # Contexto adicional
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    conversation_id: Optional[UUID] = Field(None, description="ID da conversa")
    llm_id: Optional[UUID] = Field(None, description="ID do LLM")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Timestamps
    started_at: Optional[datetime] = Field(None, description="Início da operação")
    completed_at: Optional[datetime] = Field(None, description="Fim da operação")


class UsageLogCreate(UsageLogBase):
    """Schema para criação de UsageLog"""
    pass


class UsageLogUpdate(BaseModel):
    """Schema para atualização de UsageLog"""
    
    tokens_used: Optional[int] = Field(None, description="Tokens utilizados")
    cost_usd: Optional[float] = Field(None, description="Custo em USD")
    completed_at: Optional[datetime] = Field(None, description="Fim da operação")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class UsageLogResponse(UsageLogBase):
    """Schema para resposta de UsageLog"""
    
    id: UUID = Field(..., description="ID único do log")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    model_config = ConfigDict(from_attributes=True)


class UsageLogList(BaseModel):
    """Schema para lista de UsageLog"""
    
    items: list[UsageLogResponse] = Field(..., description="Lista de logs")
    total: int = Field(..., description="Total de logs")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class UsageLogSummary(BaseModel):
    """Schema para resumo de uso"""
    
    total_operations: int = Field(..., description="Total de operações")
    total_tokens: int = Field(..., description="Total de tokens")
    total_cost_usd: float = Field(..., description="Custo total em USD")
    
    # Breakdown por tipo
    by_operation_type: Dict[str, int] = Field(..., description="Por tipo de operação")
    by_resource_type: Dict[str, int] = Field(..., description="Por tipo de recurso")
    by_llm: Dict[str, int] = Field(..., description="Por LLM")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)

"""
Schemas para Tool - ferramentas do sistema
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class ToolBase(BaseModel):
    """Schema base para Tool"""
    
    name: str = Field(..., description="Nome da ferramenta")
    description: Optional[str] = Field(None, description="Descrição da ferramenta")
    
    # Tipo e categoria
    tool_type: str = Field(..., description="Tipo da ferramenta")
    category: str = Field(..., description="Categoria da ferramenta")
    
    # Configuração
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração da ferramenta")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Schema dos parâmetros")
    
    # Status
    is_active: bool = Field(True, description="Ferramenta ativa")
    is_public: bool = Field(False, description="Ferramenta pública")
    
    # Versionamento
    version: str = Field("1.0.0", description="Versão da ferramenta")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: Optional[UUID] = Field(None, description="ID do usuário criador")


class ToolCreate(ToolBase):
    """Schema para criação de Tool"""
    pass


class ToolUpdate(BaseModel):
    """Schema para atualização de Tool"""
    
    name: Optional[str] = Field(None, description="Nome da ferramenta")
    description: Optional[str] = Field(None, description="Descrição da ferramenta")
    
    tool_type: Optional[str] = Field(None, description="Tipo da ferramenta")
    category: Optional[str] = Field(None, description="Categoria da ferramenta")
    
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração da ferramenta")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Schema dos parâmetros")
    
    is_active: Optional[bool] = Field(None, description="Ferramenta ativa")
    is_public: Optional[bool] = Field(None, description="Ferramenta pública")
    
    version: Optional[str] = Field(None, description="Versão da ferramenta")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class ToolResponse(ToolBase):
    """Schema para resposta de Tool"""
    
    id: UUID = Field(..., description="ID único da ferramenta")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas (opcional)
    user_name: Optional[str] = Field(None, description="Nome do usuário criador")
    
    # Estatísticas de uso
    usage_count: Optional[int] = Field(None, description="Número de usos")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    
    model_config = ConfigDict(from_attributes=True)


class ToolList(BaseModel):
    """Schema para lista de Tool"""
    
    items: list[ToolResponse] = Field(..., description="Lista de ferramentas")
    total: int = Field(..., description="Total de ferramentas")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class ToolExecution(BaseModel):
    """Schema para execução de ferramenta"""
    
    tool_id: UUID = Field(..., description="ID da ferramenta")
    parameters: Dict[str, Any] = Field(..., description="Parâmetros de execução")
    
    # Contexto de execução
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    agent_id: Optional[UUID] = Field(None, description="ID do agente")
    conversation_id: Optional[UUID] = Field(None, description="ID da conversa")
    
    model_config = ConfigDict(from_attributes=True)


class ToolExecutionResult(BaseModel):
    """Schema para resultado da execução"""
    
    tool_id: UUID = Field(..., description="ID da ferramenta")
    execution_id: UUID = Field(..., description="ID da execução")
    
    # Resultado
    success: bool = Field(..., description="Sucesso da execução")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado da execução")
    error: Optional[str] = Field(None, description="Erro da execução")
    
    # Métricas
    execution_time_ms: int = Field(..., description="Tempo de execução em ms")
    
    # Timestamps
    started_at: datetime = Field(..., description="Início da execução")
    completed_at: datetime = Field(..., description="Fim da execução")
    
    model_config = ConfigDict(from_attributes=True)


class ToolStatistics(BaseModel):
    """Schema para estatísticas de ferramentas"""
    
    total_tools: int = Field(..., description="Total de ferramentas")
    active_tools: int = Field(..., description="Ferramentas ativas")
    public_tools: int = Field(..., description="Ferramentas públicas")
    
    # Uso
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Por categoria
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)

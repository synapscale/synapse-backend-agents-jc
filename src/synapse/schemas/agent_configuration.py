"""
Schemas para AgentConfiguration - configurações de agentes
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AgentConfigurationBase(BaseModel):
    """Schema base para AgentConfiguration"""
    
    # Relacionamentos
    agent_id: UUID = Field(..., description="ID do agente")
    
    # Identificação da configuração
    config_name: str = Field(..., description="Nome da configuração")
    config_version: str = Field("1.0.0", description="Versão da configuração")
    
    # Configurações do agente
    llm_config: Optional[Dict[str, Any]] = Field(None, description="Configuração do LLM")
    prompt_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de prompts")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de ferramentas")
    
    # Configurações de comportamento
    behavior_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de comportamento")
    
    # Configurações de memória
    memory_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de memória")
    
    # Configurações de segurança
    security_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de segurança")
    
    # Status
    is_active: bool = Field(True, description="Configuração ativa")
    is_default: bool = Field(False, description="Configuração padrão")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário criador")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Notas
    description: Optional[str] = Field(None, description="Descrição da configuração")
    notes: Optional[str] = Field(None, description="Notas da configuração")


class AgentConfigurationCreate(AgentConfigurationBase):
    """Schema para criação de AgentConfiguration"""
    pass


class AgentConfigurationUpdate(BaseModel):
    """Schema para atualização de AgentConfiguration"""
    
    config_name: Optional[str] = Field(None, description="Nome da configuração")
    config_version: Optional[str] = Field(None, description="Versão da configuração")
    
    llm_config: Optional[Dict[str, Any]] = Field(None, description="Configuração do LLM")
    prompt_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de prompts")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de ferramentas")
    
    behavior_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de comportamento")
    memory_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de memória")
    security_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de segurança")
    
    is_active: Optional[bool] = Field(None, description="Configuração ativa")
    is_default: Optional[bool] = Field(None, description="Configuração padrão")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    description: Optional[str] = Field(None, description="Descrição da configuração")
    notes: Optional[str] = Field(None, description="Notas da configuração")


class AgentConfigurationResponse(AgentConfigurationBase):
    """Schema para resposta de AgentConfiguration"""
    
    config_id: UUID = Field(..., description="ID único da configuração")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    agent_name: Optional[str] = Field(None, description="Nome do agente")
    user_name: Optional[str] = Field(None, description="Nome do usuário criador")
    
    # Estatísticas
    usage_count: Optional[int] = Field(None, description="Número de usos")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationList(BaseModel):
    """Schema para lista de AgentConfiguration"""
    
    items: List[AgentConfigurationResponse] = Field(..., description="Lista de configurações")
    total: int = Field(..., description="Total de configurações")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationTemplate(BaseModel):
    """Schema para template de AgentConfiguration"""
    
    template_name: str = Field(..., description="Nome do template")
    template_description: Optional[str] = Field(None, description="Descrição do template")
    
    # Configurações do template
    template_config: Dict[str, Any] = Field(..., description="Configuração do template")
    
    # Categoria
    category: str = Field(..., description="Categoria do template")
    
    # Tags
    tags: Optional[List[str]] = Field(None, description="Tags do template")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationValidation(BaseModel):
    """Schema para validação de AgentConfiguration"""
    
    config_id: UUID = Field(..., description="ID da configuração")
    
    # Resultado da validação
    is_valid: bool = Field(..., description="Configuração válida")
    
    # Detalhes da validação
    validation_errors: List[str] = Field(..., description="Erros de validação")
    validation_warnings: List[str] = Field(..., description="Avisos de validação")
    
    # Validações específicas
    llm_config_valid: bool = Field(..., description="Configuração LLM válida")
    prompt_config_valid: bool = Field(..., description="Configuração de prompts válida")
    tool_config_valid: bool = Field(..., description="Configuração de ferramentas válida")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationClone(BaseModel):
    """Schema para clonagem de AgentConfiguration"""
    
    source_config_id: UUID = Field(..., description="ID da configuração origem")
    new_config_name: str = Field(..., description="Nome da nova configuração")
    
    # Configurações da clonagem
    clone_all: bool = Field(True, description="Clonar todas as configurações")
    clone_llm_config: bool = Field(True, description="Clonar configuração LLM")
    clone_prompt_config: bool = Field(True, description="Clonar configuração de prompts")
    clone_tool_config: bool = Field(True, description="Clonar configuração de ferramentas")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationComparison(BaseModel):
    """Schema para comparação de AgentConfiguration"""
    
    config_ids: List[UUID] = Field(..., description="IDs das configurações a comparar")
    
    # Resultado da comparação
    configurations: List[Dict[str, Any]] = Field(..., description="Configurações comparadas")
    differences: Dict[str, Any] = Field(..., description="Diferenças encontradas")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationHistory(BaseModel):
    """Schema para histórico de AgentConfiguration"""
    
    config_id: UUID = Field(..., description="ID da configuração")
    
    # Histórico de mudanças
    changes: List[Dict[str, Any]] = Field(..., description="Histórico de mudanças")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationStatistics(BaseModel):
    """Schema para estatísticas de AgentConfiguration"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    
    # Configurações
    total_configurations: int = Field(..., description="Total de configurações")
    active_configurations: int = Field(..., description="Configurações ativas")
    
    # Uso
    most_used_config: Optional[Dict[str, Any]] = Field(None, description="Configuração mais usada")
    least_used_config: Optional[Dict[str, Any]] = Field(None, description="Configuração menos usada")
    
    # Performance
    average_response_time_ms: Optional[float] = Field(None, description="Tempo médio de resposta")
    
    model_config = ConfigDict(from_attributes=True)


class AgentConfigurationExport(BaseModel):
    """Schema para exportação de AgentConfiguration"""
    
    config_ids: List[UUID] = Field(..., description="IDs das configurações")
    format: str = Field(..., description="Formato da exportação")
    
    # Configurações de exportação
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_history: bool = Field(False, description="Incluir histórico")
    
    model_config = ConfigDict(from_attributes=True)

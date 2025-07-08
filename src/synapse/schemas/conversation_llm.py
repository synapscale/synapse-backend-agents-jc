"""
Schemas para ConversationLLM - associação entre conversas e LLMs
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class ConversationLLMBase(BaseModel):
    """Schema base para ConversationLLM"""
    
    # Relacionamentos
    conversation_id: UUID = Field(..., description="ID da conversa")
    llm_id: UUID = Field(..., description="ID do LLM")
    
    # Configurações específicas para esta conversa
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling")
    top_k: Optional[int] = Field(None, gt=0, description="Top-k sampling")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de presença")
    
    # Status
    is_active: bool = Field(True, description="Associação ativa")
    is_primary: bool = Field(False, description="LLM primário da conversa")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class ConversationLLMCreate(ConversationLLMBase):
    """Schema para criação de ConversationLLM"""
    pass


class ConversationLLMUpdate(BaseModel):
    """Schema para atualização de ConversationLLM"""
    
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperatura do modelo")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling")
    top_k: Optional[int] = Field(None, gt=0, description="Top-k sampling")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de frequência")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="Penalidade de presença")
    
    is_active: Optional[bool] = Field(None, description="Associação ativa")
    is_primary: Optional[bool] = Field(None, description="LLM primário da conversa")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class ConversationLLMResponse(ConversationLLMBase):
    """Schema para resposta de ConversationLLM"""
    
    id: UUID = Field(..., description="ID único da associação")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    conversation_title: Optional[str] = Field(None, description="Título da conversa")
    llm_name: Optional[str] = Field(None, description="Nome do LLM")
    llm_provider: Optional[str] = Field(None, description="Provedor do LLM")
    
    # Estatísticas
    messages_count: Optional[int] = Field(None, description="Número de mensagens")
    tokens_used: Optional[int] = Field(None, description="Tokens utilizados")
    cost_usd: Optional[float] = Field(None, description="Custo em USD")
    
    # Performance
    average_response_time_ms: Optional[float] = Field(None, description="Tempo médio de resposta")
    
    # Última utilização
    last_used_at: Optional[datetime] = Field(None, description="Última utilização")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMList(BaseModel):
    """Schema para lista de ConversationLLM"""
    
    items: List[ConversationLLMResponse] = Field(..., description="Lista de associações")
    total: int = Field(..., description="Total de associações")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMUsage(BaseModel):
    """Schema para uso de ConversationLLM"""
    
    conversation_llm_id: UUID = Field(..., description="ID da associação")
    
    # Dados do uso
    tokens_input: int = Field(..., description="Tokens de entrada")
    tokens_output: int = Field(..., description="Tokens de saída")
    response_time_ms: int = Field(..., description="Tempo de resposta em ms")
    
    # Custo
    cost_usd: float = Field(..., description="Custo em USD")
    
    # Contexto
    message_id: Optional[UUID] = Field(None, description="ID da mensagem")
    
    # Timestamp
    used_at: datetime = Field(..., description="Data do uso")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMSwitch(BaseModel):
    """Schema para troca de LLM em conversa"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    new_llm_id: UUID = Field(..., description="ID do novo LLM")
    
    # Motivo da troca
    reason: Optional[str] = Field(None, description="Motivo da troca")
    
    # Manter configurações
    keep_configuration: bool = Field(True, description="Manter configurações")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMSwitchResult(BaseModel):
    """Schema para resultado da troca"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    old_llm_id: UUID = Field(..., description="ID do LLM anterior")
    new_llm_id: UUID = Field(..., description="ID do novo LLM")
    
    # Resultado
    success: bool = Field(..., description="Troca bem-sucedida")
    
    # Configurações migradas
    migrated_configuration: Optional[Dict[str, Any]] = Field(None, description="Configurações migradas")
    
    # Timestamp
    switched_at: datetime = Field(..., description="Data da troca")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMRecommendation(BaseModel):
    """Schema para recomendação de LLM"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    
    # LLM recomendado
    recommended_llm_id: UUID = Field(..., description="ID do LLM recomendado")
    recommended_llm_name: str = Field(..., description="Nome do LLM recomendado")
    
    # Motivo da recomendação
    reason: str = Field(..., description="Motivo da recomendação")
    confidence_score: float = Field(..., description="Score de confiança")
    
    # Análise
    current_performance: Optional[Dict[str, Any]] = Field(None, description="Performance atual")
    expected_improvement: Optional[Dict[str, Any]] = Field(None, description="Melhoria esperada")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMComparison(BaseModel):
    """Schema para comparação de LLMs"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    llm_ids: List[UUID] = Field(..., description="IDs dos LLMs a comparar")
    
    # Resultado da comparação
    comparison_results: List[Dict[str, Any]] = Field(..., description="Resultados da comparação")
    
    # Métricas
    performance_metrics: Dict[str, Dict[str, Any]] = Field(..., description="Métricas de performance")
    cost_comparison: Dict[str, float] = Field(..., description="Comparação de custos")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMStatistics(BaseModel):
    """Schema para estatísticas de ConversationLLM"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    
    # LLMs utilizados
    llms_used: List[Dict[str, Any]] = Field(..., description="LLMs utilizados")
    
    # Uso total
    total_tokens: int = Field(..., description="Total de tokens")
    total_cost_usd: float = Field(..., description="Custo total em USD")
    total_messages: int = Field(..., description="Total de mensagens")
    
    # Performance
    average_response_time_ms: float = Field(..., description="Tempo médio de resposta")
    
    # Por LLM
    usage_by_llm: Dict[str, Dict[str, Any]] = Field(..., description="Uso por LLM")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMOptimization(BaseModel):
    """Schema para otimização de LLM"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    
    # Configurações de otimização
    optimize_cost: bool = Field(True, description="Otimizar custo")
    optimize_speed: bool = Field(True, description="Otimizar velocidade")
    optimize_quality: bool = Field(True, description="Otimizar qualidade")
    
    # Prioridades
    priority_cost: float = Field(0.3, description="Prioridade do custo")
    priority_speed: float = Field(0.3, description="Prioridade da velocidade")
    priority_quality: float = Field(0.4, description="Prioridade da qualidade")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationLLMOptimizationResult(BaseModel):
    """Schema para resultado da otimização"""
    
    conversation_id: UUID = Field(..., description="ID da conversa")
    
    # Recomendações
    recommended_llm_id: UUID = Field(..., description="LLM recomendado")
    recommended_config: Dict[str, Any] = Field(..., description="Configuração recomendada")
    
    # Benefícios esperados
    expected_cost_reduction: float = Field(..., description="Redução de custo esperada")
    expected_speed_improvement: float = Field(..., description="Melhoria de velocidade esperada")
    expected_quality_score: float = Field(..., description="Score de qualidade esperado")
    
    model_config = ConfigDict(from_attributes=True)

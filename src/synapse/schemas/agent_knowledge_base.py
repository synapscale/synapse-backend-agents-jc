"""
Schemas para AgentKnowledgeBase - associação entre agentes e bases de conhecimento
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class AgentKnowledgeBaseBase(BaseModel):
    """Schema base para AgentKnowledgeBase"""
    
    # Relacionamentos
    agent_id: UUID = Field(..., description="ID do agente")
    knowledge_base_id: UUID = Field(..., description="ID da base de conhecimento")
    
    # Configurações da associação
    priority: int = Field(0, description="Prioridade da base de conhecimento para o agente")
    is_active: bool = Field(True, description="Associação ativa")
    
    # Configurações de busca específicas para este agente
    search_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de busca específica")
    
    # Filtros específicos
    content_filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de conteúdo")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AgentKnowledgeBaseCreate(AgentKnowledgeBaseBase):
    """Schema para criação de AgentKnowledgeBase"""
    pass


class AgentKnowledgeBaseUpdate(BaseModel):
    """Schema para atualização de AgentKnowledgeBase"""
    
    priority: Optional[int] = Field(None, description="Prioridade da base de conhecimento")
    is_active: Optional[bool] = Field(None, description="Associação ativa")
    
    search_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de busca específica")
    content_filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de conteúdo")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class AgentKnowledgeBaseResponse(AgentKnowledgeBaseBase):
    """Schema para resposta de AgentKnowledgeBase"""
    
    id: UUID = Field(..., description="ID único da associação")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    agent_name: Optional[str] = Field(None, description="Nome do agente")
    knowledge_base_name: Optional[str] = Field(None, description="Nome da base de conhecimento")
    knowledge_base_type: Optional[str] = Field(None, description="Tipo da base de conhecimento")
    
    # Estatísticas
    usage_count: Optional[int] = Field(None, description="Número de usos")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseList(BaseModel):
    """Schema para lista de AgentKnowledgeBase"""
    
    items: List[AgentKnowledgeBaseResponse] = Field(..., description="Lista de associações")
    total: int = Field(..., description="Total de associações")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseSearch(BaseModel):
    """Schema para busca usando AgentKnowledgeBase"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    query: str = Field(..., description="Consulta de busca")
    
    # Configurações de busca
    search_type: str = Field("semantic", description="Tipo de busca")
    limit: int = Field(10, description="Limite de resultados por base")
    min_score: Optional[float] = Field(None, description="Score mínimo")
    
    # Filtros
    knowledge_base_ids: Optional[List[UUID]] = Field(None, description="IDs específicas de bases de conhecimento")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseSearchResult(BaseModel):
    """Schema para resultado da busca do agente"""
    
    knowledge_base_id: UUID = Field(..., description="ID da base de conhecimento")
    knowledge_base_name: str = Field(..., description="Nome da base de conhecimento")
    
    # Resultado específico
    document_id: UUID = Field(..., description="ID do documento")
    title: str = Field(..., description="Título do documento")
    content: str = Field(..., description="Conteúdo do documento")
    
    # Score e relevância
    score: float = Field(..., description="Score de relevância")
    
    # Contexto
    source_url: Optional[str] = Field(None, description="URL de origem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseSearchResponse(BaseModel):
    """Schema para resposta da busca do agente"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    query: str = Field(..., description="Consulta original")
    
    # Resultados agrupados por base de conhecimento
    results: List[AgentKnowledgeBaseSearchResult] = Field(..., description="Resultados da busca")
    total_results: int = Field(..., description="Total de resultados")
    
    # Métricas
    search_time_ms: int = Field(..., description="Tempo de busca em ms")
    knowledge_bases_searched: int = Field(..., description="Bases de conhecimento pesquisadas")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseUsage(BaseModel):
    """Schema para uso de AgentKnowledgeBase"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    knowledge_base_id: UUID = Field(..., description="ID da base de conhecimento")
    
    # Contexto do uso
    query: str = Field(..., description="Consulta realizada")
    results_count: int = Field(..., description="Número de resultados")
    
    # Métricas
    search_time_ms: int = Field(..., description="Tempo de busca em ms")
    
    # Timestamp
    used_at: datetime = Field(..., description="Data do uso")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseConfiguration(BaseModel):
    """Schema para configuração de AgentKnowledgeBase"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    
    # Configurações globais para o agente
    default_search_type: str = Field("semantic", description="Tipo de busca padrão")
    max_results_per_kb: int = Field(5, description="Máximo de resultados por base")
    min_relevance_score: float = Field(0.7, description="Score mínimo de relevância")
    
    # Configurações de priorização
    auto_prioritize: bool = Field(True, description="Priorizar automaticamente baseado no uso")
    learning_enabled: bool = Field(True, description="Aprendizado habilitado")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseRecommendation(BaseModel):
    """Schema para recomendação de bases de conhecimento"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    
    # Base de conhecimento recomendada
    knowledge_base_id: UUID = Field(..., description="ID da base de conhecimento")
    knowledge_base_name: str = Field(..., description="Nome da base de conhecimento")
    
    # Motivo da recomendação
    reason: str = Field(..., description="Motivo da recomendação")
    confidence_score: float = Field(..., description="Score de confiança")
    
    # Detalhes
    similar_agents: Optional[List[UUID]] = Field(None, description="Agentes similares que usam esta base")
    usage_patterns: Optional[Dict[str, Any]] = Field(None, description="Padrões de uso")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseStatistics(BaseModel):
    """Schema para estatísticas de AgentKnowledgeBase"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    
    # Associações
    total_knowledge_bases: int = Field(..., description="Total de bases de conhecimento")
    active_knowledge_bases: int = Field(..., description="Bases de conhecimento ativas")
    
    # Uso
    total_searches: int = Field(..., description="Total de buscas")
    average_search_time_ms: float = Field(..., description="Tempo médio de busca")
    average_results_per_search: float = Field(..., description="Média de resultados por busca")
    
    # Por base de conhecimento
    usage_by_kb: Dict[str, int] = Field(..., description="Uso por base de conhecimento")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class AgentKnowledgeBaseBulkOperation(BaseModel):
    """Schema para operações em lote"""
    
    agent_id: UUID = Field(..., description="ID do agente")
    operation: str = Field(..., description="Tipo de operação")
    
    # Dados da operação
    knowledge_base_ids: List[UUID] = Field(..., description="IDs das bases de conhecimento")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração da operação")
    
    model_config = ConfigDict(from_attributes=True)

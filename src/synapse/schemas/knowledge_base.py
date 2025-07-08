"""
Schemas para KnowledgeBase - base de conhecimento
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class KnowledgeBaseBase(BaseModel):
    """Schema base para KnowledgeBase"""
    
    # Identificação
    name: str = Field(..., description="Nome da base de conhecimento")
    description: Optional[str] = Field(None, description="Descrição da base de conhecimento")
    
    # Tipo e categoria
    kb_type: str = Field(..., description="Tipo da base de conhecimento")
    category: str = Field(..., description="Categoria da base de conhecimento")
    
    # Configurações
    is_active: bool = Field(True, description="Base de conhecimento ativa")
    is_public: bool = Field(False, description="Base de conhecimento pública")
    
    # Configuração de indexação
    indexing_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de indexação")
    
    # Configuração de busca
    search_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de busca")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário criador")
    workspace_id: Optional[UUID] = Field(None, description="ID do workspace")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Tags e organização
    tags: Optional[List[str]] = Field(None, description="Tags da base de conhecimento")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Schema para criação de KnowledgeBase"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """Schema para atualização de KnowledgeBase"""
    
    name: Optional[str] = Field(None, description="Nome da base de conhecimento")
    description: Optional[str] = Field(None, description="Descrição da base de conhecimento")
    
    kb_type: Optional[str] = Field(None, description="Tipo da base de conhecimento")
    category: Optional[str] = Field(None, description="Categoria da base de conhecimento")
    
    is_active: Optional[bool] = Field(None, description="Base de conhecimento ativa")
    is_public: Optional[bool] = Field(None, description="Base de conhecimento pública")
    
    indexing_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de indexação")
    search_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de busca")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    tags: Optional[List[str]] = Field(None, description="Tags da base de conhecimento")


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Schema para resposta de KnowledgeBase"""
    
    id: UUID = Field(..., description="ID único da base de conhecimento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário criador")
    workspace_name: Optional[str] = Field(None, description="Nome do workspace")
    
    # Estatísticas
    documents_count: Optional[int] = Field(None, description="Número de documentos")
    total_size_bytes: Optional[int] = Field(None, description="Tamanho total em bytes")
    last_indexed_at: Optional[datetime] = Field(None, description="Última indexação")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseList(BaseModel):
    """Schema para lista de KnowledgeBase"""
    
    items: List[KnowledgeBaseResponse] = Field(..., description="Lista de bases de conhecimento")
    total: int = Field(..., description="Total de bases de conhecimento")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseDocument(BaseModel):
    """Schema para documento da KnowledgeBase"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    
    # Conteúdo do documento
    title: str = Field(..., description="Título do documento")
    content: str = Field(..., description="Conteúdo do documento")
    content_type: str = Field(..., description="Tipo do conteúdo")
    
    # Origem
    source_url: Optional[str] = Field(None, description="URL de origem")
    source_type: Optional[str] = Field(None, description="Tipo de origem")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Embeddings e indexação
    embeddings: Optional[List[float]] = Field(None, description="Embeddings do documento")
    indexed_at: Optional[datetime] = Field(None, description="Data de indexação")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseSearch(BaseModel):
    """Schema para busca na KnowledgeBase"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    query: str = Field(..., description="Consulta de busca")
    
    # Configurações de busca
    search_type: str = Field("semantic", description="Tipo de busca")
    limit: int = Field(10, description="Limite de resultados")
    min_score: Optional[float] = Field(None, description="Score mínimo")
    
    # Filtros
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de busca")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseSearchResult(BaseModel):
    """Schema para resultado da busca"""
    
    document_id: UUID = Field(..., description="ID do documento")
    title: str = Field(..., description="Título do documento")
    content: str = Field(..., description="Conteúdo do documento")
    
    # Score e relevância
    score: float = Field(..., description="Score de relevância")
    
    # Contexto
    source_url: Optional[str] = Field(None, description="URL de origem")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseSearchResponse(BaseModel):
    """Schema para resposta da busca"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    query: str = Field(..., description="Consulta original")
    
    # Resultados
    results: List[KnowledgeBaseSearchResult] = Field(..., description="Resultados da busca")
    total_results: int = Field(..., description="Total de resultados")
    
    # Métricas
    search_time_ms: int = Field(..., description="Tempo de busca em ms")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseIndexing(BaseModel):
    """Schema para indexação da KnowledgeBase"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    
    # Configurações de indexação
    force_reindex: bool = Field(False, description="Forçar reindexação")
    batch_size: int = Field(100, description="Tamanho do lote")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseIndexingStatus(BaseModel):
    """Schema para status da indexação"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    status: str = Field(..., description="Status da indexação")
    
    # Progresso
    total_documents: int = Field(..., description="Total de documentos")
    indexed_documents: int = Field(..., description="Documentos indexados")
    progress_percentage: float = Field(..., description="Porcentagem de progresso")
    
    # Timestamps
    started_at: datetime = Field(..., description="Início da indexação")
    estimated_completion: Optional[datetime] = Field(None, description="Conclusão estimada")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseStatistics(BaseModel):
    """Schema para estatísticas de KnowledgeBase"""
    
    total_knowledge_bases: int = Field(..., description="Total de bases de conhecimento")
    active_knowledge_bases: int = Field(..., description="Bases de conhecimento ativas")
    public_knowledge_bases: int = Field(..., description="Bases de conhecimento públicas")
    
    # Por tipo
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    
    # Documentos
    total_documents: int = Field(..., description="Total de documentos")
    total_size_bytes: int = Field(..., description="Tamanho total em bytes")
    
    # Uso
    total_searches: int = Field(..., description="Total de buscas")
    average_search_time_ms: float = Field(..., description="Tempo médio de busca")
    
    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseExport(BaseModel):
    """Schema para exportação de KnowledgeBase"""
    
    kb_id: UUID = Field(..., description="ID da base de conhecimento")
    format: str = Field(..., description="Formato da exportação")
    
    # Configurações
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_embeddings: bool = Field(False, description="Incluir embeddings")
    
    model_config = ConfigDict(from_attributes=True)

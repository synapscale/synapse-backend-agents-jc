"""
Schemas para WorkflowTemplate - templates de workflow
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class WorkflowTemplateBase(BaseModel):
    """Schema base para WorkflowTemplate"""
    
    # Identificação
    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    
    # Categoria e tags
    category: str = Field(..., description="Categoria do template")
    tags: Optional[List[str]] = Field(None, description="Tags do template")
    
    # Configuração do template
    template_data: Dict[str, Any] = Field(..., description="Dados do template")
    
    # Versioning
    version: str = Field("1.0.0", description="Versão do template")
    
    # Status
    is_active: bool = Field(True, description="Template ativo")
    is_public: bool = Field(False, description="Template público")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário criador")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    # Visual
    icon: Optional[str] = Field(None, description="Ícone do template")
    color: Optional[str] = Field(None, description="Cor do template")
    
    # Documentação
    documentation: Optional[str] = Field(None, description="Documentação do template")
    examples: Optional[List[Dict[str, Any]]] = Field(None, description="Exemplos de uso")


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema para criação de WorkflowTemplate"""
    pass


class WorkflowTemplateUpdate(BaseModel):
    """Schema para atualização de WorkflowTemplate"""
    
    name: Optional[str] = Field(None, description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    
    category: Optional[str] = Field(None, description="Categoria do template")
    tags: Optional[List[str]] = Field(None, description="Tags do template")
    
    template_data: Optional[Dict[str, Any]] = Field(None, description="Dados do template")
    version: Optional[str] = Field(None, description="Versão do template")
    
    is_active: Optional[bool] = Field(None, description="Template ativo")
    is_public: Optional[bool] = Field(None, description="Template público")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    
    icon: Optional[str] = Field(None, description="Ícone do template")
    color: Optional[str] = Field(None, description="Cor do template")
    
    documentation: Optional[str] = Field(None, description="Documentação do template")
    examples: Optional[List[Dict[str, Any]]] = Field(None, description="Exemplos de uso")


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema para resposta de WorkflowTemplate"""
    
    id: UUID = Field(..., description="ID único do template")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário criador")
    
    # Estatísticas
    usage_count: Optional[int] = Field(None, description="Número de usos")
    rating_average: Optional[float] = Field(None, description="Avaliação média")
    rating_count: Optional[int] = Field(None, description="Número de avaliações")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateList(BaseModel):
    """Schema para lista de WorkflowTemplate"""
    
    items: List[WorkflowTemplateResponse] = Field(..., description="Lista de templates")
    total: int = Field(..., description="Total de templates")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateUsage(BaseModel):
    """Schema para uso de WorkflowTemplate"""
    
    template_id: UUID = Field(..., description="ID do template")
    workflow_id: UUID = Field(..., description="ID do workflow criado")
    
    # Configurações de uso
    customizations: Optional[Dict[str, Any]] = Field(None, description="Customizações aplicadas")
    
    # Contexto
    used_by: UUID = Field(..., description="ID do usuário que usou")
    used_at: datetime = Field(..., description="Data de uso")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateValidation(BaseModel):
    """Schema para validação de WorkflowTemplate"""
    
    template_id: UUID = Field(..., description="ID do template")
    is_valid: bool = Field(..., description="Template válido")
    
    # Problemas encontrados
    errors: List[str] = Field(..., description="Erros de validação")
    warnings: List[str] = Field(..., description="Avisos de validação")
    
    # Validações específicas
    template_data_valid: bool = Field(..., description="Dados do template válidos")
    nodes_valid: bool = Field(..., description="Nós válidos")
    connections_valid: bool = Field(..., description="Conexões válidas")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplatePreview(BaseModel):
    """Schema para preview de WorkflowTemplate"""
    
    template_id: UUID = Field(..., description="ID do template")
    
    # Preview data
    preview_data: Dict[str, Any] = Field(..., description="Dados de preview")
    
    # Métricas estimadas
    estimated_nodes: int = Field(..., description="Número estimado de nós")
    estimated_connections: int = Field(..., description="Número estimado de conexões")
    estimated_execution_time_ms: Optional[int] = Field(None, description="Tempo estimado de execução")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateRating(BaseModel):
    """Schema para avaliação de WorkflowTemplate"""
    
    template_id: UUID = Field(..., description="ID do template")
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Avaliação
    rating: int = Field(..., ge=1, le=5, description="Avaliação (1-5)")
    review: Optional[str] = Field(None, description="Comentário da avaliação")
    
    # Contexto
    rated_at: datetime = Field(..., description="Data da avaliação")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateStatistics(BaseModel):
    """Schema para estatísticas de WorkflowTemplate"""
    
    total_templates: int = Field(..., description="Total de templates")
    active_templates: int = Field(..., description="Templates ativos")
    public_templates: int = Field(..., description="Templates públicos")
    
    # Por categoria
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    
    # Uso
    total_usage: int = Field(..., description="Total de usos")
    most_used_templates: List[Dict[str, Any]] = Field(..., description="Templates mais usados")
    
    # Avaliações
    average_rating: float = Field(..., description="Avaliação média")
    total_ratings: int = Field(..., description="Total de avaliações")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplateExport(BaseModel):
    """Schema para exportação de WorkflowTemplate"""
    
    template_id: UUID = Field(..., description="ID do template")
    format: str = Field(..., description="Formato da exportação")
    
    # Configurações de exportação
    include_metadata: bool = Field(True, description="Incluir metadata")
    include_documentation: bool = Field(True, description="Incluir documentação")
    include_examples: bool = Field(True, description="Incluir exemplos")
    
    model_config = ConfigDict(from_attributes=True)

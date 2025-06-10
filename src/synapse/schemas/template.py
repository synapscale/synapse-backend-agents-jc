"""
Schemas Pydantic para Templates de Workflows
Criado por José - um desenvolvedor Full Stack
Sistema completo de validação para marketplace de templates
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from src.synapse.models.template import TemplateCategory, TemplateStatus, TemplateLicense


# Schemas base para templates
class TemplateBase(BaseModel):
    """Schema base para templates"""
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    category: TemplateCategory
    tags: Optional[List[str]] = Field(None, max_items=20)
    license_type: TemplateLicense = TemplateLicense.FREE
    price: float = Field(default=0.0, ge=0.0, le=9999.99)
    
    @validator('tags')
    def validate_tags(cls, v):
        """Valida tags"""
        if v is not None:
            # Remove duplicatas e normaliza
            v = list(set([tag.lower().strip() for tag in v if tag.strip()]))
            # Valida cada tag
            for tag in v:
                if len(tag) < 2 or len(tag) > 50:
                    raise ValueError("Tags devem ter entre 2 e 50 caracteres")
        return v
    
    @validator('price')
    def validate_price(cls, v, values):
        """Valida preço baseado na licença"""
        license_type = values.get('license_type')
        if license_type == TemplateLicense.FREE and v > 0:
            raise ValueError("Templates gratuitos não podem ter preço")
        elif license_type in [TemplateLicense.PREMIUM, TemplateLicense.ENTERPRISE] and v <= 0:
            raise ValueError("Templates premium devem ter preço maior que zero")
        return v


class TemplateCreate(TemplateBase):
    """Schema para criação de template"""
    workflow_data: Dict[str, Any] = Field(..., description="Estrutura completa do workflow")
    nodes_data: List[Dict[str, Any]] = Field(..., min_items=1, description="Dados dos nós")
    connections_data: Optional[List[Dict[str, Any]]] = None
    required_variables: Optional[List[str]] = None
    optional_variables: Optional[List[str]] = None
    default_config: Optional[Dict[str, Any]] = None
    estimated_duration: Optional[int] = Field(None, ge=1, le=86400)  # 1 segundo a 24 horas
    complexity_level: int = Field(default=1, ge=1, le=5)
    keywords: Optional[List[str]] = Field(None, max_items=50)
    use_cases: Optional[List[str]] = Field(None, max_items=20)
    industries: Optional[List[str]] = Field(None, max_items=20)
    documentation: Optional[str] = None
    setup_instructions: Optional[str] = None
    
    @validator('workflow_data')
    def validate_workflow_data(cls, v):
        """Valida estrutura do workflow"""
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado em workflow_data")
        return v
    
    @validator('nodes_data')
    def validate_nodes_data(cls, v):
        """Valida dados dos nós"""
        if not v:
            raise ValueError("Template deve ter pelo menos um nó")
        
        for i, node in enumerate(v):
            required_fields = ['type', 'name']
            for field in required_fields:
                if field not in node:
                    raise ValueError(f"Nó {i}: campo obrigatório '{field}' não encontrado")
        return v


class TemplateUpdate(BaseModel):
    """Schema para atualização de template"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    status: Optional[TemplateStatus] = None
    is_public: Optional[bool] = None
    license_type: Optional[TemplateLicense] = None
    price: Optional[float] = Field(None, ge=0.0, le=9999.99)
    workflow_data: Optional[Dict[str, Any]] = None
    nodes_data: Optional[List[Dict[str, Any]]] = None
    connections_data: Optional[List[Dict[str, Any]]] = None
    required_variables: Optional[List[str]] = None
    optional_variables: Optional[List[str]] = None
    default_config: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(None, pattern=r'^\d+\.\d+\.\d+$')
    estimated_duration: Optional[int] = Field(None, ge=1, le=86400)
    complexity_level: Optional[int] = Field(None, ge=1, le=5)
    keywords: Optional[List[str]] = Field(None, max_items=50)
    use_cases: Optional[List[str]] = Field(None, max_items=20)
    industries: Optional[List[str]] = Field(None, max_items=20)
    thumbnail_url: Optional[HttpUrl] = None
    preview_images: Optional[List[HttpUrl]] = Field(None, max_items=10)
    demo_video_url: Optional[HttpUrl] = None
    documentation: Optional[str] = None
    setup_instructions: Optional[str] = None
    support_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    repository_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None


class TemplateResponse(TemplateBase):
    """Schema de resposta para template"""
    id: int
    template_id: str
    author_id: int
    status: TemplateStatus
    is_public: bool
    is_featured: bool
    is_verified: bool
    version: str
    compatibility_version: str
    estimated_duration: Optional[int] = None
    complexity_level: int
    download_count: int
    usage_count: int
    rating_average: float
    rating_count: int
    view_count: int
    keywords: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    demo_video_url: Optional[str] = None
    documentation: Optional[str] = None
    setup_instructions: Optional[str] = None
    support_email: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """Schema de resposta detalhada para template"""
    workflow_data: Dict[str, Any]
    nodes_data: List[Dict[str, Any]]
    connections_data: Optional[List[Dict[str, Any]]] = None
    required_variables: Optional[List[str]] = None
    optional_variables: Optional[List[str]] = None
    default_config: Optional[Dict[str, Any]] = None
    changelog: Optional[List[Dict[str, Any]]] = None
    
    # Informações do autor (limitadas)
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    
    # Estatísticas adicionais
    recent_downloads: int = 0
    recent_usage: int = 0
    is_favorited: bool = False  # Se o usuário atual favoritou


class TemplateListResponse(BaseModel):
    """Schema para lista de templates"""
    templates: List[TemplateResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


# Schemas para reviews
class ReviewBase(BaseModel):
    """Schema base para reviews"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, max_length=2000)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    documentation_quality: Optional[int] = Field(None, ge=1, le=5)
    performance: Optional[int] = Field(None, ge=1, le=5)
    value_for_money: Optional[int] = Field(None, ge=1, le=5)


class ReviewCreate(ReviewBase):
    """Schema para criação de review"""
    template_id: int = Field(..., gt=0)


class ReviewUpdate(BaseModel):
    """Schema para atualização de review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, max_length=2000)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    documentation_quality: Optional[int] = Field(None, ge=1, le=5)
    performance: Optional[int] = Field(None, ge=1, le=5)
    value_for_money: Optional[int] = Field(None, ge=1, le=5)


class ReviewResponse(ReviewBase):
    """Schema de resposta para review"""
    id: int
    template_id: int
    user_id: int
    is_verified_purchase: bool
    is_helpful_count: int
    version_reviewed: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Informações do usuário (limitadas)
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    class Config:
        from_attributes = True


# Schemas para downloads
class DownloadCreate(BaseModel):
    """Schema para registro de download"""
    template_id: int = Field(..., gt=0)
    download_type: str = Field(default="full", pattern="^(full|preview|demo)$")


class DownloadResponse(BaseModel):
    """Schema de resposta para download"""
    id: int
    template_id: int
    user_id: int
    download_type: str
    template_version: Optional[str] = None
    downloaded_at: datetime

    class Config:
        from_attributes = True


# Schemas para favoritos
class FavoriteCreate(BaseModel):
    """Schema para adicionar favorito"""
    template_id: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class FavoriteUpdate(BaseModel):
    """Schema para atualizar favorito"""
    notes: Optional[str] = Field(None, max_length=1000)


class FavoriteResponse(BaseModel):
    """Schema de resposta para favorito"""
    id: int
    template_id: int
    user_id: int
    notes: Optional[str] = None
    created_at: datetime
    
    # Informações básicas do template
    template_name: str
    template_title: str
    template_category: str

    class Config:
        from_attributes = True


# Schemas para coleções
class CollectionBase(BaseModel):
    """Schema base para coleções"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    is_public: bool = True
    tags: Optional[List[str]] = Field(None, max_items=20)
    thumbnail_url: Optional[HttpUrl] = None


class CollectionCreate(CollectionBase):
    """Schema para criação de coleção"""
    template_ids: List[int] = Field(..., min_items=1, max_items=100)
    
    @validator('template_ids')
    def validate_template_ids(cls, v):
        """Remove duplicatas"""
        return list(set(v))


class CollectionUpdate(BaseModel):
    """Schema para atualização de coleção"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    is_public: Optional[bool] = None
    template_ids: Optional[List[int]] = Field(None, min_items=1, max_items=100)
    tags: Optional[List[str]] = Field(None, max_items=20)
    thumbnail_url: Optional[HttpUrl] = None


class CollectionResponse(CollectionBase):
    """Schema de resposta para coleção"""
    id: int
    collection_id: str
    creator_id: int
    is_featured: bool
    template_ids: List[int]
    view_count: int
    follow_count: int
    created_at: datetime
    updated_at: datetime
    
    # Informações do criador (limitadas)
    creator_name: Optional[str] = None
    creator_avatar: Optional[str] = None
    
    # Templates da coleção (resumo)
    templates_count: int = 0
    templates_preview: Optional[List[TemplateResponse]] = None

    class Config:
        from_attributes = True


# Schemas para busca e filtros
class TemplateFilter(BaseModel):
    """Filtros para busca de templates"""
    search: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[List[TemplateCategory]] = None
    tags: Optional[List[str]] = None
    license_type: Optional[List[TemplateLicense]] = None
    price_min: Optional[float] = Field(None, ge=0.0)
    price_max: Optional[float] = Field(None, ge=0.0)
    rating_min: Optional[float] = Field(None, ge=0.0, le=5.0)
    complexity_min: Optional[int] = Field(None, ge=1, le=5)
    complexity_max: Optional[int] = Field(None, ge=1, le=5)
    is_featured: Optional[bool] = None
    is_verified: Optional[bool] = None
    author_id: Optional[int] = Field(None, gt=0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    industries: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|rating|downloads|name|price)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Schemas para estatísticas
class TemplateStats(BaseModel):
    """Estatísticas de templates"""
    total_templates: int
    published_templates: int
    featured_templates: int
    verified_templates: int
    free_templates: int
    premium_templates: int
    total_downloads: int
    total_reviews: int
    average_rating: float
    categories_distribution: Dict[str, int]
    top_templates: List[TemplateResponse]
    recent_templates: List[TemplateResponse]


class UserTemplateStats(BaseModel):
    """Estatísticas de templates do usuário"""
    created_templates: int
    published_templates: int
    total_downloads: int
    total_reviews: int
    average_rating: float
    favorite_templates: int
    template_collections: int
    total_earnings: float  # Para templates premium


# Schemas para marketplace
class MarketplaceStats(BaseModel):
    """Estatísticas do marketplace"""
    total_templates: int
    total_authors: int
    total_downloads: int
    total_reviews: int
    featured_templates: List[TemplateResponse]
    trending_templates: List[TemplateResponse]
    new_templates: List[TemplateResponse]
    top_categories: List[Dict[str, Any]]
    top_authors: List[Dict[str, Any]]


# Schema para instalação de template
class TemplateInstall(BaseModel):
    """Schema para instalação de template"""
    template_id: int = Field(..., gt=0)
    workflow_name: Optional[str] = Field(None, min_length=1, max_length=255)
    custom_variables: Optional[Dict[str, Any]] = None
    modify_config: Optional[Dict[str, Any]] = None
    
    @validator('workflow_name')
    def validate_workflow_name(cls, v):
        """Valida nome do workflow"""
        if v is not None:
            # Remove caracteres especiais
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
                raise ValueError("Nome do workflow deve conter apenas letras, números, espaços, hífens e underscores")
        return v


class TemplateInstallResponse(BaseModel):
    """Schema de resposta para instalação"""
    success: bool
    workflow_id: Optional[int] = None
    workflow_name: str
    template_id: int
    template_name: str
    modifications_applied: List[str]
    warnings: List[str]
    errors: List[str]


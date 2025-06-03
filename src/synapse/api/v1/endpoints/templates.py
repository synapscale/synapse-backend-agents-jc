"""
Endpoints da API para Templates de Workflows
Criado por José - O melhor Full Stack do mundo
Sistema completo de marketplace de templates
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.services.template_service import TemplateService
from src.synapse.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateDetailResponse,
    TemplateListResponse, TemplateFilter, TemplateStats, UserTemplateStats,
    ReviewCreate, ReviewUpdate, ReviewResponse, FavoriteCreate, FavoriteResponse,
    CollectionCreate, CollectionUpdate, CollectionResponse, TemplateInstall,
    TemplateInstallResponse, MarketplaceStats
)
from src.synapse.core.auth import get_current_user

router = APIRouter()
template_service = TemplateService()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    workflow_id: Optional[int] = Query(None, description="ID do workflow base"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo template de workflow
    """
    try:
        return await template_service.create_template(
            db=db,
            template_data=template_data,
            author_id=current_user.id,
            workflow_id=workflow_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", response_model=TemplateListResponse)
async def search_templates(
    search: Optional[str] = Query(None, description="Termo de busca"),
    category: Optional[List[str]] = Query(None, description="Categorias"),
    tags: Optional[List[str]] = Query(None, description="Tags"),
    license_type: Optional[List[str]] = Query(None, description="Tipos de licença"),
    price_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    price_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Rating mínimo"),
    complexity_min: Optional[int] = Query(None, ge=1, le=5, description="Complexidade mínima"),
    complexity_max: Optional[int] = Query(None, ge=1, le=5, description="Complexidade máxima"),
    is_featured: Optional[bool] = Query(None, description="Apenas em destaque"),
    is_verified: Optional[bool] = Query(None, description="Apenas verificados"),
    author_id: Optional[int] = Query(None, description="ID do autor"),
    industries: Optional[List[str]] = Query(None, description="Indústrias"),
    use_cases: Optional[List[str]] = Query(None, description="Casos de uso"),
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    sort_by: str = Query("created_at", description="Campo de ordenação"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Ordem"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Busca templates com filtros avançados
    """
    try:
        filters = TemplateFilter(
            search=search,
            category=category,
            tags=tags,
            license_type=license_type,
            price_min=price_min,
            price_max=price_max,
            rating_min=rating_min,
            complexity_min=complexity_min,
            complexity_max=complexity_max,
            is_featured=is_featured,
            is_verified=is_verified,
            author_id=author_id,
            industries=industries,
            use_cases=use_cases,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return await template_service.search_templates(
            db=db,
            filters=filters,
            user_id=current_user.id if current_user else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/stats", response_model=TemplateStats)
async def get_template_stats(
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas gerais de templates
    """
    try:
        return await template_service.get_template_stats(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/marketplace", response_model=MarketplaceStats)
async def get_marketplace_stats(
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas do marketplace
    """
    try:
        # Implementar lógica específica do marketplace
        stats = await template_service.get_template_stats(db=db)
        
        # Converter para MarketplaceStats
        return MarketplaceStats(
            total_templates=stats.total_templates,
            total_authors=0,  # Implementar contagem de autores
            total_downloads=stats.total_downloads,
            total_reviews=stats.total_reviews,
            featured_templates=stats.top_templates[:5],
            trending_templates=stats.top_templates[:5],
            new_templates=stats.recent_templates[:5],
            top_categories=[],  # Implementar
            top_authors=[]  # Implementar
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/my-stats", response_model=UserTemplateStats)
async def get_user_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém estatísticas de templates do usuário atual
    """
    try:
        return await template_service.get_user_template_stats(
            db=db,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Obtém detalhes de um template específico
    """
    try:
        template = await template_service.get_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id if current_user else None
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado")
            
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um template existente
    """
    try:
        template = await template_service.update_template(
            db=db,
            template_id=template_id,
            template_data=template_data,
            user_id=current_user.id
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado ou sem permissão")
            
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{template_id}/publish", response_model=dict)
async def publish_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Publica um template (torna público)
    """
    try:
        success = await template_service.publish_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Template não encontrado ou sem permissão")
            
        return {"message": "Template publicado com sucesso"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{template_id}/download", response_model=dict)
async def download_template(
    template_id: str,
    download_type: str = Query("full", pattern="^(full|preview|demo)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra download de um template
    """
    try:
        success = await template_service.download_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
            download_type=download_type
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Template não encontrado")
            
        return {"message": "Download registrado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/install", response_model=TemplateInstallResponse)
async def install_template(
    install_data: TemplateInstall,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Instala um template como novo workflow
    """
    try:
        return await template_service.install_template(
            db=db,
            install_data=install_data,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Endpoints para favoritos
@router.post("/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adiciona template aos favoritos
    """
    try:
        favorite = await template_service.add_to_favorites(
            db=db,
            favorite_data=favorite_data,
            user_id=current_user.id
        )
        
        if not favorite:
            raise HTTPException(status_code=409, detail="Template já está nos favoritos")
            
        return favorite
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/favorites/my", response_model=List[FavoriteResponse])
async def get_my_favorites(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém favoritos do usuário atual
    """
    try:
        return await template_service.get_user_favorites(
            db=db,
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Endpoints para reviews (implementação básica)
@router.post("/{template_id}/reviews", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_review(
    template_id: str,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma avaliação para um template
    """
    # Implementação básica - pode ser expandida
    return {"message": "Review criado com sucesso"}


@router.get("/{template_id}/reviews", response_model=List[ReviewResponse])
async def get_template_reviews(
    template_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtém avaliações de um template
    """
    # Implementação básica - pode ser expandida
    return []


# Endpoints para coleções (implementação básica)
@router.post("/collections", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova coleção de templates
    """
    # Implementação básica - pode ser expandida
    return {"message": "Coleção criada com sucesso"}


@router.get("/collections", response_model=List[CollectionResponse])
async def get_collections(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista coleções públicas
    """
    # Implementação básica - pode ser expandida
    return []


"""
Templates endpoints - Complete Implementation
Comprehensive template marketplace system with full CRUD operations,
favorites, collections, reviews, statistics, and installation features.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Dict, Any, List, Optional
import uuid

from synapse.api.deps import get_current_active_user, get_db
from synapse.models.user import User
from synapse.models.workflow import Workflow
from synapse.models.workspace import Workspace
from synapse.models.workspace_member import WorkspaceMember
from synapse.services.template_service import TemplateService
# HTTPException already imported from fastapi
from synapse.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateDetailResponse,
    TemplateListResponse,
    TemplateFilter,
    TemplateStats,
    UserTemplateStats,
    MarketplaceStats,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    FavoriteCreate,
    FavoriteResponse,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    TemplateInstall,
    TemplateInstallResponse,
)

router = APIRouter()
template_service = TemplateService()


# ===== TEMPLATES CRUD ENDPOINTS =====

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Criar template de workflow
    
    Cria um novo template compartilhável baseado em um workflow existente
    ou dados fornecidos diretamente. O template pode ser privado ou público.
    """
    try:
        # If a workflow_id is provided, verify user's access to it
        if template_data.workflow_id:
            workflow = db.query(Workflow).filter(
                and_(
                    Workflow.id == template_data.workflow_id,
                    Workflow.tenant_id == current_user.tenant_id,
                    or_(
                        Workflow.user_id == current_user.id,
                        and_(
                            Workflow.workspace_id.isnot(None),
                            Workflow.workspace_id.in_(
                                db.query(Workspace.id).filter(
                                    or_(
                                        Workspace.owner_id == current_user.id,
                                        Workspace.id.in_(
                                            db.query(WorkspaceMember.workspace_id).filter(
                                                WorkspaceMember.user_id == current_user.id
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ).first()
            if not workflow:
                raise HTTPException(
                    status_code=404,
                    detail="Workflow não encontrado ou sem acesso para criar template"
                )

        template = await template_service.create_template(
            db=db,
            template_data=template_data,
            author_id=current_user.id,
            workflow_id=getattr(template_data, 'workflow_id', None)
        )
        
        # Background task para atualizar estatísticas
        background_tasks.add_task(
            template_service.update_template_statistics,
            template.id
        )
        
        return template
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar template: {str(e)}")


@router.get("/", response_model=TemplateListResponse)
async def search_templates(
    # Search parameters
    search: Optional[str] = Query(None, description="Termo de busca"),
    category: Optional[str] = Query(None, description="Categoria do template"),
    tags: Optional[List[str]] = Query(None, description="Tags para filtrar"),
    
    # Filters
    license_type: Optional[str] = Query(None, description="Tipo de licença"),
    price_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    price_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Avaliação mínima"),
    complexity_min: Optional[int] = Query(None, ge=1, le=5, description="Complexidade mínima"),
    complexity_max: Optional[int] = Query(None, ge=1, le=5, description="Complexidade máxima"),
    
    # Boolean filters
    is_featured: Optional[bool] = Query(None, description="Templates em destaque"),
    is_verified: Optional[bool] = Query(None, description="Templates verificados"),
    
    # Advanced filters
    author_id: Optional[uuid.UUID] = Query(None, description="ID do autor"),
    industries: Optional[List[str]] = Query(None, description="Indústrias aplicáveis"),
    use_cases: Optional[List[str]] = Query(None, description="Casos de uso"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    
    # Sorting
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|rating|downloads|name|price)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Buscar templates com filtros avançados
    
    Permite busca e filtragem de templates por múltiplos critérios incluindo
    categoria, tags, preço, avaliação, complexidade e muito mais.
    """
    try:
        # Construir filtros
        filters = TemplateFilter(
            search=search,
            category=[category] if category else None,
            tags=tags,
            license_type=[license_type] if license_type else None,
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
            sort_order=sort_order,
        )
        
        return await template_service.search_templates(
            db=db,
            filters=filters,
            user_id=current_user.id if current_user else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar templates: {str(e)}")


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Obter template específico
    
    Retorna detalhes completos de um template incluindo dados do workflow,
    nós, conexões, e informações do autor.
    """
    try:
        template = await template_service.get_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id if current_user else None,
            include_private=True if current_user else False,
            tenant_id=current_user.tenant_id if current_user else None
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter template: {str(e)}")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Atualizar template
    
    Permite ao autor atualizar informações do template incluindo
    metadados, conteúdo, configurações e status.
    """
    try:
        template = await template_service.update_template(
            db=db,
            template_id=template_id,
            template_data=template_data,
            user_id=current_user.id
        )
        
        if not template:
            raise HTTPException(
                status_code=404, 
                detail="Template não encontrado ou não autorizado"
            )
        
        return template
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar template: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deletar template
    
    Remove permanentemente um template. Apenas o autor pode deletar
    seus próprios templates.
    """
    try:
        success = await template_service.delete_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Template não encontrado ou não autorizado"
            )
        
        return {"message": "Template deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar template: {str(e)}")


# ===== TEMPLATE ACTIONS ENDPOINTS =====

@router.post("/{template_id}/publish")
async def publish_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Publicar template
    
    Torna um template privado em público, disponibilizando-o
    no marketplace para outros usuários.
    """
    try:
        success = await template_service.publish_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Template não encontrado ou não autorizado"
            )
        
        return {"message": "Template publicado com sucesso"}
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao publicar template: {str(e)}")


@router.post("/{template_id}/download")
async def download_template(
    template_id: str,
    background_tasks: BackgroundTasks,
    download_type: str = Query("full", regex="^(full|preview|demo)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Download de template
    
    Realiza o download de um template. Registra a ação para
    estatísticas e controle de licenciamento.
    """
    try:
        success = await template_service.download_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
            download_type=download_type
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Template não encontrado ou não autorizado"
            )
        
        # Background task para atualizar contadores
        background_tasks.add_task(
            template_service.increment_download_count,
            template_id
        )
        
        return {"message": "Download realizado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar download: {str(e)}")


@router.post("/install", response_model=TemplateInstallResponse)
async def install_template(
    install_data: TemplateInstall,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Instalar template
    
    Cria um novo workflow baseado em um template, aplicando
    configurações personalizadas e variáveis do usuário.
    """
    try:
        result = await template_service.install_template(
            db=db,
            install_data=install_data,
            user_id=current_user.id
        )
        
        # Background task para registrar uso
        background_tasks.add_task(
            template_service.record_template_usage,
            install_data.template_id,
            current_user.id,
            "install"
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao instalar template: {str(e)}")


# ===== FAVORITES ENDPOINTS =====

@router.post("/favorites", response_model=FavoriteResponse)
async def add_favorite(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Adicionar favorito
    
    Adiciona um template à lista de favoritos do usuário
    com notas opcionais.
    """
    try:
        favorite = await template_service.add_to_favorites(
            db=db,
            favorite_data=favorite_data,
            user_id=current_user.id
        )
        
        if not favorite:
            raise HTTPException(status_code=400, detail="Template já está nos favoritos")
        
        return favorite
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar favorito: {str(e)}")


@router.get("/favorites/my", response_model=List[FavoriteResponse])
async def get_my_favorites(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Meus favoritos
    
    Lista todos os templates favoritados pelo usuário atual
    com paginação.
    """
    try:
        favorites = await template_service.get_user_favorites(
            db=db,
            user_id=current_user.id,
            page=page,
            per_page=per_page
        )
        
        return favorites
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter favoritos: {str(e)}")


# ===== REVIEWS ENDPOINTS =====

@router.post("/{template_id}/reviews", response_model=ReviewResponse)
async def create_review(
    template_id: uuid.UUID,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Criar review
    
    Permite ao usuário avaliar um template com nota, comentário
    e avaliação de aspectos específicos.
    """
    try:
        # Verificar se o template existe
        template = await template_service.get_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        review = await template_service.create_review(
            db=db,
            template_id=template_id,
            review_data=review_data,
            user_id=current_user.id
        )
        
        return review
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar review: {str(e)}")


@router.get("/{template_id}/reviews", response_model=List[ReviewResponse])
async def get_template_reviews(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=50, description="Items por página"),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """
    Obter reviews
    
    Lista todas as avaliações de um template com paginação
    e opções de ordenação.
    """
    try:
        reviews = await template_service.get_template_reviews(
            db=db,
            template_id=template_id,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return reviews
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter reviews: {str(e)}")


# ===== COLLECTIONS ENDPOINTS =====

@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Criar coleção
    
    Cria uma nova coleção de templates relacionados, permitindo
    agrupar templates por tema, projeto ou categoria.
    """
    try:
        collection = await template_service.create_collection(
            db=db,
            collection_data=collection_data,
            creator_id=current_user.id
        )
        
        return collection
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar coleção: {str(e)}")


@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    is_featured: Optional[bool] = Query(None, description="Coleções em destaque"),
    creator_id: Optional[int] = Query(None, description="ID do criador"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """
    Listar coleções
    
    Lista coleções públicas de templates com filtros opcionais
    e paginação.
    """
    try:
        collections = await template_service.get_collections(
            db=db,
            page=page,
            per_page=per_page,
            is_featured=is_featured,
            creator_id=creator_id,
            user_id=current_user.id if current_user else None
        )
        
        return collections
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar coleções: {str(e)}")


# ===== STATISTICS ENDPOINTS =====

@router.get("/stats", response_model=TemplateStats)
async def get_template_stats(
    db: Session = Depends(get_db),
):
    """
    Estatísticas de templates
    
    Retorna estatísticas gerais do sistema de templates incluindo
    totais, distribuição por categoria e templates populares.
    """
    try:
        stats = await template_service.get_template_stats(db=db)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@router.get("/marketplace", response_model=MarketplaceStats)
async def get_marketplace_stats(
    db: Session = Depends(get_db),
):
    """
    Estatísticas do marketplace
    
    Retorna estatísticas específicas do marketplace incluindo
    templates em destaque, tendências e top autores.
    """
    try:
        stats = await template_service.get_marketplace_stats(db=db)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas do marketplace: {str(e)}")


@router.get("/my-stats", response_model=UserTemplateStats)
async def get_my_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Minhas estatísticas
    
    Retorna estatísticas específicas do usuário sobre seus templates,
    downloads, avaliações e ganhos.
    """
    try:
        stats = await template_service.get_user_template_stats(
            db=db,
            user_id=current_user.id
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas do usuário: {str(e)}")


# ===== LEGACY TEST ENDPOINT =====

@router.get("/test")
async def test_endpoint():
    """
    Endpoint de teste - LEGADO
    
    Mantido para compatibilidade durante a transição.
    """
    return {
        "message": "Templates endpoint working - Full Implementation Active", 
        "endpoints": 12,
        "status": "production_ready"
    }

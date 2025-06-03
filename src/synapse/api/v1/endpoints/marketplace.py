"""
Endpoints da API para Marketplace
Criado por José - O melhor Full Stack do mundo
Endpoints para gerenciar marketplace de componentes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.services.marketplace_service import MarketplaceService
from src.synapse.schemas.marketplace import (
    ComponentCreate, ComponentUpdate, ComponentResponse, ComponentSearch,
    ComponentSearchResponse, RatingCreate, RatingResponse, RatingStats,
    PurchaseCreate, PurchaseResponse, ComponentVersionResponse,
    MarketplaceStats, BulkComponentOperation, BulkOperationResponse,
    ComponentModerationResponse, ModerationAction
)
from src.synapse.api.deps import get_current_user, get_admin_user

router = APIRouter()

# ==================== COMPONENTES ====================

@router.post("/components", response_model=ComponentResponse)
async def create_component(
    component_data: ComponentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo componente no marketplace"""
    service = MarketplaceService(db)
    return service.create_component(component_data, current_user.id)

@router.get("/components", response_model=ComponentSearchResponse)
async def search_components(
    query: Optional[str] = Query(None, description="Termo de busca"),
    category: Optional[str] = Query(None, description="Categoria do componente"),
    component_type: Optional[str] = Query(None, description="Tipo do componente"),
    tags: Optional[List[str]] = Query(None, description="Tags para filtrar"),
    is_free: Optional[bool] = Query(None, description="Apenas componentes gratuitos"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Rating mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    sort_by: Optional[str] = Query("popularity", description="Ordenação"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    db: Session = Depends(get_db)
):
    """Busca componentes no marketplace"""
    search_params = ComponentSearch(
        query=query,
        category=category,
        component_type=component_type,
        tags=tags or [],
        is_free=is_free,
        min_rating=min_rating,
        max_price=max_price,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    service = MarketplaceService(db)
    return service.search_components(search_params)

@router.get("/components/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: int,
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um componente"""
    service = MarketplaceService(db)
    component = service.get_component(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return component

@router.put("/components/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_id: int,
    component_data: ComponentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um componente"""
    service = MarketplaceService(db)
    component = service.update_component(component_id, component_data, current_user.id)
    if not component:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return component

@router.delete("/components/{component_id}")
async def delete_component(
    component_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um componente"""
    service = MarketplaceService(db)
    success = service.delete_component(component_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return {"message": "Componente removido com sucesso"}

@router.post("/components/{component_id}/download")
async def download_component(
    component_id: int,
    version: Optional[str] = Query(None, description="Versão específica"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Faz download de um componente"""
    service = MarketplaceService(db)
    download_info = service.download_component(component_id, current_user.id, version)
    if not download_info:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return download_info

@router.post("/components/{component_id}/install")
async def install_component(
    component_id: int,
    workspace_id: Optional[int] = Query(None, description="ID do workspace"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Instala um componente no workspace"""
    service = MarketplaceService(db)
    installation = service.install_component(component_id, current_user.id, workspace_id)
    if not installation:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return installation

# ==================== AVALIAÇÕES ====================

@router.post("/components/{component_id}/ratings", response_model=RatingResponse)
async def create_rating(
    component_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma avaliação para um componente"""
    service = MarketplaceService(db)
    rating_data.component_id = component_id
    return service.create_rating(rating_data, current_user.id)

@router.get("/components/{component_id}/ratings", response_model=List[RatingResponse])
async def get_component_ratings(
    component_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("newest", pattern="^(newest|oldest|highest|lowest|helpful)$"),
    db: Session = Depends(get_db)
):
    """Obtém avaliações de um componente"""
    service = MarketplaceService(db)
    return service.get_component_ratings(component_id, limit, offset, sort_by)

@router.get("/components/{component_id}/ratings/stats", response_model=RatingStats)
async def get_rating_stats(
    component_id: int,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de avaliações"""
    service = MarketplaceService(db)
    return service.get_rating_stats(component_id)

@router.put("/ratings/{rating_id}", response_model=RatingResponse)
async def update_rating(
    rating_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza uma avaliação"""
    service = MarketplaceService(db)
    rating = service.update_rating(rating_id, rating_data, current_user.id)
    if not rating:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return rating

@router.delete("/ratings/{rating_id}")
async def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove uma avaliação"""
    service = MarketplaceService(db)
    success = service.delete_rating(rating_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return {"message": "Avaliação removida com sucesso"}

@router.post("/ratings/{rating_id}/helpful")
async def mark_rating_helpful(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca uma avaliação como útil"""
    service = MarketplaceService(db)
    success = service.mark_rating_helpful(rating_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return {"message": "Avaliação marcada como útil"}

# ==================== COMPRAS ====================

@router.post("/components/{component_id}/purchase", response_model=PurchaseResponse)
async def purchase_component(
    component_id: int,
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compra um componente premium"""
    service = MarketplaceService(db)
    purchase_data.component_id = component_id
    return service.purchase_component(purchase_data, current_user.id)

@router.get("/purchases", response_model=List[PurchaseResponse])
async def get_user_purchases(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém compras do usuário"""
    service = MarketplaceService(db)
    return service.get_user_purchases(current_user.id, limit, offset)

@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de uma compra"""
    service = MarketplaceService(db)
    purchase = service.get_purchase(purchase_id, current_user.id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    return purchase

# ==================== VERSÕES ====================

@router.get("/components/{component_id}/versions", response_model=List[ComponentVersionResponse])
async def get_component_versions(
    component_id: int,
    db: Session = Depends(get_db)
):
    """Obtém versões de um componente"""
    service = MarketplaceService(db)
    return service.get_component_versions(component_id)

@router.post("/components/{component_id}/versions")
async def create_component_version(
    component_id: int,
    version: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova versão do componente"""
    service = MarketplaceService(db)
    version_info = service.create_component_version(
        component_id, version, file, current_user.id
    )
    if not version_info:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return version_info

# ==================== FAVORITOS ====================

@router.post("/components/{component_id}/favorite")
async def favorite_component(
    component_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adiciona componente aos favoritos"""
    service = MarketplaceService(db)
    success = service.favorite_component(component_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return {"message": "Componente adicionado aos favoritos"}

@router.delete("/components/{component_id}/favorite")
async def unfavorite_component(
    component_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove componente dos favoritos"""
    service = MarketplaceService(db)
    success = service.unfavorite_component(component_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return {"message": "Componente removido dos favoritos"}

@router.get("/favorites", response_model=List[ComponentResponse])
async def get_user_favorites(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém componentes favoritos do usuário"""
    service = MarketplaceService(db)
    return service.get_user_favorites(current_user.id, limit, offset)

# ==================== ESTATÍSTICAS ====================

@router.get("/stats", response_model=MarketplaceStats)
async def get_marketplace_stats(
    db: Session = Depends(get_db)
):
    """Obtém estatísticas do marketplace"""
    service = MarketplaceService(db)
    return service.get_marketplace_stats()

@router.get("/components/{component_id}/stats")
async def get_component_stats(
    component_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de um componente"""
    service = MarketplaceService(db)
    stats = service.get_component_stats(component_id, days)
    if not stats:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return stats

@router.get("/my-components/stats")
async def get_author_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas dos componentes do autor"""
    service = MarketplaceService(db)
    return service.get_author_stats(current_user.id)

# ==================== CATEGORIAS E TAGS ====================

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db)
):
    """Obtém categorias disponíveis"""
    service = MarketplaceService(db)
    return service.get_categories()

@router.get("/tags")
async def get_popular_tags(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Obtém tags populares"""
    service = MarketplaceService(db)
    return service.get_popular_tags(limit)

# ==================== RECOMENDAÇÕES ====================

@router.get("/recommendations", response_model=List[ComponentResponse])
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém recomendações personalizadas"""
    service = MarketplaceService(db)
    return service.get_recommendations(current_user.id, limit)

@router.get("/components/{component_id}/similar", response_model=List[ComponentResponse])
async def get_similar_components(
    component_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Obtém componentes similares"""
    service = MarketplaceService(db)
    return service.get_similar_components(component_id, limit)

# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/moderation", response_model=List[ComponentModerationResponse])
async def get_pending_moderation(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Obtém componentes pendentes de moderação"""
    service = MarketplaceService(db)
    return service.get_pending_moderation(limit, offset)

@router.post("/admin/components/{component_id}/moderate")
async def moderate_component(
    component_id: int,
    action: ModerationAction,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Modera um componente"""
    service = MarketplaceService(db)
    result = service.moderate_component(component_id, action, current_admin.id)
    if not result:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    return {"message": f"Componente {action.action} com sucesso"}

@router.post("/admin/components/bulk", response_model=BulkOperationResponse)
async def bulk_component_operation(
    operation: BulkComponentOperation,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Operação em lote em componentes"""
    service = MarketplaceService(db)
    return service.bulk_component_operation(operation, current_admin.id)

@router.post("/admin/components/{component_id}/feature")
async def feature_component(
    component_id: int,
    featured: bool = True,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Destaca ou remove destaque de um componente"""
    service = MarketplaceService(db)
    success = service.feature_component(component_id, featured, current_admin.id)
    if not success:
        raise HTTPException(status_code=404, detail="Componente não encontrado")
    
    action = "destacado" if featured else "removido dos destaques"
    return {"message": f"Componente {action} com sucesso"}

# ==================== RELATÓRIOS ====================

@router.get("/admin/reports/revenue")
async def get_revenue_report(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Relatório de receita"""
    service = MarketplaceService(db)
    return service.get_revenue_report(start_date, end_date)

@router.get("/admin/reports/downloads")
async def get_downloads_report(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Relatório de downloads"""
    service = MarketplaceService(db)
    return service.get_downloads_report(start_date, end_date)

@router.get("/admin/reports/top-components")
async def get_top_components_report(
    metric: str = Query("downloads", pattern="^(downloads|revenue|rating)$"),
    limit: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Relatório de top componentes"""
    service = MarketplaceService(db)
    return service.get_top_components_report(metric, limit)


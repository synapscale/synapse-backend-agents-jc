"""
Marketplace endpoints - Complete Implementation
Comprehensive marketplace system with full CRUD operations, search, ratings, downloads, purchases, versions, favorites, moderation, and reporting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from synapse.api.deps import get_current_active_user, get_db
from synapse.models.user import User
from synapse.schemas.marketplace import (
    ComponentCreate,
    ComponentUpdate,
    ComponentResponse,
    ComponentSearch,
    ComponentSearchResponse,
    RatingCreate,
    RatingResponse,
    RatingStats,
    DownloadResponse,
    PurchaseCreate,
    PurchaseResponse,

    MarketplaceStats,
    BulkComponentOperation,
    BulkOperationResponse,
    ComponentModerationResponse,
    ModerationAction,
)
from synapse.services.marketplace_service import MarketplaceService

router = APIRouter()

# ====== COMPONENT CRUD & SEARCH ======
@router.post("/", response_model=ComponentResponse)
async def create_component(
    component_data: ComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new marketplace component"""
    try:
        service = MarketplaceService(db)
        component = service.create_component(component_data, current_user.id)
        if not component:
            raise HTTPException(status_code=400, detail="Erro ao criar componente")
        return component
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ComponentSearchResponse)
async def search_components(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    component_type: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    is_free: Optional[bool] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("popularity", regex="^(popularity|rating|downloads|newest|price_low|price_high)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search marketplace components with filters"""
    try:
        service = MarketplaceService(db)
        params: Dict[str, Any] = {
            "query": query,
            "category": category,
            "component_type": component_type,
            "tags": tags or [],
            "is_free": is_free,
            "min_rating": min_rating or 0,
            "max_price": max_price,
            "sort_by": sort_by,
            "sort_order": "desc",
            "page": offset // limit + 1,
            "limit": limit,
        }
        return service.search_components(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """Get a single component by ID"""
    try:
        service = MarketplaceService(db)
        comp = service.get_component_by_id(component_id)
        if not comp:
            raise HTTPException(status_code=404, detail="Componente não encontrado")
        return comp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_id: str,
    component_data: ComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a marketplace component"""
    try:
        service = MarketplaceService(db)
        updated = service.update_component(component_id, component_data, current_user.id)
        if not updated:
            raise HTTPException(status_code=404, detail="Componente não encontrado ou não autorizado")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{component_id}")
async def delete_component(
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a marketplace component"""
    try:
        service = MarketplaceService(db)
        success = service.delete_component(component_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Componente não encontrado ou não autorizado")
        return {"detail": "Componente deletado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== DOWNLOAD & INSTALL ======
@router.post("/{component_id}/download", response_model=DownloadResponse)
async def download_component(
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Register a component download"""
    try:
        service = MarketplaceService(db)
        dl = service.download_component(component_id, current_user.id)
        return dl
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== RATINGS ======
@router.post("/{component_id}/ratings", response_model=RatingResponse)
async def create_rating(
    component_id: str,
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a rating to a component"""
    try:
        service = MarketplaceService(db)
        return service.create_rating(component_id, rating_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{component_id}/ratings", response_model=List[RatingResponse])
async def get_ratings(
    component_id: str,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("newest"),
    db: Session = Depends(get_db),
):
    """Get ratings for a component"""
    try:
        service = MarketplaceService(db)
        return service.get_component_ratings(component_id, limit=limit, offset=offset, sort_by=sort_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{component_id}/ratings/stats", response_model=RatingStats)
async def get_rating_stats(
    component_id: str,
    db: Session = Depends(get_db),
):
    """Get rating statistics for a component"""
    try:
        service = MarketplaceService(db)
        return service.get_rating_stats(component_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== PURCHASES ======
@router.post("/{component_id}/purchase", response_model=PurchaseResponse)
async def purchase_component(
    component_id: str,
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Purchase a premium component"""
    try:
        service = MarketplaceService(db)
        return service.purchase_component(component_id, purchase_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases/my", response_model=List[PurchaseResponse])
async def get_my_purchases(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get purchases for current user"""
    try:
        service = MarketplaceService(db)
        return service.get_user_purchases(current_user.id, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific purchase by ID"""
    try:
        service = MarketplaceService(db)
        result = service.get_purchase(purchase_id, current_user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Compra não encontrada")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== COMPONENT METADATA ======
@router.get("/{component_id}/metadata", response_model=Dict[str, Any])
async def get_component_metadata(
    component_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get metadata for a component including current version info"""
    try:
        service = MarketplaceService(db)
        return service.get_component_metadata(component_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== STATS & METRICS ======
@router.get("/stats", response_model=MarketplaceStats)
async def get_marketplace_stats(
    db: Session = Depends(get_db),
):
    """Get overall marketplace statistics"""
    try:
        service = MarketplaceService(db)
        return service.get_marketplace_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== CATEGORIES & TAGS ======
@router.get("/categories", response_model=Dict[str, int])
async def get_categories(
    db: Session = Depends(get_db),
):
    """Get component categories and counts"""
    try:
        service = MarketplaceService(db)
        return service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular-tags", response_model=List[str])
async def get_popular_tags(
    limit: int = Query(50, ge=1),
    db: Session = Depends(get_db),
):
    """Get most popular component tags"""
    try:
        service = MarketplaceService(db)
        return service.get_popular_tags(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== RECOMMENDATIONS & SIMILAR ======
@router.get("/recommendations", response_model=List[ComponentResponse])
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1),
):
    """Get component recommendations for user"""
    try:
        service = MarketplaceService(db)
        return service.get_recommendations(current_user.id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{component_id}", response_model=List[ComponentResponse])
async def get_similar(
    component_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=1),
):
    """Get components similar to given component"""
    try:
        service = MarketplaceService(db)
        return service.get_similar_components(component_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== MODERATION & BULK ======
@router.get("/moderation/pending", response_model=List[ComponentModerationResponse])
async def get_pending_moderation(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get components pending moderation"""
    try:
        service = MarketplaceService(db)
        return service.get_pending_moderation(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/moderation/{component_id}", response_model=ComponentModerationResponse)
async def moderate_component(
    component_id: str,
    action: ModerationAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Perform moderation action on component"""
    try:
        service = MarketplaceService(db)
        return service.moderate_component(component_id, action, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=BulkOperationResponse)
async def bulk_operations(
    operation: BulkComponentOperation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Perform bulk operations on components"""
    try:
        service = MarketplaceService(db)
        return service.bulk_component_operation(operation, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====== REPORTS ======
@router.get("/reports/revenue", response_model=Dict[str, Any])
async def get_revenue_report(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db),
):
    """Get revenue report for period"""
    try:
        service = MarketplaceService(db)
        return service.get_revenue_report(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/downloads", response_model=Dict[str, Any])
async def get_downloads_report(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db),
):
    """Get downloads report for period"""
    try:
        service = MarketplaceService(db)
        return service.get_downloads_report(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/top", response_model=Dict[str, Any])
async def get_top_components_report(
    metric: str = Query("downloads"),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    """Get top components based on metric"""
    try:
        service = MarketplaceService(db)
        return service.get_top_components_report(metric, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Serviço de Marketplace
Criado por José - O melhor Full Stack do mundo
Lógica de negócio para marketplace de componentes
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import uuid
import hashlib
import json

from src.synapse.models.marketplace import (
    MarketplaceComponent, ComponentRating, ComponentDownload, 
    ComponentPurchase, ComponentVersion
)
from src.synapse.models.user import User
from src.synapse.schemas.marketplace import (
    ComponentCreate, ComponentUpdate, ComponentSearch,
    RatingCreate, PurchaseCreate
)

class MarketplaceService:
    """
    Serviço para gerenciar marketplace de componentes
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== COMPONENTES ====================
    
    def create_component(self, component_data: ComponentCreate, author_id: int) -> MarketplaceComponent:
        """Cria um novo componente no marketplace"""
        
        # Gerar slug único
        base_slug = self._generate_slug(component_data.name)
        slug = self._ensure_unique_slug(base_slug)
        
        # Criar componente
        component = MarketplaceComponent(
            name=component_data.name,
            slug=slug,
            version=component_data.version or "1.0.0",
            title=component_data.title,
            description=component_data.description,
            short_description=component_data.short_description,
            category=component_data.category,
            subcategory=component_data.subcategory,
            tags=component_data.tags or [],
            author_id=author_id,
            author_name=self._get_user_name(author_id),
            organization=component_data.organization,
            component_type=component_data.component_type,
            component_data=component_data.component_data,
            configuration_schema=component_data.configuration_schema,
            dependencies=component_data.dependencies or [],
            compatibility=component_data.compatibility or {},
            documentation=component_data.documentation,
            readme=component_data.readme,
            changelog=component_data.changelog,
            examples=component_data.examples or [],
            icon_url=component_data.icon_url,
            screenshots=component_data.screenshots or [],
            demo_url=component_data.demo_url,
            video_url=component_data.video_url,
            is_free=component_data.is_free,
            price=component_data.price or 0.0,
            currency=component_data.currency or "USD",
            license_type=component_data.license_type or "MIT",
            keywords=component_data.keywords or [],
            status="pending"  # Requer aprovação
        )
        
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        
        # Criar primeira versão
        self._create_component_version(component.id, component_data)
        
        return component
    
    def update_component(self, component_id: int, component_data: ComponentUpdate, user_id: int) -> Optional[MarketplaceComponent]:
        """Atualiza um componente existente"""
        
        component = self.db.query(MarketplaceComponent).filter(
            and_(
                MarketplaceComponent.id == component_id,
                MarketplaceComponent.author_id == user_id
            )
        ).first()
        
        if not component:
            return None
        
        # Atualizar campos
        update_data = component_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(component, field):
                setattr(component, field, value)
        
        component.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(component)
        
        return component
    
    def get_component(self, component_id: int) -> Optional[MarketplaceComponent]:
        """Obtém um componente por ID"""
        return self.db.query(MarketplaceComponent).filter(
            MarketplaceComponent.id == component_id
        ).first()
    
    def get_component_by_slug(self, slug: str) -> Optional[MarketplaceComponent]:
        """Obtém um componente por slug"""
        return self.db.query(MarketplaceComponent).filter(
            MarketplaceComponent.slug == slug
        ).first()
    
    def search_components(self, search_params: ComponentSearch) -> Dict[str, Any]:
        """Busca componentes com filtros avançados"""
        
        query = self.db.query(MarketplaceComponent).filter(
            MarketplaceComponent.status == "approved"
        )
        
        # Filtro de texto
        if search_params.query:
            query = query.filter(
                or_(
                    MarketplaceComponent.name.ilike(f"%{search_params.query}%"),
                    MarketplaceComponent.title.ilike(f"%{search_params.query}%"),
                    MarketplaceComponent.description.ilike(f"%{search_params.query}%"),
                    MarketplaceComponent.tags.contains([search_params.query])
                )
            )
        
        # Filtros específicos
        if search_params.category:
            query = query.filter(MarketplaceComponent.category == search_params.category)
        
        if search_params.component_type:
            query = query.filter(MarketplaceComponent.component_type == search_params.component_type)
        
        if search_params.is_free is not None:
            query = query.filter(MarketplaceComponent.is_free == search_params.is_free)
        
        if search_params.min_rating:
            query = query.filter(MarketplaceComponent.rating_average >= search_params.min_rating)
        
        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(MarketplaceComponent.tags.contains([tag]))
        
        # Ordenação
        if search_params.sort_by == "popularity":
            query = query.order_by(desc(MarketplaceComponent.popularity_score))
        elif search_params.sort_by == "rating":
            query = query.order_by(desc(MarketplaceComponent.rating_average))
        elif search_params.sort_by == "downloads":
            query = query.order_by(desc(MarketplaceComponent.download_count))
        elif search_params.sort_by == "newest":
            query = query.order_by(desc(MarketplaceComponent.created_at))
        elif search_params.sort_by == "price_low":
            query = query.order_by(asc(MarketplaceComponent.price))
        elif search_params.sort_by == "price_high":
            query = query.order_by(desc(MarketplaceComponent.price))
        else:
            query = query.order_by(desc(MarketplaceComponent.popularity_score))
        
        # Paginação
        total = query.count()
        components = query.offset(search_params.offset).limit(search_params.limit).all()
        
        return {
            "components": components,
            "total": total,
            "page": search_params.offset // search_params.limit + 1,
            "pages": (total + search_params.limit - 1) // search_params.limit,
            "has_next": search_params.offset + search_params.limit < total,
            "has_prev": search_params.offset > 0
        }
    
    def get_featured_components(self, limit: int = 10) -> List[MarketplaceComponent]:
        """Obtém componentes em destaque"""
        return self.db.query(MarketplaceComponent).filter(
            and_(
                MarketplaceComponent.status == "approved",
                MarketplaceComponent.is_featured == True
            )
        ).order_by(desc(MarketplaceComponent.popularity_score)).limit(limit).all()
    
    def get_trending_components(self, days: int = 7, limit: int = 10) -> List[MarketplaceComponent]:
        """Obtém componentes em alta"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Componentes com mais downloads recentes
        trending_ids = self.db.query(
            ComponentDownload.component_id,
            func.count(ComponentDownload.id).label('recent_downloads')
        ).filter(
            ComponentDownload.created_at >= since_date
        ).group_by(ComponentDownload.component_id).order_by(
            desc('recent_downloads')
        ).limit(limit).all()
        
        component_ids = [item[0] for item in trending_ids]
        
        return self.db.query(MarketplaceComponent).filter(
            and_(
                MarketplaceComponent.id.in_(component_ids),
                MarketplaceComponent.status == "approved"
            )
        ).all()
    
    # ==================== DOWNLOADS ====================
    
    def download_component(self, component_id: int, user_id: int, download_type: str = "manual") -> ComponentDownload:
        """Registra download de um componente"""
        
        component = self.get_component(component_id)
        if not component:
            raise ValueError("Componente não encontrado")
        
        # Verificar se é premium e se usuário tem acesso
        if not component.is_free:
            purchase = self.db.query(ComponentPurchase).filter(
                and_(
                    ComponentPurchase.component_id == component_id,
                    ComponentPurchase.user_id == user_id,
                    ComponentPurchase.status == "completed"
                )
            ).first()
            
            if not purchase:
                raise ValueError("Componente premium requer compra")
        
        # Registrar download
        download = ComponentDownload(
            component_id=component_id,
            user_id=user_id,
            version=component.version,
            download_type=download_type,
            status="completed"
        )
        
        self.db.add(download)
        
        # Atualizar contador
        component.download_count += 1
        component.last_download_at = datetime.utcnow()
        component.update_statistics()
        
        self.db.commit()
        self.db.refresh(download)
        
        return download
    
    def get_user_downloads(self, user_id: int, limit: int = 50) -> List[ComponentDownload]:
        """Obtém downloads do usuário"""
        return self.db.query(ComponentDownload).filter(
            ComponentDownload.user_id == user_id
        ).order_by(desc(ComponentDownload.created_at)).limit(limit).all()
    
    # ==================== AVALIAÇÕES ====================
    
    def create_rating(self, rating_data: RatingCreate, user_id: int) -> ComponentRating:
        """Cria uma avaliação para um componente"""
        
        # Verificar se usuário já avaliou
        existing_rating = self.db.query(ComponentRating).filter(
            and_(
                ComponentRating.component_id == rating_data.component_id,
                ComponentRating.user_id == user_id
            )
        ).first()
        
        if existing_rating:
            raise ValueError("Usuário já avaliou este componente")
        
        # Verificar se usuário baixou o componente
        download = self.db.query(ComponentDownload).filter(
            and_(
                ComponentDownload.component_id == rating_data.component_id,
                ComponentDownload.user_id == user_id
            )
        ).first()
        
        rating = ComponentRating(
            component_id=rating_data.component_id,
            user_id=user_id,
            rating=rating_data.rating,
            title=rating_data.title,
            review=rating_data.review,
            ease_of_use=rating_data.ease_of_use,
            documentation_quality=rating_data.documentation_quality,
            performance=rating_data.performance,
            reliability=rating_data.reliability,
            support_quality=rating_data.support_quality,
            version_used=rating_data.version_used,
            use_case=rating_data.use_case,
            experience_level=rating_data.experience_level,
            is_verified_purchase=download is not None
        )
        
        self.db.add(rating)
        
        # Atualizar estatísticas do componente
        component = self.get_component(rating_data.component_id)
        if component:
            component.update_statistics()
        
        self.db.commit()
        self.db.refresh(rating)
        
        return rating
    
    def get_component_ratings(self, component_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Obtém avaliações de um componente"""
        
        query = self.db.query(ComponentRating).filter(
            and_(
                ComponentRating.component_id == component_id,
                ComponentRating.status == "active"
            )
        ).order_by(desc(ComponentRating.created_at))
        
        total = query.count()
        ratings = query.offset(offset).limit(limit).all()
        
        return {
            "ratings": ratings,
            "total": total,
            "average_rating": self._calculate_average_rating(component_id),
            "rating_distribution": self._get_rating_distribution(component_id)
        }
    
    # ==================== COMPRAS ====================
    
    def create_purchase(self, purchase_data: PurchaseCreate, user_id: int) -> ComponentPurchase:
        """Cria uma compra de componente premium"""
        
        component = self.get_component(purchase_data.component_id)
        if not component:
            raise ValueError("Componente não encontrado")
        
        if component.is_free:
            raise ValueError("Componente é gratuito")
        
        # Verificar se usuário já comprou
        existing_purchase = self.db.query(ComponentPurchase).filter(
            and_(
                ComponentPurchase.component_id == purchase_data.component_id,
                ComponentPurchase.user_id == user_id,
                ComponentPurchase.status == "completed"
            )
        ).first()
        
        if existing_purchase:
            raise ValueError("Usuário já possui este componente")
        
        purchase = ComponentPurchase(
            component_id=purchase_data.component_id,
            user_id=user_id,
            amount=component.price,
            currency=component.currency,
            payment_method=purchase_data.payment_method,
            transaction_id=str(uuid.uuid4()),
            payment_provider=purchase_data.payment_provider,
            status="pending",
            license_key=self._generate_license_key()
        )
        
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    def complete_purchase(self, transaction_id: str, provider_transaction_id: str) -> Optional[ComponentPurchase]:
        """Completa uma compra"""
        
        purchase = self.db.query(ComponentPurchase).filter(
            ComponentPurchase.transaction_id == transaction_id
        ).first()
        
        if not purchase:
            return None
        
        purchase.status = "completed"
        purchase.provider_transaction_id = provider_transaction_id
        purchase.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _generate_slug(self, name: str) -> str:
        """Gera slug a partir do nome"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        slug = re.sub(r'\s+', '-', slug)
        return slug.strip('-')
    
    def _ensure_unique_slug(self, base_slug: str) -> str:
        """Garante que o slug seja único"""
        slug = base_slug
        counter = 1
        
        while self.db.query(MarketplaceComponent).filter(
            MarketplaceComponent.slug == slug
        ).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _get_user_name(self, user_id: int) -> str:
        """Obtém nome do usuário"""
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.full_name if user else "Unknown"
    
    def _create_component_version(self, component_id: int, component_data: ComponentCreate) -> ComponentVersion:
        """Cria primeira versão do componente"""
        
        version = ComponentVersion(
            component_id=component_id,
            version=component_data.version or "1.0.0",
            is_latest=True,
            is_stable=True,
            component_data=component_data.component_data,
            dependencies=component_data.dependencies or [],
            file_hash=self._calculate_hash(component_data.component_data)
        )
        
        self.db.add(version)
        self.db.commit()
        
        return version
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calcula hash SHA-256 dos dados"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _calculate_average_rating(self, component_id: int) -> float:
        """Calcula rating médio de um componente"""
        result = self.db.query(func.avg(ComponentRating.rating)).filter(
            and_(
                ComponentRating.component_id == component_id,
                ComponentRating.status == "active"
            )
        ).scalar()
        
        return float(result) if result else 0.0
    
    def _get_rating_distribution(self, component_id: int) -> Dict[int, int]:
        """Obtém distribuição de ratings"""
        distribution = {}
        
        for rating in range(1, 6):
            count = self.db.query(ComponentRating).filter(
                and_(
                    ComponentRating.component_id == component_id,
                    ComponentRating.rating == rating,
                    ComponentRating.status == "active"
                )
            ).count()
            distribution[rating] = count
        
        return distribution
    
    def _generate_license_key(self) -> str:
        """Gera chave de licença única"""
        return str(uuid.uuid4()).replace('-', '').upper()
    
    # ==================== ANALYTICS ====================
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do marketplace"""
        
        total_components = self.db.query(MarketplaceComponent).filter(
            MarketplaceComponent.status == "approved"
        ).count()
        
        total_downloads = self.db.query(func.sum(MarketplaceComponent.download_count)).scalar() or 0
        
        total_revenue = self.db.query(func.sum(ComponentPurchase.amount)).filter(
            ComponentPurchase.status == "completed"
        ).scalar() or 0.0
        
        avg_rating = self.db.query(func.avg(MarketplaceComponent.rating_average)).filter(
            MarketplaceComponent.rating_count > 0
        ).scalar() or 0.0
        
        return {
            "total_components": total_components,
            "total_downloads": int(total_downloads),
            "total_revenue": float(total_revenue),
            "average_rating": round(float(avg_rating), 2),
            "active_developers": self._get_active_developers_count(),
            "categories": self._get_category_stats()
        }
    
    def _get_active_developers_count(self) -> int:
        """Conta desenvolvedores ativos"""
        return self.db.query(MarketplaceComponent.author_id).filter(
            MarketplaceComponent.status == "approved"
        ).distinct().count()
    
    def _get_category_stats(self) -> Dict[str, int]:
        """Obtém estatísticas por categoria"""
        results = self.db.query(
            MarketplaceComponent.category,
            func.count(MarketplaceComponent.id).label('count')
        ).filter(
            MarketplaceComponent.status == "approved"
        ).group_by(MarketplaceComponent.category).all()
        
        return {category: count for category, count in results}


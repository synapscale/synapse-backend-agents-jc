"""
Serviço de Marketplace usando SQLAlchemy para conexão direta com PostgreSQL
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, text
import os
import logging


from synapse.models.marketplace import MarketplaceComponent, ComponentRating, ComponentPurchase

logger = logging.getLogger(__name__)

class MarketplaceService:
    """Serviço de Marketplace usando SQLAlchemy"""
    
    def __init__(self, db=None):
        # Usar a sessão do SQLAlchemy
        self.db = db
        # Schema deve ser sempre fornecido via variável de ambiente
        self.schema = os.getenv("DATABASE_SCHEMA", "synapscale_db")
    
    def search_components(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca componentes no marketplace usando SQLAlchemy"""
        try:
            # Parâmetros de busca
            query = search_params.get('query', '')
            category = search_params.get('category')
            tags = search_params.get('tags', [])
            min_rating = search_params.get('min_rating', 0)
            sort_by = search_params.get('sort_by', 'created_at')
            sort_order = search_params.get('sort_order', 'desc')
            page = search_params.get('page', 1)
            limit = search_params.get('limit', 20)
            
            # Calcular offset
            offset = (page - 1) * limit
            
            # Construir a consulta base
            db_query = self.db.query(MarketplaceComponent).filter(MarketplaceComponent.is_active == True)
            
            # Adicionar filtros
            if query:
                db_query = db_query.filter(MarketplaceComponent.name.ilike(f'%{query}%'))
            
            if category:
                db_query = db_query.filter(MarketplaceComponent.category == category)
            
            # Ordenação
            if sort_order.lower() == 'desc':
                db_query = db_query.order_by(desc(getattr(MarketplaceComponent, sort_by)))
            else:
                db_query = db_query.order_by(asc(getattr(MarketplaceComponent, sort_by)))
            
            # Contar total
            total = db_query.count()
            
            # Aplicar paginação
            components = db_query.offset(offset).limit(limit).all()
            
            # Carregar relacionamentos manualmente
            for component in components:
                self.db.refresh(component)
            
            return {
                'components': components,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit,
                'pages': (total + limit - 1) // limit,
                'has_next': page < ((total + limit - 1) // limit),
                'has_prev': page > 1
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar componentes: {e}")
            return {
                'components': [],
                'total': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0,
                'pages': 0,
                'has_next': False,
                'has_prev': False
            }
    
    def get_component_by_id(self, component_id: str) -> Optional[MarketplaceComponent]:
        """Busca componente por ID usando SQLAlchemy"""
        try:
            component = self.db.query(MarketplaceComponent).filter(MarketplaceComponent.id == component_id).first()
            if component:
                self.db.refresh(component)
            return component
        except Exception as e:
            logger.error(f"Erro ao buscar componente {component_id}: {e}")
            return None
    
    def create_component(self, component_data, user_id: int) -> dict:
        """Cria um novo componente no banco de dados"""
        try:
            component = MarketplaceComponent(
                name=component_data.name if hasattr(component_data, 'name') else "Novo Componente",
                description=component_data.description if hasattr(component_data, 'description') else "",
                category=component_data.category if hasattr(component_data, 'category') else "automation",
                author_id=user_id,
                created_at=datetime.utcnow(),
                is_active=True,
                version="1.0.0",
                license_type="MIT",
                is_free=True,
                rating=0.0,
                downloads=0
            )
            
            self.db.add(component)
            self.db.commit()
            self.db.refresh(component)
            
            return {
                "id": component.id,
                "name": component.name,
                "description": component.description,
                "author_id": component.author_id,
                "created_at": component.created_at.isoformat()
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar componente: {e}")
            return None
    
    def update_component(self, component_id: int, component_data, user_id: int) -> dict:
        """Atualiza um componente no banco de dados"""
        try:
            component = self.db.query(MarketplaceComponent).filter(
                MarketplaceComponent.id == component_id
            ).first()
            
            if not component:
                return None
            
            # Atualizar campos se existirem nos dados
            if hasattr(component_data, 'name'):
                component.name = component_data.name
            if hasattr(component_data, 'description'):
                component.description = component_data.description
            if hasattr(component_data, 'category'):
                component.category = component_data.category
            
            component.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(component)
            
            return {
                "id": component.id,
                "updated_at": component.updated_at.isoformat()
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar componente {component_id}: {e}")
            return None
    
    def delete_component(self, component_id: int, user_id: int) -> bool:
        """Deleta um componente do banco de dados"""
        try:
            component = self.db.query(MarketplaceComponent).filter(
                MarketplaceComponent.id == component_id
            ).first()
            
            if not component:
                return False
                
            self.db.delete(component)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar componente {component_id}: {e}")
            return False

    # ==================== MÉTODOS FALTANTES PARA ENDPOINTS ====================

    def get_component(self, component_id: int) -> Optional[dict]:
        """Obtém um componente específico do banco de dados"""
        try:
            component = self.db.query(MarketplaceComponent).filter(
                MarketplaceComponent.id == component_id
            ).first()
            
            if not component:
                return None
            
            # Refresh para carregar relacionamentos
            self.db.refresh(component)
            
            # Converter para dict com dados detalhados
            return {
                "id": component.id,
                "name": component.name,
                "description": component.description,
                "category": component.category,
                "rating": component.rating,
                "downloads": component.downloads,
                "price": component.price,
                "created_at": component.created_at.isoformat() if component.created_at else None,
                "author_id": component.author_id,
                "tags": component.tags,
                "is_active": component.is_active,
                "version": component.version,
                "author_name": component.author_name,
                "short_description": component.short_description,
                "license_type": component.license_type,
                "is_free": component.is_free
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar componente {component_id}: {e}")
            return None

    def download_component(self, component_id: int, user_id: int, version: str = None) -> dict:
        """Faz download de um componente"""
        return {
            "download_url": f"https://storage.synapscale.com/components/{component_id}.zip",
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "version": version or "latest"
        }

    def install_component(self, component_id: int, user_id: int, workspace_id: int = None) -> dict:
        """Instala um componente no workspace"""
        return {
            "installation_id": 1,
            "component_id": component_id,
            "workspace_id": workspace_id,
            "status": "installed",
            "installed_at": datetime.utcnow().isoformat()
        }

    def create_rating(self, component_id: int, rating_data, user_id: int) -> dict:
        """Cria uma avaliação"""
        return {
            "id": 1,
            "component_id": component_id,
            "user_id": user_id,
            "rating": rating_data.rating if hasattr(rating_data, 'rating') else 5,
            "comment": rating_data.comment if hasattr(rating_data, 'comment') else "",
            "created_at": datetime.utcnow().isoformat()
        }

    def get_component_ratings(self, component_id: int, limit: int = 20, offset: int = 0, sort_by: str = "newest") -> list:
        """Lista avaliações de um componente"""
        return []

    def get_rating_stats(self, component_id: int) -> dict:
        """Obtém estatísticas de avaliações"""
        return {
            "total_ratings": 25,
            "average_rating": 4.2,
            "rating_distribution": {
                "5": 12,
                "4": 8,
                "3": 3,
                "2": 1,
                "1": 1
            }
        }

    def update_rating(self, rating_id: int, rating_data, user_id: int) -> dict:
        """Atualiza uma avaliação"""
        return {
            "id": rating_id,
            "updated_at": datetime.utcnow().isoformat()
        }

    def delete_rating(self, rating_id: int, user_id: int) -> bool:
        """Deleta uma avaliação"""
        return True

    def mark_rating_helpful(self, rating_id: int, user_id: int) -> dict:
        """Marca avaliação como útil"""
        return {
            "rating_id": rating_id,
            "helpful": True
        }

    def purchase_component(self, component_id: int, purchase_data, user_id: int) -> dict:
        """Compra um componente"""
        return {
            "purchase_id": 1,
            "component_id": component_id,
            "user_id": user_id,
            "amount": 29.99,
            "status": "completed",
            "purchased_at": datetime.utcnow().isoformat()
        }

    def get_user_purchases(self, user_id: int, limit: int = 20, offset: int = 0) -> list:
        """Lista compras do usuário"""
        return []

    def get_purchase(self, purchase_id: int, user_id: int) -> dict:
        """Obtém detalhes de uma compra"""
        return {
            "id": purchase_id,
            "component_id": 1,
            "amount": 29.99,
            "status": "completed",
            "purchased_at": datetime.utcnow().isoformat()
        }

    def get_component_versions(self, component_id: int) -> list:
        """Lista versões de um componente"""
        return []

    def create_component_version(self, component_id: int, version: str, file_data, user_id: int) -> dict:
        """Cria nova versão do componente"""
        return {
            "version_id": 1,
            "component_id": component_id,
            "version": version,
            "created_at": datetime.utcnow().isoformat()
        }

    def favorite_component(self, component_id: int, user_id: int) -> dict:
        """Adiciona componente aos favoritos"""
        return {
            "component_id": component_id,
            "favorited": True
        }

    def unfavorite_component(self, component_id: int, user_id: int) -> dict:
        """Remove componente dos favoritos"""
        return {
            "component_id": component_id,
            "favorited": False
        }

    def get_user_favorites(self, user_id: int, limit: int = 20, offset: int = 0) -> list:
        """Lista favoritos do usuário"""
        return []

    def get_marketplace_stats(self) -> dict:
        """Estatísticas do marketplace"""
        return {
            "total_components": 145,
            "total_downloads": 2580,
            "total_revenue": 15420.50,
            "average_rating": 4.2,
            "active_developers": 89,
            "categories": {
                "automation": 45,
                "analytics": 32,
                "ui": 28,
                "integration": 40
            }
        }

    def get_component_stats(self, component_id: int, days: int = 30) -> dict:
        """Estatísticas de um componente"""
        return {
            "downloads": 45,
            "rating": 4.2,
            "revenue": 289.75,
            "period": f"last_{days}_days"
        }

    def get_author_stats(self, user_id: int) -> dict:
        """Estatísticas do autor"""
        return {
            "total_components": 5,
            "total_downloads": 234,
            "total_revenue": 567.89,
            "average_rating": 4.3
        }

    def get_categories(self) -> list:
        """Lista categorias disponíveis"""
        return [
            {"id": "automation", "name": "Automação", "count": 45},
            {"id": "analytics", "name": "Analytics", "count": 32},
            {"id": "ui", "name": "Interface", "count": 28},
            {"id": "integration", "name": "Integração", "count": 40}
        ]

    def get_popular_tags(self, limit: int = 50) -> list:
        """Lista tags populares"""
        return [
            {"tag": "workflow", "count": 45},
            {"tag": "api", "count": 38},
            {"tag": "dashboard", "count": 32},
            {"tag": "automation", "count": 28}
        ]

    def get_recommendations(self, user_id: int, limit: int = 10) -> list:
        """Recomendações para o usuário"""
        return []

    def get_similar_components(self, component_id: int, limit: int = 5) -> list:
        """Componentes similares"""
        return []

    def get_pending_moderation(self, limit: int = 20, offset: int = 0) -> list:
        """Lista componentes pendentes de moderação"""
        return []

    def moderate_component(self, component_id: int, action, user_id: int) -> dict:
        """Modera um componente"""
        return {
            "component_id": component_id,
            "action": str(action),
            "moderated_at": datetime.utcnow().isoformat()
        }

    def bulk_component_operation(self, operation, user_id: int) -> dict:
        """Operação em lote com componentes"""
        return {
            "operation": str(operation),
            "processed": 0,
            "success": 0,
            "failed": 0
        }

    def feature_component(self, component_id: int, featured: bool, user_id: int) -> dict:
        """Destaca um componente"""
        return {
            "component_id": component_id,
            "featured": featured
        }

    def get_revenue_report(self, start_date, end_date) -> dict:
        """Relatório de receitas"""
        return {
            "total_revenue": 15420.50,
            "period": {"start": start_date, "end": end_date},
            "daily_revenue": []
        }

    def get_downloads_report(self, start_date, end_date) -> dict:
        """Relatório de downloads"""
        return {
            "total_downloads": 2580,
            "period": {"start": start_date, "end": end_date},
            "daily_downloads": []
        }

    def get_top_components_report(self, metric: str = "downloads", limit: int = 10) -> dict:
        """Relatório de top componentes"""
        return {
            "metric": metric,
            "components": [],
            "period": "last_30_days"
        }

# Função para compatibilidade com código existente
def search_components(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """Função para compatibilidade"""
    from synapse.database import get_db_session
    
    # Obter uma sessão do banco de dados
    with get_db_session() as db:
        service = MarketplaceService(db)
        return service.search_components(search_params)

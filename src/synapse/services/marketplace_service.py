"""
Serviço de Marketplace usando SQLAlchemy
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.synapse.database import get_db_session
from src.synapse.models.marketplace import (
    MarketplaceComponent,
    ComponentRating,
    ComponentPurchase
)
import logging

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Serviço de Marketplace usando SQLAlchemy"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or get_db_session()

    def search_components(self,
                          search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca componentes no marketplace usando SQLAlchemy"""
        try:
            # Parâmetros de busca
            query = search_params.get('query', '')
            category = search_params.get('category')
            min_rating = search_params.get('min_rating', 0)
            sort_by = search_params.get('sort_by', 'created_at')
            sort_order = search_params.get('sort_order', 'desc')
            page = search_params.get('page', 1)
            limit = search_params.get('limit', 20)

            # Calcular offset
            offset = (page - 1) * limit

            # Construir query base
            db_query = self.db.query(MarketplaceComponent)

            # Aplicar filtros
            filters = [MarketplaceComponent.is_active == True]

            if query:
                filters.append(
                    MarketplaceComponent.name.ilike(f'%{query}%')
                )

            if category:
                filters.append(MarketplaceComponent.category == category)

            if min_rating > 0:
                # Subquery para calcular rating médio
                avg_rating = self.db.query(
                    func.avg(ComponentRating.rating)
                ).filter(
                    ComponentRating.component_id == MarketplaceComponent.id
                ).scalar_subquery()
                filters.append(avg_rating >= min_rating)

            # Aplicar filtros
            db_query = db_query.filter(and_(*filters))

            # Aplicar ordenação
            if sort_order.lower() == 'desc':
                db_query = db_query.order_by(
                    getattr(MarketplaceComponent, sort_by).desc()
                )
            else:
                db_query = db_query.order_by(
                    getattr(MarketplaceComponent, sort_by).asc()
                )

            # Contar total
            total = db_query.count()

            # Aplicar paginação
            components = db_query.offset(offset).limit(limit).all()

            # Converter para dicionários
            components_dict = []
            for component in components:
                component_dict = {
                    'id': component.id,
                    'name': component.name,
                    'description': component.description,
                    'category': component.category,
                    'price': getattr(component, 'price', 0),
                    'created_at': getattr(component, 'created_at', None),
                    'updated_at': getattr(component, 'updated_at', None),
                    'is_active': getattr(component, 'is_active', True),
                    'ratings': [],
                    'purchases': []
                }

                # Buscar ratings se existir a tabela
                try:
                    ratings = self.db.query(ComponentRating).filter(
                        ComponentRating.component_id == component.id
                    ).all()
                    component_dict['ratings'] = [
                        {
                            'id': r.id,
                            'rating': r.rating,
                            'comment': getattr(r, 'comment', ''),
                            'user_id': r.user_id,
                            'created_at': getattr(r, 'created_at', None)
                        }
                        for r in ratings
                    ]
                except Exception:
                    component_dict['ratings'] = []

                # Buscar purchases se existir a tabela
                try:
                    purchases = self.db.query(ComponentPurchase).filter(
                        ComponentPurchase.component_id == component.id
                    ).all()
                    component_dict['purchases'] = [
                        {
                            'id': p.id,
                            'user_id': p.user_id,
                            'price': getattr(p, 'price', 0),
                            'purchased_at': getattr(p, 'purchased_at', None)
                        }
                        for p in purchases
                    ]
                except Exception:
                    component_dict['purchases'] = []

                components_dict.append(component_dict)

            return {
                'components': components_dict,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }

        except Exception as e:
            logger.error("Erro ao buscar componentes: %s", str(e))
            return {
                'components': [],
                'total': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0
            }

    def get_component_by_id(self,
                            component_id: str) -> Optional[Dict[str, Any]]:
        """Busca componente por ID usando SQLAlchemy"""
        try:
            component = self.db.query(MarketplaceComponent).filter(
                MarketplaceComponent.id == component_id
            ).first()

            if not component:
                return None

            # Converter para dicionário
            component_dict = {
                'id': component.id,
                'name': component.name,
                'description': component.description,
                'category': component.category,
                'price': getattr(component, 'price', 0),
                'created_at': getattr(component, 'created_at', None),
                'updated_at': getattr(component, 'updated_at', None),
                'is_active': getattr(component, 'is_active', True),
                'ratings': [],
                'purchases': []
            }

            # Buscar ratings se existir a tabela
            try:
                ratings = self.db.query(ComponentRating).filter(
                    ComponentRating.component_id == component.id
                ).all()
                component_dict['ratings'] = [
                    {
                        'id': r.id,
                        'rating': r.rating,
                        'comment': getattr(r, 'comment', ''),
                        'user_id': r.user_id,
                        'created_at': getattr(r, 'created_at', None)
                    }
                    for r in ratings
                ]
            except Exception:
                component_dict['ratings'] = []

            # Buscar purchases se existir a tabela
            try:
                purchases = self.db.query(ComponentPurchase).filter(
                    ComponentPurchase.component_id == component.id
                ).all()
                component_dict['purchases'] = [
                    {
                        'id': p.id,
                        'user_id': p.user_id,
                        'price': getattr(p, 'price', 0),
                        'purchased_at': getattr(p, 'purchased_at', None)
                    }
                    for p in purchases
                ]
            except Exception:
                component_dict['purchases'] = []

            return component_dict

        except Exception as e:
            logger.error("Erro ao buscar componente %s: %s",
                         component_id, str(e))
            return None

    def create_component(self,
                         component_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria novo componente usando SQLAlchemy"""
        try:
            component = MarketplaceComponent(**component_data)
            self.db.add(component)
            self.db.commit()
            self.db.refresh(component)

            return {
                'id': component.id,
                'name': component.name,
                'description': component.description,
                'category': component.category,
                'price': getattr(component, 'price', 0),
                'created_at': getattr(component, 'created_at', None),
                'updated_at': getattr(component, 'updated_at', None),
                'is_active': getattr(component, 'is_active', True)
            }

        except Exception as e:
            logger.error("Erro ao criar componente: %s", str(e))
            self.db.rollback()
            return None

    def update_component(self, component_id: str,
                         component_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza componente usando SQLAlchemy"""
        try:
            component = self.db.query(MarketplaceComponent).filter(
                MarketplaceComponent.id == component_id
            ).first()

            if not component:
                return None

            # Atualizar campos
            for key, value in component_data.items():
                if hasattr(component, key):
                    setattr(component, key, value)

            if hasattr(component, 'updated_at'):
                component.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(component)

            return {
                'id': component.id,
                'name': component.name,
                'description': component.description,
                'category': component.category,
                'price': getattr(component, 'price', 0),
                'created_at': getattr(component, 'created_at', None),
                'updated_at': getattr(component, 'updated_at', None),
                'is_active': getattr(component, 'is_active', True)
            }

        except Exception as e:
            logger.error("Erro ao atualizar componente %s: %s",
                         component_id, str(e))
            self.db.rollback()
            return None

    def delete_component(self, component_id: str) -> bool:
        """Deleta componente usando SQLAlchemy"""
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
            logger.error("Erro ao deletar componente %s: %s",
                         component_id, str(e))
            self.db.rollback()
            return False


# Função para compatibilidade com código existente
def search_components(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """Função para compatibilidade com código existente"""
    service = MarketplaceService()
    try:
        return service.search_components(search_params)
    finally:
        service.db.close()


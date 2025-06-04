"""
Correção do marketplace_service.py para usar Prisma
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from prisma import Prisma
from src.synapse.database import prisma
from src.synapse.models.marketplace import MarketplaceComponent, ComponentRating, ComponentPurchase
import logging

logger = logging.getLogger(__name__)

class MarketplaceService:
    """Serviço de Marketplace corrigido para usar Prisma"""
    
    def __init__(self):
        self.db = prisma
    
    async def search_components(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca componentes no marketplace usando Prisma"""
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
            
            # Buscar componentes usando Prisma
            components = await self.db.marketplacecomponent.find_many(
                where={
                    'AND': [
                        {'name': {'contains': query, 'mode': 'insensitive'}} if query else {},
                        {'category': category} if category else {},
                        {'is_active': True}
                    ]
                },
                include={
                    'ratings': True,
                    'purchases': True
                },
                skip=offset,
                take=limit,
                order={sort_by: sort_order}
            )
            
            # Contar total
            total = await self.db.marketplacecomponent.count(
                where={
                    'AND': [
                        {'name': {'contains': query, 'mode': 'insensitive'}} if query else {},
                        {'category': category} if category else {},
                        {'is_active': True}
                    ]
                }
            )
            
            return {
                'components': components,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar componentes: {e}")
            return {
                'components': [],
                'total': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0
            }
    
    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Busca componente por ID usando Prisma"""
        try:
            component = await self.db.marketplacecomponent.find_unique(
                where={'id': component_id},
                include={
                    'ratings': True,
                    'purchases': True
                }
            )
            return component
        except Exception as e:
            logger.error(f"Erro ao buscar componente {component_id}: {e}")
            return None
    
    async def create_component(self, component_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria novo componente usando Prisma"""
        try:
            component = await self.db.marketplacecomponent.create(
                data=component_data
            )
            return component
        except Exception as e:
            logger.error(f"Erro ao criar componente: {e}")
            return None
    
    async def update_component(self, component_id: str, component_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza componente usando Prisma"""
        try:
            component = await self.db.marketplacecomponent.update(
                where={'id': component_id},
                data=component_data
            )
            return component
        except Exception as e:
            logger.error(f"Erro ao atualizar componente {component_id}: {e}")
            return None
    
    async def delete_component(self, component_id: str) -> bool:
        """Deleta componente usando Prisma"""
        try:
            await self.db.marketplacecomponent.delete(
                where={'id': component_id}
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar componente {component_id}: {e}")
            return False

# Função para compatibilidade com código existente
def search_components(search_params: Dict[str, Any]) -> Dict[str, Any]:
    """Função síncrona para compatibilidade"""
    service = MarketplaceService()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(service.search_components(search_params))


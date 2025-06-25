from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta, timezone
import logging

from memory_bank.models.collection import MemoryCollection
from memory_bank.schemas.collection import CollectionCreate, CollectionUpdate, CollectionStats

logger = logging.getLogger(__name__)

class CollectionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_collection(self, user_id: str, collection_data: CollectionCreate) -> MemoryCollection:
        """Cria uma nova coleção de memórias"""
        try:
            # Verificar workspace se especificado
            if collection_data.workspace_id:
                from synapse.models.workspace import Workspace
                from synapse.models.workspace_member import WorkspaceMember
                
                # Verificar se o usuário é membro do workspace
                is_member = self.db.query(WorkspaceMember).filter(
                    and_(
                        WorkspaceMember.workspace_id == collection_data.workspace_id,
                        WorkspaceMember.user_id == user_id,
                        WorkspaceMember.status == "active"
                    )
                ).first() is not None
                
                if not is_member:
                    raise ValueError("Usuário não é membro do workspace especificado")
            
            # Criar coleção
            collection = MemoryCollection(
                user_id=user_id,
                workspace_id=collection_data.workspace_id,
                name=collection_data.name,
                description=collection_data.description,
                is_private=collection_data.is_private,
                max_memories=collection_data.max_memories,
                retention_days=collection_data.retention_days
            )
            
            self.db.add(collection)
            self.db.commit()
            self.db.refresh(collection)
            
            logger.info(f"Coleção criada: {collection.name} (ID: {collection.id}) para usuário {user_id}")
            return collection
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar coleção: {str(e)}")
            raise
    
    async def get_collection(self, user_id: str, collection_id: str) -> Optional[MemoryCollection]:
        """Obtém uma coleção específica"""
        return self.db.query(MemoryCollection).filter(
            and_(
                MemoryCollection.id == collection_id,
                MemoryCollection.user_id == user_id
            )
        ).first()
    
    async def update_collection(self, user_id: str, collection_id: str, collection_data: CollectionUpdate) -> Optional[MemoryCollection]:
        """Atualiza uma coleção existente"""
        try:
            collection = self.db.query(MemoryCollection).filter(
                and_(
                    MemoryCollection.id == collection_id,
                    MemoryCollection.user_id == user_id
                )
            ).first()
            
            if not collection:
                return None
            
            # Atualizar campos
            update_data = collection_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(collection, field, value)
            
            collection.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(collection)
            
            return collection
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar coleção {collection_id}: {str(e)}")
            raise
    
    async def delete_collection(self, user_id: str, collection_id: str) -> bool:
        """Deleta uma coleção e todas as suas memórias"""
        try:
            collection = self.db.query(MemoryCollection).filter(
                and_(
                    MemoryCollection.id == collection_id,
                    MemoryCollection.user_id == user_id
                )
            ).first()
            
            if not collection:
                return False
            
            # Deletar coleção (as memórias serão deletadas em cascata)
            self.db.delete(collection)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar coleção {collection_id}: {str(e)}")
            return False
    
    async def get_user_collections(
        self, 
        user_id: str, 
        workspace_id: Optional[str] = None,
        include_shared: bool = True
    ) -> List[MemoryCollection]:
        """Lista coleções do usuário, opcionalmente filtrando por workspace"""
        
        # Construir query base para coleções do usuário
        query = self.db.query(MemoryCollection).filter(MemoryCollection.user_id == user_id)
        
        # Filtrar por workspace se especificado
        if workspace_id:
            query = query.filter(MemoryCollection.workspace_id == workspace_id)
        
        # Incluir coleções compartilhadas se solicitado
        if include_shared and workspace_id:
            from synapse.models.workspace_member import WorkspaceMember
            
            # Verificar se o usuário é membro do workspace
            is_member = self.db.query(WorkspaceMember).filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.status == "active"
                )
            ).first() is not None
            
            if is_member:
                # Incluir coleções compartilhadas do workspace
                shared_query = self.db.query(MemoryCollection).filter(
                    and_(
                        MemoryCollection.workspace_id == workspace_id,
                        MemoryCollection.user_id != user_id,
                        MemoryCollection.is_private == False
                    )
                )
                
                # União das queries
                query = query.union(shared_query)
        
        # Ordenar por data de atualização
        collections = query.order_by(MemoryCollection.updated_at.desc()).all()
        
        return collections
    
    async def get_collection_stats(self, user_id: str) -> CollectionStats:
        """Obtém estatísticas das coleções do usuário"""
        try:
            # Total de coleções
            total_collections = self.db.query(func.count(MemoryCollection.id)).filter(
                MemoryCollection.user_id == user_id
            ).scalar() or 0
            
            # Total de memórias e tokens
            stats = self.db.query(
                func.sum(MemoryCollection.memory_count).label("total_memories"),
                func.sum(MemoryCollection.total_tokens).label("total_tokens")
            ).filter(
                MemoryCollection.user_id == user_id
            ).first()
            
            total_memories = stats[0] or 0
            total_tokens = stats[1] or 0
            
            # Média de memórias por coleção
            avg_memories = total_memories / total_collections if total_collections > 0 else 0
            
            # Coleção mais usada
            most_used = self.db.query(MemoryCollection).filter(
                MemoryCollection.user_id == user_id
            ).order_by(
                MemoryCollection.memory_count.desc()
            ).first()
            
            most_used_name = most_used.name if most_used else None
            
            return CollectionStats(
                total_collections=total_collections,
                total_memories=total_memories,
                total_tokens=total_tokens,
                avg_memories_per_collection=avg_memories,
                most_used_collection=most_used_name
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return CollectionStats(
                total_collections=0,
                total_memories=0,
                total_tokens=0,
                avg_memories_per_collection=0
            )

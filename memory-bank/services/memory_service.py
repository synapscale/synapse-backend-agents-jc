from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta, timezone
import json
import logging

from memory_bank.models.memory import Memory
from memory_bank.schemas.memory import MemoryCreate, MemoryUpdate, MemorySearch
from memory_bank.utils.embedding import get_embedding
from memory_bank.utils.vector_store import search_similar_vectors

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_memory(self, user_id: str, memory_data: MemoryCreate) -> Memory:
        """Cria uma nova memória com embedding automático"""
        try:
            # Verificar se a coleção existe e pertence ao usuário
            from memory_bank.models.collection import MemoryCollection
            collection = self.db.query(MemoryCollection).filter(
                and_(
                    MemoryCollection.id == memory_data.collection_id,
                    MemoryCollection.user_id == user_id
                )
            ).first()
            
            if not collection:
                raise ValueError("Coleção não encontrada ou sem permissão")
            
            # Verificar limite de memórias
            if collection.memory_count >= collection.max_memories:
                raise ValueError(f"Limite de memórias atingido ({collection.max_memories})")
            
            # Calcular tokens (simplificado)
            token_count = len(memory_data.content.split()) * 1.3
            
            # Gerar embedding se for texto
            embedding = None
            embedding_model = None
            if memory_data.content_type == "text":
                embedding, embedding_model = await get_embedding(memory_data.content)
            
            # Criar memória
            memory = Memory(
                user_id=user_id,
                collection_id=memory_data.collection_id,
                content=memory_data.content,
                content_type=memory_data.content_type,
                title=memory_data.title,
                description=memory_data.description,
                tags=memory_data.tags,
                importance_score=memory_data.importance_score,
                embedding=embedding,
                embedding_model=embedding_model,
                expires_at=memory_data.expires_at
            )
            
            self.db.add(memory)
            
            # Atualizar estatísticas da coleção
            collection.memory_count += 1
            collection.total_tokens += int(token_count)
            
            self.db.commit()
            self.db.refresh(memory)
            
            logger.info(f"Memória criada: {memory.id} para usuário {user_id}")
            return memory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar memória: {str(e)}")
            raise
    
    async def get_memory(self, user_id: str, memory_id: str) -> Optional[Memory]:
        """Obtém uma memória específica e atualiza contadores de acesso"""
        memory = self.db.query(Memory).filter(
            and_(
                Memory.id == memory_id,
                Memory.user_id == user_id
            )
        ).first()
        
        if memory:
            # Atualizar contadores de acesso
            memory.access_count += 1
            memory.last_accessed_at = datetime.now(timezone.utc)
            self.db.commit()
            
        return memory
    
    async def update_memory(self, user_id: str, memory_id: str, memory_data: MemoryUpdate) -> Optional[Memory]:
        """Atualiza uma memória existente"""
        try:
            memory = self.db.query(Memory).filter(
                and_(
                    Memory.id == memory_id,
                    Memory.user_id == user_id
                )
            ).first()
            
            if not memory:
                return None
            
            # Atualizar campos
            update_data = memory_data.dict(exclude_unset=True)
            
            # Se o conteúdo foi alterado, atualizar embedding
            if "content" in update_data and update_data["content"] != memory.content:
                if memory.content_type == "text" or ("content_type" in update_data and update_data["content_type"] == "text"):
                    embedding, embedding_model = await get_embedding(update_data["content"])
                    update_data["embedding"] = embedding
                    update_data["embedding_model"] = embedding_model
            
            # Aplicar atualizações
            for field, value in update_data.items():
                setattr(memory, field, value)
            
            memory.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(memory)
            
            return memory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar memória {memory_id}: {str(e)}")
            raise
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Deleta uma memória"""
        try:
            memory = self.db.query(Memory).filter(
                and_(
                    Memory.id == memory_id,
                    Memory.user_id == user_id
                )
            ).first()
            
            if not memory:
                return False
            
            # Atualizar estatísticas da coleção
            collection = memory.collection
            collection.memory_count = max(0, collection.memory_count - 1)
            
            # Estimar tokens (simplificado)
            token_count = len(memory.content.split()) * 1.3
            collection.total_tokens = max(0, collection.total_tokens - int(token_count))
            
            # Deletar memória
            self.db.delete(memory)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar memória {memory_id}: {str(e)}")
            return False
    
    async def search_memories(self, user_id: str, search_params: MemorySearch) -> List[Dict[str, Any]]:
        """Busca memórias por similaridade semântica"""
        try:
            # Gerar embedding para a consulta
            query_embedding, model = await get_embedding(search_params.query)
            
            # Construir filtros base
            filters = [Memory.user_id == user_id]
            
            # Adicionar filtro de coleção se especificado
            if search_params.collection_id:
                filters.append(Memory.collection_id == search_params.collection_id)
            
            # Adicionar filtro de tags se especificado
            if search_params.tags:
                # Implementação simplificada - na prática, precisaria de uma query mais complexa para JSON
                for tag in search_params.tags:
                    filters.append(Memory.tags.contains([tag]))
            
            # Buscar memórias do usuário que atendem aos filtros
            memories = self.db.query(Memory).filter(and_(*filters)).all()
            
            # Realizar busca vetorial em memória
            results = search_similar_vectors(
                query_embedding=query_embedding,
                items=memories,
                min_score=search_params.min_score,
                limit=search_params.limit
            )
            
            # Formatar resultados
            formatted_results = []
            for memory, score in results:
                # Incrementar contador de acesso
                memory.access_count += 1
                memory.last_accessed_at = datetime.now(timezone.utc)
                
                formatted_results.append({
                    "id": memory.id,
                    "title": memory.title,
                    "content": memory.content,
                    "content_type": memory.content_type,
                    "similarity_score": score,
                    "created_at": memory.created_at,
                    "tags": memory.tags,
                    "collection_id": memory.collection_id
                })
            
            self.db.commit()
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca semântica: {str(e)}")
            return []
    
    async def get_user_memories(
        self, 
        user_id: str, 
        collection_id: Optional[str] = None,
        limit: int = 50, 
        offset: int = 0,
        sort_by: str = "updated_at"
    ) -> List[Memory]:
        """Lista memórias do usuário com paginação e ordenação"""
        
        # Construir query base
        query = self.db.query(Memory).filter(Memory.user_id == user_id)
        
        # Filtrar por coleção se especificado
        if collection_id:
            query = query.filter(Memory.collection_id == collection_id)
        
        # Aplicar ordenação
        if sort_by == "importance":
            query = query.order_by(Memory.importance_score.desc(), Memory.updated_at.desc())
        elif sort_by == "access":
            query = query.order_by(Memory.access_count.desc(), Memory.updated_at.desc())
        elif sort_by == "created_at":
            query = query.order_by(Memory.created_at.desc())
        else:  # default: updated_at
            query = query.order_by(Memory.updated_at.desc())
        
        # Aplicar paginação
        memories = query.offset(offset).limit(limit).all()
        
        return memories
    
    async def cleanup_expired_memories(self) -> int:
        """Remove memórias expiradas (para execução agendada)"""
        try:
            now = datetime.now(timezone.utc)
            
            # Encontrar memórias expiradas
            expired = self.db.query(Memory).filter(
                and_(
                    Memory.expires_at.isnot(None),
                    Memory.expires_at < now
                )
            ).all()
            
            count = 0
            for memory in expired:
                # Atualizar estatísticas da coleção
                collection = memory.collection
                collection.memory_count = max(0, collection.memory_count - 1)
                
                # Estimar tokens (simplificado)
                token_count = len(memory.content.split()) * 1.3
                collection.total_tokens = max(0, collection.total_tokens - int(token_count))
                
                # Deletar memória
                self.db.delete(memory)
                count += 1
            
            self.db.commit()
            logger.info(f"Limpeza de memórias: {count} memórias expiradas removidas")
            
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro na limpeza de memórias expiradas: {str(e)}")
            return 0

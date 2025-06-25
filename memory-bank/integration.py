"""
Funções de integração do Memory Bank com o SynapScale Backend
"""
import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("memory-bank-integration")

def is_memory_bank_enabled() -> bool:
    """
    Verifica se o Memory Bank está habilitado
    """
    return os.getenv("ENABLE_MEMORY_BANK", "false").lower() == "true"

def get_memory_bank_config() -> Dict[str, Any]:
    """
    Obtém a configuração do Memory Bank
    """
    return {
        "embedding_model": os.getenv("MEMORY_BANK_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "vector_store": os.getenv("MEMORY_BANK_VECTOR_STORE", "faiss"),
        "max_memories": int(os.getenv("MEMORY_BANK_MAX_MEMORIES", "1000"))
    }

def setup_memory_bank(app: FastAPI) -> None:
    """
    Configura o Memory Bank no SynapScale Backend
    """
    if not is_memory_bank_enabled():
        logger.info("Memory Bank está desabilitado. Pulando configuração.")
        return
    
    try:
        # Importar o router do Memory Bank
        from memory_bank.api import router
        
        # Registrar o router na API
        app.include_router(
            router,
            prefix="/api/v1/memory-bank",
            tags=["memory-bank"]
        )
        
        logger.info("Memory Bank configurado com sucesso!")
        logger.info(f"Configuração: {get_memory_bank_config()}")
        
    except ImportError as e:
        logger.error(f"Erro ao importar Memory Bank: {e}")
        logger.error("Verifique se o Memory Bank está instalado corretamente.")
    except Exception as e:
        logger.error(f"Erro ao configurar Memory Bank: {e}")

async def add_memory(
    user_id: int,
    content: str,
    collection_name: str,
    workspace_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncSession] = None
) -> Optional[Dict[str, Any]]:
    """
    Adiciona uma memória ao Memory Bank
    
    Args:
        user_id: ID do usuário
        content: Conteúdo da memória
        collection_name: Nome da coleção
        workspace_id: ID do workspace (opcional)
        metadata: Metadados da memória (opcional)
        db: Sessão do banco de dados (opcional)
        
    Returns:
        Memória criada ou None se ocorrer um erro
    """
    if not is_memory_bank_enabled():
        logger.warning("Memory Bank está desabilitado. Não é possível adicionar memória.")
        return None
    
    try:
        # Importar o serviço de memória
        from memory_bank.services import MemoryService, CollectionService
        
        # Verificar se a coleção existe
        collection_service = CollectionService(db)
        collection = await collection_service.get_by_name(collection_name, user_id)
        
        # Se a coleção não existir, criar
        if not collection:
            collection = await collection_service.create({
                "name": collection_name,
                "description": f"Coleção {collection_name} criada automaticamente",
                "user_id": user_id,
                "workspace_id": workspace_id,
                "is_active": True,
                "metadata": {"auto_created": True}
            })
        
        # Adicionar a memória
        memory_service = MemoryService(db)
        memory = await memory_service.create({
            "collection_id": collection.id,
            "content": content,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "metadata": metadata or {},
            "is_active": True
        })
        
        return memory.to_dict() if memory else None
        
    except ImportError as e:
        logger.error(f"Erro ao importar serviços do Memory Bank: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao adicionar memória: {e}")
        return None

async def search_memories(
    user_id: int,
    query: str,
    collection_name: Optional[str] = None,
    workspace_id: Optional[int] = None,
    limit: int = 5,
    threshold: float = 0.7,
    db: Optional[AsyncSession] = None
) -> List[Dict[str, Any]]:
    """
    Busca memórias no Memory Bank por similaridade semântica
    
    Args:
        user_id: ID do usuário
        query: Consulta para busca
        collection_name: Nome da coleção (opcional)
        workspace_id: ID do workspace (opcional)
        limit: Número máximo de resultados
        threshold: Limiar de similaridade (0-1)
        db: Sessão do banco de dados (opcional)
        
    Returns:
        Lista de memórias encontradas
    """
    if not is_memory_bank_enabled():
        logger.warning("Memory Bank está desabilitado. Não é possível buscar memórias.")
        return []
    
    try:
        # Importar o serviço de memória
        from memory_bank.services import MemoryService, CollectionService
        
        # Se collection_name for fornecido, buscar apenas nessa coleção
        collection_id = None
        if collection_name:
            collection_service = CollectionService(db)
            collection = await collection_service.get_by_name(collection_name, user_id)
            if collection:
                collection_id = collection.id
            else:
                logger.warning(f"Coleção {collection_name} não encontrada para o usuário {user_id}")
                return []
        
        # Buscar memórias
        memory_service = MemoryService(db)
        memories = await memory_service.search({
            "query": query,
            "user_id": user_id,
            "collection_id": collection_id,
            "workspace_id": workspace_id,
            "limit": limit,
            "threshold": threshold
        })
        
        return [memory.to_dict() for memory in memories]
        
    except ImportError as e:
        logger.error(f"Erro ao importar serviços do Memory Bank: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro ao buscar memórias: {e}")
        return []

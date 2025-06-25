"""
Integração do Memory Bank com o SynapScale Backend
"""
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.database import get_async_db
from synapse.api.deps import get_current_user
from synapse.models.user import User

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("synapse-memory-bank-integration")

# Criar router
router = APIRouter()

def integrate_memory_bank(api_router: APIRouter) -> None:
    """
    Integra o Memory Bank com o SynapScale Backend
    
    Args:
        api_router: Router principal da API
    """
    if is_memory_bank_available():
        logger.info("Integrando Memory Bank com SynapScale Backend...")
        api_router.include_router(
            router,
            prefix="/memory-bank",
            tags=["memory-bank"]
        )
        logger.info("Memory Bank integrado com sucesso!")
    else:
        logger.info("Memory Bank não está disponível. Pulando integração.")

def setup_memory_bank(app: FastAPI) -> bool:
    """
    Configura o Memory Bank no SynapScale Backend
    
    Args:
        app: Aplicação FastAPI
        
    Returns:
        bool: True se a configuração foi bem-sucedida, False caso contrário
    """
    try:
        # Importar a função de integração do Memory Bank
        from memory_bank.integration import setup_memory_bank as mb_setup
        
        # Configurar o Memory Bank
        mb_setup(app)
        
        return True
    except ImportError as e:
        logger.error(f"Erro ao importar Memory Bank: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao configurar Memory Bank: {e}")
        return False

def is_memory_bank_available() -> bool:
    """
    Verifica se o Memory Bank está disponível
    """
    try:
        import memory_bank
        from memory_bank.integration import is_memory_bank_enabled
        return is_memory_bank_enabled()
    except ImportError:
        return False

@router.post("/memories", response_model=Dict[str, Any])
async def add_memory(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adiciona uma memória ao Memory Bank
    
    Args:
        data: Dados da memória
            - content: Conteúdo da memória
            - collection_name: Nome da coleção
            - workspace_id: ID do workspace (opcional)
            - metadata: Metadados da memória (opcional)
    """
    if not is_memory_bank_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory Bank não está disponível"
        )
    
    # Validar dados
    if "content" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo 'content' é obrigatório"
        )
    
    if "collection_name" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo 'collection_name' é obrigatório"
        )
    
    try:
        # Importar função de integração
        from memory_bank.integration import add_memory as mb_add_memory
        
        # Adicionar memória
        memory = await mb_add_memory(
            user_id=current_user.id,
            content=data["content"],
            collection_name=data["collection_name"],
            workspace_id=data.get("workspace_id"),
            metadata=data.get("metadata"),
            db=db
        )
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao adicionar memória"
            )
        
        return memory
        
    except ImportError as e:
        logger.error(f"Erro ao importar Memory Bank: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory Bank não está disponível"
        )
    except Exception as e:
        logger.error(f"Erro ao adicionar memória: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar memória: {str(e)}"
        )

@router.post("/search", response_model=List[Dict[str, Any]])
async def search_memories(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca memórias no Memory Bank por similaridade semântica
    
    Args:
        data: Dados da busca
            - query: Consulta para busca
            - collection_name: Nome da coleção (opcional)
            - workspace_id: ID do workspace (opcional)
            - limit: Número máximo de resultados (opcional, padrão: 5)
            - threshold: Limiar de similaridade (opcional, padrão: 0.7)
    """
    if not is_memory_bank_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory Bank não está disponível"
        )
    
    # Validar dados
    if "query" not in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo 'query' é obrigatório"
        )
    
    try:
        # Importar função de integração
        from memory_bank.integration import search_memories as mb_search_memories
        
        # Buscar memórias
        memories = await mb_search_memories(
            user_id=current_user.id,
            query=data["query"],
            collection_name=data.get("collection_name"),
            workspace_id=data.get("workspace_id"),
            limit=data.get("limit", 5),
            threshold=data.get("threshold", 0.7),
            db=db
        )
        
        return memories
        
    except ImportError as e:
        logger.error(f"Erro ao importar Memory Bank: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory Bank não está disponível"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar memórias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar memórias: {str(e)}"
        )

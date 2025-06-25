from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from synapse.api.deps import get_db, get_current_user
from synapse.models.user import User
from memory_bank.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse, MemorySearch
from memory_bank.services.memory_service import MemoryService

router = APIRouter()

@router.post("/memories", response_model=MemoryResponse, status_code=201, tags=["memories"])
async def create_memory(
    memory_data: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova memória.
    
    - **content**: Conteúdo da memória (texto, código, etc.)
    - **content_type**: Tipo de conteúdo (text, code, image, etc.)
    - **collection_id**: ID da coleção onde a memória será armazenada
    - **title**: Título opcional da memória
    - **tags**: Lista de tags para categorização
    - **importance_score**: Pontuação de importância (1-10)
    - **expires_at**: Data de expiração opcional
    """
    try:
        memory_service = MemoryService(db)
        memory = await memory_service.create_memory(
            user_id=str(current_user.id),
            memory_data=memory_data
        )
        return memory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar memória: {str(e)}")

@router.get("/memories/{memory_id}", response_model=MemoryResponse, tags=["memories"])
async def get_memory(
    memory_id: str = Path(..., description="ID da memória"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma memória específica pelo ID.
    """
    memory_service = MemoryService(db)
    memory = await memory_service.get_memory(
        user_id=str(current_user.id),
        memory_id=memory_id
    )
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memória não encontrada")
    
    return memory

@router.put("/memories/{memory_id}", response_model=MemoryResponse, tags=["memories"])
async def update_memory(
    memory_data: MemoryUpdate,
    memory_id: str = Path(..., description="ID da memória"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma memória existente.
    """
    try:
        memory_service = MemoryService(db)
        memory = await memory_service.update_memory(
            user_id=str(current_user.id),
            memory_id=memory_id,
            memory_data=memory_data
        )
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memória não encontrada")
        
        return memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar memória: {str(e)}")

@router.delete("/memories/{memory_id}", status_code=204, tags=["memories"])
async def delete_memory(
    memory_id: str = Path(..., description="ID da memória"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma memória.
    """
    memory_service = MemoryService(db)
    success = await memory_service.delete_memory(
        user_id=str(current_user.id),
        memory_id=memory_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Memória não encontrada")
    
    return {"status": "success"}

@router.post("/memories/search", tags=["memories"])
async def search_memories(
    search_params: MemorySearch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca memórias por similaridade semântica.
    
    - **query**: Texto para busca semântica
    - **collection_id**: Filtrar por coleção específica (opcional)
    - **limit**: Número máximo de resultados (1-100)
    - **min_score**: Pontuação mínima de similaridade (0-1)
    - **tags**: Filtrar por tags (opcional)
    """
    memory_service = MemoryService(db)
    results = await memory_service.search_memories(
        user_id=str(current_user.id),
        search_params=search_params
    )
    
    return {
        "query": search_params.query,
        "results": results,
        "count": len(results)
    }

@router.get("/memories", response_model=List[MemoryResponse], tags=["memories"])
async def get_user_memories(
    collection_id: Optional[str] = Query(None, description="Filtrar por coleção"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    sort_by: str = Query("updated_at", description="Campo para ordenação: updated_at, created_at, importance, access"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista memórias do usuário com paginação e ordenação.
    """
    memory_service = MemoryService(db)
    memories = await memory_service.get_user_memories(
        user_id=str(current_user.id),
        collection_id=collection_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by
    )
    
    return memories

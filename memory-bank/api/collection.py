from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from synapse.api.deps import get_db, get_current_user
from synapse.models.user import User
from memory_bank.schemas.collection import CollectionCreate, CollectionUpdate, CollectionResponse, CollectionStats
from memory_bank.services.collection_service import CollectionService

router = APIRouter()

@router.post("/collections", response_model=CollectionResponse, status_code=201, tags=["collections"])
async def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova coleção de memórias.
    
    - **name**: Nome da coleção
    - **description**: Descrição opcional
    - **is_private**: Se a coleção é privada ou compartilhada
    - **max_memories**: Número máximo de memórias (padrão: 1000)
    - **retention_days**: Dias de retenção, 0=sem expiração (padrão: 90)
    - **workspace_id**: ID do workspace (opcional)
    """
    try:
        collection_service = CollectionService(db)
        collection = await collection_service.create_collection(
            user_id=str(current_user.id),
            collection_data=collection_data
        )
        return collection
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar coleção: {str(e)}")

@router.get("/collections/{collection_id}", response_model=CollectionResponse, tags=["collections"])
async def get_collection(
    collection_id: str = Path(..., description="ID da coleção"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma coleção específica pelo ID.
    """
    collection_service = CollectionService(db)
    collection = await collection_service.get_collection(
        user_id=str(current_user.id),
        collection_id=collection_id
    )
    
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    return collection

@router.put("/collections/{collection_id}", response_model=CollectionResponse, tags=["collections"])
async def update_collection(
    collection_data: CollectionUpdate,
    collection_id: str = Path(..., description="ID da coleção"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma coleção existente.
    """
    try:
        collection_service = CollectionService(db)
        collection = await collection_service.update_collection(
            user_id=str(current_user.id),
            collection_id=collection_id,
            collection_data=collection_data
        )
        
        if not collection:
            raise HTTPException(status_code=404, detail="Coleção não encontrada")
        
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar coleção: {str(e)}")

@router.delete("/collections/{collection_id}", status_code=204, tags=["collections"])
async def delete_collection(
    collection_id: str = Path(..., description="ID da coleção"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma coleção e todas as suas memórias.
    """
    collection_service = CollectionService(db)
    success = await collection_service.delete_collection(
        user_id=str(current_user.id),
        collection_id=collection_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    return {"status": "success"}

@router.get("/collections", response_model=List[CollectionResponse], tags=["collections"])
async def get_user_collections(
    workspace_id: Optional[str] = Query(None, description="Filtrar por workspace"),
    include_shared: bool = Query(True, description="Incluir coleções compartilhadas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista coleções do usuário, opcionalmente filtrando por workspace.
    """
    collection_service = CollectionService(db)
    collections = await collection_service.get_user_collections(
        user_id=str(current_user.id),
        workspace_id=workspace_id,
        include_shared=include_shared
    )
    
    return collections

@router.get("/collections/stats", response_model=CollectionStats, tags=["collections"])
async def get_collection_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém estatísticas das coleções do usuário.
    """
    collection_service = CollectionService(db)
    stats = await collection_service.get_collection_stats(
        user_id=str(current_user.id)
    )
    
    return stats

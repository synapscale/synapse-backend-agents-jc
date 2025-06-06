"""
Endpoints para gerenciamento de nodes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.models.node import Node
from src.synapse.api.deps import get_current_user
from src.synapse.schemas.node import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    NodeListResponse
)

router = APIRouter()

@router.get("/", response_model=NodeListResponse)
async def list_nodes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar nodes disponíveis"""
    query = db.query(Node)
    
    # Filtrar por usuário ou nodes públicos
    if is_public is True:
        query = query.filter(Node.is_public == True)
    else:
        query = query.filter(Node.user_id == current_user.id)
    
    # Filtros adicionais
    if type:
        query = query.filter(Node.type == type)
    
    if category:
        query = query.filter(Node.category == category)
    
    if search:
        query = query.filter(
            Node.name.ilike(f"%{search}%") |
            Node.description.ilike(f"%{search}%")
        )
    
    # Ordenar por popularidade
    query = query.order_by(Node.downloads_count.desc())
    
    # Paginação
    total = query.count()
    nodes = query.offset((page - 1) * size).limit(size).all()
    
    return NodeListResponse(
        items=nodes,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.post("/", response_model=NodeResponse)
async def create_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo node"""
    node = Node(
        **node_data.dict(),
        user_id=current_user.id
    )
    
    db.add(node)
    db.commit()
    db.refresh(node)
    
    return node

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter node específico"""
    node = db.query(Node).filter(
        Node.id == node_id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node não encontrado"
        )
    
    # Verificar permissão
    if node.user_id != current_user.id and not node.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este node"
        )
    
    return node

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar node"""
    node = db.query(Node).filter(
        Node.id == node_id,
        Node.user_id == current_user.id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node não encontrado"
        )
    
    # Atualizar campos
    for field, value in node_data.dict(exclude_unset=True).items():
        setattr(node, field, value)
    
    db.commit()
    db.refresh(node)
    
    return node

@router.delete("/{node_id}")
async def delete_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar node"""
    node = db.query(Node).filter(
        Node.id == node_id,
        Node.user_id == current_user.id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node não encontrado"
        )
    
    db.delete(node)
    db.commit()
    
    return {"message": "Node deletado com sucesso"}

@router.post("/{node_id}/download")
async def download_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fazer download/instalar node"""
    node = db.query(Node).filter(
        Node.id == node_id,
        Node.is_public == True
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node não encontrado ou não público"
        )
    
    # Incrementar contador de downloads
    node.downloads_count += 1
    db.commit()
    
    return {
        "message": "Node baixado com sucesso",
        "node_id": node_id,
        "downloads_count": node.downloads_count
    }

@router.post("/{node_id}/rate")
async def rate_node(
    node_id: str,
    rating: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Avaliar node"""
    node = db.query(Node).filter(
        Node.id == node_id,
        Node.is_public == True
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node não encontrado ou não público"
        )
    
    # TODO: Implementar sistema de avaliações
    # Por enquanto, apenas atualizar média simples
    current_total = node.rating_average * node.rating_count
    new_total = current_total + rating
    node.rating_count += 1
    node.rating_average = new_total / node.rating_count
    
    db.commit()
    
    return {
        "message": "Avaliação registrada com sucesso",
        "rating_average": node.rating_average,
        "rating_count": node.rating_count
    }

@router.get("/categories/")
async def list_node_categories(
    db: Session = Depends(get_db)
):
    """Listar categorias de nodes disponíveis"""
    categories = db.query(Node.category).filter(
        Node.category.isnot(None),
        Node.is_public == True
    ).distinct().all()
    
    return {
        "categories": [cat[0] for cat in categories if cat[0]]
    }

@router.get("/types/")
async def list_node_types(
    db: Session = Depends(get_db)
):
    """Listar tipos de nodes disponíveis"""
    types = db.query(Node.type).filter(
        Node.type.isnot(None),
        Node.is_public == True
    ).distinct().all()
    
    return {
        "types": [type_[0] for type_ in types if type_[0]]
    }


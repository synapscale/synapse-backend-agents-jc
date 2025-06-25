"""
Endpoints para gerenciamento de nodes
Criado por José - um desenvolvedor Full Stack
API completa para CRUD e gerenciamento de nodes de workflow
"""

import logging
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from synapse.api.deps import get_current_user
from synapse.database import get_db
from synapse.models.node import Node, NodeType, NodeRating
from synapse.models.user import User
from synapse.schemas.node import (
    NodeCreate,
    NodeListResponse,
    NodeResponse,
    NodeUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=NodeListResponse,
    summary="Listar nodes",
    tags=["workflows"],
)
async def list_nodes(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    type: Optional[str] = Query(None, description="Filtrar por tipo de node"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    is_public: Optional[bool] = Query(None, description="Filtrar nodes públicos"),
    search: Optional[str] = Query(None, description="Termo de busca"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NodeListResponse:
    """
    Lista nodes disponíveis com filtros e paginação.
    
    Retorna nodes próprios ou públicos dependendo dos filtros,
    ordenados por popularidade (downloads).
    
    Args:
        page: Número da página (1-based)
        size: Número de itens por página
        type: Tipo específico de node para filtrar
        category: Categoria específica para filtrar
        is_public: Se True, mostra apenas nodes públicos
        search: Termo para buscar em nome e descrição
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        NodeListResponse: Lista paginada de nodes
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando nodes para usuário {current_user.id} - página: {page}, público: {is_public}")
        
        query = db.query(Node)

        # Filtrar por usuário ou nodes públicos
        if is_public is True:
            query = query.filter(Node.is_public == True)
            logger.info("Filtrando apenas nodes públicos")
        else:
            query = query.filter(Node.user_id == current_user.id)
            logger.info(f"Filtrando nodes do usuário {current_user.id}")

        # Filtros adicionais
        if type:
            query = query.filter(Node.type == type)
            logger.info(f"Filtrando por tipo: {type}")

        if category:
            query = query.filter(Node.category == category)
            logger.info(f"Filtrando por categoria: {category}")

        if search:
            query = query.filter(
                Node.name.ilike(f"%{search}%") | Node.description.ilike(f"%{search}%"),
            )
            logger.info(f"Filtrando por busca: '{search}'")

        # Ordenar por popularidade
        query = query.order_by(Node.downloads_count.desc())

        # Paginação
        total = query.count()
        nodes = query.offset((page - 1) * size).limit(size).all()

        logger.info(f"Retornados {len(nodes)} nodes de {total} total para usuário {current_user.id}")
        
        return NodeListResponse(
            items=nodes,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )
    except Exception as e:
        logger.error(f"Erro ao listar nodes para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/", response_model=NodeResponse, summary="Criar node", tags=["workflows"])
async def create_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NodeResponse:
    """
    Cria um novo node personalizado.
    
    Permite criar nodes customizados com lógica específica
    para uso em workflows.
    
    Args:
        node_data: Dados do node a ser criado
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        NodeResponse: Node criado
        
    Raises:
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Criando node '{node_data.name}' para usuário {current_user.id}")
        
        node = Node(**node_data.dict(), user_id=current_user.id)

        db.add(node)
        db.commit()
        db.refresh(node)

        logger.info(f"Node '{node.name}' criado com sucesso (ID: {node.id}) para usuário {current_user.id}")
        return node
    except Exception as e:
        logger.error(f"Erro ao criar node para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{node_id}", response_model=NodeResponse, summary="Obter node", tags=["workflows"])
async def get_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NodeResponse:
    """
    Obtém um node específico por ID.
    
    Retorna dados completos do node se o usuário
    tiver permissão de acesso.
    
    Args:
        node_id: ID único do node
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        NodeResponse: Dados do node
        
    Raises:
        HTTPException: 404 se node não encontrado
        HTTPException: 403 se sem permissão de acesso
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo node {node_id} para usuário {current_user.id}")
        
        # Validate node_id format (UUID)
        try:
            from uuid import UUID
            node_uuid = UUID(node_id)
        except (ValueError, TypeError):
            logger.warning(f"node_id inválido: {node_id}")
            raise HTTPException(status_code=404, detail="Node não encontrado")
        
        try:
            node = db.query(Node).filter(Node.id == node_uuid).first()

            if not node:
                logger.warning(f"Node {node_id} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Node não encontrado",
                )

            # Verificar permissão
            if node.user_id != current_user.id and not node.is_public:
                logger.warning(f"Usuário {current_user.id} sem permissão para acessar node {node_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para acessar este node",
                )

            logger.info(f"Node {node_id} obtido com sucesso para usuário {current_user.id}")
            
            # Convert to proper response model with fallback values
            try:
                if hasattr(node, 'to_dict'):
                    node_dict = node.to_dict()
                    return NodeResponse(**node_dict)
                else:
                    # Fallback manual conversion
                    return NodeResponse(
                        id=str(node.id),
                        name=getattr(node, 'name', ''),
                        description=getattr(node, 'description', ''),
                        type=getattr(node, 'type', 'operation'),
                        category=getattr(node, 'category', ''),
                        user_id=str(getattr(node, 'user_id', '')),
                        workspace_id=str(getattr(node, 'workspace_id', '')) if getattr(node, 'workspace_id') else None,
                        is_public=getattr(node, 'is_public', False),
                        downloads_count=getattr(node, 'downloads_count', 0),
                        rating_average=getattr(node, 'rating_average', 0),
                        rating_count=getattr(node, 'rating_count', 0),
                        created_at=getattr(node, 'created_at', None),
                        updated_at=getattr(node, 'updated_at', None)
                    )
            except (ValueError, TypeError) as e:
                logger.error(f"Erro na conversão do modelo Node: {str(e)}")
                raise HTTPException(status_code=500, detail="Erro na conversão de dados")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro de serviço ao obter node {node_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro no serviço de nodes")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao obter node {node_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{node_id}", response_model=NodeResponse, summary="Atualizar node", tags=["workflows"])
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NodeResponse:
    """
    Atualiza um node existente do usuário.
    
    Permite modificar propriedades do node se o usuário
    for o proprietário.
    
    Args:
        node_id: ID único do node
        node_data: Dados atualizados do node
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        NodeResponse: Node atualizado
        
    Raises:
        HTTPException: 404 se node não encontrado
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Atualizando node {node_id} para usuário {current_user.id}")
        
        # Validate node_id format (UUID)
        try:
            from uuid import UUID
            node_uuid = UUID(node_id)
        except (ValueError, TypeError):
            logger.warning(f"node_id inválido: {node_id}")
            raise HTTPException(status_code=404, detail="Node não encontrado")
        
        try:
            node = (
                db.query(Node)
                .filter(Node.id == node_uuid, Node.user_id == current_user.id)
                .first()
            )

            if not node:
                logger.warning(f"Node {node_id} não encontrado ou sem permissão para usuário {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Node não encontrado",
                )

            # Atualizar campos
            update_count = 0
            for field, value in node_data.dict(exclude_unset=True).items():
                if getattr(node, field) != value:
                    setattr(node, field, value)
                    update_count += 1

            if update_count > 0:
                db.commit()
                db.refresh(node)
                logger.info(f"Node {node_id} atualizado com sucesso - {update_count} campos modificados")
            else:
                logger.info(f"Nenhuma alteração necessária no node {node_id}")

            # Convert to proper response model with fallback values
            try:
                if hasattr(node, 'to_dict'):
                    node_dict = node.to_dict()
                    return NodeResponse(**node_dict)
                else:
                    # Fallback manual conversion
                    return NodeResponse(
                        id=str(node.id),
                        name=getattr(node, 'name', ''),
                        description=getattr(node, 'description', ''),
                        type=getattr(node, 'type', 'operation'),
                        category=getattr(node, 'category', ''),
                        user_id=str(getattr(node, 'user_id', '')),
                        workspace_id=str(getattr(node, 'workspace_id', '')) if getattr(node, 'workspace_id') else None,
                        is_public=getattr(node, 'is_public', False),
                        downloads_count=getattr(node, 'downloads_count', 0),
                        rating_average=getattr(node, 'rating_average', 0),
                        rating_count=getattr(node, 'rating_count', 0),
                        created_at=getattr(node, 'created_at', None),
                        updated_at=getattr(node, 'updated_at', None)
                    )
            except (ValueError, TypeError) as e:
                logger.error(f"Erro na conversão do modelo Node: {str(e)}")
                raise HTTPException(status_code=500, detail="Erro na conversão de dados")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro de serviço ao atualizar node {node_id}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro no serviço de nodes")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao atualizar node {node_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{node_id}", summary="Deletar node", tags=["workflows"])
async def delete_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Remove um node do usuário.
    
    Deleta permanentemente o node se o usuário
    for o proprietário.
    
    Args:
        node_id: ID único do node
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se node não encontrado
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Deletando node {node_id} para usuário {current_user.id}")
        
        # Validate node_id format (UUID)
        try:
            from uuid import UUID
            node_uuid = UUID(node_id)
        except (ValueError, TypeError):
            logger.warning(f"node_id inválido: {node_id}")
            raise HTTPException(status_code=404, detail="Node não encontrado")
        
        try:
            node = (
                db.query(Node)
                .filter(Node.id == node_uuid, Node.user_id == current_user.id)
                .first()
            )

            if not node:
                logger.warning(f"Node {node_id} não encontrado ou sem permissão para usuário {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Node não encontrado",
                )

            node_name = node.name
            db.delete(node)
            db.commit()

            logger.info(f"Node '{node_name}' (ID: {node_id}) deletado com sucesso para usuário {current_user.id}")
            return {"message": "Node deletado com sucesso"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro de serviço ao deletar node {node_id}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro no serviço de nodes")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral ao deletar node {node_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{node_id}/download", summary="Download/instalar node", tags=["workflows"])
async def download_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Faz download/instalação de um node público.
    
    Registra download e incrementa contador de popularidade
    para nodes públicos disponíveis.
    
    Args:
        node_id: ID único do node
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, Any]: Informações do download
        
    Raises:
        HTTPException: 404 se node não encontrado ou não público
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Fazendo download do node {node_id} para usuário {current_user.id}")
        
        # Validate node_id format (UUID)
        try:
            from uuid import UUID
            node_uuid = UUID(node_id)
        except (ValueError, TypeError):
            logger.warning(f"node_id inválido: {node_id}")
            raise HTTPException(status_code=404, detail="Node não encontrado ou não público")
        
        try:
            node = db.query(Node).filter(Node.id == node_uuid, Node.is_public == True).first()

            if not node:
                logger.warning(f"Node {node_id} não encontrado ou não é público")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Node não encontrado ou não público",
                )

            # Incrementar contador de downloads
            node.downloads_count += 1
            db.commit()

            logger.info(f"Download do node '{node.name}' (ID: {node_id}) registrado para usuário {current_user.id} - total downloads: {node.downloads_count}")
            
            return {
                "message": "Node baixado com sucesso",
                "node_id": str(node.id),  # Ensure ID is properly serialized as string
                "node_name": getattr(node, 'name', ''),
                "downloads_count": getattr(node, 'downloads_count', 0),
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro de serviço ao fazer download do node {node_id}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro no serviço de nodes")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro geral no download do node {node_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{node_id}/rate", summary="Avaliar node", tags=["workflows"])
async def rate_node(
    node_id: str,
    rating: int = Query(..., ge=1, le=5, description="Avaliação de 1 a 5"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Avalia um node público com nota de 1 a 5.
    
    Permite usuários avaliarem nodes públicos para
    melhorar a descoberta e qualidade.
    
    Args:
        node_id: ID único do node
        rating: Nota de 1 a 5
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, Any]: Resultado da avaliação
        
    Raises:
        HTTPException: 404 se node não encontrado ou não público
        HTTPException: 400 se rating inválido
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Avaliando node {node_id} com nota {rating} por usuário {current_user.id}")
        
        node = db.query(Node).filter(Node.id == node_id, Node.is_public == True).first()

        if not node:
            logger.warning(f"Node {node_id} não encontrado ou não é público para avaliação")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node não encontrado ou não público",
            )

        # Salvar avaliação do usuário
        rating_obj = NodeRating(node_id=node.id, user_id=current_user.id, rating=rating)
        db.add(rating_obj)
        db.commit()
        db.refresh(rating_obj)

        # Após avaliação, recalcule rating_average e rating_count
        rating_stats = db.query(
            func.avg(NodeRating.rating).label("avg_rating"),
            func.count(NodeRating.rating).label("count_rating")
        ).filter(NodeRating.node_id == node.id).first()
        node.rating_average = float(rating_stats.avg_rating or 0)
        node.rating_count = int(rating_stats.count_rating or 0)
        db.commit()
        db.refresh(node)
        response = {
            "id": str(node.id),
            "name": node.name,
            "category": node.category,
            "rating_average": node.rating_average,
            "rating_count": node.rating_count,
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao avaliar node {node_id} por usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/categories/", response_model=List[str], summary="Listar categorias", tags=["workflows"])
async def list_node_categories(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Lista todas as categorias de nodes disponíveis.
    
    Retorna lista única de categorias existentes
    no sistema para facilitar filtros.
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        List[str]: Lista de categorias únicas
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info("Obtendo lista de categorias de nodes")
        
        # Buscar categorias únicas
        categories_query = db.query(Node.category).filter(
            Node.category.isnot(None),
            Node.is_public == True
        ).distinct()
        
        categories = [cat[0] for cat in categories_query.all() if cat[0]]
        categories.sort()  # Ordenar alfabeticamente
        
        logger.info(f"Retornadas {len(categories)} categorias de nodes")
        return categories
    except Exception as e:
        logger.error(f"Erro ao obter categorias de nodes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/types/", response_model=List[str], summary="Listar tipos", tags=["workflows"])
async def list_node_types(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Lista todos os tipos de nodes disponíveis.
    
    Retorna lista única de tipos existentes
    no sistema para facilitar filtros.
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        List[str]: Lista de tipos únicos
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info("Obtendo lista de tipos de nodes")
        
        # Buscar tipos únicos
        types_query = db.query(Node.type).filter(
            Node.type.isnot(None),
            Node.is_public == True
        ).distinct()
        
        types = [typ[0] for typ in types_query.all() if typ[0]]
        types.sort()  # Ordenar alfabeticamente
        
        logger.info(f"Retornados {len(types)} tipos de nodes")
        return types
    except Exception as e:
        logger.error(f"Erro ao obter tipos de nodes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

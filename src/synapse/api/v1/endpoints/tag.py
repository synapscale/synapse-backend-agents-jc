import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from synapse.database import get_db
from synapse.models.tag import Tag
from synapse.models.user import User
from synapse.api.deps import get_current_user
from synapse.schemas.tag import TagCreateSchema, TagResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", summary="Criar nova tag")
async def create_tag(
    tag_data: TagCreateSchema, current_user: User = Depends(get_current_user)
) -> TagResponseSchema:
    """Cria uma nova tag para o usuário"""
    try:
        logger.info(f"Criando nova tag para usuário {current_user.id}")

        # Validate tag data
        if not tag_data or not isinstance(tag_data, dict):
            logger.warning(
                f"Dados de tag inválidos para usuário {current_user.id}: {tag_data}"
            )
            raise HTTPException(status_code=400, detail="Dados da tag são obrigatórios")

        try:
            # Create tag with user ID
            tag_obj = Tag(**tag_data, created_by_user_id=current_user.id)
            db = next(get_db())
            db.add(tag_obj)
            db.commit()
            db.refresh(tag_obj)

            # Convert to dict safely
            try:
                result = tag_obj.to_dict()
                logger.info(f"Tag criada com sucesso para usuário {current_user.id}")
                return result
            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter tag para dict: {str(conversion_error)}"
                )
                # Return basic dict structure as fallback
                return {
                    "id": str(tag_obj.id) if hasattr(tag_obj, "id") else None,
                    "tag_name": getattr(tag_obj, "tag_name", None),
                    "target_type": getattr(tag_obj, "target_type", None),
                    "target_id": (
                        str(getattr(tag_obj, "target_id", None))
                        if getattr(tag_obj, "target_id", None)
                        else None
                    ),
                    "created_by_user_id": current_user.id,
                }

        except Exception as db_error:
            db.rollback()
            logger.error(f"Erro de banco ao criar tag: {str(db_error)}")
            raise HTTPException(
                status_code=500, detail="Erro ao salvar tag no banco de dados"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao criar tag para usuário {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", summary="Listar tags")
def list_tags(
    target_type: Optional[str] = Query(None),
    target_id: Optional[UUID] = Query(None),
    tag_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista tags com filtros opcionais"""
    try:
        logger.info(
            f"Listando tags para usuário {current_user.id} - target_type: {target_type}, target_id: {target_id}, tag_name: {tag_name}"
        )

        try:
            # Build query with filters
            query = db.query(Tag)
            if target_type:
                query = query.filter(Tag.target_type == target_type)
            if target_id:
                query = query.filter(Tag.target_id == target_id)
            if tag_name:
                query = query.filter(Tag.tag_name == tag_name)

            # Execute query
            tags = query.order_by(Tag.created_at.desc()).limit(100).all()

            # Convert results safely
            try:
                result = []
                for tag in tags:
                    try:
                        result.append(tag.to_dict())
                    except Exception as tag_error:
                        logger.warning(
                            f"Erro ao converter tag {getattr(tag, 'id', 'unknown')} para dict: {str(tag_error)}"
                        )
                        # Add fallback dict
                        result.append(
                            {
                                "id": str(tag.id) if hasattr(tag, "id") else None,
                                "tag_name": getattr(tag, "tag_name", None),
                                "target_type": getattr(tag, "target_type", None),
                                "target_id": (
                                    str(getattr(tag, "target_id", None))
                                    if getattr(tag, "target_id", None)
                                    else None
                                ),
                                "created_by_user_id": getattr(
                                    tag, "created_by_user_id", None
                                ),
                            }
                        )

                logger.info(
                    f"Retornadas {len(result)} tags para usuário {current_user.id}"
                )
                return result

            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter lista de tags: {str(conversion_error)}"
                )
                return []  # Return empty list as fallback

        except Exception as db_error:
            logger.error(f"Erro de banco ao listar tags: {str(db_error)}")
            raise HTTPException(
                status_code=500, detail="Erro ao buscar tags no banco de dados"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao listar tags para usuário {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post(
    "/conversations/{conversation_id}/tags",
    summary="Adicionar tag a conversa",
)
def add_tag_to_conversation(
    conversation_id: UUID,
    tag: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Adiciona uma tag a uma conversa específica"""
    try:
        logger.info(
            f"Adicionando tag à conversa {conversation_id} para usuário {current_user.id}"
        )

        # Validate conversation_id
        if not conversation_id:
            logger.warning(f"ID da conversa inválido: {conversation_id}")
            raise HTTPException(status_code=400, detail="ID da conversa é obrigatório")

        # Validate tag data
        if not tag or not isinstance(tag, dict):
            logger.warning(
                f"Dados de tag inválidos para conversa {conversation_id}: {tag}"
            )
            raise HTTPException(status_code=400, detail="Dados da tag são obrigatórios")

        try:
            # Create tag for conversation
            tag_obj = Tag(
                target_type="conversation",
                target_id=conversation_id,
                created_by_user_id=current_user.id,
                **tag,
            )
            db.add(tag_obj)
            db.commit()
            db.refresh(tag_obj)

            # Convert to dict safely
            try:
                result = tag_obj.to_dict()
                logger.info(f"Tag adicionada à conversa {conversation_id} com sucesso")
                return result
            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter tag da conversa para dict: {str(conversion_error)}"
                )
                # Return basic dict structure as fallback
                return {
                    "id": str(tag_obj.id) if hasattr(tag_obj, "id") else None,
                    "tag_name": getattr(tag_obj, "tag_name", None),
                    "target_type": "conversation",
                    "target_id": str(conversation_id),
                    "created_by_user_id": current_user.id,
                }

        except Exception as db_error:
            db.rollback()
            logger.error(
                f"Erro de banco ao adicionar tag à conversa {conversation_id}: {str(db_error)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar tag da conversa no banco de dados",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao adicionar tag à conversa {conversation_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/conversations/{conversation_id}/tags",
    summary="Listar tags de conversa",
)
def list_tags_for_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as tags de uma conversa específica"""
    try:
        logger.info(
            f"Listando tags da conversa {conversation_id} para usuário {current_user.id}"
        )

        # Validate conversation_id
        if not conversation_id:
            logger.warning(f"ID da conversa inválido: {conversation_id}")
            raise HTTPException(status_code=400, detail="ID da conversa é obrigatório")

        try:
            # Query tags for conversation
            tags = (
                db.query(Tag)
                .filter(
                    Tag.target_type == "conversation", Tag.target_id == conversation_id
                )
                .order_by(Tag.created_at.desc())
                .all()
            )

            # Convert results safely
            try:
                result = []
                for tag in tags:
                    try:
                        result.append(tag.to_dict())
                    except Exception as tag_error:
                        logger.warning(
                            f"Erro ao converter tag {getattr(tag, 'id', 'unknown')} da conversa: {str(tag_error)}"
                        )
                        # Add fallback dict
                        result.append(
                            {
                                "id": str(tag.id) if hasattr(tag, "id") else None,
                                "tag_name": getattr(tag, "tag_name", None),
                                "target_type": "conversation",
                                "target_id": str(conversation_id),
                                "created_by_user_id": getattr(
                                    tag, "created_by_user_id", None
                                ),
                            }
                        )

                logger.info(
                    f"Retornadas {len(result)} tags da conversa {conversation_id}"
                )
                return result

            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter tags da conversa {conversation_id}: {str(conversion_error)}"
                )
                return []  # Return empty list as fallback

        except Exception as db_error:
            logger.error(
                f"Erro de banco ao buscar tags da conversa {conversation_id}: {str(db_error)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar tags da conversa no banco de dados",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao listar tags da conversa {conversation_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post(
    "/messages/{message_id}/tags", summary="Adicionar tag a mensagem"
)
def add_tag_to_message(
    message_id: UUID,
    tag: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Adiciona uma tag a uma mensagem específica"""
    try:
        logger.info(
            f"Adicionando tag à mensagem {message_id} para usuário {current_user.id}"
        )

        # Validate message_id
        if not message_id:
            logger.warning(f"ID da mensagem inválido: {message_id}")
            raise HTTPException(status_code=400, detail="ID da mensagem é obrigatório")

        # Validate tag data
        if not tag or not isinstance(tag, dict):
            logger.warning(f"Dados de tag inválidos para mensagem {message_id}: {tag}")
            raise HTTPException(status_code=400, detail="Dados da tag são obrigatórios")

        try:
            # Create tag for message
            tag_obj = Tag(
                target_type="message",
                target_id=message_id,
                created_by_user_id=current_user.id,
                **tag,
            )
            db.add(tag_obj)
            db.commit()
            db.refresh(tag_obj)

            # Convert to dict safely
            try:
                result = tag_obj.to_dict()
                logger.info(f"Tag adicionada à mensagem {message_id} com sucesso")
                return result
            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter tag da mensagem para dict: {str(conversion_error)}"
                )
                # Return basic dict structure as fallback
                return {
                    "id": str(tag_obj.id) if hasattr(tag_obj, "id") else None,
                    "tag_name": getattr(tag_obj, "tag_name", None),
                    "target_type": "message",
                    "target_id": str(message_id),
                    "created_by_user_id": current_user.id,
                }

        except Exception as db_error:
            db.rollback()
            logger.error(
                f"Erro de banco ao adicionar tag à mensagem {message_id}: {str(db_error)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar tag da mensagem no banco de dados",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao adicionar tag à mensagem {message_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/messages/{message_id}/tags", summary="Listar tags de mensagem"
)
def list_tags_for_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as tags de uma mensagem específica"""
    try:
        logger.info(
            f"Listando tags da mensagem {message_id} para usuário {current_user.id}"
        )

        # Validate message_id
        if not message_id:
            logger.warning(f"ID da mensagem inválido: {message_id}")
            raise HTTPException(status_code=400, detail="ID da mensagem é obrigatório")

        try:
            # Query tags for message
            tags = (
                db.query(Tag)
                .filter(Tag.target_type == "message", Tag.target_id == message_id)
                .order_by(Tag.created_at.desc())
                .all()
            )

            # Convert results safely
            try:
                result = []
                for tag in tags:
                    try:
                        result.append(tag.to_dict())
                    except Exception as tag_error:
                        logger.warning(
                            f"Erro ao converter tag {getattr(tag, 'id', 'unknown')} da mensagem: {str(tag_error)}"
                        )
                        # Add fallback dict
                        result.append(
                            {
                                "id": str(tag.id) if hasattr(tag, "id") else None,
                                "tag_name": getattr(tag, "tag_name", None),
                                "target_type": "message",
                                "target_id": str(message_id),
                                "created_by_user_id": getattr(
                                    tag, "created_by_user_id", None
                                ),
                            }
                        )

                logger.info(f"Retornadas {len(result)} tags da mensagem {message_id}")
                return result

            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter tags da mensagem {message_id}: {str(conversion_error)}"
                )
                return []  # Return empty list as fallback

        except Exception as db_error:
            logger.error(
                f"Erro de banco ao buscar tags da mensagem {message_id}: {str(db_error)}"
            )
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar tags da mensagem no banco de dados",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao listar tags da mensagem {message_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

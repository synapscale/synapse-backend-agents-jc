"""
Endpoints para gerenciamento de conversações e mensagens
Criado por José - um desenvolvedor Full Stack
API completa para chat e comunicação com agents
"""

import logging
from typing import Optional, Dict, Any
import time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from synapse.api.deps import get_current_user
from synapse.services.llm_service import get_llm_service, UnifiedLLMService
from synapse.database import get_db
from synapse.models.agent import Agent
from synapse.models.conversation import Conversation
from synapse.models.message import Message
from synapse.models.user import User
from synapse.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=ConversationListResponse,
    summary="Listar conversas",
    tags=["ai"],
)
async def list_conversations(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    agent_id: Optional[str] = Query(None, description="Filtrar por agent específico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationListResponse:
    """
    Lista todas as conversações do usuário com paginação.
    
    Retorna conversações ordenadas pela última mensagem,
    com opção de filtrar por agent específico.
    
    Args:
        page: Número da página (1-based)
        size: Número de itens por página
        agent_id: ID do agent para filtrar conversações
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        ConversationListResponse: Lista paginada de conversações
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando conversações para usuário {current_user.id} - página: {page}, agent: {agent_id}")
        
        query = db.query(Conversation).filter(Conversation.user_id == current_user.id)

        if agent_id:
            query = query.filter(Conversation.agent_id == agent_id)
            logger.info(f"Filtrando por agent {agent_id}")

        query = query.order_by(Conversation.updated_at.desc().nullslast())

        # Paginação
        total = query.count()
        conversations = query.offset((page - 1) * size).limit(size).all()

        logger.info(f"Retornadas {len(conversations)} conversações de {total} total para usuário {current_user.id}")
        
        return ConversationListResponse(
            items=conversations,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )
    except Exception as e:
        logger.error(f"Erro ao listar conversações para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/", response_model=ConversationResponse, summary="Criar conversação", tags=["ai"])
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    """
    Cria uma nova conversação para o usuário.
    
    Permite iniciar uma conversa com um agent específico
    ou criar uma conversação geral.
    
    Args:
        conversation_data: Dados da conversação a ser criada
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        ConversationResponse: Conversação criada
        
    Raises:
        HTTPException: 400 se dados inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Criando conversação '{conversation_data.title}' para usuário {current_user.id}")
        
        conversation = Conversation(
            title=conversation_data.title,
            agent_id=conversation_data.agent_id,
            user_id=current_user.id,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Conversação '{conversation.title}' criada com sucesso (ID: {conversation.id}) para usuário {current_user.id}")
        return {
            "id": str(conversation.id),
            "user_id": str(conversation.user_id),
            "agent_id": str(conversation.agent_id) if conversation.agent_id else None,
            "workspace_id": conversation.workspace_id,
            "title": conversation.title,
            "status": conversation.status,
            "message_count": conversation.message_count,
            "total_tokens_used": conversation.total_tokens_used,
            "context": conversation.context,
            "settings": conversation.settings,
            "last_message_at": conversation.last_message_at,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
    except Exception as e:
        logger.error(f"Erro ao criar conversação para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{conversation_id}", response_model=ConversationResponse, summary="Obter conversação", tags=["ai"])
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    """
    Obtém uma conversação específica do usuário.
    
    Retorna dados completos da conversação se o usuário
    for o proprietário.
    
    Args:
        conversation_id: ID único da conversação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        ConversationResponse: Dados da conversação
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Obtendo conversação {conversation_id} para usuário {current_user.id}")
        
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        logger.info(f"Conversação {conversation_id} obtida com sucesso para usuário {current_user.id}")
        
        # Return properly formatted response
        return ConversationResponse(
            id=str(conversation.id),
            user_id=str(conversation.user_id),
            agent_id=str(conversation.agent_id) if conversation.agent_id else None,
            workspace_id=str(conversation.workspace_id) if conversation.workspace_id else None,
            title=conversation.title or "",
            status=conversation.status or "active",
            message_count=conversation.message_count or 0,
            total_tokens_used=conversation.total_tokens_used or 0,
            context=conversation.context or {},
            settings=conversation.settings or {},
            last_message_at=conversation.last_message_at,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao obter conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"ID de conversação inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Erro interno ao obter conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{conversation_id}", summary="Deletar conversação", tags=["ai"])
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Remove uma conversação e todas suas mensagens.
    
    Deleta permanentemente a conversação e mensagens
    associadas se o usuário for o proprietário.
    
    Args:
        conversation_id: ID único da conversação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Deletando conversação {conversation_id} para usuário {current_user.id}")
        
        # Validate conversation_id
        if not conversation_id or len(conversation_id.strip()) == 0:
            logger.warning(f"ID de conversação vazio fornecido por usuário {current_user.id}")
            raise HTTPException(status_code=400, detail="ID da conversação é obrigatório")
        
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        # Deletar mensagens associadas em uma transação
        try:
            message_count = db.query(Message).filter(Message.conversation_id == conversation_id).count()
            db.query(Message).filter(Message.conversation_id == conversation_id).delete()

            # Deletar conversação
            conversation_title = conversation.title or "Sem título"
            db.delete(conversation)
            db.commit()

            logger.info(f"Conversação '{conversation_title}' (ID: {conversation_id}) e {message_count} mensagens deletadas com sucesso para usuário {current_user.id}")
            return {"message": "Conversação deletada com sucesso"}
            
        except Exception as delete_error:
            logger.error(f"Erro ao deletar dados da conversação {conversation_id}: {str(delete_error)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro ao deletar conversação")
            
    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao deletar conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"ID de conversação inválido: {str(e)}")
    except Exception as e:
        logger.error(f"Erro interno ao deletar conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{conversation_id}/messages", response_model=MessageListResponse, summary="Listar mensagens", tags=["ai"])
async def list_messages(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageListResponse:
    """
    Lista todas as mensagens de uma conversação.
    
    Retorna mensagens ordenadas cronologicamente
    com paginação eficiente.
    
    Args:
        conversation_id: ID único da conversação
        page: Número da página (1-based)
        size: Número de itens por página
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        MessageListResponse: Lista paginada de mensagens
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listando mensagens da conversação {conversation_id} para usuário {current_user.id} - página: {page}")
        
        # Validate conversation_id
        if not conversation_id or len(conversation_id.strip()) == 0:
            logger.warning(f"ID de conversação vazio fornecido por usuário {current_user.id}")
            raise HTTPException(status_code=400, detail="ID da conversação é obrigatório")
        
        # Verificar se conversação existe e pertence ao usuário
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        # Buscar mensagens com contagem total
        try:
            messages_query = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
            )
            
            total = messages_query.count()
            messages = messages_query.offset((page - 1) * size).limit(size).all()

            # Convert messages to proper response format with fallback values
            items = []
            for msg in messages:
                try:
                    message_data = {
                        "id": str(msg.id),
                        "conversation_id": str(msg.conversation_id),
                        "role": msg.role or "user",
                        "content": msg.content or "",
                        "attachments": msg.attachments if msg.attachments is not None else [],
                        "model_used": msg.model_used,
                        "model_provider": msg.model_provider,
                        "tokens_used": msg.tokens_used or 0,
                        "processing_time_ms": msg.processing_time_ms or 0,
                        "temperature": msg.temperature,
                        "max_tokens": msg.max_tokens,
                        "status": msg.status or "sent",
                        "error_message": msg.error_message,
                        "rating": msg.rating,
                        "feedback": msg.feedback,
                        "created_at": msg.created_at,
                        "updated_at": msg.updated_at,
                    }
                    items.append(message_data)
                except Exception as msg_error:
                    logger.warning(f"Erro ao converter mensagem {msg.id}: {str(msg_error)}")
                    # Skip problematic message but continue processing others
                    continue

            logger.info(f"Retornadas {len(items)} mensagens de {total} total da conversação {conversation_id}")
            
            return MessageListResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size if total > 0 else 1,
            )
            
        except Exception as query_error:
            logger.error(f"Erro na consulta de mensagens da conversação {conversation_id}: {str(query_error)}")
            raise HTTPException(status_code=500, detail="Erro ao buscar mensagens")
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Erro de validação ao listar mensagens da conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Parâmetros inválidos: {str(e)}")
    except Exception as e:
        logger.error(f"Erro interno ao listar mensagens da conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{conversation_id}/messages", response_model=MessageResponse, summary="Enviar mensagem", tags=["ai"])
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> MessageResponse:
    """
    Envia uma mensagem em uma conversação.
    
    Processa a mensagem do usuário e, se há um agent
    configurado, gera resposta automaticamente.
    
    Args:
        conversation_id: ID único da conversação
        message_data: Dados da mensagem a ser enviada
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        MessageResponse: Mensagem enviada
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 500 se erro interno do servidor
    """
    try:
        start_time = time.time()
        logger.info(f"Enviando mensagem na conversação {conversation_id} para usuário {current_user.id}")
        
        # Verificar se conversação existe e pertence ao usuário
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        # Criar mensagem do usuário
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message_data.content,
            attachments=message_data.attachments or [],
        )

        db.add(user_message)
        db.flush()  # Para obter o ID
        
        logger.info(f"Mensagem do usuário criada (ID: {user_message.id}) na conversação {conversation_id}")

        # Processar resposta do agent se configurado
        if conversation.agent_id:
            try:
                agent = db.query(Agent).filter(Agent.id == conversation.agent_id).first()
                if agent and agent.is_available():
                    logger.info(f"Processando resposta do agent {agent.id} para conversação {conversation_id}")
                    
                    # Buscar histórico de mensagens
                    past_messages = (
                        db.query(Message)
                        .filter(Message.conversation_id == conversation_id)
                        .order_by(Message.created_at.asc())
                        .all()
                    )

                    chat_history = [
                        {"role": msg.role, "content": msg.content} for msg in past_messages
                    ]
                    chat_history.append({"role": "user", "content": message_data.content})

                    # Obter configuração do LLM
                    llm_cfg = agent.get_llm_config()
                    
                    # Fazer chamada para LLM
                    llm_response = await llm_service.chat_completion(
                        messages=chat_history,
                        provider=llm_cfg["provider"],
                        model=llm_cfg["model"],
                        temperature=llm_cfg["temperature"],
                        max_tokens=llm_cfg["max_tokens"],
                    )

                    # Criar resposta do agent
                    processing_time = int((time.time() - start_time) * 1000)
                    agent_response = Message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=llm_response.content,
                        model_used=llm_cfg["model"],
                        model_provider=llm_cfg["provider"],
                        tokens_used=llm_response.usage.get("tokens", 0),
                        processing_time_ms=processing_time,
                    )
                    db.add(agent_response)
                    
                    # Atualizar estatísticas
                    conversation.total_tokens_used += agent_response.tokens_used
                    logger.info(f"Resposta do agent criada - tokens: {agent_response.tokens_used}, tempo: {processing_time}ms")
                else:
                    logger.warning(f"Agent {conversation.agent_id} não disponível para conversação {conversation_id}")
            except Exception as agent_error:
                logger.error(f"Erro ao processar resposta do agent: {str(agent_error)}")
                # Continuar mesmo se o agent falhar

        # Atualizar estatísticas da conversação
        conversation.message_count += 1 if not conversation.agent_id else 2
        conversation.updated_at = func.now()

        db.commit()
        db.refresh(user_message)

        logger.info(f"Mensagem processada com sucesso na conversação {conversation_id}")
        return {
            "id": str(user_message.id),
            "conversation_id": str(user_message.conversation_id),
            "role": user_message.role,
            "content": user_message.content,
            "attachments": user_message.attachments,
            "model_used": user_message.model_used,
            "model_provider": user_message.model_provider,
            "tokens_used": user_message.tokens_used,
            "processing_time_ms": user_message.processing_time_ms,
            "temperature": user_message.temperature,
            "max_tokens": user_message.max_tokens,
            "status": user_message.status,
            "error_message": user_message.error_message,
            "rating": user_message.rating,
            "feedback": user_message.feedback,
            "created_at": user_message.created_at,
            "updated_at": user_message.updated_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem na conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/{conversation_id}/title", summary="Atualizar título", tags=["ai"])
async def update_conversation_title(
    conversation_id: str,
    title: str = Query(..., description="Novo título da conversação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Atualiza o título de uma conversação.
    
    Permite personalizar o nome da conversação
    para melhor organização.
    
    Args:
        conversation_id: ID único da conversação
        title: Novo título para a conversação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 400 se título inválido
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Atualizando título da conversação {conversation_id} para '{title}' - usuário {current_user.id}")
        
        if not title or len(title.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título não pode estar vazio",
            )
        
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        old_title = conversation.title
        conversation.title = title.strip()
        db.commit()

        logger.info(f"Título da conversação {conversation_id} atualizado de '{old_title}' para '{title}'")
        return {"message": "Título atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar título da conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{conversation_id}/archive", summary="Arquivar conversação", tags=["ai"])
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Arquiva uma conversação para organização.
    
    Move a conversação para o estado arquivado,
    removendo-a da lista principal.
    
    Args:
        conversation_id: ID único da conversação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 400 se já arquivada
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Arquivando conversação {conversation_id} para usuário {current_user.id}")
        
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        if conversation.status == "archived":
            logger.warning(f"Conversação {conversation_id} já está arquivada")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversação já está arquivada",
            )

        conversation.status = "archived"
        db.commit()

        logger.info(f"Conversação '{conversation.title}' (ID: {conversation_id}) arquivada com sucesso")
        return {"message": "Conversação arquivada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao arquivar conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{conversation_id}/unarchive", summary="Desarquivar conversação", tags=["ai"])
async def unarchive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Desarquiva uma conversação arquivada.
    
    Retorna a conversação para o estado ativo,
    tornando-a visível na lista principal.
    
    Args:
        conversation_id: ID único da conversação
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Dict[str, str]: Mensagem de confirmação
        
    Raises:
        HTTPException: 404 se conversação não encontrada
        HTTPException: 403 se não for o proprietário
        HTTPException: 400 se não estiver arquivada
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Desarquivando conversação {conversation_id} para usuário {current_user.id}")
        
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            logger.warning(f"Conversação {conversation_id} não encontrada para usuário {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversação não encontrada",
            )

        if conversation.status != "archived":
            logger.warning(f"Conversação {conversation_id} não está arquivada")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversação não está arquivada",
            )

        conversation.status = "active"
        db.commit()

        logger.info(f"Conversação '{conversation.title}' (ID: {conversation_id}) desarquivada com sucesso")
        return {"message": "Conversação desarquivada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desarquivar conversação {conversation_id} para usuário {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

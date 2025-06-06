"""
Endpoints para gerenciamento de conversações
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.models.conversation import Conversation
from src.synapse.models.message import Message
from src.synapse.api.deps import get_current_user
from src.synapse.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    MessageListResponse
)

router = APIRouter()

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    agent_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar conversações do usuário"""
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    
    if agent_id:
        query = query.filter(Conversation.agent_id == agent_id)
    
    # Ordenar por última mensagem
    query = query.order_by(Conversation.last_message_at.desc().nullslast())
    
    # Paginação
    total = query.count()
    conversations = query.offset((page - 1) * size).limit(size).all()
    
    return ConversationListResponse(
        items=conversations,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova conversação"""
    conversation = Conversation(
        **conversation_data.dict(),
        user_id=current_user.id
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter conversação específica"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    return conversation

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar conversação"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    # Deletar mensagens associadas
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Deletar conversação
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversação deletada com sucesso"}

@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar mensagens da conversação"""
    # Verificar se conversação existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    # Buscar mensagens
    query = db.query(Message).filter(Message.conversation_id == conversation_id)
    query = query.order_by(Message.created_at.asc())
    
    # Paginação
    total = query.count()
    messages = query.offset((page - 1) * size).limit(size).all()
    
    return MessageListResponse(
        items=messages,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enviar mensagem na conversação"""
    # Verificar se conversação existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    # Criar mensagem do usuário
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content,
        attachments=message_data.attachments or []
    )
    
    db.add(user_message)
    db.flush()  # Para obter o ID
    
    # TODO: Processar mensagem com agente e gerar resposta
    # Por enquanto, criar resposta simples
    if conversation.agent_id:
        agent_response = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=f"Resposta do agente para: {message_data.content}",
            model_used="gpt-3.5-turbo",
            tokens_used=50,
            processing_time_ms=1000
        )
        db.add(agent_response)
    
    # Atualizar estatísticas da conversação
    conversation.message_count += 1 if not conversation.agent_id else 2
    conversation.last_message_at = func.now()
    
    db.commit()
    db.refresh(user_message)
    
    return user_message

@router.put("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar título da conversação"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    conversation.title = title
    db.commit()
    
    return {"message": "Título atualizado com sucesso"}

@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Arquivar conversação"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    conversation.status = "archived"
    db.commit()
    
    return {"message": "Conversação arquivada com sucesso"}

@router.post("/{conversation_id}/unarchive")
async def unarchive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desarquivar conversação"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversação não encontrada"
        )
    
    conversation.status = "active"
    db.commit()
    
    return {"message": "Conversação desarquivada com sucesso"}


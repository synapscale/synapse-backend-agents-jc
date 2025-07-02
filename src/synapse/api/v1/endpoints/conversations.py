"""
Conversations endpoints - Complete Implementation

This module handles conversation management, message handling, and related operations.
Supports creating conversations, sending messages, archiving, and conversation lifecycle management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, desc
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from uuid import UUID

from synapse.api.deps import get_current_active_user, get_db
from synapse.models.conversation import Conversation
from synapse.models.message import Message
from synapse.models.user import User
from synapse.models.agent import Agent
from synapse.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ConversationTitleUpdate,
    MessageCreate,
    MessageResponse,
    MessageListResponse
)
from fastapi import HTTPException

router = APIRouter()

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    search: Optional[str] = Query(None, description="Search in title or messages"),
    status: Optional[str] = Query(None, description="Filter by status (active, archived, deleted)"),
    agent_id: Optional[UUID] = Query(None, description="Filter by agent"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar conversas do usuário com filtros e paginação"""
    try:
        # Build base query
        query = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages)
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            # Search in conversation title or message content
            query = query.outerjoin(Message).filter(
                or_(
                    Conversation.title.ilike(search_term),
                    Message.content.ilike(search_term)
                )
            ).distinct()
        
        if status:
            query = query.filter(Conversation.status == status)
            
        if agent_id:
            query = query.filter(Conversation.agent_id == agent_id)
        
        # Order by last activity (most recent first)
        query = query.order_by(desc(Conversation.updated_at))
        
        # Pagination
        total = query.count()
        offset = (page - 1) * size
        conversations = query.offset(offset).limit(size).all()
        
        # Convert to response model
        response_conversations = []
        for conv in conversations:
            # Get latest message for preview
            latest_message = None
            message_count = 0
            if conv.messages:
                conv.messages.sort(key=lambda x: x.created_at, reverse=True)
                latest_message = conv.messages[0] if conv.messages else None
                message_count = len(conv.messages)
            
            conv_dict = {
                "id": conv.id,
                "user_id": conv.user_id,
                "agent_id": conv.agent_id,
                "workspace_id": conv.workspace_id,
                "tenant_id": conv.tenant_id,
                "title": conv.title,
                "status": conv.status,
                "message_count": conv.message_count,
                "total_tokens_used": conv.total_tokens_used,
                "agent_name": conv.agent.name if conv.agent else None,
                "latest_message": {
                    "id": latest_message.id,
                    "content": latest_message.content[:100] + "..." if len(latest_message.content) > 100 else latest_message.content,
                    "role": latest_message.role,
                    "created_at": latest_message.created_at
                } if latest_message else None,
                "last_message_at": conv.last_message_at,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "context": conv.context,
                "settings": conv.settings
            }
            response_conversations.append(ConversationResponse(**conv_dict))
        
        return response_conversations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao listar conversas",
            details=str(e)
        )

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Criar nova conversação"""
    try:
        # Verify agent exists and user has access
        if conversation_data.agent_id:
            agent = db.query(Agent).filter(
                and_(
                    Agent.id == conversation_data.agent_id,
                    or_(
                        Agent.user_id == current_user.id,  # User owns the agent
                        Agent.scope == "global",  # Global agent
                        and_(
                            Agent.scope == "workspace",
                            # TODO: Check workspace membership
                            Agent.workspace_id.in_(
                                # Get user's workspaces
                                db.query(Agent.workspace_id).filter(Agent.user_id == current_user.id)
                            )
                        )
                    ),
                    Agent.is_active == True
                )
            ).first()
            
            if not agent:
                raise HTTPException(
                    status_code=404,
                    message="Agente não encontrado ou sem acesso"
                )
        
        # Generate title if not provided
        title = conversation_data.title or f"Nova Conversa - {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"
        
        # Create conversation
        new_conversation = Conversation(
            title=title,
            user_id=current_user.id,
            agent_id=conversation_data.agent_id,
            workspace_id=conversation_data.workspace_id,
            tenant_id=current_user.tenant_id,  # Get from current user
            status="active",
            context=conversation_data.context or {},
            settings=conversation_data.settings or {}
        )
        
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        
        # Load agent relationship
        if new_conversation.agent_id:
            new_conversation.agent = db.query(Agent).filter(Agent.id == new_conversation.agent_id).first()
        
        # Convert to response
        conv_dict = {
            "id": new_conversation.id,
            "user_id": new_conversation.user_id,
            "agent_id": new_conversation.agent_id,
            "workspace_id": new_conversation.workspace_id,
            "tenant_id": new_conversation.tenant_id,
            "title": new_conversation.title,
            "status": new_conversation.status,
            "message_count": new_conversation.message_count,
            "total_tokens_used": new_conversation.total_tokens_used,
            "agent_name": new_conversation.agent.name if new_conversation.agent else None,
            "latest_message": None,
            "last_message_at": new_conversation.last_message_at,
            "created_at": new_conversation.created_at,
            "updated_at": new_conversation.updated_at,
            "context": new_conversation.context,
            "settings": new_conversation.settings
        }
        
        return ConversationResponse(**conv_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao criar conversação",
            details=str(e)
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter conversação específica"""
    try:
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages)
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        # Get latest message for preview
        latest_message = None
        message_count = len(conversation.messages) if conversation.messages else 0
        
        if conversation.messages:
            conversation.messages.sort(key=lambda x: x.created_at, reverse=True)
            latest_message = conversation.messages[0]
        
        # Convert to response
        conv_dict = {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "workspace_id": conversation.workspace_id,
            "tenant_id": conversation.tenant_id,
            "title": conversation.title,
            "status": conversation.status,
            "message_count": conversation.message_count,
            "total_tokens_used": conversation.total_tokens_used,
            "agent_name": conversation.agent.name if conversation.agent else None,
            "latest_message": {
                "id": latest_message.id,
                "content": latest_message.content,
                "role": latest_message.role,
                "created_at": latest_message.created_at
            } if latest_message else None,
            "last_message_at": conversation.last_message_at,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "context": conversation.context,
            "settings": conversation.settings
        }
        
        return ConversationResponse(**conv_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao buscar conversação",
            details=str(e)
        )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deletar conversação"""
    try:
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        # Delete all messages first
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversação deletada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao deletar conversação",
            details=str(e)
        )

# Messages endpoints
@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar mensagens da conversação"""
    try:
        # Verify conversation ownership
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        # Get messages with pagination
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        
        total = query.count()
        offset = (page - 1) * size
        messages = query.offset(offset).limit(size).all()
        
        # Convert to response
        response_messages = []
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "content": msg.content,
                "role": msg.role,
                "agent_id": None,  # Message model doesn't have agent_id
                "agent_name": None,  # Message model doesn't have agent relationship
                "metadata": msg.attachments or {},  # Use attachments as metadata
                "tokens_used": msg.tokens_used,
                "cost": 0.0,  # Message model doesn't have cost field
                "created_at": msg.created_at,
                "updated_at": msg.updated_at
            }
            response_messages.append(MessageResponse(**msg_dict))
        
        return response_messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao listar mensagens",
            details=str(e)
        )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enviar mensagem na conversação"""
    try:
        # Verify conversation ownership
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).options(selectinload(Conversation.agent)).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        # Note: Message model doesn't have agent_id field
        # Agent information is handled at conversation level
        
        # Create message
        new_message = Message(
            conversation_id=conversation_id,
            content=message_data.content,
            role=message_data.role,
            attachments=message_data.metadata or {},  # Use attachments field for metadata
            tokens_used=message_data.tokens_used or 0
            # Note: Message model doesn't have cost field
        )
        
        db.add(new_message)
        
        # Update conversation's updated_at
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(new_message)
        
        # Convert to response
        msg_dict = {
            "id": new_message.id,
            "conversation_id": new_message.conversation_id,
            "content": new_message.content,
            "role": new_message.role,
            "agent_id": conversation.agent_id,  # Get from conversation level
            "agent_name": conversation.agent.name if conversation.agent else None,  # Get from conversation
            "metadata": new_message.attachments or {},
            "tokens_used": new_message.tokens_used,
            "cost": 0.0,  # Message model doesn't have cost field
            "created_at": new_message.created_at,
            "updated_at": new_message.updated_at
        }
        
        return MessageResponse(**msg_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao enviar mensagem",
            details=str(e)
        )

# Conversation management endpoints
@router.put("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: UUID,
    title_data: ConversationTitleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar título da conversação"""
    try:
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages)
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        # Update title
        conversation.title = title_data.title
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conversation)
        
        # Get latest message for response
        latest_message = None
        message_count = len(conversation.messages) if conversation.messages else 0
        
        if conversation.messages:
            conversation.messages.sort(key=lambda x: x.created_at, reverse=True)
            latest_message = conversation.messages[0]
        
        # Convert to response
        conv_dict = {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "workspace_id": conversation.workspace_id,
            "tenant_id": conversation.tenant_id,
            "title": conversation.title,
            "status": conversation.status,
            "message_count": conversation.message_count,
            "total_tokens_used": conversation.total_tokens_used,
            "agent_name": conversation.agent.name if conversation.agent else None,
            "latest_message": {
                "id": latest_message.id,
                "content": latest_message.content[:100] + "..." if len(latest_message.content) > 100 else latest_message.content,
                "role": latest_message.role,
                "created_at": latest_message.created_at
            } if latest_message else None,
            "last_message_at": conversation.last_message_at,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "context": conversation.context,
            "settings": conversation.settings
        }
        
        return ConversationResponse(**conv_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao atualizar título",
            details=str(e)
        )

@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Arquivar conversação"""
    try:
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        conversation.status = "archived"
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Conversação arquivada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao arquivar conversação",
            details=str(e)
        )

@router.post("/{conversation_id}/unarchive")
async def unarchive_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Desarquivar conversação"""
    try:
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                message="Conversação não encontrada"
            )
        
        conversation.status = "active"
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Conversação desarquivada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao desarquivar conversação",
            details=str(e)
        )

"""
Endpoints para gerenciamento de agentes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.models.agent import Agent
from src.synapse.api.deps import get_current_user
from src.synapse.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse
)

router = APIRouter()

@router.get("/", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    agent_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar agentes do usuário"""
    query = db.query(Agent).filter(Agent.user_id == current_user.id)
    
    # Filtros
    if agent_type:
        query = query.filter(Agent.agent_type == agent_type)
    
    if search:
        query = query.filter(
            Agent.name.ilike(f"%{search}%") |
            Agent.description.ilike(f"%{search}%")
        )
    
    # Ordenar por atividade recente
    query = query.order_by(Agent.last_active_at.desc().nullslast())
    
    # Paginação
    total = query.count()
    agents = query.offset((page - 1) * size).limit(size).all()
    
    return AgentListResponse(
        items=agents,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo agente"""
    agent = Agent(
        **agent_data.dict(),
        user_id=current_user.id
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter agente específico"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar agente"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    # Atualizar campos
    for field, value in agent_data.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    return agent

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar agente"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    db.delete(agent)
    db.commit()
    
    return {"message": "Agente deletado com sucesso"}

@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ativar agente"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    agent.status = "active"
    db.commit()
    
    return {"message": "Agente ativado com sucesso"}

@router.post("/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar agente"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    agent.status = "inactive"
    db.commit()
    
    return {"message": "Agente desativado com sucesso"}

@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter estatísticas do agente"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    return {
        "agent_id": agent_id,
        "conversation_count": agent.conversation_count,
        "message_count": agent.message_count,
        "rating_average": agent.rating_average,
        "rating_count": agent.rating_count,
        "last_active_at": agent.last_active_at,
        "created_at": agent.created_at
    }

@router.post("/{agent_id}/duplicate", response_model=AgentResponse)
async def duplicate_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicar agente"""
    original = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agente não encontrado"
        )
    
    # Criar cópia
    duplicate = Agent(
        name=f"{original.name} (Cópia)",
        description=original.description,
        user_id=current_user.id,
        agent_type=original.agent_type,
        personality=original.personality,
        instructions=original.instructions,
        model_provider=original.model_provider,
        model_name=original.model_name,
        temperature=original.temperature,
        max_tokens=original.max_tokens,
        tools=original.tools,
        knowledge_base=original.knowledge_base,
        status="draft"
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate


"""
Endpoints de usuário (profile e preferences)
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user
from synapse.database import get_db
from synapse.models.user import User
from synapse.schemas.user import UserProfileResponse, UserProfileUpdate, UserPreferences
from synapse.schemas.response import (
    DataResponse, 
    wrap_data_response, 
    add_request_context
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter perfil do usuário autenticado"""
    profile_data = UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    response = wrap_data_response(
        data=profile_data.dict(),
        message="Perfil do usuário recuperado com sucesso"
    )
    return add_request_context(response, request)

@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Atualizar perfil do usuário autenticado"""
    try:
        if profile_data.full_name:
            current_user.full_name = profile_data.full_name
        if profile_data.username:
            # Verificar se username já existe
            existing = db.query(User).filter(
                User.username == profile_data.username,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Username já está em uso"
                )
            current_user.username = profile_data.username
        
        db.commit()
        db.refresh(current_user)
        
        updated_profile = UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
        response = wrap_data_response(
            data=updated_profile.dict(),
            message="Perfil do usuário atualizado com sucesso"
        )
        return add_request_context(response, request)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Obter preferências do usuário"""
    # Preferências padrão se não existir
    default_preferences = {
        "theme": "light",
        "language": "pt-BR",
        "notifications": {
            "email": True,
            "push": False,
            "desktop": True
        },
        "workspace": {
            "default_view": "grid",
            "auto_save": True,
            "show_tips": True
        }
    }
    
    # Aqui você pode implementar um sistema de preferências mais sofisticado
    # Por enquanto, retorna as preferências padrão
    response = wrap_data_response(
        data=default_preferences,
        message="Preferências do usuário recuperadas com sucesso"
    )
    return add_request_context(response, request)

@router.put("/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    preferences: Dict[str, Any],
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Atualizar preferências do usuário"""
    try:
        # Aqui você implementaria a lógica para salvar as preferências
        # Por enquanto, apenas retorna as preferências recebidas
        logger.info(f"Atualizando preferências do usuário {current_user.id}: {preferences}")
        
        response = wrap_data_response(
            data=preferences,
            message="Preferências do usuário atualizadas com sucesso"
        )
        return add_request_context(response, request)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

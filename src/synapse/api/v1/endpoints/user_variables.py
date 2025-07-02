"""
User Variables endpoints - Simplified Implementation

This module handles basic CRUD operations for user variables.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from synapse.api.deps import get_current_active_user, get_db
from synapse.models.user_variable import UserVariable
from synapse.models.user import User
from synapse.schemas.user_features import (
    UserVariableCreate,
    UserVariableUpdate,
    UserVariableResponse
)
# HTTPException already imported from fastapi

router = APIRouter()

# Temporary encryption functions until proper service is implemented
def encrypt_value(value: str) -> str:
    """Temporary encryption - implement proper encryption later"""
    # For now, just return the value as is
    # TODO: Implement proper encryption
    return value

def decrypt_value(value: str) -> str:
    """Temporary decryption - implement proper decryption later"""
    # For now, just return the value as is
    # TODO: Implement proper decryption
    return value

@router.get("/", response_model=List[UserVariableResponse])
async def list_user_variables(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in key or description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listar variáveis do usuário com filtros e paginação"""
    try:
        # Build query
        query = db.query(UserVariable).filter(
            UserVariable.user_id == current_user.id,
            UserVariable.is_active == True
        )
        
        # Apply filters
        if category:
            query = query.filter(UserVariable.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UserVariable.key.ilike(search_term),
                    UserVariable.description.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(UserVariable.is_active == is_active)
        
        # Pagination
        total = query.count()
        offset = (page - 1) * size
        variables = query.offset(offset).limit(size).all()
        
        # Convert to response model
        response_variables = []
        for var in variables:
            var_dict = {
                "id": var.id,
                "key": var.key,
                "value": decrypt_value(var.value) if var.is_encrypted else var.value,
                "user_id": var.user_id,
                "description": var.description,
                "category": var.category,
                "is_secret": var.is_secret,
                "is_encrypted": var.is_encrypted,
                "is_active": var.is_active,
                "tenant_id": var.tenant_id,
                "created_at": var.created_at,
                "updated_at": var.updated_at
            }
            response_variables.append(UserVariableResponse(**var_dict))
        
        return response_variables
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao listar variáveis do usuário",
            details=str(e)
        )

@router.post("/", response_model=UserVariableResponse)
async def create_user_variable(
    variable_data: UserVariableCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Criar nova variável do usuário"""
    try:
        # Check if key already exists for this user
        existing = db.query(UserVariable).filter(
            and_(
                UserVariable.user_id == current_user.id,
                UserVariable.key == variable_data.key,
                UserVariable.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                message="Chave já existe",
                details=f"A chave '{variable_data.key}' já existe para este usuário"
            )
        
        # Encrypt value if needed
        stored_value = variable_data.value
        if variable_data.is_encrypted:
            stored_value = encrypt_value(variable_data.value)
        
        # Create variable
        new_variable = UserVariable(
            user_id=current_user.id,
            key=variable_data.key,
            value=stored_value,
            description=variable_data.description,
            category=variable_data.category or "general",
            is_secret=variable_data.is_secret or False,
            is_encrypted=variable_data.is_encrypted or False,
            is_active=True,
            tenant_id=variable_data.tenant_id or current_user.tenant_id
        )
        
        db.add(new_variable)
        db.commit()
        db.refresh(new_variable)
        
        # Return response with decrypted value for display
        response_dict = {
            "id": new_variable.id,
            "key": new_variable.key,
            "value": variable_data.value,  # Return original unencrypted value
            "user_id": new_variable.user_id,
            "description": new_variable.description,
            "category": new_variable.category,
            "is_secret": new_variable.is_secret,
            "is_encrypted": new_variable.is_encrypted,
            "is_active": new_variable.is_active,
            "tenant_id": new_variable.tenant_id,
            "created_at": new_variable.created_at,
            "updated_at": new_variable.updated_at
        }
        
        return UserVariableResponse(**response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao criar variável",
            details=str(e)
        )

@router.get("/{variable_id}", response_model=UserVariableResponse)
async def get_user_variable(
    variable_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter variável específica do usuário"""
    try:
        variable = db.query(UserVariable).filter(
            and_(
                UserVariable.id == variable_id,
                UserVariable.user_id == current_user.id,
                UserVariable.is_active == True
            )
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=404,
                message="Variável não encontrada"
            )
        
        # Return with decrypted value
        response_dict = {
            "id": variable.id,
            "key": variable.key,
            "value": decrypt_value(variable.value) if variable.is_encrypted else variable.value,
            "user_id": variable.user_id,
            "description": variable.description,
            "category": variable.category,
            "is_secret": variable.is_secret,
            "is_encrypted": variable.is_encrypted,
            "is_active": variable.is_active,
            "tenant_id": variable.tenant_id,
            "created_at": variable.created_at,
            "updated_at": variable.updated_at
        }
        
        return UserVariableResponse(**response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao buscar variável",
            details=str(e)
        )

@router.put("/{variable_id}", response_model=UserVariableResponse)
async def update_user_variable(
    variable_id: UUID,
    variable_data: UserVariableUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar variável do usuário"""
    try:
        variable = db.query(UserVariable).filter(
            and_(
                UserVariable.id == variable_id,
                UserVariable.user_id == current_user.id,
                UserVariable.is_active == True
            )
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=404,
                message="Variável não encontrada"
            )
        
        # Update fields
        if variable_data.value is not None:
            if variable_data.is_encrypted or variable.is_encrypted:
                variable.value = encrypt_value(variable_data.value)
                variable.is_encrypted = True
            else:
                variable.value = variable_data.value
                variable.is_encrypted = False
        
        if variable_data.description is not None:
            variable.description = variable_data.description
            
        if variable_data.category is not None:
            variable.category = variable_data.category
            
        if variable_data.is_secret is not None:
            variable.is_secret = variable_data.is_secret
            
        if variable_data.is_encrypted is not None:
            variable.is_encrypted = variable_data.is_encrypted
            if variable_data.is_encrypted and variable_data.value:
                variable.value = encrypt_value(variable_data.value)
        
        variable.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(variable)
        
        # Return response with decrypted value
        response_dict = {
            "id": variable.id,
            "key": variable.key,
            "value": decrypt_value(variable.value) if variable.is_encrypted else variable.value,
            "user_id": variable.user_id,
            "description": variable.description,
            "category": variable.category,
            "is_secret": variable.is_secret,
            "is_encrypted": variable.is_encrypted,
            "is_active": variable.is_active,
            "tenant_id": variable.tenant_id,
            "created_at": variable.created_at,
            "updated_at": variable.updated_at
        }
        
        return UserVariableResponse(**response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao atualizar variável",
            details=str(e)
        )

@router.delete("/{variable_id}")
async def delete_user_variable(
    variable_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remover variável do usuário (soft delete)"""
    try:
        variable = db.query(UserVariable).filter(
            and_(
                UserVariable.id == variable_id,
                UserVariable.user_id == current_user.id,
                UserVariable.is_active == True
            )
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=404,
                message="Variável não encontrada"
            )
        
        # Soft delete
        variable.is_active = False
        variable.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Variável removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            message="Erro ao remover variável",
            details=str(e)
        )

@router.get("/key/{key}", response_model=UserVariableResponse)
async def get_user_variable_by_key(
    key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obter variável do usuário por chave"""
    try:
        variable = db.query(UserVariable).filter(
            and_(
                UserVariable.key == key,
                UserVariable.user_id == current_user.id,
                UserVariable.is_active == True
            )
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=404,
                message="Variável não encontrada"
            )
        
        # Return with decrypted value
        response_dict = {
            "id": variable.id,
            "key": variable.key,
            "value": decrypt_value(variable.value) if variable.is_encrypted else variable.value,
            "user_id": variable.user_id,
            "description": variable.description,
            "category": variable.category,
            "is_secret": variable.is_secret,
            "is_encrypted": variable.is_encrypted,
            "is_active": variable.is_active,
            "tenant_id": variable.tenant_id,
            "created_at": variable.created_at,
            "updated_at": variable.updated_at
        }
        
        return UserVariableResponse(**response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Erro ao buscar variável",
            details=str(e)
        )

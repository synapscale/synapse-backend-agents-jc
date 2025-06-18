"""
Endpoints da API para gerenciamento de variáveis do usuário
Criado por José - um desenvolvedor Full Stack
Sistema de variáveis personalizado para usuários
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile, status
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user, get_db
from synapse.models.user import User
from synapse.models.user_variable import UserVariable
from synapse.schemas.user_variable import (
    UserVariableCreate,
    UserVariableUpdate,
    UserVariableResponse,
    UserVariableWithValue,
    UserVariableList,
    UserVariableBulkCreate,
    UserVariableBulkUpdate,
    UserVariableImport,
    UserVariableExport,
    UserVariableStats,
    UserVariableValidation,
    UserVariableBulkValidation,
)
from synapse.services.variable_service import VariableService
from synapse.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=UserVariableList,
    summary="Listar variáveis do usuário",
    response_description="Lista de variáveis do usuário retornada com sucesso",
    tags=["user-variables"],
)
async def get_user_variables(
    skip: int = Query(0, ge=0, description="Número de registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros por página (paginação)"),
    search: str | None = Query(None, description="Buscar por chave ou descrição da variável"),
    is_active: bool | None = Query(None, description="Filtrar por status ativo/inativo"),
    category: str | None = Query(None, description="Filtrar por categoria da variável"),
    sort_by: str = Query("key", description="Campo para ordenação (ex: key, created_at, updated_at)"),
    sort_order: str = Query(
        "asc", pattern="^(asc|desc)$", description="Ordem de classificação: ascendente ou descendente"
    ),
    include_values: bool = Query(False, description="Incluir valores das variáveis na resposta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableList:
    """
    Lista todas as variáveis do usuário com paginação e filtros.
    """
    try:
        variables, total = VariableService.get_user_variables_paginated(
            db, current_user.id, skip, limit, search, is_active, category, sort_by, sort_order
        )

        return UserVariableList(
            variables=[
                UserVariableResponse(
                    id=v.id,
                    key=v.key,
                    value=v.get_decrypted_value() if include_values else None,
                    description=v.description,
                    category=v.category,
                    is_encrypted=v.is_encrypted,
                    is_active=v.is_active,
                    created_at=v.created_at,
                    updated_at=v.updated_at,
                )
                for v in variables
            ],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Erro ao listar variáveis do usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar variáveis"
        )


@router.get("/{variable_id}", response_model=UserVariableWithValue)
async def get_variable(
    variable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém uma variável específica do usuário por ID.
    """
    variable = VariableService.get_user_variable_by_id(db, current_user.id, variable_id)
    if not variable:
        raise HTTPException(status_code=404, detail="Variável não encontrada")
    
    return UserVariableWithValue(
        id=variable.id,
        key=variable.key,
        value=variable.get_decrypted_value(),
        description=variable.description,
        category=variable.category,
        is_encrypted=variable.is_encrypted,
        is_active=variable.is_active,
        created_at=variable.created_at,
        updated_at=variable.updated_at,
    )


@router.post(
    "/",
    response_model=UserVariableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova variável do usuário",
    response_description="Variável criada com sucesso",
    tags=["user-variables"],
)
async def create_variable(
    variable_data: UserVariableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableResponse:
    """
    Cria uma nova variável para o usuário.
    """
    try:
        variable = VariableService.create_user_variable(db, current_user.id, variable_data)
        return UserVariableResponse(
            id=variable.id,
            key=variable.key,
            description=variable.description,
            category=variable.category,
            is_encrypted=variable.is_encrypted,
            is_active=variable.is_active,
            created_at=variable.created_at,
            updated_at=variable.updated_at,
        )
    except Exception as e:
        logger.error(f"Erro ao criar variável para usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar variável"
        )


# ============================================================================
# NOVOS ENDPOINTS PARA API KEYS LLM USANDO USER_VARIABLES
# ============================================================================

@router.post("/api-keys/{provider}", response_model=dict, tags=["User API Keys"])
async def create_user_api_key(
    provider: str,
    request: UserVariableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Configura uma API key específica do usuário para um provedor LLM
    
    Usa a tabela user_variables existente com categoria 'api_keys'
    """
    try:
        from synapse.core.llm.user_variables_llm_service import user_variables_llm_service
        
        # Validar provedor
        valid_providers = ["openai", "anthropic", "google", "grok", "deepseek", "llama"]
        if provider.lower() not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provedor inválido. Valores aceitos: {', '.join(valid_providers)}"
            )
        
        # Criar/atualizar API key usando user_variables
        success = user_variables_llm_service.create_or_update_user_api_key(
            db=db,
            user_id=str(current_user.id),
            provider=provider.lower(),
            api_key=request.value
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao salvar API key")
        
        return {
            "message": f"API key {provider} configurada com sucesso",
            "provider": provider.lower(),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar API key: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/api-keys", response_model=List[dict], tags=["User API Keys"])
async def list_user_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista todas as API keys configuradas pelo usuário
    
    Retorna dados mascarados para segurança
    """
    try:
        from synapse.core.llm.user_variables_llm_service import user_variables_llm_service
        
        api_keys = user_variables_llm_service.list_user_api_keys(
            db=db,
            user_id=str(current_user.id)
        )
        
        return api_keys
        
    except Exception as e:
        logger.error(f"Erro ao listar API keys: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/api-keys/{provider}", response_model=dict, tags=["User API Keys"])
async def delete_user_api_key(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove uma API key específica do usuário
    """
    try:
        from synapse.core.llm.user_variables_llm_service import user_variables_llm_service
        
        success = user_variables_llm_service.delete_user_api_key(
            db=db,
            user_id=str(current_user.id),
            provider=provider.lower()
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"API key para {provider} não encontrada"
            )
        
        return {
            "message": f"API key {provider} removida com sucesso",
            "provider": provider.lower(),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover API key: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/api-keys/providers", response_model=List[dict], tags=["User API Keys"])
async def get_supported_providers():
    """
    Lista todos os provedores LLM suportados
    """
    providers = [
        {
            "name": "openai",
            "display_name": "OpenAI",
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "description": "OpenAI GPT models"
        },
        {
            "name": "anthropic", 
            "display_name": "Anthropic Claude",
            "models": ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"],
            "description": "Anthropic Claude models"
        },
        {
            "name": "google",
            "display_name": "Google Gemini", 
            "models": ["gemini-pro", "gemini-pro-vision"],
            "description": "Google Gemini models"
        },
        {
            "name": "grok",
            "display_name": "xAI Grok",
            "models": ["grok-beta"],
            "description": "xAI Grok models"
        },
        {
            "name": "deepseek",
            "display_name": "DeepSeek",
            "models": ["deepseek-chat", "deepseek-coder"],
            "description": "DeepSeek models"
        },
        {
            "name": "llama",
            "display_name": "Meta Llama",
            "models": ["llama-2-70b", "llama-2-13b"],
            "description": "Meta Llama models"
        }
    ]
    
    return providers 
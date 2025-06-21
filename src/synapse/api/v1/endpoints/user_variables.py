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


def mask_sensitive_value(value: str, key: str = "") -> str:
    """
    Retorna o valor completo sem mascaramento.
    Mascaramento foi removido conforme solicitado.
    
    Args:
        value: Valor a ser retornado
        key: Nome da chave (não usado mais)
        
    Returns:
        str: Valor completo sem mascaramento
    """
    return value if value else ""


def is_sensitive_key(key: str) -> bool:
    """
    Verifica se uma chave contém informações sensíveis.
    
    Args:
        key: Nome da chave
        
    Returns:
        bool: True se for uma chave sensível
    """
    sensitive_patterns = [
        "API_KEY", "SECRET", "PASSWORD", "TOKEN", "PRIVATE", 
        "CREDENTIAL", "AUTH", "CERT", "KEY", "PASS"
    ]
    
    key_upper = key.upper()
    return any(pattern in key_upper for pattern in sensitive_patterns)


@router.get(
    "/",
    response_model=UserVariableList,
    summary="Listar variáveis do usuário",
    response_description="Lista de variáveis do usuário retornada com sucesso",
    tags=["data"],
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
        # 🔍 DEBUG: Log de entrada
        logger.info(f"🔍 DEBUG: Endpoint chamado - include_values={include_values}, user={current_user.id}")
        
        variables, total = VariableService.get_variables(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active,
            category=category,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        logger.info(f"🔍 DEBUG: Encontradas {len(variables)} variáveis")

        # Verificar e migrar variáveis com problemas de criptografia (uma vez por sessão)
        migration_attempted = getattr(current_user, '_migration_attempted', False)
        if not migration_attempted:
            try:
                migration_stats = UserVariable.check_and_migrate_user_variables(current_user.id, db)
                if migration_stats["migrated"] > 0:
                    logger.info(f"🔄 Migração automática: {migration_stats['migrated']} variáveis migradas para o usuário {current_user.id}")
                    # Recarregar variáveis após migração
                    variables, total = VariableService.get_variables(
                        db=db,
                        user_id=current_user.id,
                        skip=skip,
                        limit=limit,
                        search=search,
                        is_active=is_active,
                        category=category,
                        sort_by=sort_by,
                        sort_order=sort_order,
                    )
                # Marcar que já tentamos migração nesta sessão
                current_user._migration_attempted = True
            except Exception as e:
                logger.warning(f"Erro na migração automática para usuário {current_user.id}: {e}")

        # Preparar lista de variáveis com valores mascarados
        variable_responses = []
        for v in variables:
            value_to_use = None
            
            try:
                decrypted_value = v.get_decrypted_value()
                
                if decrypted_value:
                    # Determinar como mostrar o valor baseado no include_values e sensibilidade
                    # Sempre mostrar valores completos - mascaramento removido
                    value_to_use = decrypted_value
                else:
                    # Se não conseguiu descriptografar mas tem valor bruto
                    if v.value:
                        # Fallback: mostrar que existe valor mas não consegue descriptografar
                        value_to_use = "****[criptografado]"
                        logger.warning(f"Variável {v.key} existe mas não pôde ser descriptografada. Chave de criptografia pode ter mudado.")
                    else:
                        value_to_use = None
                    
            except Exception as e:
                logger.warning(f"Erro ao descriptografar variável {v.key} do usuário {current_user.id}: {e}")
                # Fallback: se existe valor bruto, indicar que está criptografado
                if v.value:
                    value_to_use = "****[erro_descriptografia]"
                else:
                    value_to_use = "****erro"
            
            logger.info(f"🔍 DEBUG: {v.key} - valor final: {repr(value_to_use)}")
            
            # Criar resposta com o valor determinado
            var_response = UserVariableResponse(
                id=v.id,
                key=v.key,
                value=value_to_use,
                description=v.description,
                category=v.category,
                is_encrypted=v.is_encrypted,
                is_active=v.is_active,
                created_at=v.created_at,
                updated_at=v.updated_at,
            )
            
            logger.info(f"🔍 DEBUG: {v.key} - objeto criado com valor: {repr(var_response.value)}")
            
            variable_responses.append(var_response)

        # Obter categorias únicas
        categories = list(set(v.category for v in variables if v.category))
        
        result = UserVariableList(
            variables=variable_responses,
            total=total,
            categories=categories,
        )
        
        logger.info(f"🔍 DEBUG: Lista criada com {len(result.variables)} variáveis")
        for var in result.variables:
            logger.info(f"🔍 DEBUG: Lista final - {var.key}: {repr(var.value)}")
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar variáveis do usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar variáveis"
        )


@router.get("/debug/masking", response_model=dict, tags=["data"])
async def test_masking(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint de teste para verificar o mascaramento de valores
    """
    try:
        from synapse.models.user_variable import UserVariable
        
        variables = db.query(UserVariable).filter(UserVariable.user_id == current_user.id).all()
        
        result = []
        for var in variables:
            decrypted_value = var.get_decrypted_value()
            is_sensitive = is_sensitive_key(var.key) or var.is_encrypted
            # Mascaramento removido - sempre mostrar valor completo
            displayed_value = decrypted_value
            
            result.append({
                "key": var.key,
                "original_value": decrypted_value,
                "is_sensitive": is_sensitive,
                "displayed_value": displayed_value,
                "masking_disabled": True
            })
        
        return {"test_results": result}
    except Exception as e:
        return {"error": str(e)}


@router.get("/{variable_id}", response_model=UserVariableWithValue, tags=["data"])
async def get_variable(
    variable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém uma variável específica do usuário por ID.
    """
    variable = VariableService.get_variable_by_id(db, variable_id, current_user.id)
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
    tags=["data"],
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
        variable = VariableService.create_variable(db, current_user.id, variable_data)
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

@router.post("/api-keys/{provider}", response_model=dict, tags=["data"])
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
            user_id=current_user.id,  # Manter como UUID
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


@router.get("/api-keys", response_model=List[dict], tags=["data"])
async def list_user_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista todas as API keys configuradas pelo usuário
    
    Retorna valores completos sem mascaramento
    """
    try:
        from synapse.core.llm.user_variables_llm_service import user_variables_llm_service
        
        api_keys = user_variables_llm_service.list_user_api_keys(
            db=db,
            user_id=current_user.id  # Manter como UUID
        )
        
        return api_keys
        
    except Exception as e:
        logger.error(f"Erro ao listar API keys: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/api-keys/{provider}", response_model=dict, tags=["data"])
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
            user_id=current_user.id,  # Manter como UUID
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


@router.get("/api-keys/providers", response_model=List[dict], tags=["data"])
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
"""
Endpoints para gerenciamento de variáveis do usuário
Criado por José - um desenvolvedor Full Stack
API REST completa para sistema de variáveis personalizado
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from synapse.database import get_db
from synapse.api.deps import get_current_user
from synapse.models.user import User
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
# UserAPIKey removido - usando user_variables para API keys
# encryption_service removido - usando UserVariable.encrypt_value/decrypt_value
from synapse.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


# Schemas
class APIKeyCreate(BaseModel):
    """Schema para criar/atualizar uma API key"""
    provider_name: str = Field(..., description="Nome do provedor (openai, anthropic, google, etc.)")
    api_key: str = Field(..., description="Chave da API")

    class Config:
        json_schema_extra = {
            "example": {
                "provider_name": "openai",
                "api_key": "sk-your_openai_api_key_here"
            }
        }


class APIKeyResponse(BaseModel):
    """Schema para resposta de API key (sem expor a chave real)"""
    id: str
    provider_name: str
    is_active: str
    masked_key: str  # Apenas os últimos 4 caracteres
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "provider_name": "openai",
                "is_active": "true",
                "masked_key": "****xxxx1234",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class APIKeyUpdate(BaseModel):
    """Schema para atualizar uma API key"""
    api_key: Optional[str] = None
    is_active: Optional[str] = None


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
    Lista todas as variáveis do usuário autenticado, com filtros, busca e paginação.

    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Quantos registros retornar (máximo 500)
    - **search**: Termo para buscar por chave ou descrição
    - **is_active**: Filtrar por status ativo/inativo
    - **category**: Filtrar por categoria da variável
    - **sort_by**: Campo para ordenação
    - **sort_order**: Ordem de classificação (asc/desc)
    - **include_values**: Se deve incluir os valores das variáveis na resposta

    Exemplo de resposta:
    ```json
    {
      "variables": [
        {
          "id": 1,
          "key": "API_KEY",
          "description": "Chave da API",
          "is_active": true,
          "is_sensitive": true,
          ...
        }
      ],
      "total": 1,
      "categories": ["CONFIG", "SECRET"]
    }
    ```
    """
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
    # Converter para response models
    if include_values:
        variable_responses = [
            UserVariableWithValue(
                **var.to_dict(include_value=True),
                is_sensitive=var.is_sensitive(),
            )
            for var in variables
        ]
    else:
        variable_responses = [
            UserVariableResponse(
                **var.to_dict(include_value=False),
                is_sensitive=var.is_sensitive(),
            )
            for var in variables
        ]
    # Obter categorias distintas
    categories = list({v.category for v in variables if v.category})
    # Logging de auditoria
    if search or is_active is not None:
        logger.info(f"Usuário {current_user.id} buscou variáveis com filtros: search={search}, is_active={is_active}")
    return UserVariableList(
        variables=variable_responses,
        total=total,
        categories=categories,
    )


@router.get("/{variable_id}", response_model=UserVariableWithValue)
async def get_variable(
    variable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém uma variável específica pelo ID
    """
    variable = VariableService.get_variable_by_id(db, variable_id, current_user.id)

    return UserVariableWithValue(
        **variable.to_dict(include_value=True),
        is_sensitive=variable.is_sensitive(),
    )


@router.get(
    "/key/{key}",
    response_model=UserVariableWithValue,
    summary="Obter variável do usuário por chave",
    response_description="Variável retornada com sucesso",
    tags=["user-variables"],
)
async def get_variable_by_key(
    key: str = Path(..., description="Chave da variável a ser consultada"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableWithValue:
    """
    Obtém uma variável específica do usuário autenticado pela chave.

    - **key**: Chave da variável

    Exemplo de resposta:
    ```json
    {
      "id": 1,
      "key": "API_KEY",
      "description": "Chave da API",
      "is_active": true,
      "is_sensitive": true,
      ...
    }
    ```
    """
    variable = VariableService.get_variable_by_key(db, key, current_user.id)
    if not variable:
        logger.info(f"Usuário {current_user.id} tentou acessar variável inexistente por chave: {key}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variável com chave '{key}' não encontrada",
        )
    return UserVariableWithValue(
        **variable.to_dict(include_value=True),
        is_sensitive=variable.is_sensitive(),
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
    Cria uma nova variável para o usuário autenticado.

    Corpo de requisição:
    ```json
    {
      "key": "API_KEY",
      "value": "123456",
      "description": "Chave da API",
      "is_active": true
    }
    ```

    Exemplo de resposta:
    ```json
    {
      "id": 1,
      "key": "API_KEY",
      "description": "Chave da API",
      "is_active": true,
      "is_sensitive": true,
      ...
    }
    ```
    """
    variable = VariableService.create_variable(db, current_user.id, variable_data)
    logger.info(f"Usuário {current_user.id} criou variável: {variable_data.key}")
    return UserVariableResponse(
        **variable.to_dict(include_value=False),
        is_sensitive=variable.is_sensitive(),
    )


@router.put(
    "/{variable_id}",
    response_model=UserVariableResponse,
    summary="Atualizar variável do usuário",
    response_description="Variável atualizada com sucesso",
    tags=["user-variables"],
)
async def update_variable(
    variable_id: int = Path(..., description="ID da variável a ser atualizada"),
    variable_data: UserVariableUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableResponse:
    """
    Atualiza uma variável existente do usuário autenticado.

    - **variable_id**: ID da variável

    Corpo de requisição:
    ```json
    {
      "value": "novo_valor",
      "description": "Nova descrição",
      "is_active": false
    }
    ```

    Exemplo de resposta:
    ```json
    {
      "id": 1,
      "key": "API_KEY",
      "description": "Nova descrição",
      "is_active": false,
      "is_sensitive": true,
      ...
    }
    ```
    """
    variable = VariableService.update_variable(
        db, variable_id, current_user.id, variable_data
    )
    if not variable:
        logger.info(f"Usuário {current_user.id} tentou atualizar variável inexistente: {variable_id}")
        raise HTTPException(status_code=404, detail="Variável não encontrada")
    logger.info(f"Usuário {current_user.id} atualizou variável: {variable_id}")
    return UserVariableResponse(
        **variable.to_dict(include_value=False),
        is_sensitive=variable.is_sensitive(),
    )


@router.delete(
    "/{variable_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover variável do usuário",
    response_description="Variável removida com sucesso",
    tags=["user-variables"],
)
async def delete_variable(
    variable_id: int = Path(..., description="ID da variável a ser removida"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove uma variável do usuário autenticado pelo ID.

    - **variable_id**: ID da variável
    """
    VariableService.delete_variable(db, variable_id, current_user.id)
    logger.info(f"Usuário {current_user.id} removeu variável: {variable_id}")


@router.post(
    "/bulk",
    response_model=list[UserVariableResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Criar múltiplas variáveis em lote",
    response_description="Variáveis criadas em lote com sucesso",
    tags=["user-variables"],
)
async def bulk_create_variables(
    variables_data: UserVariableBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserVariableResponse]:
    """
    Cria múltiplas variáveis para o usuário autenticado em uma única requisição.
    """
    variables = VariableService.bulk_create_variables(
        db,
        current_user.id,
        variables_data.variables,
    )
    logger.info(f"Usuário {current_user.id} criou {len(variables)} variáveis em lote.")
    return [
        UserVariableResponse(
            **var.to_dict(include_value=False),
            is_sensitive=var.is_sensitive(),
        )
        for var in variables
    ]


@router.put(
    "/bulk",
    response_model=dict[int, UserVariableResponse],
    summary="Atualizar múltiplas variáveis em lote",
    response_description="Variáveis atualizadas em lote com sucesso",
    tags=["user-variables"],
)
async def bulk_update_variables(
    updates_data: UserVariableBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[int, UserVariableResponse]:
    """
    Atualiza múltiplas variáveis do usuário autenticado em uma única requisição.
    """
    updated = VariableService.bulk_update_variables(
        db, current_user.id, updates_data.updates
    )
    logger.info(f"Usuário {current_user.id} atualizou {len(updated)} variáveis em lote.")
    return {
        var.id: UserVariableResponse(
            **var.to_dict(include_value=False),
            is_sensitive=var.is_sensitive(),
        )
        for var in updated
    }


@router.delete(
    "/bulk",
    response_model=dict[str, int],
    summary="Remover múltiplas variáveis em lote",
    response_description="Variáveis removidas em lote com sucesso",
    tags=["user-variables"],
)
async def bulk_delete_variables(
    variable_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    """
    Remove múltiplas variáveis do usuário autenticado em uma única requisição.
    """
    count = VariableService.bulk_delete_variables(db, current_user.id, variable_ids)
    logger.info(f"Usuário {current_user.id} removeu {count} variáveis em lote.")
    return {"removed": count}


@router.post(
    "/import",
    response_model=Dict[str, Any],
    summary="Importar variáveis via JSON",
    response_description="Variáveis importadas com sucesso",
    tags=["user-variables"],
)
async def import_variables(
    import_data: UserVariableImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Importa variáveis do usuário autenticado a partir de um JSON.
    """
    result = VariableService.import_variables(db, current_user.id, import_data)
    logger.info(f"Usuário {current_user.id} importou variáveis via JSON.")
    return result


@router.post(
    "/import/file",
    response_model=Dict[str, Any],
    summary="Importar variáveis via arquivo .env",
    response_description="Variáveis importadas de arquivo com sucesso",
    tags=["user-variables"],
)
async def import_variables_from_file(
    file: UploadFile = File(..., description="Arquivo .env para importar"),
    overwrite_existing: bool = Query(
        False, description="Sobrescrever variáveis existentes"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Importa variáveis do usuário autenticado a partir de um arquivo .env.
    """
    result = VariableService.import_variables_from_file(
        db, current_user.id, file, overwrite_existing
    )
    logger.info(f"Usuário {current_user.id} importou variáveis via arquivo .env.")
    return result


@router.post(
    "/export",
    response_model=Dict[str, Any],
    summary="Exportar variáveis do usuário",
    response_description="Variáveis exportadas com sucesso",
    tags=["user-variables"],
)
async def export_variables(
    export_data: UserVariableExport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Exporta variáveis do usuário autenticado para JSON ou .env.
    """
    result = VariableService.export_variables(db, current_user.id, export_data)
    logger.info(f"Usuário {current_user.id} exportou variáveis.")
    return result


@router.get(
    "/stats/summary",
    response_model=UserVariableStats,
    summary="Obter estatísticas das variáveis do usuário",
    response_description="Estatísticas retornadas com sucesso",
    tags=["user-variables"],
)
async def get_variables_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableStats:
    """
    Obtém estatísticas das variáveis do usuário autenticado.
    """
    stats = VariableService.get_variables_stats(db, current_user.id)
    return stats


@router.post(
    "/validate",
    response_model=UserVariableValidation,
    summary="Validar chave de variável",
    response_description="Validação de chave realizada com sucesso",
    tags=["user-variables"],
)
async def validate_variable_key(
    key: str = Query(..., description="Chave da variável para validar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableValidation:
    """
    Valida se a chave de variável é válida e disponível para o usuário autenticado.
    """
    return VariableService.validate_variable_key(db, current_user.id, key)


@router.post(
    "/validate/bulk",
    response_model=UserVariableBulkValidation,
    summary="Validar múltiplas chaves de variáveis",
    response_description="Validação em lote realizada com sucesso",
    tags=["user-variables"],
)
async def validate_variable_keys_bulk(
    keys: list[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserVariableBulkValidation:
    """
    Valida múltiplas chaves de variáveis para o usuário autenticado.
    """
    return VariableService.validate_variable_keys_bulk(db, current_user.id, keys)


@router.get(
    "/env/dict",
    response_model=dict[str, str],
    summary="Obter variáveis do usuário como dicionário",
    response_description="Variáveis retornadas como dicionário",
    tags=["user-variables"],
)
async def get_env_dict(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Retorna todas as variáveis do usuário autenticado como um dicionário.
    """
    return VariableService.get_env_dict(db, current_user.id)


@router.get(
    "/env/string",
    response_model=dict[str, str],
    summary="Obter variáveis do usuário como string .env",
    response_description="Variáveis retornadas como string .env",
    tags=["user-variables"],
)
async def get_env_string(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Retorna todas as variáveis do usuário autenticado como uma string no formato .env.
    """
    return VariableService.get_env_string(db, current_user.id)


# Endpoints para uso interno (workflows)
@router.get(
    "/internal/env-dict/{user_id}",
    response_model=dict[str, str],
    include_in_schema=False,
)
async def get_user_env_dict_internal(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Endpoint interno para obter variáveis de um usuário específico
    Usado pelo sistema de execução de workflows
    """
    return VariableService.get_user_env_dict(db, user_id)


@router.get("/api-keys", response_model=List[APIKeyResponse], summary="Listar API keys do usuário")
async def list_user_api_keys(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[APIKeyResponse]:
    """
    Lista todas as API keys configuradas pelo usuário
    """
    try:
        api_keys = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == current_user.id
        ).all()
        
        result = []
        for key in api_keys:
            # Descriptografar apenas para mascarar
            try:
                decrypted_key = encryption_service.decrypt_api_key(key.encrypted_api_key)
                masked_key = f"****{decrypted_key[-4:] if len(decrypted_key) >= 4 else '****'}"
            except:
                masked_key = "****erro"
            
            result.append(APIKeyResponse(
                id=str(key.id),
                provider_name=key.provider_name,
                is_active=key.is_active,
                masked_key=masked_key,
                created_at=key.created_at.isoformat(),
                updated_at=key.updated_at.isoformat()
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao listar API keys do usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar API keys"
        )


@router.post("/api-keys", response_model=APIKeyResponse, summary="Adicionar/Atualizar API key")
async def create_or_update_api_key(
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> APIKeyResponse:
    """
    Adiciona ou atualiza uma API key para o usuário
    """
    try:
        # Validar formato da API key
        if not encryption_service.validate_api_key_format(
            api_key_data.provider_name, 
            api_key_data.api_key
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato inválido de API key para o provedor {api_key_data.provider_name}"
            )
        
        # Verificar se já existe uma chave para este provedor
        existing_key = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == api_key_data.provider_name
        ).first()
        
        # Criptografar a nova chave
        encrypted_key = encryption_service.encrypt_api_key(api_key_data.api_key)
        
        if existing_key:
            # Atualizar chave existente
            existing_key.encrypted_api_key = encrypted_key
            db.commit()
            db.refresh(existing_key)
            user_api_key = existing_key
        else:
            # Criar nova chave
            user_api_key = UserAPIKey(
                user_id=current_user.id,
                provider_name=api_key_data.provider_name,
                encrypted_api_key=encrypted_key,
                is_active="true"
            )
            db.add(user_api_key)
            db.commit()
            db.refresh(user_api_key)
        
        # Mascarar a chave para resposta
        masked_key = f"****{api_key_data.api_key[-4:] if len(api_key_data.api_key) >= 4 else '****'}"
        
        logger.info(f"API key {api_key_data.provider_name} configurada para usuário {current_user.id}")
        
        return APIKeyResponse(
            id=str(user_api_key.id),
            provider_name=user_api_key.provider_name,
            is_active=user_api_key.is_active,
            masked_key=masked_key,
            created_at=user_api_key.created_at.isoformat(),
            updated_at=user_api_key.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar API key para usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao salvar API key"
        )


@router.delete("/api-keys/{provider_name}", summary="Remover API key")
async def delete_api_key(
    provider_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Remove uma API key do usuário
    """
    try:
        api_key = db.query(UserAPIKey).filter(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider_name == provider_name
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key para {provider_name} não encontrada"
            )
        
        db.delete(api_key)
        db.commit()
        
        logger.info(f"API key {provider_name} removida para usuário {current_user.id}")
        
        return {"message": f"API key para {provider_name} removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao remover API key para usuário {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao remover API key"
        )


@router.get("/supported-providers", summary="Listar provedores suportados")
async def get_supported_providers() -> Dict[str, Any]:
    """
    Lista todos os provedores LLM suportados
    """
    providers = [
        {
            "id": "openai",
            "name": "OpenAI",
            "description": "GPT-4, GPT-3.5-turbo e outros modelos OpenAI",
            "key_format": "sk-...",
            "website": "https://platform.openai.com/api-keys"
        },
        {
            "id": "anthropic",
            "name": "Anthropic Claude",
            "description": "Claude 3 Opus, Sonnet, Haiku",
            "key_format": "sk-ant-...",
            "website": "https://console.anthropic.com/"
        },
        {
            "id": "google",
            "name": "Google Gemini",
            "description": "Gemini 1.5 Pro, Flash e outros modelos Google",
            "key_format": "AIza...",
            "website": "https://aistudio.google.com/app/apikey"
        },
        {
            "id": "grok",
            "name": "xAI Grok",
            "description": "Modelos Grok da xAI",
            "key_format": "xai-...",
            "website": "https://console.x.ai/"
        },
        {
            "id": "deepseek",
            "name": "DeepSeek",
            "description": "DeepSeek Chat e Coder",
            "key_format": "sk-...",
            "website": "https://platform.deepseek.com/"
        },
        {
            "id": "llama",
            "name": "Meta Llama",
            "description": "Llama 3 e Llama 2",
            "key_format": "meta-...",
            "website": "https://llama.meta.com/"
        }
    ]
    
    return {
        "providers": providers,
        "count": len(providers)
    }


# Adicionar novos endpoints para API keys LLM
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
    
    Valores das chaves são mascarados por segurança
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
            raise HTTPException(status_code=404, detail="API key não encontrada")
        
        return {
            "message": f"API key {provider} removida com sucesso",
            "provider": provider.lower(),
            "status": "deleted"
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

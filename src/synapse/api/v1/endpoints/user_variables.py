"""
Endpoints para gerenciamento de variáveis do usuário
Criado por José - um desenvolvedor Full Stack
API REST completa para sistema de variáveis personalizado
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.orm import Session

from src.synapse.database import get_db
from src.synapse.api.deps import get_current_user
from src.synapse.models.user import User
from src.synapse.schemas.user_variable import (
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
    UserVariableBulkValidation
)
from src.synapse.services.variable_service import VariableService
from src.synapse.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/variables", tags=["User Variables"])

@router.get("/", response_model=UserVariableList)
async def get_user_variables(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por chave ou descrição"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    sort_by: str = Query("key", description="Campo para ordenação"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Ordem de classificação"),
    include_values: bool = Query(False, description="Incluir valores das variáveis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as variáveis do usuário com filtros e paginação
    """
    variables, total = VariableService.get_variables(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Converter para response models
    if include_values:
        variable_responses = [
            UserVariableWithValue(
                **var.to_dict(include_value=True),
                is_sensitive=var.is_sensitive()
            ) for var in variables
        ]
    else:
        variable_responses = [
            UserVariableResponse(
                **var.to_dict(include_value=False),
                is_sensitive=var.is_sensitive()
            ) for var in variables
        ]
    
    # Obter categorias disponíveis
    categories = VariableService.get_available_categories(db, current_user.id)
    
    return UserVariableList(
        variables=variable_responses,
        total=total,
        categories=categories
    )

@router.get("/{variable_id}", response_model=UserVariableWithValue)
async def get_variable(
    variable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma variável específica pelo ID
    """
    variable = VariableService.get_variable_by_id(db, variable_id, current_user.id)
    
    return UserVariableWithValue(
        **variable.to_dict(include_value=True),
        is_sensitive=variable.is_sensitive()
    )

@router.get("/key/{key}", response_model=UserVariableWithValue)
async def get_variable_by_key(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma variável específica pela chave
    """
    variable = VariableService.get_variable_by_key(db, key, current_user.id)
    
    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variável com chave '{key}' não encontrada"
        )
    
    return UserVariableWithValue(
        **variable.to_dict(include_value=True),
        is_sensitive=variable.is_sensitive()
    )

@router.post("/", response_model=UserVariableResponse, status_code=status.HTTP_201_CREATED)
async def create_variable(
    variable_data: UserVariableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova variável para o usuário
    """
    variable = VariableService.create_variable(db, current_user.id, variable_data)
    
    return UserVariableResponse(
        **variable.to_dict(include_value=False),
        is_sensitive=variable.is_sensitive()
    )

@router.put("/{variable_id}", response_model=UserVariableResponse)
async def update_variable(
    variable_id: int,
    variable_data: UserVariableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma variável existente
    """
    variable = VariableService.update_variable(db, variable_id, current_user.id, variable_data)
    
    return UserVariableResponse(
        **variable.to_dict(include_value=False),
        is_sensitive=variable.is_sensitive()
    )

@router.delete("/{variable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variable(
    variable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove uma variável do usuário
    """
    VariableService.delete_variable(db, variable_id, current_user.id)

@router.post("/bulk", response_model=List[UserVariableResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_variables(
    variables_data: UserVariableBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria múltiplas variáveis em lote
    """
    variables = VariableService.bulk_create_variables(
        db, current_user.id, variables_data.variables
    )
    
    return [
        UserVariableResponse(
            **var.to_dict(include_value=False),
            is_sensitive=var.is_sensitive()
        ) for var in variables
    ]

@router.put("/bulk", response_model=Dict[int, UserVariableResponse])
async def bulk_update_variables(
    updates_data: UserVariableBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza múltiplas variáveis em lote
    """
    variables = VariableService.bulk_update_variables(
        db, current_user.id, updates_data.updates
    )
    
    return {
        var_id: UserVariableResponse(
            **var.to_dict(include_value=False),
            is_sensitive=var.is_sensitive()
        ) for var_id, var in variables.items()
    }

@router.delete("/bulk", response_model=Dict[str, int])
async def bulk_delete_variables(
    variable_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove múltiplas variáveis em lote
    """
    deleted_count = VariableService.bulk_delete_variables(
        db, current_user.id, variable_ids
    )
    
    return {"deleted_count": deleted_count}

@router.post("/import", response_model=Dict[str, Any])
async def import_variables(
    import_data: UserVariableImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importa variáveis de um arquivo .env
    """
    result = VariableService.import_from_env(db, current_user.id, import_data)
    return result

@router.post("/import/file", response_model=Dict[str, Any])
async def import_variables_from_file(
    file: UploadFile = File(..., description="Arquivo .env para importar"),
    overwrite_existing: bool = Query(False, description="Sobrescrever variáveis existentes"),
    default_category: Optional[str] = Query("CONFIG", description="Categoria padrão"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importa variáveis de um arquivo .env enviado
    """
    # Verificar tipo do arquivo
    if not file.filename.endswith('.env'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ter extensão .env"
        )
    
    # Ler conteúdo do arquivo
    content = await file.read()
    env_content = content.decode('utf-8')
    
    # Criar objeto de importação
    import_data = UserVariableImport(
        env_content=env_content,
        overwrite_existing=overwrite_existing,
        default_category=default_category
    )
    
    result = VariableService.import_from_env(db, current_user.id, import_data)
    return result

@router.post("/export", response_model=Dict[str, Any])
async def export_variables(
    export_data: UserVariableExport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exporta variáveis do usuário em diferentes formatos
    """
    result = VariableService.export_variables(db, current_user.id, export_data)
    return result

@router.get("/stats/summary", response_model=UserVariableStats)
async def get_variables_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém estatísticas das variáveis do usuário
    """
    return VariableService.get_stats(db, current_user.id)

@router.post("/validate", response_model=UserVariableValidation)
async def validate_variable_key(
    key: str = Query(..., description="Chave da variável para validar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Valida uma chave de variável
    """
    return VariableService.validate_variable(key)

@router.post("/validate/bulk", response_model=UserVariableBulkValidation)
async def validate_variable_keys_bulk(
    keys: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Valida múltiplas chaves de variáveis
    """
    if len(keys) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 100 chaves por validação em lote"
        )
    
    validations = []
    summary = {"valid": 0, "invalid": 0, "warnings": 0}
    
    for key in keys:
        validation = VariableService.validate_variable(key)
        validations.append(validation)
        
        if validation.is_valid:
            summary["valid"] += 1
        else:
            summary["invalid"] += 1
        
        if validation.warnings:
            summary["warnings"] += 1
    
    return UserVariableBulkValidation(
        validations=validations,
        summary=summary
    )

@router.get("/categories/list", response_model=List[str])
async def get_available_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as categorias usadas pelo usuário
    """
    return VariableService.get_available_categories(db, current_user.id)

@router.get("/env/dict", response_model=Dict[str, str])
async def get_env_dict(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todas as variáveis ativas como dicionário
    Usado para injetar em execuções de workflows
    """
    return VariableService.get_user_env_dict(db, current_user.id)

@router.get("/env/string", response_model=Dict[str, str])
async def get_env_string(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todas as variáveis ativas como string .env
    """
    env_string = VariableService.get_user_env_string(db, current_user.id)
    return {"env_content": env_string}

# Endpoints para uso interno (workflows)
@router.get("/internal/env-dict/{user_id}", response_model=Dict[str, str], include_in_schema=False)
async def get_user_env_dict_internal(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint interno para obter variáveis de um usuário específico
    Usado pelo sistema de execução de workflows
    """
    return VariableService.get_user_env_dict(db, user_id)

@router.get("/internal/categories", response_model=List[str], include_in_schema=False)
async def get_all_categories_internal(
    db: Session = Depends(get_db)
):
    """
    Endpoint interno para obter todas as categorias do sistema
    """
    from ..models.user_variable import UserVariable
    
    categories = db.query(UserVariable.category).filter(
        UserVariable.category.isnot(None)
    ).distinct().all()
    
    return [c[0] for c in categories if c[0]]


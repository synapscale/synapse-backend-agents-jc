"""
Schemas para NodeExecutionStatus - status de execução de nós
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID


class NodeExecutionStatusBase(BaseModel):
    """Schema base para NodeExecutionStatus"""
    
    # Identificação
    name: str = Field(..., min_length=1, max_length=100, description="Nome único do status")
    display_name: str = Field(..., min_length=1, max_length=255, description="Nome para exibição")
    description: Optional[str] = Field(None, description="Descrição do status")
    
    # Configuração
    color: Optional[str] = Field(None, max_length=7, description="Cor em formato hex")
    is_final: bool = Field(False, description="Status final de execução")
    is_error: bool = Field(False, description="Indica erro")
    is_success: bool = Field(False, description="Indica sucesso")
    can_retry: bool = Field(True, description="Permite retry")
    blocks_workflow: bool = Field(False, description="Bloqueia o workflow")
    
    # Status
    is_active: bool = Field(True, description="Status ativo")

    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#'):
            raise ValueError('Color must start with #')
        if v is not None and len(v) != 7:
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores and hyphens only')
        return v

    @validator('is_final', 'is_error', 'is_success')
    def validate_final_status(cls, v, values):
        # Se é final, deve ser sucesso ou erro
        if values.get('is_final') and not (values.get('is_success') or values.get('is_error')):
            if 'is_final' in values and values['is_final']:
                raise ValueError('Final status must be either success or error')
        return v


class NodeExecutionStatusCreate(NodeExecutionStatusBase):
    """Schema para criação de NodeExecutionStatus"""
    pass


class NodeExecutionStatusUpdate(BaseModel):
    """Schema para atualização de NodeExecutionStatus"""
    
    display_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome para exibição")
    description: Optional[str] = Field(None, description="Descrição do status")
    
    # Configuração
    color: Optional[str] = Field(None, max_length=7, description="Cor em formato hex")
    is_final: Optional[bool] = Field(None, description="Status final de execução")
    is_error: Optional[bool] = Field(None, description="Indica erro")
    is_success: Optional[bool] = Field(None, description="Indica sucesso")
    can_retry: Optional[bool] = Field(None, description="Permite retry")
    blocks_workflow: Optional[bool] = Field(None, description="Bloqueia o workflow")
    
    # Status
    is_active: Optional[bool] = Field(None, description="Status ativo")

    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#'):
            raise ValueError('Color must start with #')
        if v is not None and len(v) != 7:
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v


class NodeExecutionStatusResponse(NodeExecutionStatusBase):
    """Schema para resposta de NodeExecutionStatus"""
    
    id: UUID = Field(..., description="ID único do status")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Campos computados
    is_terminal: Optional[bool] = Field(None, description="É um status terminal")
    is_retryable: Optional[bool] = Field(None, description="É possível retry")
    blocks_execution: Optional[bool] = Field(None, description="Bloqueia execução")
    
    # Estatísticas
    usage_count: Optional[int] = Field(None, description="Número de execuções com este status")
    success_rate: Optional[float] = Field(None, description="Taxa de sucesso")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusList(BaseModel):
    """Schema para lista de NodeExecutionStatus"""
    
    items: List[NodeExecutionStatusResponse] = Field(..., description="Lista de status")
    total: int = Field(..., description="Total de status")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusFilter(BaseModel):
    """Schema para filtro de NodeExecutionStatus"""
    
    is_active: Optional[bool] = Field(None, description="Filtrar por status ativo")
    is_final: Optional[bool] = Field(None, description="Filtrar por status final")
    is_error: Optional[bool] = Field(None, description="Filtrar por erro")
    is_success: Optional[bool] = Field(None, description="Filtrar por sucesso")
    can_retry: Optional[bool] = Field(None, description="Filtrar por retry")
    blocks_workflow: Optional[bool] = Field(None, description="Filtrar por bloqueio")
    search: Optional[str] = Field(None, description="Buscar por nome ou descrição")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusStatistics(BaseModel):
    """Schema para estatísticas de NodeExecutionStatus"""
    
    # Totais
    total_statuses: int = Field(..., description="Total de status")
    active_statuses: int = Field(..., description="Status ativos")
    inactive_statuses: int = Field(..., description="Status inativos")
    
    # Por tipo
    final_statuses: int = Field(..., description="Status finais")
    error_statuses: int = Field(..., description="Status de erro")
    success_statuses: int = Field(..., description="Status de sucesso")
    retryable_statuses: int = Field(..., description="Status com retry")
    blocking_statuses: int = Field(..., description="Status que bloqueiam")
    
    # Uso
    total_executions: int = Field(..., description="Total de execuções")
    average_executions_per_status: float = Field(..., description="Média de execuções por status")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusValidation(BaseModel):
    """Schema para validação de NodeExecutionStatus"""
    
    name: str = Field(..., description="Nome a validar")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusValidationResult(BaseModel):
    """Schema para resultado da validação"""
    
    is_valid: bool = Field(..., description="Nome válido")
    is_available: bool = Field(..., description="Nome disponível")
    
    # Sugestões
    suggestions: List[str] = Field([], description="Sugestões de nomes")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusFlow(BaseModel):
    """Schema para fluxo de NodeExecutionStatus"""
    
    status_id: UUID = Field(..., description="ID do status")
    
    # Transições possíveis
    next_possible_statuses: List[UUID] = Field([], description="Próximos status possíveis")
    previous_possible_statuses: List[UUID] = Field([], description="Status anteriores possíveis")
    
    # Regras
    requires_retry: bool = Field(False, description="Requer retry")
    can_skip: bool = Field(False, description="Pode pular")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusTransition(BaseModel):
    """Schema para transição de NodeExecutionStatus"""
    
    from_status_id: UUID = Field(..., description="Status de origem")
    to_status_id: UUID = Field(..., description="Status de destino")
    
    # Condições
    conditions: Optional[Dict[str, Any]] = Field(None, description="Condições para transição")
    
    # Validação
    is_valid_transition: bool = Field(..., description="Transição válida")
    
    model_config = ConfigDict(from_attributes=True)


class NodeExecutionStatusHealth(BaseModel):
    """Schema para saúde de NodeExecutionStatus"""
    
    # Status geral
    total_statuses: int = Field(..., description="Total de status")
    healthy_statuses: int = Field(..., description="Status saudáveis")
    
    # Problemas
    duplicate_names: List[str] = Field([], description="Nomes duplicados")
    missing_final_statuses: bool = Field(False, description="Faltam status finais")
    conflicting_configurations: List[str] = Field([], description="Configurações conflitantes")
    
    # Recomendações
    recommendations: List[str] = Field([], description="Recomendações")
    
    model_config = ConfigDict(from_attributes=True)

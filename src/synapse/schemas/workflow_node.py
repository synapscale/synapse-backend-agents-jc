"""
Schemas para WorkflowNode - nós de workflow
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class WorkflowNodeBase(BaseModel):
    """Schema base para WorkflowNode"""
    
    # Identificação
    name: str = Field(..., description="Nome do nó")
    description: Optional[str] = Field(None, description="Descrição do nó")
    
    # Tipo e categoria
    node_type: str = Field(..., description="Tipo do nó")
    category: str = Field(..., description="Categoria do nó")
    
    # Posicionamento no workflow
    position_x: float = Field(..., description="Posição X no canvas")
    position_y: float = Field(..., description="Posição Y no canvas")
    
    # Configuração do nó
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração do nó")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parâmetros do nó")
    
    # Schemas
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Schema de entrada")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Schema de saída")
    
    # Estado
    is_active: bool = Field(True, description="Nó ativo")
    
    # Relacionamentos
    workflow_id: UUID = Field(..., description="ID do workflow")
    parent_node_id: Optional[UUID] = Field(None, description="ID do nó pai")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowNodeCreate(WorkflowNodeBase):
    """Schema para criação de WorkflowNode"""
    pass


class WorkflowNodeUpdate(BaseModel):
    """Schema para atualização de WorkflowNode"""
    
    name: Optional[str] = Field(None, description="Nome do nó")
    description: Optional[str] = Field(None, description="Descrição do nó")
    
    node_type: Optional[str] = Field(None, description="Tipo do nó")
    category: Optional[str] = Field(None, description="Categoria do nó")
    
    position_x: Optional[float] = Field(None, description="Posição X no canvas")
    position_y: Optional[float] = Field(None, description="Posição Y no canvas")
    
    configuration: Optional[Dict[str, Any]] = Field(None, description="Configuração do nó")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parâmetros do nó")
    
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Schema de entrada")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Schema de saída")
    
    is_active: Optional[bool] = Field(None, description="Nó ativo")
    parent_node_id: Optional[UUID] = Field(None, description="ID do nó pai")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowNodeResponse(WorkflowNodeBase):
    """Schema para resposta de WorkflowNode"""
    
    id: UUID = Field(..., description="ID único do nó")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    workflow_name: Optional[str] = Field(None, description="Nome do workflow")
    parent_node_name: Optional[str] = Field(None, description="Nome do nó pai")
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    
    # Estatísticas
    executions_count: Optional[int] = Field(None, description="Número de execuções")
    success_rate: Optional[float] = Field(None, description="Taxa de sucesso")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowNodeList(BaseModel):
    """Schema para lista de WorkflowNode"""
    
    items: List[WorkflowNodeResponse] = Field(..., description="Lista de nós")
    total: int = Field(..., description="Total de nós")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowNodeExecution(BaseModel):
    """Schema para execução de WorkflowNode"""
    
    node_id: UUID = Field(..., description="ID do nó")
    workflow_execution_id: UUID = Field(..., description="ID da execução do workflow")
    
    # Dados de entrada
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    
    # Resultado
    output_data: Optional[Dict[str, Any]] = Field(None, description="Dados de saída")
    status: str = Field(..., description="Status da execução")
    
    # Métricas
    execution_time_ms: Optional[int] = Field(None, description="Tempo de execução em ms")
    memory_used_mb: Optional[float] = Field(None, description="Memória usada em MB")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    error_stack: Optional[str] = Field(None, description="Stack trace do erro")
    
    # Timestamps
    started_at: datetime = Field(..., description="Início da execução")
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowNodeValidation(BaseModel):
    """Schema para validação de WorkflowNode"""
    
    node_id: UUID = Field(..., description="ID do nó")
    is_valid: bool = Field(..., description="Nó válido")
    
    # Problemas encontrados
    errors: List[str] = Field(..., description="Erros de validação")
    warnings: List[str] = Field(..., description="Avisos de validação")
    
    # Validações específicas
    configuration_valid: bool = Field(..., description="Configuração válida")
    parameters_valid: bool = Field(..., description="Parâmetros válidos")
    schema_valid: bool = Field(..., description="Schemas válidos")
    connections_valid: bool = Field(..., description="Conexões válidas")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowNodeTemplate(BaseModel):
    """Schema para template de WorkflowNode"""
    
    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição do template")
    
    node_type: str = Field(..., description="Tipo do nó")
    category: str = Field(..., description="Categoria do nó")
    
    # Template configuration
    default_configuration: Dict[str, Any] = Field(..., description="Configuração padrão")
    default_parameters: Dict[str, Any] = Field(..., description="Parâmetros padrão")
    
    input_schema: Dict[str, Any] = Field(..., description="Schema de entrada")
    output_schema: Dict[str, Any] = Field(..., description="Schema de saída")
    
    # Metadata
    icon: Optional[str] = Field(None, description="Ícone do template")
    color: Optional[str] = Field(None, description="Cor do template")
    tags: Optional[List[str]] = Field(None, description="Tags do template")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowNodeStatistics(BaseModel):
    """Schema para estatísticas de WorkflowNode"""
    
    total_nodes: int = Field(..., description="Total de nós")
    active_nodes: int = Field(..., description="Nós ativos")
    
    # Por tipo
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    
    # Execuções
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Performance
    average_execution_time_ms: float = Field(..., description="Tempo médio de execução")
    average_memory_used_mb: float = Field(..., description="Memória média usada")
    
    model_config = ConfigDict(from_attributes=True)

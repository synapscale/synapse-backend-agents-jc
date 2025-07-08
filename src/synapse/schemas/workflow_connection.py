"""
Schemas para WorkflowConnection - conexões entre nós de workflow
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class WorkflowConnectionBase(BaseModel):
    """Schema base para WorkflowConnection"""
    
    # Nós conectados
    source_node_id: UUID = Field(..., description="ID do nó de origem")
    target_node_id: UUID = Field(..., description="ID do nó de destino")
    
    # Portas de conexão
    source_port: Optional[str] = Field(None, description="Porta de saída do nó de origem")
    target_port: Optional[str] = Field(None, description="Porta de entrada do nó de destino")
    
    # Configuração da conexão
    connection_type: str = Field("default", description="Tipo da conexão")
    
    # Condições
    condition: Optional[Dict[str, Any]] = Field(None, description="Condição para ativação")
    
    # Transformação de dados
    data_transformation: Optional[Dict[str, Any]] = Field(None, description="Transformação de dados")
    
    # Estado
    is_active: bool = Field(True, description="Conexão ativa")
    
    # Relacionamentos
    workflow_id: UUID = Field(..., description="ID do workflow")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowConnectionCreate(WorkflowConnectionBase):
    """Schema para criação de WorkflowConnection"""
    pass


class WorkflowConnectionUpdate(BaseModel):
    """Schema para atualização de WorkflowConnection"""
    
    source_port: Optional[str] = Field(None, description="Porta de saída do nó de origem")
    target_port: Optional[str] = Field(None, description="Porta de entrada do nó de destino")
    
    connection_type: Optional[str] = Field(None, description="Tipo da conexão")
    condition: Optional[Dict[str, Any]] = Field(None, description="Condição para ativação")
    data_transformation: Optional[Dict[str, Any]] = Field(None, description="Transformação de dados")
    
    is_active: Optional[bool] = Field(None, description="Conexão ativa")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class WorkflowConnectionResponse(WorkflowConnectionBase):
    """Schema para resposta de WorkflowConnection"""
    
    id: UUID = Field(..., description="ID único da conexão")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    workflow_name: Optional[str] = Field(None, description="Nome do workflow")
    source_node_name: Optional[str] = Field(None, description="Nome do nó de origem")
    target_node_name: Optional[str] = Field(None, description="Nome do nó de destino")
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    
    # Estatísticas
    executions_count: Optional[int] = Field(None, description="Número de execuções")
    success_rate: Optional[float] = Field(None, description="Taxa de sucesso")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionList(BaseModel):
    """Schema para lista de WorkflowConnection"""
    
    items: List[WorkflowConnectionResponse] = Field(..., description="Lista de conexões")
    total: int = Field(..., description="Total de conexões")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionExecution(BaseModel):
    """Schema para execução de WorkflowConnection"""
    
    connection_id: UUID = Field(..., description="ID da conexão")
    workflow_execution_id: UUID = Field(..., description="ID da execução do workflow")
    
    # Dados que passaram pela conexão
    input_data: Optional[Dict[str, Any]] = Field(None, description="Dados de entrada")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Dados de saída (após transformação)")
    
    # Status da execução
    status: str = Field(..., description="Status da execução")
    
    # Condição
    condition_result: Optional[bool] = Field(None, description="Resultado da condição")
    condition_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes da condição")
    
    # Transformação
    transformation_applied: bool = Field(False, description="Transformação aplicada")
    transformation_details: Optional[Dict[str, Any]] = Field(None, description="Detalhes da transformação")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    # Timestamps
    started_at: datetime = Field(..., description="Início da execução")
    completed_at: Optional[datetime] = Field(None, description="Fim da execução")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionValidation(BaseModel):
    """Schema para validação de WorkflowConnection"""
    
    connection_id: UUID = Field(..., description="ID da conexão")
    is_valid: bool = Field(..., description="Conexão válida")
    
    # Problemas encontrados
    errors: List[str] = Field(..., description="Erros de validação")
    warnings: List[str] = Field(..., description="Avisos de validação")
    
    # Validações específicas
    nodes_exist: bool = Field(..., description="Nós existem")
    ports_compatible: bool = Field(..., description="Portas compatíveis")
    condition_valid: bool = Field(..., description="Condição válida")
    transformation_valid: bool = Field(..., description="Transformação válida")
    no_circular_dependency: bool = Field(..., description="Sem dependência circular")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionPath(BaseModel):
    """Schema para caminho de conexões"""
    
    workflow_id: UUID = Field(..., description="ID do workflow")
    start_node_id: UUID = Field(..., description="ID do nó inicial")
    end_node_id: UUID = Field(..., description="ID do nó final")
    
    # Caminho encontrado
    path: List[UUID] = Field(..., description="Caminho de nós")
    connections: List[UUID] = Field(..., description="Conexões no caminho")
    
    # Métricas
    path_length: int = Field(..., description="Comprimento do caminho")
    estimated_execution_time_ms: Optional[int] = Field(None, description="Tempo estimado de execução")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionGraph(BaseModel):
    """Schema para grafo de conexões"""
    
    workflow_id: UUID = Field(..., description="ID do workflow")
    
    # Nós e conexões
    nodes: List[Dict[str, Any]] = Field(..., description="Nós do grafo")
    connections: List[Dict[str, Any]] = Field(..., description="Conexões do grafo")
    
    # Análise do grafo
    is_acyclic: bool = Field(..., description="Grafo acíclico")
    connected_components: int = Field(..., description="Componentes conectados")
    
    # Nós especiais
    entry_nodes: List[UUID] = Field(..., description="Nós de entrada")
    exit_nodes: List[UUID] = Field(..., description="Nós de saída")
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowConnectionStatistics(BaseModel):
    """Schema para estatísticas de WorkflowConnection"""
    
    total_connections: int = Field(..., description="Total de conexões")
    active_connections: int = Field(..., description="Conexões ativas")
    
    # Por tipo
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    
    # Execuções
    total_executions: int = Field(..., description="Total de execuções")
    successful_executions: int = Field(..., description="Execuções bem-sucedidas")
    failed_executions: int = Field(..., description="Execuções falhadas")
    
    # Condições
    conditions_with_condition: int = Field(..., description="Conexões com condição")
    conditions_with_transformation: int = Field(..., description="Conexões com transformação")
    
    model_config = ConfigDict(from_attributes=True)

#!/usr/bin/env python3
"""
Script para corrigir classes faltantes nos schemas
"""

# Adicionar no workflow.py
workflow_classes = """
class WorkflowSearch(BaseModel):
    \"\"\"Schema para busca de workflows\"\"\"
    query: Optional[str] = Field(None, description="Termo de busca")
    tags: Optional[List[str]] = Field(None, description="Tags para filtrar")
    category: Optional[str] = Field(None, description="Categoria")
    status: Optional[str] = Field(None, description="Status do workflow")

class WorkflowStats(BaseModel):
    \"\"\"Schema para estatísticas de workflow\"\"\"
    total_executions: int = Field(0, description="Total de execuções")
    success_rate: float = Field(0.0, description="Taxa de sucesso")
    avg_execution_time: float = Field(0.0, description="Tempo médio de execução")
    last_execution: Optional[datetime] = Field(None, description="Última execução")

class WorkflowVersion(BaseModel):
    \"\"\"Schema para versão de workflow\"\"\"
    version: str = Field(..., description="Número da versão")
    changelog: Optional[str] = Field(None, description="Log de mudanças")
    created_at: datetime = Field(..., description="Data de criação")
    is_active: bool = Field(True, description="Versão ativa")

class WorkflowTemplate(BaseModel):
    \"\"\"Schema para template de workflow\"\"\"
    name: str = Field(..., description="Nome do template")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    tags: Optional[List[str]] = Field(None, description="Tags")

class WorkflowTemplateResponse(WorkflowTemplate):
    \"\"\"Schema de resposta para template de workflow\"\"\"
    id: str = Field(..., description="ID do template")
    created_at: datetime = Field(..., description="Data de criação")

class NodeBase(BaseModel):
    \"\"\"Schema base para nós\"\"\"
    name: str = Field(..., description="Nome do nó")
    type: str = Field(..., description="Tipo do nó")
    position_x: float = Field(0, description="Posição X")
    position_y: float = Field(0, description="Posição Y")

class NodeCreate(NodeBase):
    \"\"\"Schema para criação de nós\"\"\"
    config: Optional[dict] = Field(None, description="Configuração do nó")

class NodeUpdate(BaseModel):
    \"\"\"Schema para atualização de nós\"\"\"
    name: Optional[str] = Field(None, description="Nome do nó")
    config: Optional[dict] = Field(None, description="Configuração do nó")
    position_x: Optional[float] = Field(None, description="Posição X")
    position_y: Optional[float] = Field(None, description="Posição Y")

class NodeResponse(NodeBase):
    \"\"\"Schema de resposta para nós\"\"\"
    id: str = Field(..., description="ID do nó")
    workflow_id: str = Field(..., description="ID do workflow")
    created_at: datetime = Field(..., description="Data de criação")

class ConnectionBase(BaseModel):
    \"\"\"Schema base para conexões\"\"\"
    source_node_id: str = Field(..., description="ID do nó de origem")
    target_node_id: str = Field(..., description="ID do nó de destino")

class ConnectionCreate(ConnectionBase):
    \"\"\"Schema para criação de conexões\"\"\"
    pass

class ConnectionUpdate(BaseModel):
    \"\"\"Schema para atualização de conexões\"\"\"
    source_node_id: Optional[str] = Field(None, description="ID do nó de origem")
    target_node_id: Optional[str] = Field(None, description="ID do nó de destino")

class ConnectionResponse(ConnectionBase):
    \"\"\"Schema de resposta para conexões\"\"\"
    id: str = Field(..., description="ID da conexão")
    workflow_id: str = Field(..., description="ID do workflow")
    created_at: datetime = Field(..., description="Data de criação")

class ExecutionLogResponse(BaseModel):
    \"\"\"Schema de resposta para logs de execução\"\"\"
    id: str = Field(..., description="ID do log")
    execution_id: str = Field(..., description="ID da execução")
    level: str = Field(..., description="Nível do log")
    message: str = Field(..., description="Mensagem")
    timestamp: datetime = Field(..., description="Timestamp")

class WorkflowExecutionCreate(BaseModel):
    \"\"\"Schema para criação de execução de workflow\"\"\"
    workflow_id: str = Field(..., description="ID do workflow")
    input_data: Optional[dict] = Field(None, description="Dados de entrada")
    
class WorkflowExecutionUpdate(BaseModel):
    \"\"\"Schema para atualização de execução de workflow\"\"\"
    status: Optional[str] = Field(None, description="Status da execução")
    output_data: Optional[dict] = Field(None, description="Dados de saída")

class WorkflowMetrics(BaseModel):
    \"\"\"Schema para métricas de workflow\"\"\"
    total_runs: int = Field(0, description="Total de execuções")
    success_count: int = Field(0, description="Execuções com sucesso")
    error_count: int = Field(0, description="Execuções com erro")
    avg_duration: float = Field(0.0, description="Duração média")

class WorkflowAnalytics(BaseModel):
    \"\"\"Schema para analytics de workflow\"\"\"
    performance_score: float = Field(0.0, description="Score de performance")
    reliability_score: float = Field(0.0, description="Score de confiabilidade")
    usage_trend: List[dict] = Field(default_factory=list, description="Tendência de uso")
"""

with open('src/synapse/schemas/workflow.py', 'r') as f:
    content = f.read()

# Adicionar as classes faltantes
if 'class WorkflowSearch' not in content:
    content += workflow_classes

with open('src/synapse/schemas/workflow.py', 'w') as f:
    f.write(content)

print("Classes adicionadas ao workflow.py!") 
"""
Schemas Pydantic para Audit Log
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
Tabela: audit_log
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class AuditOperation(str, Enum):
    """Operações de auditoria - ALINHADO COM O BANCO"""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FAILED_LOGIN = "FAILED_LOGIN"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    BACKUP = "BACKUP"
    RESTORE = "RESTORE"


class AuditSeverity(str, Enum):
    """Níveis de severidade para auditoria"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Categorias de eventos de auditoria"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CHANGE = "system_change"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BILLING = "billing"
    API = "api"


# ==================== AUDIT LOG SCHEMAS ====================


class AuditLogBase(BaseModel):
    """Schema base para audit log - ALINHADO COM audit_log TABLE"""

    table_name: str = Field(..., min_length=1, description="Nome da tabela afetada")
    record_id: uuid.UUID = Field(..., description="ID do registro afetado")
    operation: AuditOperation = Field(..., description="Operação realizada")
    diffs: Optional[Dict[str, Any]] = Field(None, description="Diferenças dos dados")

    @validator("table_name")
    def validate_table_name(cls, v):
        """Valida nome da tabela"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Nome da tabela é obrigatório")
        # Validar se é um nome de tabela válido
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Nome da tabela deve conter apenas letras, números e underscore"
            )
        return v.strip().lower()


class AuditLogCreate(AuditLogBase):
    """Schema para criação de audit log"""

    changed_by: Optional[uuid.UUID] = Field(
        None, description="ID do usuário que fez a mudança"
    )


class AuditLogResponse(AuditLogBase):
    """Schema de resposta para audit log - ALINHADO COM audit_log TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    audit_id: uuid.UUID = Field(..., description="ID único do audit log")
    changed_by: Optional[uuid.UUID] = Field(None, description="ID do usuário")
    changed_at: datetime = Field(..., description="Data e hora da mudança")


# ==================== SCHEMAS EXPANDIDOS ====================


class AuditLogWithUser(AuditLogResponse):
    """Audit log com informações do usuário"""

    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    user_ip: Optional[str] = Field(None, description="IP do usuário")


class AuditLogDetailed(AuditLogResponse):
    """Audit log com informações detalhadas"""

    # Informações do usuário
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")

    # Informações do contexto
    session_id: Optional[str] = Field(None, description="ID da sessão")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")

    # Metadados adicionais
    severity: AuditSeverity = Field(
        AuditSeverity.MEDIUM, description="Severidade do evento"
    )
    category: AuditCategory = Field(
        AuditCategory.DATA_MODIFICATION, description="Categoria do evento"
    )
    tags: List[str] = Field(default_factory=list, description="Tags para classificação")

    # Informações técnicas
    method: Optional[str] = Field(None, description="Método HTTP usado")
    endpoint: Optional[str] = Field(None, description="Endpoint acessado")
    response_status: Optional[int] = Field(None, description="Status da resposta")
    processing_time_ms: Optional[int] = Field(
        None, description="Tempo de processamento"
    )


# ==================== SCHEMAS DE AUDIT ESPECÍFICOS ====================


class UserAuditEvent(BaseModel):
    """Evento de auditoria específico para usuários"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    action: str = Field(..., description="Ação realizada")
    target_user_id: Optional[uuid.UUID] = Field(None, description="ID do usuário alvo")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Detalhes da ação"
    )
    ip_address: Optional[str] = Field(None, description="IP do usuário")
    user_agent: Optional[str] = Field(None, description="User agent")


class WorkspaceAuditEvent(BaseModel):
    """Evento de auditoria específico para workspaces"""

    workspace_id: uuid.UUID = Field(..., description="ID do workspace")
    user_id: uuid.UUID = Field(..., description="ID do usuário")
    action: str = Field(..., description="Ação realizada")
    resource_type: str = Field(..., description="Tipo de recurso")
    resource_id: Optional[uuid.UUID] = Field(None, description="ID do recurso")
    changes: Dict[str, Any] = Field(
        default_factory=dict, description="Mudanças realizadas"
    )


class SecurityAuditEvent(BaseModel):
    """Evento de auditoria de segurança"""

    event_type: str = Field(..., description="Tipo do evento de segurança")
    user_id: Optional[uuid.UUID] = Field(None, description="ID do usuário")
    ip_address: str = Field(..., description="IP de origem")
    severity: AuditSeverity = Field(..., description="Severidade do evento")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Detalhes do evento"
    )
    blocked: bool = Field(False, description="Se a ação foi bloqueada")


class APIAuditEvent(BaseModel):
    """Evento de auditoria para chamadas de API"""

    api_key_id: Optional[uuid.UUID] = Field(None, description="ID da API key")
    user_id: Optional[uuid.UUID] = Field(None, description="ID do usuário")
    endpoint: str = Field(..., description="Endpoint acessado")
    method: str = Field(..., description="Método HTTP")
    status_code: int = Field(..., description="Código de status")
    response_time_ms: int = Field(..., description="Tempo de resposta")
    request_size: Optional[int] = Field(None, description="Tamanho da requisição")
    response_size: Optional[int] = Field(None, description="Tamanho da resposta")
    ip_address: str = Field(..., description="IP de origem")


# ==================== SCHEMAS DE BUSCA E FILTRAGEM ====================


class AuditLogSearchRequest(BaseModel):
    """Schema para busca de audit logs"""

    # Filtros por dados
    table_name: Optional[str] = Field(None, description="Filtrar por tabela")
    operation: Optional[AuditOperation] = Field(
        None, description="Filtrar por operação"
    )
    changed_by: Optional[uuid.UUID] = Field(None, description="Filtrar por usuário")
    record_id: Optional[uuid.UUID] = Field(None, description="Filtrar por registro")

    # Filtros por tempo
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    last_hours: Optional[int] = Field(
        None, ge=1, le=8760, description="Últimas N horas"
    )

    # Filtros por contexto
    severity: Optional[AuditSeverity] = Field(
        None, description="Filtrar por severidade"
    )
    category: Optional[AuditCategory] = Field(None, description="Filtrar por categoria")
    ip_address: Optional[str] = Field(None, description="Filtrar por IP")

    # Busca textual
    search_query: Optional[str] = Field(None, description="Busca textual nos dados")

    # Paginação
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(50, ge=1, le=1000, description="Tamanho da página")

    # Ordenação
    sort_by: str = Field("changed_at", description="Campo para ordenação")
    sort_order: str = Field("desc", description="Ordem da classificação")


class AuditLogListResponse(BaseModel):
    """Schema para listagem de audit logs"""

    logs: List[AuditLogResponse] = Field(..., description="Lista de audit logs")
    total: int = Field(..., description="Total de logs")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")

    # Estatísticas da busca
    operations_summary: Dict[str, int] = Field(
        default_factory=dict, description="Resumo por operação"
    )
    tables_summary: Dict[str, int] = Field(
        default_factory=dict, description="Resumo por tabela"
    )
    users_summary: Dict[str, int] = Field(
        default_factory=dict, description="Resumo por usuário"
    )


# ==================== SCHEMAS DE RELATÓRIOS ====================


class AuditReport(BaseModel):
    """Schema para relatórios de auditoria"""

    report_id: str = Field(..., description="ID único do relatório")
    title: str = Field(..., description="Título do relatório")
    description: Optional[str] = Field(None, description="Descrição do relatório")

    # Período do relatório
    start_date: datetime = Field(..., description="Data inicial")
    end_date: datetime = Field(..., description="Data final")

    # Filtros aplicados
    filters: Dict[str, Any] = Field(
        default_factory=dict, description="Filtros utilizados"
    )

    # Estatísticas gerais
    total_events: int = Field(0, description="Total de eventos")
    unique_users: int = Field(0, description="Usuários únicos")
    unique_tables: int = Field(0, description="Tabelas únicas")

    # Breakdown por operação
    operations_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Eventos por operação"
    )

    # Breakdown por severidade
    severity_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Eventos por severidade"
    )

    # Top usuários
    top_users: List[Dict[str, Union[str, int]]] = Field(
        default_factory=list, description="Usuários mais ativos"
    )

    # Top tabelas
    top_tables: List[Dict[str, Union[str, int]]] = Field(
        default_factory=list, description="Tabelas mais modificadas"
    )

    # Timestamps
    generated_at: datetime = Field(..., description="Data de geração")
    generated_by: uuid.UUID = Field(..., description="Gerado por usuário")


class AuditReportRequest(BaseModel):
    """Schema para solicitação de relatório de auditoria"""

    title: str = Field(
        ..., min_length=1, max_length=200, description="Título do relatório"
    )
    description: Optional[str] = Field(None, description="Descrição do relatório")

    # Período
    start_date: datetime = Field(..., description="Data inicial")
    end_date: datetime = Field(..., description="Data final")

    # Filtros
    include_operations: Optional[List[AuditOperation]] = Field(
        None, description="Operações a incluir"
    )
    include_tables: Optional[List[str]] = Field(None, description="Tabelas a incluir")
    include_users: Optional[List[uuid.UUID]] = Field(
        None, description="Usuários a incluir"
    )
    min_severity: Optional[AuditSeverity] = Field(None, description="Severidade mínima")

    # Configurações do relatório
    include_details: bool = Field(True, description="Incluir detalhes dos eventos")
    group_by_day: bool = Field(True, description="Agrupar por dia")
    include_charts: bool = Field(True, description="Incluir gráficos")
    format: str = Field("json", description="Formato do relatório")


# ==================== SCHEMAS DE COMPLIANCE ====================


class ComplianceAuditCheck(BaseModel):
    """Schema para verificação de compliance"""

    check_id: str = Field(..., description="ID da verificação")
    rule_name: str = Field(..., description="Nome da regra")
    description: str = Field(..., description="Descrição da regra")

    # Período da verificação
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")

    # Resultado
    status: str = Field(..., description="Status da verificação")
    score: float = Field(..., ge=0, le=100, description="Score de compliance")
    violations: List[Dict[str, Any]] = Field(
        default_factory=list, description="Violações encontradas"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recomendações"
    )

    # Metadados
    checked_at: datetime = Field(..., description="Data da verificação")
    checked_by: Optional[uuid.UUID] = Field(None, description="Verificado por")


class DataRetentionCheck(BaseModel):
    """Schema para verificação de retenção de dados"""

    table_name: str = Field(..., description="Nome da tabela")
    retention_days: int = Field(..., description="Dias de retenção")
    records_to_delete: int = Field(0, description="Registros a deletar")
    oldest_record_date: Optional[datetime] = Field(
        None, description="Data do registro mais antigo"
    )
    compliance_status: str = Field(..., description="Status de compliance")
    last_cleanup: Optional[datetime] = Field(None, description="Última limpeza")


# ==================== SCHEMAS DE EXPORTAÇÃO ====================


class AuditExportRequest(BaseModel):
    """Schema para exportação de audit logs"""

    # Filtros para exportação
    filters: AuditLogSearchRequest = Field(..., description="Filtros para exportação")

    # Configurações de exportação
    format: str = Field("csv", description="Formato da exportação")
    include_user_details: bool = Field(True, description="Incluir detalhes do usuário")
    include_diffs: bool = Field(True, description="Incluir diffs dos dados")
    compress: bool = Field(False, description="Comprimir arquivo")

    # Configurações de entrega
    email_to: Optional[str] = Field(None, description="Email para envio")
    webhook_url: Optional[str] = Field(None, description="URL do webhook")


class AuditExportResult(BaseModel):
    """Schema para resultado da exportação"""

    export_id: str = Field(..., description="ID da exportação")
    status: str = Field(..., description="Status da exportação")
    total_records: int = Field(0, description="Total de registros exportados")
    file_size: Optional[int] = Field(None, description="Tamanho do arquivo")
    download_url: Optional[str] = Field(None, description="URL para download")
    expires_at: Optional[datetime] = Field(
        None, description="Data de expiração do link"
    )
    created_at: datetime = Field(..., description="Data de criação")
    completed_at: Optional[datetime] = Field(None, description="Data de conclusão")

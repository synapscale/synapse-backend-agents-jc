"""
Schemas Pydantic para User Analytics e Insights
ALINHADO PERFEITAMENTE COM O BANCO PostgreSQL schema synapscale_db
Tabelas: user_behavior_metrics, user_insights
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ==================== ENUMS ALINHADOS COM O BANCO ====================


class PeriodType(str, Enum):
    """Tipos de período para métricas - ALINHADO COM O BANCO"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class InsightType(str, Enum):
    """Tipos de insights - ALINHADO COM O BANCO"""

    USAGE_PATTERN = "usage_pattern"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"
    OPPORTUNITY = "opportunity"
    ACHIEVEMENT = "achievement"
    TREND = "trend"


class InsightCategory(str, Enum):
    """Categorias de insights - ALINHADO COM O BANCO"""

    PRODUCTIVITY = "productivity"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    USAGE = "usage"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    RETENTION = "retention"
    OPTIMIZATION = "optimization"


class InsightPriority(str, Enum):
    """Prioridades de insights - ALINHADO COM O BANCO"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserFeedback(str, Enum):
    """Feedback do usuário sobre insights"""

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    IRRELEVANT = "irrelevant"
    ALREADY_KNOWN = "already_known"


# ==================== USER BEHAVIOR METRICS SCHEMAS ====================


class UserBehaviorMetricsBase(BaseModel):
    """Schema base para métricas de comportamento - ALINHADO COM user_behavior_metrics TABLE"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    date: datetime = Field(..., description="Data da métrica")
    period_type: PeriodType = Field(..., description="Tipo do período")

    # Métricas de sessão
    session_count: int = Field(0, ge=0, description="Número de sessões")
    total_session_duration: int = Field(
        0, ge=0, description="Duração total das sessões (segundos)"
    )
    avg_session_duration: float = Field(
        0.0, ge=0, description="Duração média das sessões"
    )

    # Métricas de navegação
    page_views: int = Field(0, ge=0, description="Visualizações de página")
    unique_pages_visited: int = Field(0, ge=0, description="Páginas únicas visitadas")

    # Métricas de produtividade
    workflows_created: int = Field(0, ge=0, description="Workflows criados")
    workflows_executed: int = Field(0, ge=0, description="Workflows executados")
    components_used: int = Field(0, ge=0, description="Componentes utilizados")

    # Métricas de colaboração
    collaborations_initiated: int = Field(0, ge=0, description="Colaborações iniciadas")

    # Métricas de monetização
    marketplace_purchases: int = Field(0, ge=0, description="Compras no marketplace")
    revenue_generated: float = Field(0.0, ge=0, description="Receita gerada")
    components_published: int = Field(0, ge=0, description="Componentes publicados")

    # Métricas de qualidade
    error_count: int = Field(0, ge=0, description="Número de erros")
    support_tickets: int = Field(0, ge=0, description="Tickets de suporte")
    feature_requests: int = Field(0, ge=0, description="Solicitações de features")

    # Scores calculados
    engagement_score: float = Field(
        0.0, ge=0, le=100, description="Score de engajamento"
    )
    satisfaction_score: float = Field(
        0.0, ge=0, le=100, description="Score de satisfação"
    )
    value_score: float = Field(0.0, ge=0, le=100, description="Score de valor")


class UserBehaviorMetricsCreate(UserBehaviorMetricsBase):
    """Schema para criação de métricas de comportamento"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class UserBehaviorMetricsUpdate(BaseModel):
    """Schema para atualização de métricas de comportamento"""

    # Permitir atualização de qualquer campo métrico
    session_count: Optional[int] = Field(
        None, ge=0, description="Novo número de sessões"
    )
    total_session_duration: Optional[int] = Field(
        None, ge=0, description="Nova duração total"
    )
    avg_session_duration: Optional[float] = Field(
        None, ge=0, description="Nova duração média"
    )
    page_views: Optional[int] = Field(None, ge=0, description="Novas visualizações")
    unique_pages_visited: Optional[int] = Field(
        None, ge=0, description="Novas páginas únicas"
    )
    workflows_created: Optional[int] = Field(
        None, ge=0, description="Novos workflows criados"
    )
    workflows_executed: Optional[int] = Field(
        None, ge=0, description="Novos workflows executados"
    )
    components_used: Optional[int] = Field(
        None, ge=0, description="Novos componentes usados"
    )
    collaborations_initiated: Optional[int] = Field(
        None, ge=0, description="Novas colaborações"
    )
    marketplace_purchases: Optional[int] = Field(
        None, ge=0, description="Novas compras"
    )
    revenue_generated: Optional[float] = Field(None, ge=0, description="Nova receita")
    components_published: Optional[int] = Field(
        None, ge=0, description="Novos componentes publicados"
    )
    error_count: Optional[int] = Field(None, ge=0, description="Novo número de erros")
    support_tickets: Optional[int] = Field(None, ge=0, description="Novos tickets")
    feature_requests: Optional[int] = Field(
        None, ge=0, description="Novas solicitações"
    )
    engagement_score: Optional[float] = Field(
        None, ge=0, le=100, description="Novo score de engajamento"
    )
    satisfaction_score: Optional[float] = Field(
        None, ge=0, le=100, description="Novo score de satisfação"
    )
    value_score: Optional[float] = Field(
        None, ge=0, le=100, description="Novo score de valor"
    )


class UserBehaviorMetricsResponse(UserBehaviorMetricsBase):
    """Schema de resposta para métricas - ALINHADO COM user_behavior_metrics TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único da métrica")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Última atualização")


# ==================== USER INSIGHTS SCHEMAS ====================


class UserInsightBase(BaseModel):
    """Schema base para insights - ALINHADO COM user_insights TABLE"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    insight_type: InsightType = Field(..., description="Tipo do insight")
    category: InsightCategory = Field(..., description="Categoria do insight")
    priority: InsightPriority = Field(..., description="Prioridade do insight")

    # Conteúdo do insight
    title: str = Field(
        ..., min_length=1, max_length=200, description="Título do insight"
    )
    description: str = Field(..., min_length=1, description="Descrição do insight")
    recommendation: Optional[str] = Field(None, description="Recomendação de ação")

    # Dados de suporte
    supporting_data: Optional[Dict[str, Any]] = Field(
        None, description="Dados que suportam o insight"
    )
    confidence_score: float = Field(..., ge=0, le=100, description="Score de confiança")

    # Ação sugerida
    suggested_action: Optional[str] = Field(
        None, max_length=100, description="Ação sugerida"
    )
    action_url: Optional[str] = Field(None, max_length=500, description="URL para ação")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Dados para a ação")

    # Estado do insight
    is_read: bool = Field(False, description="Se foi lido")
    is_dismissed: bool = Field(False, description="Se foi dispensado")
    is_acted_upon: bool = Field(False, description="Se houve ação")

    # Configurações de expiração
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    is_evergreen: bool = Field(False, description="Se é sempre relevante")

    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        """Valida score de confiança"""
        if not 0 <= v <= 100:
            raise ValueError("Score de confiança deve estar entre 0 e 100")
        return v


class UserInsightCreate(UserInsightBase):
    """Schema para criação de insights"""

    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")


class UserInsightUpdate(BaseModel):
    """Schema para atualização de insights"""

    priority: Optional[InsightPriority] = Field(None, description="Nova prioridade")
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Novo título"
    )
    description: Optional[str] = Field(None, min_length=1, description="Nova descrição")
    recommendation: Optional[str] = Field(None, description="Nova recomendação")
    supporting_data: Optional[Dict[str, Any]] = Field(
        None, description="Novos dados de suporte"
    )
    confidence_score: Optional[float] = Field(
        None, ge=0, le=100, description="Novo score"
    )
    suggested_action: Optional[str] = Field(
        None, max_length=100, description="Nova ação sugerida"
    )
    action_url: Optional[str] = Field(None, max_length=500, description="Nova URL")
    action_data: Optional[Dict[str, Any]] = Field(
        None, description="Novos dados de ação"
    )
    is_read: Optional[bool] = Field(None, description="Novo status de leitura")
    is_dismissed: Optional[bool] = Field(None, description="Novo status de dispensado")
    is_acted_upon: Optional[bool] = Field(None, description="Novo status de ação")
    user_feedback: Optional[UserFeedback] = Field(
        None, description="Feedback do usuário"
    )
    expires_at: Optional[datetime] = Field(None, description="Nova data de expiração")
    is_evergreen: Optional[bool] = Field(None, description="Novo status evergreen")


class UserInsightResponse(UserInsightBase):
    """Schema de resposta para insights - ALINHADO COM user_insights TABLE"""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: uuid.UUID = Field(..., description="ID único do insight")
    user_feedback: Optional[UserFeedback] = Field(
        None, description="Feedback do usuário"
    )
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")

    # Timestamps
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")
    read_at: Optional[datetime] = Field(None, description="Data de leitura")
    acted_at: Optional[datetime] = Field(None, description="Data da ação")


# ==================== SCHEMAS AGREGADOS E ESTATÍSTICAS ====================


class UserEngagementSummary(BaseModel):
    """Resumo de engajamento do usuário"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")

    # Métricas agregadas
    total_sessions: int = Field(0, description="Total de sessões")
    total_time_spent: int = Field(0, description="Tempo total gasto (segundos)")
    avg_daily_usage: float = Field(0.0, description="Uso médio diário (minutos)")

    # Scores
    overall_engagement_score: float = Field(
        0.0, description="Score geral de engajamento"
    )
    trend_direction: str = Field("stable", description="Direção da tendência")

    # Comparações
    compared_to_previous_period: float = Field(
        0.0, description="Comparação com período anterior (%)"
    )
    compared_to_average_user: float = Field(
        0.0, description="Comparação com usuário médio (%)"
    )


class UserProductivityMetrics(BaseModel):
    """Métricas de produtividade do usuário"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    period: str = Field(..., description="Período das métricas")

    # Métricas de criação
    workflows_created: int = Field(0, description="Workflows criados")
    components_created: int = Field(0, description="Componentes criados")

    # Métricas de execução
    workflows_executed: int = Field(0, description="Workflows executados")
    success_rate: float = Field(0.0, description="Taxa de sucesso (%)")
    avg_execution_time: float = Field(0.0, description="Tempo médio de execução")

    # Métricas de qualidade
    error_rate: float = Field(0.0, description="Taxa de erro (%)")
    optimization_score: float = Field(0.0, description="Score de otimização")

    # Comparações
    productivity_rank: Optional[int] = Field(
        None, description="Ranking de produtividade"
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list, description="Sugestões de melhoria"
    )


class UserInsightSummary(BaseModel):
    """Resumo de insights do usuário"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")

    # Contadores por status
    total_insights: int = Field(0, description="Total de insights")
    unread_insights: int = Field(0, description="Insights não lidos")
    active_insights: int = Field(0, description="Insights ativos")
    acted_upon_insights: int = Field(0, description="Insights com ação tomada")

    # Contadores por categoria
    insights_by_category: Dict[str, int] = Field(
        default_factory=dict, description="Insights por categoria"
    )
    insights_by_priority: Dict[str, int] = Field(
        default_factory=dict, description="Insights por prioridade"
    )

    # Métricas de engajamento
    action_rate: float = Field(0.0, description="Taxa de ação sobre insights (%)")
    avg_confidence_score: float = Field(0.0, description="Score médio de confiança")

    # Últimas atividades
    last_insight_date: Optional[datetime] = Field(
        None, description="Data do último insight"
    )
    last_action_date: Optional[datetime] = Field(
        None, description="Data da última ação"
    )


# ==================== SCHEMAS DE BUSCA E FILTROS ====================


class UserMetricsSearchRequest(BaseModel):
    """Schema para busca de métricas de usuário"""

    user_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs dos usuários")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    period_type: Optional[PeriodType] = Field(None, description="Tipo de período")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

    # Filtros por métricas
    min_engagement_score: Optional[float] = Field(
        None, ge=0, le=100, description="Score mínimo"
    )
    max_engagement_score: Optional[float] = Field(
        None, ge=0, le=100, description="Score máximo"
    )

    # Paginação
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(50, ge=1, le=1000, description="Tamanho da página")


class UserInsightsSearchRequest(BaseModel):
    """Schema para busca de insights de usuário"""

    user_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs dos usuários")
    tenant_id: Optional[uuid.UUID] = Field(None, description="ID do tenant")
    insight_types: Optional[List[InsightType]] = Field(
        None, description="Tipos de insight"
    )
    categories: Optional[List[InsightCategory]] = Field(None, description="Categorias")
    priorities: Optional[List[InsightPriority]] = Field(None, description="Prioridades")

    # Filtros por status
    is_read: Optional[bool] = Field(None, description="Status de leitura")
    is_dismissed: Optional[bool] = Field(None, description="Status de dispensado")
    is_acted_upon: Optional[bool] = Field(None, description="Status de ação")
    is_expired: Optional[bool] = Field(None, description="Status de expiração")

    # Filtros por tempo
    created_after: Optional[datetime] = Field(None, description="Criado após")
    created_before: Optional[datetime] = Field(None, description="Criado antes")

    # Busca textual
    search_query: Optional[str] = Field(None, description="Busca no título/descrição")

    # Paginação
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(50, ge=1, le=200, description="Tamanho da página")


# ==================== SCHEMAS DE LISTAGEM ====================


class UserMetricsListResponse(BaseModel):
    """Schema para listagem de métricas"""

    metrics: List[UserBehaviorMetricsResponse] = Field(
        ..., description="Lista de métricas"
    )
    total: int = Field(..., description="Total de métricas")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")

    # Estatísticas agregadas
    aggregated_stats: Dict[str, float] = Field(
        default_factory=dict, description="Estatísticas agregadas"
    )


class UserInsightsListResponse(BaseModel):
    """Schema para listagem de insights"""

    insights: List[UserInsightResponse] = Field(..., description="Lista de insights")
    total: int = Field(..., description="Total de insights")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")

    # Resumo dos insights
    summary: UserInsightSummary = Field(..., description="Resumo dos insights")


# ==================== SCHEMAS DE AÇÕES EM LOTE ====================


class BulkInsightAction(BaseModel):
    """Schema para ações em lote em insights"""

    insight_ids: List[uuid.UUID] = Field(
        ..., min_items=1, description="IDs dos insights"
    )
    action: str = Field(..., description="Ação a ser realizada")
    user_feedback: Optional[UserFeedback] = Field(
        None, description="Feedback do usuário"
    )


class BulkInsightActionResult(BaseModel):
    """Resultado de ação em lote"""

    processed: int = Field(..., description="Quantidade processada")
    errors: List[str] = Field(default_factory=list, description="Erros encontrados")
    updated_insights: List[UserInsightResponse] = Field(
        default_factory=list, description="Insights atualizados"
    )


# ==================== SCHEMAS DE RELATÓRIOS ====================


class UserAnalyticsReport(BaseModel):
    """Relatório de analytics do usuário"""

    user_id: uuid.UUID = Field(..., description="ID do usuário")
    report_period: str = Field(..., description="Período do relatório")
    generated_at: datetime = Field(..., description="Data de geração")

    # Resumos
    engagement_summary: UserEngagementSummary = Field(
        ..., description="Resumo de engajamento"
    )
    productivity_metrics: UserProductivityMetrics = Field(
        ..., description="Métricas de produtividade"
    )
    insight_summary: UserInsightSummary = Field(..., description="Resumo de insights")

    # Tendências
    usage_trends: List[Dict[str, Any]] = Field(
        default_factory=list, description="Tendências de uso"
    )
    performance_trends: List[Dict[str, Any]] = Field(
        default_factory=list, description="Tendências de performance"
    )

    # Recomendações
    recommendations: List[str] = Field(
        default_factory=list, description="Recomendações"
    )
    next_actions: List[str] = Field(
        default_factory=list, description="Próximas ações sugeridas"
    )

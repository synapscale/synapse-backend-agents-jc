"""
Modelos Analytics para Insights e Métricas
Criado por José - um desenvolvedor Full Stack
Sistema avançado de analytics e business intelligence

NOTA: A classe AnalyticsEvent foi movida para analytics_event.py para evitar conflitos
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    BigInteger,
    DECIMAL,
    text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from synapse.database import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid


class EventType(PyEnum):
    """Tipos de eventos para analytics"""

    PAGE_VIEW = "page_view"
    USER_ACTION = "user_action"
    WORKFLOW_EXECUTION = "workflow_execution"
    COMPONENT_USAGE = "component_usage"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"
    BUSINESS_EVENT = "business_event"


class MetricType(PyEnum):
    """Tipos de métricas"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"


# REMOVIDO: class AnalyticsEvent - duplicata removida (mantida em analytics_event.py)
# A classe AnalyticsEvent foi movida para analytics_event.py para evitar conflitos


class AnalyticsUserBehaviorMetric(Base):
    """
    Modelo para métricas de comportamento do usuário
    Agregações e insights sobre como os usuários usam o sistema
    """

    __tablename__ = "user_behavior_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )

    # Período da métrica
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly

    # Métricas de engajamento
    session_count = Column(Integer, default=0, nullable=False)
    total_session_duration = Column(Integer, default=0, nullable=False)  # segundos
    avg_session_duration = Column(Float, default=0.0, nullable=False)
    page_views = Column(Integer, default=0, nullable=False)
    unique_pages_visited = Column(Integer, default=0, nullable=False)

    # Métricas de atividade
    workflows_created = Column(Integer, default=0, nullable=False)
    workflows_executed = Column(Integer, default=0, nullable=False)
    components_used = Column(Integer, default=0, nullable=False)
    collaborations_initiated = Column(Integer, default=0, nullable=False)

    # Métricas de valor
    marketplace_purchases = Column(Integer, default=0, nullable=False)
    revenue_generated = Column(Float, default=0.0, nullable=False)
    components_published = Column(Integer, default=0, nullable=False)

    # Métricas de qualidade
    error_count = Column(Integer, default=0, nullable=False)
    support_tickets = Column(Integer, default=0, nullable=False)
    feature_requests = Column(Integer, default=0, nullable=False)

    # Scores calculados
    engagement_score = Column(Float, default=0.0, nullable=False)  # 0-100
    satisfaction_score = Column(Float, default=0.0, nullable=False)  # 0-100
    value_score = Column(Float, default=0.0, nullable=False)  # 0-100

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relacionamentos
    user = relationship("User")

    def __repr__(self):
        return f"<UserBehaviorMetric(user_id={self.user_id}, date={self.date}, period='{self.period_type}')>"


class SystemPerformanceMetric(Base):
    """
    Modelo para métricas de performance do sistema
    """

    __tablename__ = "system_performance_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Identificação da métrica
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(20), nullable=False)  # counter, gauge, histogram, timer

    # Contexto
    service = Column(
        String(50), nullable=False, index=True
    )  # api, frontend, executor, etc.
    environment = Column(String(20), default="production", nullable=False)

    # Valores
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # ms, bytes, percent, count, etc.

    # Dimensões adicionais
    tags = Column(JSON, default=dict)  # Tags para filtragem e agrupamento

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<SystemPerformanceMetric(metric_name='{self.metric_name}', value={self.value}, service='{self.service}')>"


class BusinessMetric(Base):
    """
    Modelo para métricas de negócio
    KPIs e métricas importantes para o negócio
    """

    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Período
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(
        String(20), nullable=False
    )  # daily, weekly, monthly, quarterly

    # Métricas de usuários
    total_users = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    churned_users = Column(Integer, default=0, nullable=False)

    # Métricas de engajamento
    total_sessions = Column(Integer, default=0, nullable=False)
    avg_session_duration = Column(Float, default=0.0, nullable=False)
    total_page_views = Column(Integer, default=0, nullable=False)
    bounce_rate = Column(Float, default=0.0, nullable=False)

    # Métricas de produto
    workflows_created = Column(Integer, default=0, nullable=False)
    workflows_executed = Column(Integer, default=0, nullable=False)
    components_published = Column(Integer, default=0, nullable=False)
    components_downloaded = Column(Integer, default=0, nullable=False)

    # Métricas de colaboração
    workspaces_created = Column(Integer, default=0, nullable=False)
    teams_formed = Column(Integer, default=0, nullable=False)
    collaborative_sessions = Column(Integer, default=0, nullable=False)

    # Métricas financeiras
    total_revenue = Column(Float, default=0.0, nullable=False)
    recurring_revenue = Column(Float, default=0.0, nullable=False)
    marketplace_revenue = Column(Float, default=0.0, nullable=False)
    avg_revenue_per_user = Column(Float, default=0.0, nullable=False)

    # Métricas de qualidade
    error_rate = Column(Float, default=0.0, nullable=False)
    avg_response_time = Column(Float, default=0.0, nullable=False)
    uptime_percentage = Column(Float, default=100.0, nullable=False)
    customer_satisfaction = Column(Float, default=0.0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<BusinessMetric(date={self.date}, period='{self.period_type}', total_users={self.total_users})>"






class AnalyticsUserInsight(Base):
    """
    Modelo para insights personalizados dos usuários
    IA gera insights baseados no comportamento e dados
    """

    __tablename__ = "user_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )

    # Classificação do insight
    insight_type = Column(
        String(50), nullable=False, index=True
    )  # performance, usage, recommendation, etc.
    category = Column(String(50), nullable=False, index=True)
    priority = Column(
        String(20), default="medium", nullable=False
    )  # low, medium, high, critical

    # Conteúdo
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text)

    # Dados de suporte
    supporting_data = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.0, nullable=False)  # 0-1

    # Ação sugerida
    suggested_action = Column(String(100))
    action_url = Column(String(500))
    action_data = Column(JSON, default=dict)

    # Interação do usuário
    is_read = Column(Boolean, default=False, nullable=False)
    is_dismissed = Column(Boolean, default=False, nullable=False)
    is_acted_upon = Column(Boolean, default=False, nullable=False)
    user_feedback = Column(String(20))  # helpful, not_helpful, irrelevant

    # Validade
    expires_at = Column(DateTime)
    is_evergreen = Column(
        Boolean, default=False, nullable=False
    )  # Insight sempre relevante

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime)
    acted_at = Column(DateTime)

    # Relacionamentos
    user = relationship("User")

    def __repr__(self):
        return f"<UserInsight(id={self.id}, user_id={self.user_id}, type='{self.insight_type}')>"




# AnalyticsAlert is now defined in analytics_alert.py to avoid duplication


class AnalyticsExport(Base):
    __tablename__ = "analytics_exports"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    export_type = Column(String(50), nullable=False)
    export_query = Column("query", JSONB, nullable=False)
    file_path = Column(String(500))
    status = Column(String(20), nullable=False, server_default=text("'pending'"))
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True))


class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    id = Column(UUID(as_uuid=True), primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 4), nullable=False)
    dimensions = Column(JSONB, server_default=text("'{}'"), nullable=False)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


 
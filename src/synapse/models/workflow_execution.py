"""
Modelo WorkflowExecution para engine de execução de workflows
Criado por José - um desenvolvedor Full Stack
Sistema completo de execução em tempo real
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    text,
    UUID,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.dialects.postgresql import JSONB

from synapse.database import Base


class ExecutionStatus(str, Enum):
    """Status de execução do workflow"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class NodeExecutionStatus(str, Enum):
    """Status de execução de um nó específico"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


class WorkflowExecution(Base):
    """
    Modelo para execução de workflows
    Gerencia o estado e progresso de execução de workflows
    """

    __tablename__ = "workflow_executions"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )

    # Relacionamentos
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.workflows.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status e controle
    status = Column(String(20), nullable=False, server_default=text("'pending'"))
    priority = Column(Integer, default=5, index=True)  # 1-10, maior = mais prioritário

    # Dados de execução
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    context_data = Column(JSON, nullable=True)  # Contexto de execução
    variables = Column(JSON, nullable=True)  # Variáveis do usuário

    # Progresso
    total_nodes = Column(Integer, default=0)
    completed_nodes = Column(Integer, default=0)
    failed_nodes = Column(Integer, default=0)
    progress_percentage = Column(Integer, default=0)

    # Controle de tempo
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True))
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # Em segundos
    actual_duration = Column(Integer, nullable=True)  # Em segundos

    # Logs e debugging
    execution_log = Column(Text, nullable=True)
    error_message = Column(Text)
    error_details = Column(JSON, nullable=True)
    debug_info = Column(JSON, nullable=True)

    # Configurações
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    auto_retry = Column(Boolean, default=True)
    notify_on_completion = Column(Boolean, default=True)
    notify_on_failure = Column(Boolean, default=True)

    # Metadados
    tags = Column(JSON, nullable=True)  # Tags para organização
    meta_data = Column(JSON, nullable=True)  # Metadados adicionais

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    workflow = relationship("Workflow", back_populates="executions")
    user = relationship("User", back_populates="workflow_executions")
    node_executions = relationship(
        "NodeExecution",
        back_populates="workflow_execution",
        cascade="all, delete-orphan",
    )
    metrics = relationship(
        "WorkflowExecutionMetric",
        back_populates="workflow_execution",
        cascade="all, delete-orphan",
    )
    queue_entries = relationship(
        "WorkflowExecutionQueue",
        back_populates="workflow_execution",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, execution_id='{self.execution_id}', status='{self.status}')>"

    @property
    def is_running(self) -> bool:
        """Verifica se a execução está em andamento"""
        return self.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]

    @property
    def is_completed(self) -> bool:
        """Verifica se a execução foi concluída"""
        return self.status in [
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.TIMEOUT,
        ]

    @property
    def duration_seconds(self) -> int | None:
        """Calcula a duração da execução em segundos"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        elif self.started_at:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return None

    def update_progress(self):
        """Atualiza o progresso baseado nos nós executados"""
        if self.total_nodes > 0:
            self.progress_percentage = int(
                (self.completed_nodes / self.total_nodes) * 100
            )
        else:
            self.progress_percentage = 0


# COMENTADO: Esta classe duplica a tabela com NodeExecution em node_execution.py
# Use NodeExecution de node_execution.py ao invés desta classe
#
# class NodeExecution(Base):
#     """
#     Modelo para execução de nós individuais
#     Rastreia o estado de cada nó durante a execução
#     """
#
#     __tablename__ = "node_executions"
#     __table_args__ = {"schema": "synapscale_db"}
#
#     # Campos principais
#     id = Column(Integer, primary_key=True, index=True)

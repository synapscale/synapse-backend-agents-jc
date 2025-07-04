"""
Modelos para templates de workflows
Sistema completo de marketplace de templates
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    DECIMAL,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSON, JSONB
from sqlalchemy.orm import relationship

from synapse.database import Base


class TemplateCategory(str, Enum):
    """Categorias de templates"""
    AUTOMATION = "automation"
    DATA_PROCESSING = "data_processing"
    AI_WORKFLOWS = "ai_workflows"
    MARKETING = "marketing"
    PRODUCTIVITY = "productivity"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    CONTENT_CREATION = "content_creation"
    CUSTOMER_SERVICE = "customer_service"
    FINANCE = "finance"
    HR = "hr"
    SALES = "sales"
    OTHER = "other"


class TemplateStatus(str, Enum):
    """Status do template"""
    DRAFT = "draft"
    PUBLISHED = "published"
    FEATURED = "featured"
    DEPRECATED = "deprecated"
    PRIVATE = "private"


class TemplateLicense(str, Enum):
    """Licenças de templates"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class TemplateReview(Base):
    """
    Modelo para avaliações de templates
    """

    __tablename__ = "template_reviews"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_templates.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )

    # Avaliação
    rating = Column(Integer, nullable=False)  # 1-5 estrelas
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Aspectos específicos (1-5)
    ease_of_use = Column(Integer, nullable=True)
    documentation_quality = Column(Integer, nullable=True)
    performance = Column(Integer, nullable=True)
    value_for_money = Column(Integer, nullable=True)

    # Status
    is_verified_purchase = Column(Boolean, default=False)
    is_helpful_count = Column(Integer, default=0)
    is_reported = Column(Boolean, default=False)

    # Metadados
    version_reviewed = Column(String(20), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    template = relationship("WorkflowTemplate", back_populates="reviews")
    user = relationship("User", back_populates="template_reviews")
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
        index=True,
    )
    tenant = relationship(
        "synapse.models.tenant.Tenant",
        back_populates="template_reviews"
    )

    def __repr__(self):
        return f"<TemplateReview(id={self.id}, rating={self.rating}, template_id={self.template_id})>"


class TemplateDownload(Base):
    """
    Modelo para rastreamento de downloads de templates
    """

    __tablename__ = "template_downloads"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_templates.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
        index=True,
    )

    # Informações do download
    download_type = Column(String(20), default="full")  # full, preview, demo
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Metadados
    template_version = Column(String(20), nullable=True)

    # Timestamps
    downloaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relacionamentos
    template = relationship("WorkflowTemplate", back_populates="downloads")
    user = relationship("User", back_populates="template_downloads")
    tenant = relationship(
        "synapse.models.tenant.Tenant",
        back_populates="template_downloads"
    )

    def __repr__(self):
        return f"<TemplateDownload(id={self.id}, template_id={self.template_id}, user_id={self.user_id})>"


class TemplateFavorite(Base):
    """
    Modelo para templates favoritos dos usuários
    """

    __tablename__ = "template_favorites"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_templates.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
        index=True,
    )

    # Metadados
    notes = Column(Text, nullable=True)  # Notas pessoais do usuário

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    template = relationship("WorkflowTemplate", back_populates="favorites")
    user = relationship("User", back_populates="favorite_templates")
    tenant = relationship(
        "synapse.models.tenant.Tenant",
        back_populates="template_favorites"
    )

    def __repr__(self):
        return f"<TemplateFavorite(id={self.id}, template_id={self.template_id}, user_id={self.user_id})>"


class TemplateCollection(Base):
    """
    Modelo para coleções de templates
    Permite agrupar templates relacionados
    """

    __tablename__ = "template_collections"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String(36), unique=True, index=True)

    # Informações básicas
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Relacionamentos
    creator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
        index=True,
    )

    # Configurações
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Metadados
    template_ids = Column(JSONB, nullable=False)  # Lista de IDs de templates
    tags = Column(JSONB, nullable=True)

    # Recursos visuais
    thumbnail_url = Column(String(500), nullable=True)

    # Estatísticas
    view_count = Column(Integer, default=0)
    follow_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    creator = relationship("User", back_populates="template_collections")
    tenant = relationship("synapse.models.tenant.Tenant", back_populates="template_collections")

    def __repr__(self):
        return f"<TemplateCollection(id={self.id}, name='{self.name}', creator_id={self.creator_id})>"


class TemplateUsage(Base):
    """
    Modelo para rastreamento de uso de templates
    Analytics detalhados de como os templates são usados
    """

    __tablename__ = "template_usage"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos principais
    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_templates.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
        index=True,
    )
    workflow_id = Column(Integer, ForeignKey("synapscale_db.workflows.id"), nullable=True, index=True)

    # Informações de uso
    usage_type = Column(String(20), nullable=False)  # create, clone, execute, modify
    success = Column(Boolean, default=True)

    # Metadados
    template_version = Column(String(20), nullable=True)
    modifications_made = Column(JSONB, nullable=True)  # Modificações feitas pelo usuário
    execution_time = Column(Integer, nullable=True)  # Tempo de execução em segundos

    # Contexto
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    used_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relacionamentos
    template = relationship("WorkflowTemplate")
    user = relationship("User", back_populates="template_usage")
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.tenants.id"),
        nullable=False,
        index=True
    )
    tenant = relationship(
        "synapse.models.tenant.Tenant",
        back_populates="template_usage"
    )
    workflow = relationship("Workflow")

    def __repr__(self):
        return f"<TemplateUsage(id={self.id}, template_id={self.template_id}, usage_type='{self.usage_type}')>"

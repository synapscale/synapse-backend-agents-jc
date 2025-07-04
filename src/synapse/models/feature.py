from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid


class Feature(Base):
    __tablename__ = "features"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Estrutura EXATA do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, nullable=False)  # Chave única da feature
    name = Column(String, nullable=False)  # Nome legível da feature
    description = Column(Text)  # Descrição detalhada
    category = Column(String)  # Categoria para organização
    is_active = Column(Boolean, default=True)  # Feature ativa
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    plan_features = relationship("PlanFeature", back_populates="feature", cascade="all, delete-orphan")
    plan_entitlements = relationship("PlanEntitlement", back_populates="feature", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Feature(id={self.id}, key='{self.key}', name='{self.name}')>"

    @property
    def code(self):
        """Compatibilidade com API: mapeia key para code"""
        return self.key

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "key": self.key,
            "code": self.code,  # Para compatibilidade com API
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WorkspaceFeature(Base):
    """Features customizadas por workspace"""

    __tablename__ = "workspace_features"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos EXATOS da estrutura do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False
    )
    feature_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.features.id"), nullable=False
    )
    is_enabled = Column(Boolean, default=True)
    config = Column(JSONB, default=dict)
    usage_count = Column(Integer, default=0)
    limit_value = Column(Integer)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False
    )

    # Relacionamentos
    workspace = relationship("Workspace", back_populates="workspace_features")
    feature = relationship("Feature")
    tenant = relationship(
        "synapse.models.tenant.Tenant",
        back_populates="workspace_features"
    )

    def __repr__(self):
        return f"<WorkspaceFeature(workspace_id={self.workspace_id}, feature_id={self.feature_id})>"

    def is_available(self) -> bool:
        """Verifica se a feature está disponível"""
        if not self.is_enabled:
            return False
        if self.expires_at and self.expires_at < func.now():
            return False
        return True

    def can_use(self) -> bool:
        """Verifica se a feature pode ser usada (considerando limites)"""
        if not self.is_available():
            return False
        if self.limit_value and self.usage_count >= self.limit_value:
            return False
        return True

    def increment_usage(self):
        """Incrementa o contador de uso"""
        self.usage_count += 1

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "feature_id": str(self.feature_id),
            "tenant_id": str(self.tenant_id),
            "is_enabled": self.is_enabled,
            "config": self.config,
            "usage_count": self.usage_count,
            "limit_value": self.limit_value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_available": self.is_available(),
            "can_use": self.can_use(),
        }

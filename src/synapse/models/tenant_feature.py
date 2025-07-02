from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from synapse.database import Base
import uuid


class TenantFeature(Base):
    """Features por tenant - estrutura EXATA do banco de dados"""

    __tablename__ = "tenant_features"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos EXATOS da estrutura do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False
    )
    feature_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.features.id"), nullable=False
    )
    is_enabled = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    limit_value = Column(Integer)
    config = Column(JSONB, default=dict)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="tenant_features")
    feature = relationship("Feature")

    def __repr__(self):
        return (
            f"<TenantFeature(tenant_id={self.tenant_id}, feature_id={self.feature_id})>"
        )

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

    def reset_usage(self):
        """Reseta o contador de uso"""
        self.usage_count = 0

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "feature_id": str(self.feature_id),
            "is_enabled": self.is_enabled,
            "usage_count": self.usage_count,
            "limit_value": self.limit_value,
            "config": self.config,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_available": self.is_available(),
            "can_use": self.can_use(),
        }

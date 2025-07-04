import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from synapse.database import Base


class ComponentVersion(Base):
    __tablename__ = "component_versions"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    component_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.marketplace_components.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id", ondelete="CASCADE"), nullable=True)
    
    # Version information
    version = Column(String(20), nullable=False)
    is_latest = Column(Boolean, nullable=False)
    is_stable = Column(Boolean, nullable=False)
    
    # Documentation
    changelog = Column(Text)
    breaking_changes = Column(Text)
    migration_guide = Column(Text)
    
    # Technical details
    component_data = Column(JSONB, nullable=False)
    file_size = Column(Integer)
    min_platform_version = Column(String(20))
    max_platform_version = Column(String(20))
    dependencies = Column(JSONB)
    
    # Statistics
    download_count = Column(Integer, nullable=False, default=0)
    
    # Status
    status = Column(String(20), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deprecated_at = Column(DateTime(timezone=True))

    # Relationships
    tenant = relationship("Tenant", back_populates="component_versions")
    component = relationship("MarketplaceComponent", back_populates="versions")

    def __repr__(self):
        return f"<ComponentVersion(id={self.id}, version='{self.version}', status='{self.status}')>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "component_id": str(self.component_id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "version": self.version,
            "is_latest": self.is_latest,
            "is_stable": self.is_stable,
            "changelog": self.changelog,
            "breaking_changes": self.breaking_changes,
            "migration_guide": self.migration_guide,
            "component_data": self.component_data,
            "file_size": self.file_size,
            "min_platform_version": self.min_platform_version,
            "max_platform_version": self.max_platform_version,
            "dependencies": self.dependencies,
            "download_count": self.download_count,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
        } 
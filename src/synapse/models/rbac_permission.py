"""RBAC Permission Model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class RBACPermission(Base):
    """Role-Based Access Control permissions"""
    
    __tablename__ = "rbac_permissions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    key = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    resource = Column(String(100), nullable=True)
    action = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="rbac_permissions")
    role_permissions = relationship("RBACRolePermission", back_populates="permission")

    def __str__(self):
        return f"RBACPermission({self.key})"

    @property
    def full_permission(self):
        """Get full permission string in format resource:action"""
        if self.resource and self.action:
            return f"{self.resource}:{self.action}"
        return self.key

    @classmethod
    def get_by_key(cls, session, key, tenant_id=None):
        """Get permission by key with optional tenant scoping"""
        query = session.query(cls).filter(cls.key == key)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        return query.first()

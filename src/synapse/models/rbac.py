"""
RBAC models aggregator - importa todos os modelos relacionados a RBAC
"""

from .rbac_role import RBACRole
from .rbac_permission import RBACPermission
from .rbac_role_permission import RBACRolePermission

# Aliases para compatibilidade com endpoints
RbacRole = RBACRole
RbacPermission = RBACPermission
RbacRolePermission = RBACRolePermission

# Exportar para que possam ser importados com from synapse.models.rbac import ...
__all__ = [
    'RBACRole',
    'RBACPermission', 
    'RBACRolePermission',
    'RbacRole',
    'RbacPermission',
    'RbacRolePermission',
]

# Modelo adicional que pode estar sendo usado
try:
    from .user_tenant_role import UserTenantRole
    __all__.append('UserTenantRole')
except ImportError:
    # Criar um placeholder se não existir
    from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
    from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
    from sqlalchemy.orm import relationship
    from sqlalchemy.sql import func
    import uuid

    from synapse.database import Base

    class UserTenantRole(Base):
        """Modelo de role de usuário por tenant"""
        __tablename__ = "user_tenant_roles"
        __table_args__ = {"schema": "synapscale_db"}
        
        id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
        user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
        role_id = Column(PostgresUUID(as_uuid=True), ForeignKey("synapscale_db.rbac_roles.id"), nullable=False)
        tenant_id = Column(PostgresUUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
        granted = Column(Boolean, server_default="true")
        conditions = Column(JSONB, server_default="{}")
        created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
        updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
        
        # Relacionamentos
        user = relationship("User", back_populates="tenant_roles")
        role = relationship("RBACRole", back_populates="user_assignments")
        tenant = relationship("Tenant", back_populates="user_roles")
    
    __all__.append('UserTenantRole') 
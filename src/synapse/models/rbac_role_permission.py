"""RBAC Role Permission Model"""

from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class RBACRolePermission(Base):
    """Role-Permission assignment with conditions"""
    
    __tablename__ = "rbac_role_permissions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    role_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.rbac_roles.id"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.rbac_permissions.id"), nullable=False)
    granted = Column(Boolean, nullable=True, server_default="true")
    conditions = Column(JSONB, nullable=True, server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    role = relationship("RBACRole", back_populates="permissions")
    permission = relationship("RBACPermission", back_populates="role_permissions")
    tenant = relationship("Tenant", back_populates="rbac_role_permissions")

    def __str__(self):
        status = "granted" if self.granted else "denied"
        return f"RBACRolePermission(role={self.role_id}, permission={self.permission_id}, {status})"

    def is_granted(self, context=None):
        """Check if permission is granted with optional context evaluation"""
        if not self.granted:
            return False
        
        # If no conditions, permission is granted
        if not self.conditions:
            return True
        
        # Evaluate conditions against context
        if context:
            return self._evaluate_conditions(context)
        
        return True

    def _evaluate_conditions(self, context):
        """Evaluate permission conditions against provided context"""
        if not self.conditions or not context:
            return True
        
        # Simple condition evaluation (can be extended)
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            context_value = context[key]
            
            # Handle different condition types
            if isinstance(expected_value, dict):
                if "$in" in expected_value:
                    if context_value not in expected_value["$in"]:
                        return False
                elif "$eq" in expected_value:
                    if context_value != expected_value["$eq"]:
                        return False
                elif "$ne" in expected_value:
                    if context_value == expected_value["$ne"]:
                        return False
            else:
                if context_value != expected_value:
                    return False
        
        return True

    @classmethod
    def has_permission(cls, session, role_id, permission_key, tenant_id=None, context=None):
        """Check if role has specific permission"""
        query = session.query(cls).join(cls.permission).filter(
            cls.role_id == role_id,
            cls.permission.has(key=permission_key)
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        role_permission = query.first()
        if not role_permission:
            return False
        
        return role_permission.is_granted(context)

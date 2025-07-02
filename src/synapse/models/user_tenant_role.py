"""
Model para roles de usuários por tenant
ALINHADO PERFEITAMENTE COM A TABELA user_tenant_roles
"""

from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone, timedelta
from synapse.database import Base


class UserTenantRole(Base):
    """Model para roles de usuários por tenant - ALINHADO COM user_tenant_roles TABLE"""

    __tablename__ = "user_tenant_roles"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False
    )
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.rbac_roles.id"), nullable=False
    )
    granted_by = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True
    )
    granted_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, server_default=func.true())
    conditions = Column(JSONB, server_default=func.text("'{}'::jsonb"))
    created_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )

    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id], back_populates="tenant_roles")
    tenant = relationship("Tenant", back_populates="user_roles")
    role = relationship("RBACRole", back_populates="user_assignments")
    granter = relationship("User", foreign_keys=[granted_by])

    def __repr__(self):
        return f"<UserTenantRole(id={self.id}, user_id={self.user_id}, tenant_id={self.tenant_id}, role_id={self.role_id})>"

    def is_valid(self):
        """Verifica se o role assignment é válido"""
        if not self.is_active:
            return False

        if self.expires_at:
            from datetime import datetime, timezone

            return datetime.now(timezone.utc) < self.expires_at

        return True

    def is_expired(self):
        """Verifica se o role assignment está expirado"""
        if not self.expires_at:
            return False

        return datetime.now(timezone.utc) >= self.expires_at

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "tenant_id": str(self.tenant_id),
            "role_id": str(self.role_id),
            "granted_by": str(self.granted_by) if self.granted_by else None,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_permanent(self) -> bool:
        """Verifica se é um role permanente (sem expiração)"""
        return self.expires_at is None

    def days_until_expiry(self) -> int:
        """Retorna quantos dias até a expiração (None se permanente)"""
        if not self.expires_at:
            return None

        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    def is_expiring_soon(self, days: int = 7) -> bool:
        """Verifica se o role está expirando em breve"""
        if not self.expires_at:
            return False

        days_left = self.days_until_expiry()
        return days_left is not None and days_left <= days

    def activate(self):
        """Ativa o role assignment"""
        self.is_active = True

    def deactivate(self):
        """Desativa o role assignment"""
        self.is_active = False

    def extend_expiry(self, days: int):
        """Estende a expiração por X dias"""
        if not self.expires_at:
            # Se não tem expiração, define uma nova data
            self.expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        else:
            # Se já tem expiração, estende
            self.expires_at += timedelta(days=days)

    def set_expiry(self, expires_at: datetime):
        """Define uma nova data de expiração"""
        self.expires_at = expires_at

    def make_permanent(self):
        """Remove a expiração, tornando o role permanente"""
        self.expires_at = None

    def get_permissions(self):
        """Retorna todas as permissões deste role assignment"""
        if not self.is_valid():
            return []
        return self.role.get_permissions() if self.role else []

    def has_permission(self, permission_key: str) -> bool:
        """Verifica se tem uma permissão específica"""
        if not self.is_valid():
            return False
        return self.role.has_permission(permission_key) if self.role else False

    @classmethod
    def assign_role(
        cls,
        user_id: str,
        tenant_id: str,
        role_id: str,
        granted_by: str = None,
        expires_at: datetime = None,
        conditions: dict = None,
    ):
        """Atribui um role a um usuário em um tenant"""
        return cls(
            user_id=user_id,
            tenant_id=tenant_id,
            role_id=role_id,
            granted_by=granted_by,
            expires_at=expires_at,
            conditions=conditions or {},
        )

    @classmethod
    def find_user_roles(
        cls, session, user_id: str, tenant_id: str = None, active_only: bool = True
    ):
        """Busca todos os roles de um usuário"""
        query = session.query(cls).filter(cls.user_id == user_id)

        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)

        if active_only:
            query = query.filter(cls.is_active == True)

        return query.all()

    @classmethod
    def user_has_role(
        cls, session, user_id: str, tenant_id: str, role_name: str
    ) -> bool:
        """Verifica se um usuário tem um role específico em um tenant"""
        from synapse.models.rbac_role import RBACRole

        return (
            session.query(cls)
            .join(RBACRole)
            .filter(
                cls.user_id == user_id,
                cls.tenant_id == tenant_id,
                RBACRole.name == role_name,
                cls.is_active == True,
            )
            .first()
            is not None
        )

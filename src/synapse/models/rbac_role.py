"""
Model para roles RBAC
ALINHADO PERFEITAMENTE COM A TABELA rbac_roles
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from synapse.database import Base


class RBACRole(Base):
    """Model para roles RBAC - ALINHADO COM rbac_roles TABLE"""

    __tablename__ = "rbac_roles"
    __table_args__ = {"schema": "synapscale_db"}

    # Campos exatos da tabela
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, server_default=func.false())
    role_metadata = Column("metadata", JSONB, server_default=func.text("'{}'::jsonb"))
    created_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True
    )

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="rbac_roles")
    permissions = relationship(
        "RBACRolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    user_assignments = relationship(
        "UserTenantRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<RBACRole(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"
        )

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "is_system": self.is_system,
            "metadata": self.role_metadata,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_permissions(self):
        """Retorna todas as permissões ativas deste role"""
        return [rp.permission for rp in self.permissions if rp.granted]

    def has_permission(self, permission_key):
        """Verifica se o role tem uma permissão específica"""
        for rp in self.permissions:
            if rp.granted and rp.permission.key == permission_key:
                return True
        return False

    def is_global(self) -> bool:
        """Verifica se é um role global"""
        return self.tenant_id is None

    def get_users(self):
        """Retorna todos os usuários que têm este role"""
        return [ua.user for ua in self.user_assignments]

    def is_assigned_to_user(self, user_id) -> bool:
        """Verifica se este role está atribuído a um usuário específico"""
        for ua in self.user_assignments:
            if ua.user_id == user_id:
                return True
        return False

    def add_permission(self, permission_id, granted=True, conditions=None):
        """Adiciona uma permissão ao role"""
        from synapse.models.rbac_role_permission import RBACRolePermission

        role_permission = RBACRolePermission(
            role_id=self.id,
            permission_id=permission_id,
            granted=granted,
            conditions=conditions or {},
            tenant_id=self.tenant_id,
        )
        return role_permission

    def remove_permission(self, permission_id):
        """Remove uma permissão do role"""
        for rp in self.permissions:
            if rp.permission_id == permission_id:
                self.permissions.remove(rp)
                return True
        return False

    @classmethod
    def create_system_role(
        cls, name: str, description: str, tenant_id: str = None, metadata: dict = None
    ):
        """Cria um role do sistema"""
        return cls(
            name=name,
            description=description,
            is_system=True,
            tenant_id=tenant_id,
            role_metadata=metadata or {},
        )

    @classmethod
    def create_custom_role(
        cls, name: str, description: str, tenant_id: str, metadata: dict = None
    ):
        """Cria um role customizado para um tenant"""
        return cls(
            name=name,
            description=description,
            is_system=False,
            tenant_id=tenant_id,
            role_metadata=metadata or {},
        )

    @classmethod
    def find_by_name(cls, session, name: str, tenant_id: str = None):
        """Busca um role pelo nome e tenant"""
        query = session.query(cls).filter(cls.name == name)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        else:
            query = query.filter(cls.tenant_id.is_(None))
        return query.first()

    @classmethod
    def get_system_roles(cls, session, tenant_id: str = None):
        """Retorna todos os roles do sistema"""
        query = session.query(cls).filter(cls.is_system == True)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        return query.all()

    @classmethod
    def get_custom_roles(cls, session, tenant_id: str):
        """Retorna todos os roles customizados de um tenant"""
        return (
            session.query(cls)
            .filter(cls.is_system == False, cls.tenant_id == tenant_id)
            .all()
        )

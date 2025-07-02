"""
Serviço de Multi-Tenancy
Gerencia contexto de tenant e isolamento de dados
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from synapse.models import Tenant, User, Workspace
from synapse.core.services.base_service import BaseService


class TenantService(BaseService):
    """Serviço para gerenciar multi-tenancy"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.current_tenant_id: Optional[UUID] = None

    def set_current_tenant(self, tenant_id: UUID) -> None:
        """Define o tenant atual para o contexto da requisição"""
        self.current_tenant_id = tenant_id

    def get_current_tenant(self) -> Optional[Tenant]:
        """Obtém o tenant atual"""
        if not self.current_tenant_id:
            return None
        return self.db.query(Tenant).filter(Tenant.id == self.current_tenant_id).first()

    def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Obtém tenant por ID"""
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Obtém tenant por slug"""
        return self.db.query(Tenant).filter(Tenant.slug == slug).first()

    def get_user_tenant(self, user_id: UUID) -> Optional[Tenant]:
        """Obtém o tenant de um usuário através de workspace_members"""
        from synapse.models import WorkspaceMember

        # Buscar através de workspace_members -> workspace -> tenant
        result = (
            self.db.query(Tenant)
            .join(Workspace, Workspace.tenant_id == Tenant.id)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .filter(WorkspaceMember.user_id == user_id)
            .first()
        )
        return result

    def user_has_access_to_tenant(self, user_id: UUID, tenant_id: UUID) -> bool:
        """Verifica se um usuário tem acesso a um tenant"""
        from synapse.models import WorkspaceMember

        # Verificar se o usuário é membro de algum workspace do tenant
        result = (
            self.db.query(WorkspaceMember)
            .join(Workspace, WorkspaceMember.workspace_id == Workspace.id)
            .filter(
                and_(
                    WorkspaceMember.user_id == user_id, Workspace.tenant_id == tenant_id
                )
            )
            .first()
        )
        return result is not None

    def get_user_tenants(self, user_id: UUID) -> List[Tenant]:
        """Obtém todos os tenants que um usuário tem acesso"""
        from synapse.models import WorkspaceMember

        return (
            self.db.query(Tenant)
            .join(Workspace, Workspace.tenant_id == Tenant.id)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .filter(WorkspaceMember.user_id == user_id)
            .distinct()
            .all()
        )

    def create_tenant(
        self, name: str, slug: str, description: Optional[str] = None, **kwargs
    ) -> Tenant:
        """Cria um novo tenant"""
        tenant = Tenant(name=name, slug=slug, description=description, **kwargs)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def update_tenant(
        self, tenant_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Tenant]:
        """Atualiza um tenant"""
        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return None

        for key, value in updates.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def delete_tenant(self, tenant_id: UUID) -> bool:
        """Deleta um tenant (soft delete)"""
        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return False

        tenant.status = TenantStatus.SUSPENDED
        self.db.commit()
        return True

    def get_tenant_workspaces(self, tenant_id: UUID) -> List[Workspace]:
        """Obtém todos os workspaces de um tenant"""
        return self.db.query(Workspace).filter(Workspace.tenant_id == tenant_id).all()

    def get_tenant_users(self, tenant_id: UUID) -> List[User]:
        """Obtém todos os usuários de um tenant"""
        from synapse.models import WorkspaceMember

        return (
            self.db.query(User)
            .join(WorkspaceMember, WorkspaceMember.user_id == User.id)
            .join(Workspace, WorkspaceMember.workspace_id == Workspace.id)
            .filter(Workspace.tenant_id == tenant_id)
            .distinct()
            .all()
        )

    def get_tenant_stats(self, tenant_id: UUID) -> Dict[str, Any]:
        """Obtém estatísticas do tenant"""
        from synapse.models import WorkspaceMember, Conversation, Message

        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return {}

        # Contar workspaces
        workspace_count = (
            self.db.query(Workspace).filter(Workspace.tenant_id == tenant_id).count()
        )

        # Contar usuários únicos
        user_count = (
            self.db.query(User.id)
            .join(WorkspaceMember, WorkspaceMember.user_id == User.id)
            .join(Workspace, WorkspaceMember.workspace_id == Workspace.id)
            .filter(Workspace.tenant_id == tenant_id)
            .distinct()
            .count()
        )

        # Contar conversas
        conversation_count = (
            self.db.query(Conversation)
            .filter(Conversation.tenant_id == tenant_id)
            .count()
        )

        # Contar mensagens
        message_count = (
            self.db.query(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Conversation.tenant_id == tenant_id)
            .count()
        )

        return {
            "tenant_id": str(tenant_id),
            "tenant_name": tenant.name,
            "workspace_count": workspace_count,
            "user_count": user_count,
            "conversation_count": conversation_count,
            "message_count": message_count,
            "status": tenant.status.value,
            "created_at": tenant.created_at.isoformat(),
        }

    def apply_tenant_filter(self, query, model_class, tenant_id: Optional[UUID] = None):
        """Aplica filtro de tenant em uma query"""
        if tenant_id is None:
            tenant_id = self.current_tenant_id

        if not tenant_id:
            return query

        # Verificar se o modelo tem tenant_id
        if hasattr(model_class, "tenant_id"):
            return query.filter(model_class.tenant_id == tenant_id)

        # Para modelos que não têm tenant_id direto, usar relacionamentos
        if model_class.__name__ == "Message":
            return query.join(Conversation).filter(Conversation.tenant_id == tenant_id)

        return query

    def ensure_tenant_access(self, user_id: UUID, tenant_id: UUID) -> bool:
        """Garante que um usuário tem acesso ao tenant"""
        if not self.user_has_access_to_tenant(user_id, tenant_id):
            raise PermissionError(
                f"User {user_id} does not have access to tenant {tenant_id}"
            )
        return True


class TenantContext:
    """Context manager para definir tenant atual"""

    def __init__(self, tenant_service: TenantService, tenant_id: UUID):
        self.tenant_service = tenant_service
        self.tenant_id = tenant_id
        self.previous_tenant_id = None

    def __enter__(self):
        self.previous_tenant_id = self.tenant_service.current_tenant_id
        self.tenant_service.set_current_tenant(self.tenant_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tenant_service.current_tenant_id = self.previous_tenant_id

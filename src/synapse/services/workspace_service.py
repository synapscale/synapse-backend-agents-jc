"""
Serviço de gerenciamento de workspaces com validações rigorosas e sincronização automática
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta, timezone
import uuid
import secrets
import logging

from synapse.models.workspace import Workspace, WorkspaceType
from synapse.models.user import User
from synapse.schemas.models import (
    WorkspaceCreate,
    WorkspaceUpdate,
    MemberInvite,
    ProjectCreate,
    ProjectUpdate,
    CommentCreate,
)
from synapse.models.subscription import UserSubscription, PlanType, SubscriptionStatus
from synapse.models.tenant import Tenant, TenantStatus
from synapse.models.plan import Plan
from synapse.models.workspace_member import WorkspaceMember, WorkspaceRole
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.workspace_invitation import WorkspaceInvitation

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Serviço para gerenciamento de workspaces com sincronização automática"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== WORKSPACES ====================

    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Obtém assinatura ativa do usuário"""
        return (
            self.db.query(UserSubscription)
            .join(Plan)
            .filter(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.status == SubscriptionStatus.ACTIVE,
                )
            )
            .first()
        )

    def can_create_workspace(self, user_id: str) -> Dict[str, Any]:
        """Verifica se o usuário pode criar um novo workspace"""
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return {
                "can_create": False,
                "reason": "Usuário não possui assinatura ativa",
                "max_workspaces": 0,
                "current_workspaces": 0,
            }

        current_count = (
            self.db.query(Workspace).filter(Workspace.owner_id == user_id).count()
        )

        can_create = current_count < subscription.plan.max_workspaces

        return {
            "can_create": can_create,
            "reason": "Limite de workspaces atingido" if not can_create else None,
            "max_workspaces": subscription.plan.max_workspaces,
            "current_workspaces": current_count,
            "plan_name": subscription.plan.name,
        }

    def can_create_collaborative_workspace(self, user_id: str) -> Dict[str, Any]:
        """Verifica se o usuário pode criar workspaces colaborativos"""
        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return {
                "can_create": False,
                "reason": "Usuário não possui assinatura ativa",
            }

        if not subscription.plan.allow_collaborative_workspaces:
            return {
                "can_create": False,
                "reason": f"Plano {subscription.plan.name} não permite workspaces colaborativos",
            }

        workspace_check = self.can_create_workspace(user_id)
        return workspace_check

    def _create_workspace_complete(
        self, user_id: str, workspace_data: WorkspaceCreate
    ) -> Workspace:
        """
        Cria um novo workspace com validações rigorosas de plano (método de instância)
        """
        try:
            # Obter usuário
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuário não encontrado")

            # Determinar tipo do workspace
            workspace_type = (
                workspace_data.type if hasattr(workspace_data, "type") else None
            )
            if not workspace_type:
                # Se não especificado, determinar automaticamente
                rules = self.get_workspace_creation_rules(user_id)
                if not rules["has_individual_workspace"]:
                    workspace_type = WorkspaceType.INDIVIDUAL
                elif rules["can_create_collaborative"]:
                    workspace_type = WorkspaceType.COLLABORATIVE
                else:
                    raise ValueError("Não é possível determinar o tipo de workspace")

            # Validar se pode criar workspace
            validation = self._validate_workspace_creation(user_id, workspace_type)
            if not validation["can_create"]:
                raise ValueError(validation["reason"])

            # Criar workspace usando método correto
            workspace = self._create_workspace_record(
                user=user,
                name=workspace_data.name,
                description=workspace_data.description,
                workspace_type=workspace_type,
            )

            # Criar membership do owner
            self._create_owner_membership(workspace, user)

            # Registrar atividade
            self._register_workspace_activity(
                workspace=workspace,
                user=user,
                action="workspace_created",
                description=f"Workspace '{workspace.name}' foi criado como {workspace_type.value}",
            )

            # Atualizar contadores da assinatura
            self._update_subscription_counters(user_id, increment_workspaces=1)

            # Commit da transação
            self.db.commit()

            logger.info(
                f"Workspace '{workspace.name}' criado com sucesso para usuário {user_id}"
            )
            return workspace

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar workspace: {e}")
            raise e

    @staticmethod
    def create_workspace(
        db: Session, workspace_data: WorkspaceCreate, user_id: str, tenant_id: str
    ) -> Workspace:
        """Criar um novo workspace"""
        workspace = Workspace(
            **workspace_data.dict(), user_id=user_id, tenant_id=tenant_id
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def get_user_workspaces(
        db: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        """Obter workspaces do usuário"""
        return (
            db.query(Workspace)
            .filter(Workspace.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_workspace_by_id(
        db: Session, workspace_id: str, user_id: str
    ) -> Optional[Workspace]:
        """Obter workspace por ID (verificando se pertence ao usuário)"""
        return (
            db.query(Workspace)
            .filter(and_(Workspace.id == workspace_id, Workspace.user_id == user_id))
            .first()
        )

    @staticmethod
    def update_workspace(
        db: Session, workspace: Workspace, workspace_data: WorkspaceUpdate
    ) -> Workspace:
        """Atualizar workspace"""
        for field, value in workspace_data.dict(exclude_unset=True).items():
            setattr(workspace, field, value)

        db.commit()
        db.refresh(workspace)
        return workspace

    @staticmethod
    def delete_workspace(db: Session, workspace: Workspace) -> None:
        """Deletar workspace"""
        db.delete(workspace)
        db.commit()

    def _validate_workspace_creation(
        self, user_id: str, workspace_type: Optional[WorkspaceType]
    ) -> Dict[str, Any]:
        """Validações rigorosas antes de criar workspace"""

        # 1. Verificar assinatura ativa
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return {
                "can_create": False,
                "reason": "Usuário não possui assinatura ativa",
                "error_code": "NO_SUBSCRIPTION",
            }

        # 2. Verificar limites do plano
        plan = subscription.plan
        current_workspaces = subscription.current_workspaces or 0

        if current_workspaces >= plan.max_workspaces:
            return {
                "can_create": False,
                "reason": f"Limite de workspaces atingido ({current_workspaces}/{plan.max_workspaces}). Faça upgrade do seu plano.",
                "error_code": "WORKSPACE_LIMIT_REACHED",
            }

        # 3. Verificar regra de workspace individual (apenas 1 permitido)
        if workspace_type == WorkspaceType.INDIVIDUAL:
            individual_count = self._count_individual_workspaces(user_id)
            if individual_count >= 1:
                return {
                    "can_create": False,
                    "reason": "Você já possui um workspace individual. Apenas 1 workspace individual é permitido por usuário.",
                    "error_code": "INDIVIDUAL_LIMIT_REACHED",
                }

        # 4. Verificar se plano permite workspaces colaborativos
        if workspace_type == WorkspaceType.COLLABORATIVE:
            if not plan.allow_collaborative_workspaces:
                return {
                    "can_create": False,
                    "reason": f"Seu plano {plan.name} não permite workspaces colaborativos. Faça upgrade para criar workspaces de equipe.",
                    "error_code": "COLLABORATIVE_NOT_ALLOWED",
                }

        return {"can_create": True, "reason": "Validação passou"}

    def _determine_workspace_type(
        self, user_id: str, requested_type: Optional[WorkspaceType]
    ) -> WorkspaceType:
        """
        Determina o tipo de workspace seguindo as regras:
        1. Se é o primeiro workspace do usuário → individual (obrigatório)
        2. Se já tem workspace individual → collaborative (obrigatório)
        3. Se especificou individual mas já tem um → força collaborative
        """
        individual_count = self._count_individual_workspaces(user_id)
        total_count = self._count_total_workspaces(user_id)

        # Primeiro workspace sempre individual
        if total_count == 0:
            logger.info("Primeiro workspace do usuário - forçando tipo individual")
            return WorkspaceType.INDIVIDUAL

        # Se já tem workspace individual, próximos são colaborativos
        if individual_count >= 1:
            if requested_type == WorkspaceType.INDIVIDUAL:
                logger.warning(
                    "Usuário tentou criar segundo workspace individual - forçando collaborative"
                )
            return WorkspaceType.COLLABORATIVE

        # Se não tem individual ainda, pode criar
        return requested_type or WorkspaceType.INDIVIDUAL

    def _get_plan_for_workspace_type(
        self, workspace_type: WorkspaceType
    ) -> Optional[Plan]:
        """
        Determina o plano baseado no tipo de workspace
        - Individual: sempre plano 'free'
        - Collaborative: plano baseado na assinatura do usuário
        """
        try:
            if workspace_type == WorkspaceType.INDIVIDUAL:
                # Workspace individual sempre usa plano free
                plan = (
                    self.db.query(Plan)
                    .filter(
                        Plan.slug == "free",  # Busca por slug ao invés de type
                        Plan.is_active == True,
                    )
                    .first()
                )

                if not plan:
                    logger.error("Plano 'free' não encontrado no banco")
                    return None

                logger.info(f"Plano 'free' selecionado para workspace individual")
                return plan

            else:  # WorkspaceType.COLLABORATIVE
                # Para workspace colaborativo, usar plano da assinatura
                # Por enquanto, usar plano 'free' como padrão
                # TODO: Implementar lógica baseada na assinatura do usuário
                plan = (
                    self.db.query(Plan)
                    .filter(
                        Plan.slug == "free",  # Busca por slug ao invés de type
                        Plan.is_active == True,
                    )
                    .first()
                )

                if not plan:
                    logger.error("Plano padrão não encontrado no banco")
                    return None

                logger.info(
                    f"Plano '{plan.slug}' selecionado para workspace colaborativo"
                )
                return plan

        except Exception as e:
            logger.error(f"Erro ao determinar plano para workspace: {e}")
            return None

    def _create_workspace_record(
        self,
        user: User,
        name: str,
        description: Optional[str],
        workspace_type: WorkspaceType,
        **kwargs,
    ) -> Workspace:
        """Cria o registro do workspace com configurações apropriadas (NOVA ARQUITETURA)"""

        # Configurações baseadas no tipo
        if workspace_type == WorkspaceType.INDIVIDUAL:
            max_members = 1
            enable_chat = False
            enable_video_calls = False
            allow_guest_access = False
        else:  # COLLABORATIVE
            max_members = kwargs.get("max_members", 10)
            enable_chat = kwargs.get("enable_chat", True)
            enable_video_calls = kwargs.get("enable_video_calls", True)
            allow_guest_access = kwargs.get("allow_guest_access", False)

        # NOVA ARQUITETURA: Obter ou criar tenant para o usuário
        tenant = self._get_or_create_user_tenant(user, workspace_type)

        logger.info(
            f"Usando tenant {tenant.id} (plan: {tenant.plan_id}) para workspace {name}"
        )

        # NOVA ARQUITETURA: Criar workspace com tenant_id ao invés de plan_id
        workspace = Workspace(
            id=uuid.uuid4(),
            name=name,
            slug=self._generate_unique_slug(self.db, name, user.username),
            description=description,
            type=workspace_type,
            owner_id=user.id,
            tenant_id=tenant.id,  # ✅ NOVA ARQUITETURA: tenant_id ao invés de plan_id
            is_public=kwargs.get("is_public", False),
            is_template=False,
            allow_guest_access=allow_guest_access,
            require_approval=kwargs.get("require_approval", False),
            max_members=max_members,
            max_projects=kwargs.get("max_projects", 20),
            max_storage_mb=kwargs.get("max_storage_mb", 1024),
            enable_real_time_editing=kwargs.get("enable_real_time_editing", True),
            enable_comments=kwargs.get("enable_comments", True),
            enable_chat=enable_chat,
            enable_video_calls=enable_video_calls,
            notification_settings=kwargs.get(
                "notification_settings", {"email_notifications": True}
            ),
            member_count=1,  # Será o owner
            project_count=0,
            activity_count=1,  # Atividade de criação
            storage_used_mb=0.0,
            status="active",
            last_activity_at=datetime.now(timezone.utc),
        )

        # Atualizar contador do tenant
        tenant.workspace_count = (tenant.workspace_count or 0) + 1

        self.db.add(workspace)
        self.db.flush()

        logger.info(
            f"Workspace criado: {workspace.id} (tenant: {tenant.id}, plan via tenant)"
        )
        return workspace

    def _get_or_create_user_tenant(
        self, user: User, workspace_type: WorkspaceType
    ) -> Tenant:
        """
        Obtém tenant existente do usuário ou cria um novo com plano apropriado
        NOVA ARQUITETURA: tenants são o ponto central dos planos
        """
        # Primeiro, tentar encontrar tenant existente do usuário
        # Para agora, vamos assumir que cada usuário pode ter apenas um tenant
        existing_tenant = (
            self.db.query(Tenant)
            .join(Workspace, Tenant.id == Workspace.tenant_id)
            .filter(Workspace.owner_id == user.id)
            .first()
        )

        if existing_tenant:
            logger.info(
                f"Tenant existente encontrado: {existing_tenant.id} para usuário {user.id}"
            )
            return existing_tenant

        # Se não encontrou, criar novo tenant
        logger.info(f"Criando novo tenant para usuário {user.id}")

        # Obter plano apropriado para o tipo de workspace
        plan = self._get_plan_for_workspace_type(workspace_type)
        if not plan:
            raise ValueError(
                f"Não foi possível encontrar plano para workspace tipo {workspace_type.value}"
            )

        # Criar tenant com plano
        tenant = Tenant(
            id=uuid.uuid4(),
            name=f"Tenant de {user.full_name}",
            slug=f"tenant-{user.username}-{uuid.uuid4().hex[:8]}",
            status=TenantStatus.ACTIVE.value,
            plan_id=plan.id,  # ✅ TENANT TEM O PLAN_ID
            max_workspaces=plan.max_workspaces or 3,
            max_storage_mb=plan.max_storage_mb or 1024,  # Já em MB no plano
            max_api_calls_per_day=plan.max_api_calls_per_day or 1000,
            max_members_per_workspace=plan.max_members_per_workspace or 5,
        )

        self.db.add(tenant)
        self.db.flush()

        logger.info(f"Tenant criado: {tenant.id} com plan_id: {tenant.plan_id}")
        return tenant

    def _create_owner_membership(
        self, workspace: Workspace, user: User
    ) -> WorkspaceMember:
        """Cria membership automática como OWNER"""

        membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
            status="active",
            is_favorite=workspace.type
            == WorkspaceType.INDIVIDUAL,  # Individual sempre favorito
            notification_preferences={
                "email_notifications": True,
                "push_notifications": False,
                "activity_digest": "daily",
            },
            last_seen_at=datetime.now(timezone.utc),
            joined_at=datetime.now(timezone.utc),
        )

        self.db.add(membership)
        self.db.flush()
        return membership

    def _register_workspace_activity(
        self,
        workspace: Workspace,
        user: User,
        action: str,
        description: str,
        resource_type: str = "workspace",
        meta_data: Optional[Dict] = None,
    ) -> WorkspaceActivity:
        """Registra atividade no workspace"""

        activity = WorkspaceActivity(
            id=uuid.uuid4(),
            workspace_id=workspace.id,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(workspace.id),
            description=description,
            meta_data=meta_data or {"workspace_type": workspace.type.value},
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(activity)
        self.db.flush()
        return activity

    def _update_subscription_counters(
        self, user_id: str, increment_workspaces: int = 0, increment_storage: float = 0
    ):
        """Atualiza contadores da assinatura"""

        subscription = self.get_user_subscription(user_id)
        if subscription:
            subscription.current_workspaces = (
                subscription.current_workspaces or 0
            ) + increment_workspaces
            subscription.current_storage_mb = (
                subscription.current_storage_mb or 0
            ) + increment_storage
            self.db.add(subscription)

    def delete_workspace(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Deleta um workspace (soft delete)"""
        try:
            workspace = (
                self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            )
            if not workspace:
                return {"success": False, "error": "Workspace não encontrado"}

            # Verificar se é o owner
            if str(workspace.owner_id) != str(user_id):
                return {
                    "success": False,
                    "error": "Apenas o proprietário pode deletar o workspace",
                }

            # Soft delete
            workspace.status = "deleted"
            workspace.updated_at = datetime.now(timezone.utc)

            # Registrar atividade
            self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="workspace_deleted",
                resource_type="workspace",
                resource_id=None,
                description=f"Workspace '{workspace.name}' foi deletado",
            )

            self.db.commit()
            return {"success": True, "message": "Workspace deletado com sucesso"}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar workspace {workspace_id}: {str(e)}")
            return {"success": False, "error": f"Erro interno: {str(e)}"}

    def get_workspace_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """Busca workspace por ID (NOVA ARQUITETURA - com eager loading)"""
        return (
            self.db.query(Workspace)
            .options(joinedload(Workspace.tenant).joinedload(Tenant.plan))
            .filter(Workspace.id == workspace_id, Workspace.status != "deleted")
            .first()
        )

    def get_workspace_members_count(self, workspace_id: str) -> int:
        """Conta membros ativos do workspace"""
        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.status == "active",
            )
            .count()
        )

    def get_workspace_projects_count(self, workspace_id: str) -> int:
        """Conta projetos ativos do workspace"""
        return (
            self.db.query(WorkspaceProject)
            .filter(
                WorkspaceProject.workspace_id == workspace_id,
                WorkspaceProject.status == "active",
            )
            .count()
        )

    def update_workspace(
        self, workspace_id: str, workspace_data: WorkspaceUpdate, user_id: str
    ) -> Optional[dict]:
        """Atualiza dados do workspace"""
        try:
            workspace = self.get_workspace_by_id(workspace_id)
            if not workspace:
                return None

            # Verificar permissão (owner ou admin)
            if not self._has_permission(workspace_id, user_id, "admin"):
                raise PermissionError("Sem permissão para editar workspace")

            # Atualizar campos
            for field, value in workspace_data.dict(exclude_unset=True).items():
                if hasattr(workspace, field):
                    setattr(workspace, field, value)

            workspace.updated_at = datetime.now(timezone.utc)

            # Registrar atividade
            self._log_activity(
                workspace_id=workspace_id,
                user_id=user_id,
                action="workspace_updated",
                resource_type="workspace",
                resource_id=None,
                description=f"Workspace '{workspace.name}' foi atualizado",
            )

            self.db.commit()
            return workspace.to_dict()

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar workspace {workspace_id}: {str(e)}")
            return None

    def get_workspace(self, workspace_id: str) -> Optional[dict]:
        """Busca workspace por ID e retorna como dict"""
        workspace = self.get_workspace_by_id(workspace_id)
        return workspace.to_dict() if workspace else None

    def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Obtém um workspace por slug"""
        return (
            self.db.query(Workspace)
            .filter(and_(Workspace.slug == slug, Workspace.status == "active"))
            .first()
        )

    def get_user_workspaces(self, user_id: str) -> list[dict[str, Any]]:
        """Lista workspaces do usuário (NOVA ARQUITETURA - com eager loading)"""
        # Workspaces onde é owner (com tenant e plan via JOIN)
        owned_workspaces = (
            self.db.query(Workspace)
            .options(joinedload(Workspace.tenant).joinedload(Tenant.plan))
            .filter(Workspace.owner_id == user_id, Workspace.status == "active")
            .all()
        )

        # Workspaces onde é membro (com tenant e plan via JOIN)
        member_workspaces = (
            self.db.query(Workspace)
            .options(joinedload(Workspace.tenant).joinedload(Tenant.plan))
            .join(WorkspaceMember)
            .filter(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.status == "active",
                Workspace.status == "active",
            )
            .all()
        )

        # Combinar e remover duplicatas
        all_workspaces = list(
            {w.id: w for w in owned_workspaces + member_workspaces}.values()
        )

        # ✅ NOVA ARQUITETURA: to_dict() agora retorna plan info via workspace.tenant.plan
        logger.info(
            f"Retornando {len(all_workspaces)} workspaces para usuário {user_id} com plan info via tenant"
        )
        return [workspace.to_dict() for workspace in all_workspaces]

    def get_workspace_limits(self, user_id: str) -> Dict[str, Any]:
        """Obtém informações sobre limites e uso atual do usuário"""

        subscription = self.get_user_subscription(user_id)

        if not subscription:
            return {"plan": None, "limits": {}, "usage": {}, "available": {}}

        current_workspaces = (
            self.db.query(Workspace).filter(Workspace.owner_id == user_id).count()
        )

        plan = subscription.plan

        return {
            "plan": {
                "name": plan.name,
                "slug": plan.slug,  # Usar slug ao invés de type
                "allow_collaborative_workspaces": plan.allow_collaborative_workspaces,
            },
            "limits": {
                "max_workspaces": plan.max_workspaces,
                "max_members_per_workspace": plan.max_members_per_workspace,
                "max_projects_per_workspace": plan.max_projects_per_workspace,
                "max_storage_mb": plan.max_storage_mb,
                "max_executions_per_month": plan.max_executions_per_month,
            },
            "usage": {
                "current_workspaces": current_workspaces,
                "current_storage_mb": subscription.current_storage_mb,
                "current_executions_this_month": subscription.current_executions_this_month,
            },
            "available": {
                "workspaces": plan.max_workspaces - current_workspaces,
                "storage_mb": plan.max_storage_mb - subscription.current_storage_mb,
                "executions": plan.max_executions_per_month
                - subscription.current_executions_this_month,
            },
        }

    def get_plan_limits(self, workspace_id: str) -> Dict[str, Any]:
        """Obtém os limites do plano de um workspace específico"""
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            return {"error": "Workspace não encontrado"}

        return workspace.get_plan_limits()

    def validate_workspace_consistency(self, user_id: str) -> Dict[str, Any]:
        """Valida a consistência dos workspaces do usuário"""

        individual_workspaces = (
            self.db.query(Workspace)
            .filter(
                and_(
                    Workspace.owner_id == user_id,
                    Workspace.type == WorkspaceType.INDIVIDUAL,
                )
            )
            .count()
        )

        issues = []

        if individual_workspaces == 0:
            issues.append("Usuário não possui workspace individual obrigatório")
        elif individual_workspaces > 1:
            issues.append("Usuário possui múltiplos workspaces individuais")

        subscription = self.get_user_subscription(user_id)
        if not subscription:
            issues.append("Usuário não possui assinatura ativa")

        return {
            "is_consistent": len(issues) == 0,
            "issues": issues,
            "individual_workspaces": individual_workspaces,
            "has_subscription": subscription is not None,
        }

    def get_workspace_creation_rules(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém as regras de criação de workspaces para um usuário específico

        Args:
            user_id: ID do usuário

        Returns:
            Dict com as regras de criação, incluindo:
            - can_create_individual: bool
            - can_create_collaborative: bool
            - has_individual_workspace: bool
            - current_workspaces: int
            - max_workspaces: int
            - user_username: str
        """
        try:
            # Obter usuário
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuário não encontrado")

            # Obter assinatura ativa
            subscription = (
                self.db.query(UserSubscription)
                .join(Plan)
                .filter(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.status == SubscriptionStatus.ACTIVE,
                    )
                )
                .first()
            )

            # Se não tem assinatura, criar uma padrão (FREE)
            if not subscription:
                # Buscar plano FREE padrão
                free_plan = (
                    self.db.query(Plan)
                    .filter(Plan.slug == "free")  # Busca por slug ao invés de type
                    .first()
                )

                if free_plan:
                    subscription = UserSubscription(
                        user_id=user_id,
                        plan_id=free_plan.id,
                        status=SubscriptionStatus.ACTIVE,
                        started_at=datetime.now(timezone.utc),
                        current_workspaces=0,
                        current_storage_mb=0.0,
                    )
                    self.db.add(subscription)
                    self.db.commit()
                    self.db.refresh(subscription)
                else:
                    # Fallback se não há plano FREE
                    return {
                        "can_create_individual": False,
                        "can_create_collaborative": False,
                        "has_individual_workspace": False,
                        "current_workspaces": 0,
                        "max_workspaces": 0,
                        "user_username": user.username or user.email,
                        "error": "Nenhum plano disponível",
                    }

            # Contar workspaces atuais
            current_workspaces = (
                self.db.query(Workspace).filter(Workspace.owner_id == user_id).count()
            )

            # Verificar se tem workspace individual
            has_individual = (
                self.db.query(Workspace)
                .filter(
                    and_(
                        Workspace.owner_id == user_id,
                        Workspace.type == WorkspaceType.INDIVIDUAL,
                    )
                )
                .count()
                > 0
            )

            # Determinar capacidades
            can_create_individual = (
                not has_individual
                and current_workspaces < subscription.plan.max_workspaces
            )
            can_create_collaborative = (
                subscription.plan.allow_collaborative_workspaces
                and current_workspaces < subscription.plan.max_workspaces
            )

            return {
                "can_create_individual": can_create_individual,
                "can_create_collaborative": can_create_collaborative,
                "has_individual_workspace": has_individual,
                "current_workspaces": current_workspaces,
                "max_workspaces": subscription.plan.max_workspaces,
                "user_username": user.username or user.email,
                "plan_name": subscription.plan.name,
                "plan_slug": subscription.plan.slug,  # Usar slug ao invés de type
            }

        except Exception as e:
            logger.error(
                f"Erro ao obter regras de criação para usuário {user_id}: {str(e)}"
            )
            # Retornar valores padrão seguros
            return {
                "can_create_individual": False,
                "can_create_collaborative": False,
                "has_individual_workspace": False,
                "current_workspaces": 0,
                "max_workspaces": 0,
                "user_username": "unknown",
                "error": str(e),
            }

    # ==================== MEMBROS ====================

    def invite_member(
        self, workspace_id: str, invite_data: MemberInvite, inviter_id: str
    ) -> WorkspaceInvitation:
        """Convida um membro para o workspace"""
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace não encontrado")

        # Verificar permissão
        if not self._has_permission(workspace_id, inviter_id, "admin"):
            raise PermissionError("Sem permissão para convidar membros")

        # Verificar limite de membros
        if workspace.member_count >= workspace.max_members:
            raise ValueError("Limite de membros atingido")

        # Verificar se usuário já é membro
        existing_user = self._get_user_by_email(invite_data.email)
        if existing_user and self._is_workspace_member(
            workspace_id, str(existing_user)
        ):
            raise ValueError("Usuário já é membro do workspace")

        # Criar convite
        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            inviter_id=inviter_id,
            invited_user_id=existing_user if existing_user else None,
            email=invite_data.email,
            role=invite_data.role,
            message=invite_data.message,
            token=secrets.token_urlsafe(32),
            status="pending",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        self.db.add(invitation)

        # Registrar atividade
        self._log_activity(
            workspace_id=workspace_id,
            user_id=inviter_id,
            action="member_invited",
            resource_type="invitation",
            resource_id=str(invitation.id),
            description=f"Usuário {invite_data.email} foi convidado com role {invite_data.role.value}",
        )

        self.db.commit()
        return invitation

    def accept_invitation(self, token: str, user_id: str) -> WorkspaceMember | None:
        """Aceita um convite para workspace"""
        invitation = (
            self.db.query(WorkspaceInvitation)
            .filter(
                WorkspaceInvitation.token == token,
                WorkspaceInvitation.status == "pending",
            )
            .first()
        )

        if not invitation:
            raise ValueError("Convite não encontrado ou já processado")

        if invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = "expired"
            self.db.commit()
            raise ValueError("Convite expirado")

        # Verificar se usuário já é membro
        if self._is_workspace_member(str(invitation.workspace_id), user_id):
            raise ValueError("Usuário já é membro do workspace")

        # Criar membership
        member = self._add_member(
            str(invitation.workspace_id), user_id, invitation.role
        )

        # Atualizar convite
        invitation.status = "accepted"
        invitation.responded_at = datetime.now(timezone.utc)

        # Registrar atividade
        self._log_activity(
            workspace_id=str(invitation.workspace_id),
            user_id=user_id,
            action="member_joined",
            resource_type="member",
            resource_id=str(member.id),
            description=f"Usuário aceitou convite e se juntou ao workspace",
        )

        self.db.commit()
        return member

    def remove_member(self, workspace_id: str, member_id: int, remover_id: str) -> bool:
        """Remove um membro do workspace"""
        try:
            # Verificar permissão
            if not self._has_permission(workspace_id, remover_id, "admin"):
                raise PermissionError("Sem permissão para remover membros")

            member = (
                self.db.query(WorkspaceMember)
                .filter(
                    WorkspaceMember.id == member_id,
                    WorkspaceMember.workspace_id == workspace_id,
                )
                .first()
            )

            if not member:
                return False

            # Não permitir remover o owner
            workspace = self.get_workspace_by_id(workspace_id)
            if workspace and str(member.user_id) == str(workspace.owner_id):
                raise ValueError("Não é possível remover o proprietário do workspace")

            # Remover membro
            member.status = "removed"
            member.left_at = datetime.now(timezone.utc)

            # Atualizar contador
            workspace.member_count = max(0, workspace.member_count - 1)

            # Registrar atividade
            self._log_activity(
                workspace_id=workspace_id,
                user_id=remover_id,
                action="member_removed",
                resource_type="member",
                resource_id=str(member.id),
                description=f"Membro foi removido do workspace",
            )

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao remover membro {member_id}: {str(e)}")
            return False

    def update_member_role(
        self,
        workspace_id: str,
        member_id: int,
        new_role: WorkspaceRole,
        updater_id: str,
    ) -> WorkspaceMember | None:
        """Atualiza o papel de um membro"""
        try:
            # Verificar permissão
            if not self._has_permission(workspace_id, updater_id, "admin"):
                raise PermissionError("Sem permissão para alterar roles")

            member = (
                self.db.query(WorkspaceMember)
                .filter(
                    WorkspaceMember.id == member_id,
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.status == "active",
                )
                .first()
            )

            if not member:
                return None

            # Não permitir alterar role do owner
            workspace = self.get_workspace_by_id(workspace_id)
            if workspace and str(member.user_id) == str(workspace.owner_id):
                raise ValueError("Não é possível alterar o role do proprietário")

            old_role = member.role
            member.role = new_role

            # Registrar atividade
            self._log_activity(
                workspace_id=workspace_id,
                user_id=updater_id,
                action="member_role_updated",
                resource_type="member",
                resource_id=str(member.id),
                description=f"Role do membro alterado de {old_role} para {new_role.value}",
            )

            self.db.commit()
            return member

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar role do membro {member_id}: {str(e)}")
            return None

    def get_workspace_members(self, workspace_id: str) -> list[dict]:
        """Lista membros do workspace com informações do usuário"""
        from synapse.models.user import User

        members = (
            self.db.query(WorkspaceMember, User)
            .join(User, WorkspaceMember.user_id == User.id)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.status == "active",
            )
            .all()
        )

        result = []
        for member, user in members:
            result.append(
                {
                    "id": member.id,
                    "workspace_id": str(member.workspace_id),
                    "user_id": str(member.user_id),
                    "user_name": user.full_name or user.username,
                    "user_email": user.email,
                    "user_avatar": getattr(user, "avatar_url", None),
                    "role": member.role.value.lower(),  # Converter para lowercase
                    "status": member.status,
                    "joined_at": member.joined_at,
                    "last_active_at": member.last_seen_at,
                }
            )

        return result

    # ==================== PROJETOS ====================

    def create_project(
        self, workspace_id: str, project_data: ProjectCreate, creator_id: str
    ) -> WorkspaceProject:
        """Cria um novo projeto no workspace"""
        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace não encontrado")

        # Verificar permissão
        if not self._has_permission(workspace_id, creator_id, "write"):
            raise PermissionError("Sem permissão para criar projetos")

        # Verificar limite de projetos
        if workspace.project_count >= workspace.max_projects:
            raise ValueError("Limite de projetos atingido")

        # Criar workflow se necessário
        workflow_id = project_data.workflow_id
        if not workflow_id:
            # Criar workflow vazio
            from synapse.models.workflow import Workflow

            workflow = Workflow(
                name=f"Workflow - {project_data.name}",
                description=f"Workflow gerado para o projeto {project_data.name}",
                user_id=creator_id,
                workspace_id=workspace_id,
                definition={"nodes": [], "connections": []},
                is_active=True,
            )
            self.db.add(workflow)
            self.db.flush()
            workflow_id = str(workflow.id)

        # Criar projeto
        project = WorkspaceProject(
            workspace_id=workspace_id,
            workflow_id=workflow_id,
            name=project_data.name,
            description=project_data.description,
            color=project_data.color or "#10B981",
            allow_concurrent_editing=project_data.allow_concurrent_editing,
            auto_save_interval=project_data.auto_save_interval,
            version_control_enabled=project_data.version_control_enabled,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_edited_at=datetime.now(timezone.utc),
        )

        self.db.add(project)
        self.db.flush()

        # Adicionar criador como colaborador
        self._add_project_collaborator(
            str(project.id),
            creator_id,
            can_edit=True,
            can_comment=True,
            can_share=True,
            can_delete=True,
        )

        # Atualizar contador do workspace
        workspace.project_count += 1

        # Registrar atividade
        self._log_activity(
            workspace_id=workspace_id,
            user_id=creator_id,
            action="project_created",
            resource_type="project",
            resource_id=str(project.id),
            description=f"Projeto '{project.name}' foi criado",
        )

        self.db.commit()
        return project

    def update_project(
        self, project_id: int, project_data: ProjectUpdate, user_id: int
    ) -> WorkspaceProject | None:
        """Atualiza um projeto"""

        project = self.get_project(project_id)
        if not project:
            return None

        # Verificar permissão
        if not self._can_edit_project(project_id, user_id):
            raise PermissionError("Usuário não tem permissão para editar projeto")

        # Atualizar campos
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        project.last_edited_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(project)

        # Registrar atividade
        self._log_activity(
            project.workspace_id,
            user_id,
            "updated",
            "project",
            project_id,
            f"Projeto '{project.name}' foi atualizado",
        )

        return project

    def get_project(self, project_id: int) -> WorkspaceProject | None:
        """Obtém um projeto por ID"""
        return (
            self.db.query(WorkspaceProject)
            .filter(
                and_(
                    WorkspaceProject.id == project_id,
                    WorkspaceProject.status == "active",
                ),
            )
            .first()
        )

    def get_workspace_projects(
        self, workspace_id: str, user_id: str
    ) -> list[WorkspaceProject]:
        """Obtém projetos do workspace que o usuário tem acesso"""

        # Verificar se é membro do workspace (converter para string)
        if not self._is_workspace_member(str(workspace_id), str(user_id)):
            return []

        return (
            self.db.query(WorkspaceProject)
            .filter(
                and_(
                    WorkspaceProject.workspace_id == workspace_id,
                    WorkspaceProject.status == "active",
                ),
            )
            .all()
        )

    def delete_project(self, project_id: int, user_id: int) -> bool:
        """Deleta um projeto (soft delete)"""

        project = self.get_project(project_id)
        if not project:
            return False

        # Verificar permissão
        collaborator = (
            self.db.query(ProjectCollaborator)
            .filter(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.can_delete == True,
                ),
            )
            .first()
        )

        if not collaborator:
            raise PermissionError("Usuário não tem permissão para deletar projeto")

        project.status = "deleted"
        project.updated_at = datetime.utcnow()

        # Atualizar contador
        workspace = self.get_workspace(project.workspace_id)
        if workspace:
            workspace["project_count"] -= 1

        self.db.commit()

        # Registrar atividade
        self._log_activity(
            project.workspace_id,
            user_id,
            "deleted",
            "project",
            project_id,
            f"Projeto '{project.name}' foi deletado",
        )

        return True

    # ==================== COLABORAÇÃO ====================

    def add_project_collaborator(
        self, project_id: int, user_id: int, permissions: dict[str, bool], adder_id: int
    ) -> ProjectCollaborator:
        """Adiciona colaborador ao projeto"""

        project = self.get_project(project_id)
        if not project:
            raise ValueError("Projeto não encontrado")

        # Verificar se usuário é membro do workspace
        if not self._is_workspace_member(project.workspace_id, user_id):
            raise ValueError("Usuário não é membro do workspace")

        # Verificar permissão do adder
        if not self._can_edit_project(project_id, adder_id):
            raise PermissionError(
                "Usuário não tem permissão para adicionar colaboradores"
            )

        # Verificar se já é colaborador
        existing = (
            self.db.query(ProjectCollaborator)
            .filter(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id,
                ),
            )
            .first()
        )

        if existing:
            raise ValueError("Usuário já é colaborador do projeto")

        collaborator = ProjectCollaborator(
            project_id=project_id,
            user_id=user_id,
            can_edit=permissions.get("can_edit", True),
            can_comment=permissions.get("can_comment", True),
            can_share=permissions.get("can_share", False),
            can_delete=permissions.get("can_delete", False),
        )

        self.db.add(collaborator)

        # Atualizar contador
        project.collaborator_count += 1

        self.db.commit()
        self.db.refresh(collaborator)

        # Registrar atividade
        user = self.db.query(User).filter(User.id == user_id).first()
        self._log_activity(
            project.workspace_id,
            adder_id,
            "added_collaborator",
            "project",
            project_id,
            f"{user['full_name'] if user else 'Usuário'} foi adicionado como colaborador",
        )

        return collaborator

    def create_comment(
        self, project_id: int, comment_data: CommentCreate, user_id: int
    ) -> ProjectComment:
        """Cria um comentário no projeto"""

        project = self.get_project(project_id)
        if not project:
            raise ValueError("Projeto não encontrado")

        # Verificar permissão
        if not self._can_comment_project(project_id, user_id):
            raise PermissionError("Usuário não tem permissão para comentar")

        comment = ProjectComment(
            project_id=project_id,
            user_id=user_id,
            parent_id=comment_data.parent_id,
            content=comment_data.content,
            content_type=comment_data.content_type or "text",
            node_id=comment_data.node_id,
            position_x=comment_data.position_x,
            position_y=comment_data.position_y,
        )

        self.db.add(comment)

        # Atualizar contador
        project.comment_count += 1

        self.db.commit()
        self.db.refresh(comment)

        # Registrar atividade
        self._log_activity(
            project.workspace_id,
            user_id,
            "commented",
            "project",
            project_id,
            f"Adicionou comentário no projeto '{project.name}'",
        )

        return comment

    def get_project_comments(
        self, project_id: int, user_id: int
    ) -> list[ProjectComment]:
        """Obtém comentários do projeto"""

        # Verificar acesso ao projeto
        if not self._can_view_project(project_id, user_id):
            return []

        return (
            self.db.query(ProjectComment)
            .filter(
                ProjectComment.project_id == project_id,
            )
            .order_by(ProjectComment.created_at)
            .all()
        )

    # ==================== ATIVIDADES ====================

    def get_workspace_activities(
        self, workspace_id: str, user_id: str, limit: int = 50
    ) -> list[dict]:
        """Lista atividades do workspace"""
        try:
            # Verificar permissão
            if not self._has_permission(workspace_id, user_id, "read"):
                raise PermissionError("Sem permissão para ver atividades")

            activities = (
                self.db.query(WorkspaceActivity)
                .filter(WorkspaceActivity.workspace_id == workspace_id)
                .order_by(WorkspaceActivity.created_at.desc())
                .limit(limit)
                .all()
            )

            # Converter para dict
            result = []
            for activity in activities:
                activity_dict = {
                    "id": activity.id,
                    "workspace_id": activity.workspace_id,
                    "user_id": activity.user_id,
                    "user_name": (
                        activity.user.full_name if activity.user else "Unknown"
                    ),
                    "action": activity.action,
                    "resource_type": activity.resource_type,
                    "resource_id": activity.resource_id,
                    "description": activity.description,
                    "meta_data": activity.meta_data,
                    "created_at": activity.created_at.isoformat(),
                }
                result.append(activity_dict)

            return result

        except Exception as e:
            logger.error(f"Erro ao obter atividades do workspace: {e}")
            return []

    # ==================== MÉTODOS AUXILIARES ====================

    @staticmethod
    def _generate_unique_slug(db: Session, name: str, username: str) -> str:
        """Gera slug único para o workspace"""
        import re

        # Limpar nome para slug
        base_slug = re.sub(r"[^a-zA-Z0-9\s-]", "", name.lower())
        base_slug = re.sub(r"\s+", "-", base_slug.strip())
        base_slug = f"{username}-{base_slug}"

        # Verificar unicidade
        counter = 1
        slug = base_slug
        while db.query(Workspace).filter(Workspace.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _add_member(
        self, workspace_id: str, user_id: str, role: WorkspaceRole
    ) -> WorkspaceMember:
        """Adiciona um membro ao workspace"""
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            status="active",
            is_favorite=False,
            notification_preferences={
                "email_notifications": True,
                "push_notifications": True,
                "activity_digest": "daily",
            },
            joined_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
        )

        self.db.add(member)
        self.db.flush()

        # Atualizar contador do workspace
        workspace = self.get_workspace_by_id(workspace_id)
        if workspace:
            workspace.member_count += 1

        return member

    def _add_project_collaborator(
        self, project_id: str, user_id: str, **permissions
    ) -> ProjectCollaborator:
        """Adiciona um colaborador ao projeto"""
        collaborator = ProjectCollaborator(
            project_id=project_id,
            user_id=user_id,
            can_edit=permissions.get("can_edit", True),
            can_comment=permissions.get("can_comment", True),
            can_share=permissions.get("can_share", False),
            can_delete=permissions.get("can_delete", False),
            added_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
        )

        self.db.add(collaborator)
        return collaborator

    def _has_permission(self, workspace_id: str, user_id: str, permission: str) -> bool:
        """Verifica se usuário tem permissão específica"""
        # Owner sempre tem todas as permissões
        workspace = self.get_workspace_by_id(workspace_id)
        if workspace and str(workspace.owner_id) == str(user_id):
            return True

        # Verificar membership
        member = (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.status == "active",
            )
            .first()
        )

        if not member:
            return False

        # Mapear permissões por role
        permissions_map = {
            WorkspaceRole.ADMIN: ["read", "write", "admin"],
            WorkspaceRole.MEMBER: ["read", "write"],
            WorkspaceRole.VIEWER: ["read"],
        }

        allowed_permissions = permissions_map.get(member.role, [])
        return permission in allowed_permissions

    def _is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
        """Verifica se usuário é membro do workspace"""
        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.status == "active",
            )
            .first()
            is not None
        )

    def _can_edit_project(self, project_id: str, user_id: str) -> bool:
        """Verifica se usuário pode editar projeto"""
        collaborator = (
            self.db.query(ProjectCollaborator)
            .filter(
                ProjectCollaborator.project_id == project_id,
                ProjectCollaborator.user_id == user_id,
            )
            .first()
        )

        return collaborator and collaborator.can_edit

    def _can_comment_project(self, project_id: int, user_id: int) -> bool:
        """Verifica se usuário pode comentar no projeto"""

        collaborator = (
            self.db.query(ProjectCollaborator)
            .filter(
                and_(
                    ProjectCollaborator.project_id == project_id,
                    ProjectCollaborator.user_id == user_id,
                    ProjectCollaborator.can_comment == True,
                ),
            )
            .first()
        )

        return collaborator is not None

    def _can_view_project(self, project_id: int, user_id: int) -> bool:
        """Verifica se usuário pode visualizar projeto"""

        project = self.get_project(project_id)
        if not project:
            return False

        return self._is_workspace_member(project.workspace_id, user_id)

    def _get_user_by_email(self, email: str) -> int | None:
        """Obtém ID do usuário por email"""
        user = self.db.query(User).filter(User.email == email).first()
        return user.id if user else None

    def _log_activity(
        self,
        workspace_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        description: str = "",
        meta_data: dict | None = None,
    ):
        """Registra atividade no workspace"""
        activity = WorkspaceActivity(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            meta_data=meta_data or {},
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(activity)

        # Atualizar contador de atividades do workspace
        workspace = self.get_workspace_by_id(workspace_id)
        if workspace:
            workspace.activity_count += 1

    # ==================== ANALYTICS ====================

    def get_workspace_stats(self, workspace_id: str, user_id: str) -> dict[str, Any]:
        """Obtém estatísticas do workspace"""
        if not self._has_permission(workspace_id, user_id, "read"):
            raise PermissionError("Sem permissão para ver estatísticas")

        workspace = self.get_workspace_by_id(workspace_id)
        if not workspace:
            return {}

        return {
            "member_count": workspace.member_count,
            "project_count": workspace.project_count,
            "activity_count": workspace.activity_count,
            "storage_used_mb": workspace.storage_used_mb,
            "storage_limit_mb": workspace.max_storage_mb,
            "created_at": workspace.created_at,
            "last_activity": workspace.last_activity_at,
        }

    def _count_individual_workspaces(self, user_id: str) -> int:
        """Conta workspaces individuais do usuário"""
        return (
            self.db.query(Workspace)
            .filter(
                and_(
                    Workspace.owner_id == user_id,
                    Workspace.type == WorkspaceType.INDIVIDUAL,
                )
            )
            .count()
        )

    def _count_total_workspaces(self, user_id: str) -> int:
        """Conta total de workspaces do usuário"""
        return self.db.query(Workspace).filter(Workspace.owner_id == user_id).count()

    def change_member_role(
        self, workspace_id: str, user_id: str, role: WorkspaceRole
    ) -> bool:
        """Altera role de um membro"""
        member = (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.status == "active",
            )
            .first()
        )

        if not member:
            return False

        member.role = role
        self.db.commit()
        return True

    # ==================== MÉTODOS ADICIONAIS ====================

    def get_user_invitations(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[dict]:
        """Obtém convites recebidos pelo usuário"""
        try:
            # Import necessário
            from synapse.models.user import User
            from synapse.models.workspace_invitation import WorkspaceInvitation

            # Buscar user por ID para obter email
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []

            # Query base
            query = self.db.query(WorkspaceInvitation).filter(
                WorkspaceInvitation.email == user.email
            )

            # Aplicar filtro de status se fornecido
            if status:
                query = query.filter(WorkspaceInvitation.status == status)

            # Ordenar por data de criação (mais recentes primeiro)
            query = query.order_by(WorkspaceInvitation.created_at.desc())

            # Aplicar paginação
            invitations = query.offset(offset).limit(limit).all()

            # Converter para dict
            result = []
            for invitation in invitations:
                invitation_dict = {
                    "id": invitation.id,
                    "workspace_id": invitation.workspace_id,
                    "workspace_name": (
                        invitation.workspace.name if invitation.workspace else "Unknown"
                    ),
                    "inviter_name": (
                        invitation.inviter.full_name
                        if invitation.inviter
                        else "Unknown"
                    ),
                    "status": invitation.status,
                    "role": invitation.role.value,
                    "message": invitation.message,
                    "expires_at": (
                        invitation.expires_at.isoformat()
                        if invitation.expires_at
                        else None
                    ),
                    "created_at": invitation.created_at.isoformat(),
                    "accepted_at": (
                        invitation.accepted_at.isoformat()
                        if invitation.accepted_at
                        else None
                    ),
                }
                result.append(invitation_dict)

            return result

        except Exception as e:
            logger.error(f"Erro ao obter convites: {e}")
            return []

    def accept_invitation(self, invitation_id: int, user_id: str) -> bool:
        """Aceita um convite de workspace"""
        try:
            # Por enquanto retorna False - implementar quando necessário
            return False
        except Exception as e:
            logger.error(f"Erro ao aceitar convite: {e}")
            return False

    def decline_invitation(self, invitation_id: int, user_id: str) -> bool:
        """Recusa um convite de workspace"""
        try:
            # Por enquanto retorna False - implementar quando necessário
            return False
        except Exception as e:
            logger.error(f"Erro ao recusar convite: {e}")
            return False

    def search_projects(self, search_params, user_id: str) -> List[dict]:
        """Busca projetos com filtros"""
        try:
            # Import necessário
            from synapse.models.workspace import WorkspaceProject

            query = self.db.query(WorkspaceProject).filter(
                WorkspaceProject.status == "active"
            )

            # Filtrar apenas projetos de workspaces que o usuário tem acesso
            workspace_ids = []
            user_workspaces = self.get_user_workspaces(user_id)
            for workspace in user_workspaces:
                # Converter string UUID para UUID se necessário
                workspace_id = workspace["id"]
                if isinstance(workspace_id, str):
                    import uuid

                    try:
                        workspace_id = uuid.UUID(workspace_id)
                    except ValueError:
                        continue
                workspace_ids.append(workspace_id)

            if workspace_ids:
                query = query.filter(WorkspaceProject.workspace_id.in_(workspace_ids))
            else:
                return []  # Usuário não tem acesso a nenhum workspace

            # Aplicar filtros de busca
            if hasattr(search_params, "query") and search_params.query:
                query = query.filter(
                    or_(
                        WorkspaceProject.name.ilike(f"%{search_params.query}%"),
                        WorkspaceProject.description.ilike(f"%{search_params.query}%"),
                    )
                )

            # Filtro de workspace específico
            if hasattr(search_params, "workspace_id") and search_params.workspace_id:
                query = query.filter(
                    WorkspaceProject.workspace_id == search_params.workspace_id
                )

            # Filtro de status
            if hasattr(search_params, "status") and search_params.status:
                query = query.filter(WorkspaceProject.status == search_params.status)

            # Filtro de projetos com colaboradores
            if (
                hasattr(search_params, "has_collaborators")
                and search_params.has_collaborators
            ):
                query = query.filter(WorkspaceProject.collaborator_count > 0)

            # Ordenação
            sort_by = getattr(search_params, "sort_by", "updated")
            if sort_by == "updated":
                query = query.order_by(WorkspaceProject.updated_at.desc())
            elif sort_by == "created":
                query = query.order_by(WorkspaceProject.created_at.desc())
            elif sort_by == "name":
                query = query.order_by(WorkspaceProject.name.asc())
            elif sort_by == "activity":
                query = query.order_by(WorkspaceProject.last_edited_at.desc())

            # Aplicar paginação
            limit = getattr(search_params, "limit", 20)
            offset = getattr(search_params, "offset", 0)
            projects = query.offset(offset).limit(limit).all()

            # Converter para dict
            result = []
            for project in projects:
                project_dict = {
                    "id": project.id,
                    "workspace_id": project.workspace_id,
                    "workflow_id": project.workflow_id,
                    "name": project.name,
                    "description": project.description,
                    "color": project.color,
                    "status": project.status,
                    "is_template": project.is_template,
                    "is_public": project.is_public,
                    "collaborator_count": project.collaborator_count,
                    "edit_count": project.edit_count,
                    "comment_count": project.comment_count,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                    "last_edited_at": project.last_edited_at.isoformat(),
                }
                result.append(project_dict)

            return result

        except Exception as e:
            logger.error(f"Erro na busca de projetos: {e}")
            return []

    def search_workspaces(self, search_params, user_id: str) -> List[dict]:
        """Busca workspaces com filtros (NOVA ARQUITETURA - com eager loading)"""
        try:
            query = (
                self.db.query(Workspace)
                .options(joinedload(Workspace.tenant).joinedload(Tenant.plan))
                .filter(Workspace.status == "active")
            )

            # Aplicar filtros de busca
            if hasattr(search_params, "query") and search_params.query:
                query = query.filter(
                    or_(
                        Workspace.name.ilike(f"%{search_params.query}%"),
                        Workspace.description.ilike(f"%{search_params.query}%"),
                    )
                )

            # Filtro de workspace público
            if (
                hasattr(search_params, "is_public")
                and search_params.is_public is not None
            ):
                query = query.filter(Workspace.is_public == search_params.is_public)

            # Filtro de workspaces com projetos
            if hasattr(search_params, "has_projects") and search_params.has_projects:
                query = query.filter(Workspace.project_count > 0)

            # Filtro de número mínimo de membros
            if hasattr(search_params, "min_members") and search_params.min_members:
                query = query.filter(
                    Workspace.member_count >= search_params.min_members
                )

            # Filtro de número máximo de membros
            if hasattr(search_params, "max_members") and search_params.max_members:
                query = query.filter(
                    Workspace.member_count <= search_params.max_members
                )

            # Ordenação
            sort_by = getattr(search_params, "sort_by", "activity")
            if sort_by == "activity":
                query = query.order_by(Workspace.last_activity_at.desc())
            elif sort_by == "members":
                query = query.order_by(Workspace.member_count.desc())
            elif sort_by == "projects":
                query = query.order_by(Workspace.project_count.desc())
            elif sort_by == "created":
                query = query.order_by(Workspace.created_at.desc())
            elif sort_by == "name":
                query = query.order_by(Workspace.name.asc())

            # Aplicar paginação
            limit = getattr(search_params, "limit", 20)
            offset = getattr(search_params, "offset", 0)
            workspaces = query.offset(offset).limit(limit).all()

            # Converter para dict
            return [workspace.to_dict() for workspace in workspaces]

        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []

    def get_project_versions(
        self, project_id: int, user_id: str, limit: int = 20, offset: int = 0
    ) -> Optional[List[dict]]:
        """Obtém versões de um projeto"""
        try:
            # Verificar se o projeto existe e se o usuário tem permissão
            project = self.get_project(project_id)
            if not project:
                return []

            # Verificar se usuário pode visualizar o projeto
            if not self._can_view_project(project_id, user_id):
                return []

            # Buscar versões do projeto
            query = (
                self.db.query(ProjectVersion)
                .filter(ProjectVersion.project_id == project_id)
                .order_by(ProjectVersion.created_at.desc())
            )

            # Aplicar paginação
            versions = query.offset(offset).limit(limit).all()

            # Converter para dict
            result = []
            for version in versions:
                version_dict = {
                    "id": version.id,
                    "project_id": version.project_id,
                    "version_number": version.version_number,
                    "version_name": version.version_name,
                    "description": version.description,
                    "is_major": version.is_major,
                    "is_auto_save": version.is_auto_save,
                    "file_size": version.file_size,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.user.full_name if version.user else "Unknown",
                }
                result.append(version_dict)

            return result

        except Exception as e:
            logger.error(f"Erro ao obter versões: {e}")
            return []

    def create_project_version(
        self, project_id: int, version_data, user_id: str
    ) -> dict:
        """Cria uma nova versão do projeto"""
        try:
            # Implementação básica
            return {
                "id": 1,
                "version": "1.0.0",
                "description": "Nova versão",
                "created_at": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Erro ao criar versão: {e}")
            raise e

    def restore_project_version(
        self, project_id: int, version_id: int, user_id: str
    ) -> bool:
        """Restaura uma versão específica do projeto"""
        try:
            # Por enquanto retorna True - implementar quando necessário
            return True
        except Exception as e:
            logger.error(f"Erro ao restaurar versão: {e}")
            return False

    def get_project_activities(
        self, project_id: int, user_id: str, limit: int = 50, offset: int = 0
    ) -> Optional[List[dict]]:
        """Obtém atividades de um projeto"""
        try:
            # Verificar se o projeto existe e se o usuário tem permissão
            project = self.get_project(project_id)
            if not project:
                return []

            # Verificar se usuário pode visualizar o projeto
            if not self._can_view_project(project_id, user_id):
                return []

            # Buscar atividades relacionadas ao projeto no workspace
            query = (
                self.db.query(WorkspaceActivity)
                .filter(
                    and_(
                        WorkspaceActivity.workspace_id == project.workspace_id,
                        WorkspaceActivity.resource_type == "project",
                        WorkspaceActivity.resource_id == str(project_id),
                    )
                )
                .order_by(WorkspaceActivity.created_at.desc())
            )

            # Aplicar paginação
            activities = query.offset(offset).limit(limit).all()

            # Converter para dict
            result = []
            for activity in activities:
                activity_dict = {
                    "id": activity.id,
                    "workspace_id": activity.workspace_id,
                    "user_id": activity.user_id,
                    "user_name": (
                        activity.user.full_name if activity.user else "Unknown"
                    ),
                    "action": activity.action,
                    "resource_type": activity.resource_type,
                    "resource_id": activity.resource_id,
                    "description": activity.description,
                    "meta_data": activity.meta_data,
                    "created_at": activity.created_at.isoformat(),
                }
                result.append(activity_dict)

            return result

        except Exception as e:
            logger.error(f"Erro ao obter atividades: {e}")
            return []

    def bulk_member_operation(self, workspace_id: int, operation, user_id: str) -> dict:
        """Executa operação em lote em membros"""
        try:
            return {"success": True, "processed": 0, "errors": []}
        except Exception as e:
            logger.error(f"Erro na operação em lote: {e}")
            return {"success": False, "processed": 0, "errors": [str(e)]}

    def bulk_project_operation(
        self, workspace_id: int, operation, user_id: str
    ) -> dict:
        """Executa operação em lote em projetos"""
        try:
            return {"success": True, "processed": 0, "errors": []}
        except Exception as e:
            logger.error(f"Erro na operação em lote: {e}")
            return {"success": False, "processed": 0, "errors": [str(e)]}

    def get_notification_settings(
        self, workspace_id: int, user_id: str
    ) -> Optional[dict]:
        """Obtém configurações de notificação do workspace"""
        try:
            return {"email_notifications": True, "push_notifications": True}
        except Exception as e:
            logger.error(f"Erro ao obter configurações: {e}")
            return None

    def update_notification_settings(
        self, workspace_id: int, preferences, user_id: str
    ) -> dict:
        """Atualiza configurações de notificação"""
        try:
            return {"success": True, "message": "Configurações atualizadas"}
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {e}")
            return {"success": False, "message": str(e)}

    def create_integration(
        self, workspace_id: int, integration_data, user_id: str
    ) -> dict:
        """Cria uma nova integração"""
        try:
            return {"id": 1, "name": "Integration", "type": "generic"}
        except Exception as e:
            logger.error(f"Erro ao criar integração: {e}")
            raise e

    def get_workspace_integrations(self, workspace_id: int, user_id: str) -> List[dict]:
        """Obtém integrações do workspace"""
        try:
            return []
        except Exception as e:
            logger.error(f"Erro ao obter integrações: {e}")
            return []

    def update_integration(
        self, integration_id: int, integration_data, user_id: str
    ) -> dict:
        """Atualiza uma integração"""
        try:
            return {"id": integration_id, "name": "Integration", "type": "generic"}
        except Exception as e:
            logger.error(f"Erro ao atualizar integração: {e}")
            raise e

    def delete_integration(self, integration_id: int, user_id: str) -> bool:
        """Deleta uma integração"""
        try:
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar integração: {e}")
            return False

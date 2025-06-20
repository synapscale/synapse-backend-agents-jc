"""
Serviço de gerenciamento de workspaces com validações rigorosas e sincronização automática
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta, timezone
import uuid
import secrets
import logging

from synapse.models.workspace import (
    Workspace, WorkspaceProject, ProjectCollaborator,
    ProjectComment, ProjectVersion,
    PermissionLevel, WorkspaceType
)
from synapse.models.workspace_member import WorkspaceMember, WorkspaceRole
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.workspace_invitation import WorkspaceInvitation
from synapse.models.user import User
from synapse.models.workflow import Workflow
from synapse.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, MemberInvite,
    ProjectCreate, ProjectUpdate, CommentCreate
)
from synapse.models.subscription import UserSubscription, Plan, PlanType, SubscriptionStatus

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
                    UserSubscription.status == SubscriptionStatus.ACTIVE
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
                "current_workspaces": 0
            }

        current_count = (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == user_id)
            .count()
        )

        can_create = current_count < subscription.plan.max_workspaces
        
        return {
            "can_create": can_create,
            "reason": "Limite de workspaces atingido" if not can_create else None,
            "max_workspaces": subscription.plan.max_workspaces,
            "current_workspaces": current_count,
            "plan_name": subscription.plan.name
        }

    def can_create_collaborative_workspace(self, user_id: str) -> Dict[str, Any]:
        """Verifica se o usuário pode criar workspaces colaborativos"""
        subscription = self.get_user_subscription(user_id)
        
        if not subscription:
            return {
                "can_create": False,
                "reason": "Usuário não possui assinatura ativa"
            }

        if not subscription.plan.allow_collaborative_workspaces:
            return {
                "can_create": False,
                "reason": f"Plano {subscription.plan.name} não permite workspaces colaborativos"
            }

        workspace_check = self.can_create_workspace(user_id)
        return workspace_check

    @staticmethod
    def create_workspace(db: Session, user_id: str, workspace_data: WorkspaceCreate) -> Workspace:
        """
        Cria um novo workspace com validações rigorosas de plano
        """
        try:
            # Obter assinatura do usuário
            user_subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if not user_subscription:
                raise ValueError("Usuário não possui assinatura ativa")

            # Verificar regras de criação
            rules = WorkspaceService.get_workspace_creation_rules(db, user_id)
            
            # Determinar tipo do workspace
            workspace_type = workspace_data.type if hasattr(workspace_data, 'type') else None
            if not workspace_type:
                if rules["can_create_individual"]:
                    workspace_type = WorkspaceType.INDIVIDUAL
                elif rules["can_create_collaborative"]:
                    workspace_type = WorkspaceType.COLLABORATIVE
                else:
                    raise ValueError("Não é possível determinar o tipo de workspace")

            # Validar limites do plano
            if workspace_type == WorkspaceType.COLLABORATIVE:
                if not user_subscription.plan.allow_collaborative_workspaces:
                    raise ValueError("Plano atual não permite workspaces colaborativos")

            if rules["current_workspaces"] >= user_subscription.plan.max_workspaces:
                raise ValueError(f"Limite de workspaces atingido ({user_subscription.plan.max_workspaces})")

            # Gerar slug único
            base_slug = WorkspaceService._generate_unique_slug(
                db, workspace_data.name, rules["user_username"]
            )

            # Determinar plan_id baseado no tipo de workspace
            plan_id = user_subscription.plan_id
            if workspace_type == WorkspaceType.INDIVIDUAL:
                # Workspace individual sempre usa o plano do usuário
                plan_id = user_subscription.plan_id
            else:
                # Workspace colaborativo pode ter plano específico
                plan_id = getattr(workspace_data, 'plan_id', user_subscription.plan_id)

            # Criar workspace
            workspace = Workspace(
                name=workspace_data.name,
                slug=base_slug,
                type=workspace_type,
                description=workspace_data.description,
                owner_id=user_id,
                plan_id=plan_id,  # NOVO CAMPO
                is_public=getattr(workspace_data, 'is_public', False),
                allow_guest_access=getattr(workspace_data, 'allow_guest_access', False),
                require_approval=getattr(workspace_data, 'require_approval', True),
                max_members=user_subscription.plan.max_members_per_workspace,
                max_projects=user_subscription.plan.max_projects_per_workspace,
                max_storage_mb=user_subscription.plan.max_storage_mb,
                enable_real_time_editing=getattr(workspace_data, 'enable_real_time_editing', True),
                enable_comments=getattr(workspace_data, 'enable_comments', True),
                enable_chat=getattr(workspace_data, 'enable_chat', True),
                enable_video_calls=getattr(workspace_data, 'enable_video_calls', False),
                notification_settings=getattr(workspace_data, 'notification_settings', {}),
                status="active",
                last_activity_at=datetime.now(timezone.utc)
            )

            db.add(workspace)
            db.flush()

            # Criar membership do owner
            owner_member = WorkspaceMember.create_owner_membership(
                workspace_id=str(workspace.id),
                user_id=user_id
            )
            db.add(owner_member)

            # Atualizar contador de workspaces do usuário
            user_subscription.current_workspaces += 1

            # Registrar atividade
            activity = WorkspaceActivity(
                workspace_id=workspace.id,
                user_id=user_id,
                action="workspace_created",
                resource_type="workspace",
                resource_id=str(workspace.id),
                description=f"Workspace '{workspace.name}' foi criado",
                meta_data={
                    "workspace_type": workspace_type.value,
                    "plan_name": user_subscription.plan.name
                }
            )
            db.add(activity)
            
            # Incrementar contador de atividades
            workspace.activity_count = 1

            db.commit()
            
            logger.info(f"Workspace criado: {workspace.name} (ID: {workspace.id})")
            return workspace

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar workspace: {str(e)}")
            raise

    def _validate_workspace_creation(self, user_id: str, workspace_type: Optional[WorkspaceType]) -> Dict[str, Any]:
        """Validações rigorosas antes de criar workspace"""
        
        # 1. Verificar assinatura ativa
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return {
                "can_create": False,
                "reason": "Usuário não possui assinatura ativa",
                "error_code": "NO_SUBSCRIPTION"
            }

        # 2. Verificar limites do plano
        plan = subscription.plan
        current_workspaces = subscription.current_workspaces or 0
        
        if current_workspaces >= plan.max_workspaces:
            return {
                "can_create": False,
                "reason": f"Limite de workspaces atingido ({current_workspaces}/{plan.max_workspaces}). Faça upgrade do seu plano.",
                "error_code": "WORKSPACE_LIMIT_REACHED"
            }

        # 3. Verificar regra de workspace individual (apenas 1 permitido)
        if workspace_type == WorkspaceType.INDIVIDUAL:
            individual_count = self._count_individual_workspaces(user_id)
            if individual_count >= 1:
                return {
                    "can_create": False,
                    "reason": "Você já possui um workspace individual. Apenas 1 workspace individual é permitido por usuário.",
                    "error_code": "INDIVIDUAL_LIMIT_REACHED"
                }

        # 4. Verificar se plano permite workspaces colaborativos
        if workspace_type == WorkspaceType.COLLABORATIVE:
            if not plan.allow_collaborative_workspaces:
                return {
                    "can_create": False,
                    "reason": f"Seu plano {plan.name} não permite workspaces colaborativos. Faça upgrade para criar workspaces de equipe.",
                    "error_code": "COLLABORATIVE_NOT_ALLOWED"
                }

        return {"can_create": True, "reason": "Validação passou"}

    def _determine_workspace_type(self, user_id: str, requested_type: Optional[WorkspaceType]) -> WorkspaceType:
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
                logger.warning("Usuário tentou criar segundo workspace individual - forçando collaborative")
            return WorkspaceType.COLLABORATIVE
        
        # Se não tem individual ainda, pode criar
        return requested_type or WorkspaceType.INDIVIDUAL

    def _get_plan_for_workspace_type(self, workspace_type: WorkspaceType) -> Optional[Plan]:
        """
        Determina o plano baseado no tipo de workspace
        - Individual: sempre plano 'free'
        - Collaborative: plano baseado na assinatura do usuário
        """
        try:
            if workspace_type == WorkspaceType.INDIVIDUAL:
                # Workspace individual sempre usa plano free
                plan = self.db.query(Plan).filter(
                    Plan.type == PlanType.FREE,
                    Plan.is_active == True
                ).first()
                
                if not plan:
                    logger.error("Plano 'free' não encontrado no banco")
                    return None
                    
                logger.info(f"Plano 'free' selecionado para workspace individual")
                return plan
            
            else:  # WorkspaceType.COLLABORATIVE
                # Para workspace colaborativo, usar plano da assinatura
                # Por enquanto, usar plano 'free' como padrão
                # TODO: Implementar lógica baseada na assinatura do usuário
                plan = self.db.query(Plan).filter(
                    Plan.type == PlanType.FREE,
                    Plan.is_active == True
                ).first()
                
                if not plan:
                    logger.error("Plano padrão não encontrado no banco")
                    return None
                    
                logger.info(f"Plano '{plan.type.value}' selecionado para workspace colaborativo")
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
        **kwargs
    ) -> Workspace:
        """Cria o registro do workspace com configurações apropriadas"""
        
        # Configurações baseadas no tipo
        if workspace_type == WorkspaceType.INDIVIDUAL:
            max_members = 1
            enable_chat = False
            enable_video_calls = False
            allow_guest_access = False
        else:  # COLLABORATIVE
            max_members = kwargs.get('max_members', 10)
            enable_chat = kwargs.get('enable_chat', True)
            enable_video_calls = kwargs.get('enable_video_calls', True)
            allow_guest_access = kwargs.get('allow_guest_access', False)

        workspace = Workspace(
            id=uuid.uuid4(),
            name=name,
            slug=self._generate_unique_slug(name, user.username),
            description=description,
            type=workspace_type,
            owner_id=user.id,
            is_public=kwargs.get('is_public', False),
            is_template=False,
            allow_guest_access=allow_guest_access,
            require_approval=kwargs.get('require_approval', False),
            max_members=max_members,
            max_projects=kwargs.get('max_projects', 20),
            max_storage_mb=kwargs.get('max_storage_mb', 1024),
            enable_real_time_editing=kwargs.get('enable_real_time_editing', True),
            enable_comments=kwargs.get('enable_comments', True),
            enable_chat=enable_chat,
            enable_video_calls=enable_video_calls,
            notification_settings=kwargs.get('notification_settings', {"email_notifications": True}),
            member_count=1,  # Será o owner
            project_count=0,
            activity_count=1,  # Atividade de criação
            storage_used_mb=0.0,
            status="active",
            last_activity_at=datetime.now(timezone.utc)
        )
        
        self.db.add(workspace)
        self.db.flush()
        return workspace

    def _create_owner_membership(self, workspace: Workspace, user: User) -> WorkspaceMember:
        """Cria membership automática como OWNER"""
        
        membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
            status='active',
            is_favorite=workspace.type == WorkspaceType.INDIVIDUAL,  # Individual sempre favorito
            notification_preferences={
                "email_notifications": True,
                "push_notifications": False,
                "activity_digest": "daily"
            },
            last_seen_at=datetime.now(timezone.utc),
            joined_at=datetime.now(timezone.utc)
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
        meta_data: Optional[Dict] = None
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
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(activity)
        self.db.flush()
        return activity

    def _update_subscription_counters(self, user_id: str, increment_workspaces: int = 0, increment_storage: float = 0):
        """Atualiza contadores da assinatura"""
        
        subscription = self.get_user_subscription(user_id)
        if subscription:
            subscription.current_workspaces = (subscription.current_workspaces or 0) + increment_workspaces
            subscription.current_storage_mb = (subscription.current_storage_mb or 0) + increment_storage
            self.db.add(subscription)

    def delete_workspace(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Deleta um workspace (soft delete)"""
        try:
            workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                return {"success": False, "error": "Workspace não encontrado"}

            # Verificar se é o owner
            if str(workspace.owner_id) != str(user_id):
                return {"success": False, "error": "Apenas o proprietário pode deletar o workspace"}

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
                description=f"Workspace '{workspace.name}' foi deletado"
            )

            self.db.commit()
            return {"success": True, "message": "Workspace deletado com sucesso"}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar workspace {workspace_id}: {str(e)}")
            return {"success": False, "error": f"Erro interno: {str(e)}"}

    def get_workspace_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """Busca workspace por ID"""
        return self.db.query(Workspace).filter(
            Workspace.id == workspace_id,
            Workspace.status != "deleted"
        ).first()

    def get_workspace_members_count(self, workspace_id: str) -> int:
        """Conta membros ativos do workspace"""
        return self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.status == "active"
        ).count()

    def get_workspace_projects_count(self, workspace_id: str) -> int:
        """Conta projetos ativos do workspace"""
        return self.db.query(WorkspaceProject).filter(
            WorkspaceProject.workspace_id == workspace_id,
            WorkspaceProject.status == "active"
        ).count()

    def update_workspace(self, workspace_id: str, workspace_data: WorkspaceUpdate, user_id: str) -> Optional[dict]:
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
                description=f"Workspace '{workspace.name}' foi atualizado"
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
        return self.db.query(Workspace).filter(
            and_(
                Workspace.slug == slug,
                Workspace.status == "active"
            )
        ).first()
    
    def get_user_workspaces(
        self, user_id: str
    ) -> list[dict[str, Any]]:
        """Lista workspaces do usuário"""
        # Workspaces onde é owner
        owned_workspaces = self.db.query(Workspace).filter(
            Workspace.owner_id == user_id,
            Workspace.status == "active"
        ).all()

        # Workspaces onde é membro
        member_workspaces = (
            self.db.query(Workspace)
            .join(WorkspaceMember)
            .filter(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.status == "active",
                Workspace.status == "active"
            )
            .all()
        )

        # Combinar e remover duplicatas
        all_workspaces = list({w.id: w for w in owned_workspaces + member_workspaces}.values())
        
        return [workspace.to_dict() for workspace in all_workspaces]

    def get_workspace_limits(self, user_id: str) -> Dict[str, Any]:
        """Obtém informações sobre limites e uso atual do usuário"""
        
        subscription = self.get_user_subscription(user_id)
        
        if not subscription:
            return {
                "plan": None,
                "limits": {},
                "usage": {},
                "available": {}
            }

        current_workspaces = (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == user_id)
            .count()
        )

        plan = subscription.plan

        return {
            "plan": {
                "name": plan.name,
                "type": plan.type.value,
                "allow_collaborative_workspaces": plan.allow_collaborative_workspaces
            },
            "limits": {
                "max_workspaces": plan.max_workspaces,
                "max_members_per_workspace": plan.max_members_per_workspace,
                "max_projects_per_workspace": plan.max_projects_per_workspace,
                "max_storage_mb": plan.max_storage_mb,
                "max_executions_per_month": plan.max_executions_per_month
            },
            "usage": {
                "current_workspaces": current_workspaces,
                "current_storage_mb": subscription.current_storage_mb,
                "current_executions_this_month": subscription.current_executions_this_month
            },
            "available": {
                "workspaces": plan.max_workspaces - current_workspaces,
                "storage_mb": plan.max_storage_mb - subscription.current_storage_mb,
                "executions": plan.max_executions_per_month - subscription.current_executions_this_month
            }
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
                    Workspace.type == WorkspaceType.INDIVIDUAL
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
            "has_subscription": subscription is not None
        }

    @staticmethod
    def get_workspace_creation_rules(db: Session, user_id: str) -> Dict[str, Any]:
        """Retorna regras de criação de workspace para o usuário"""
        
        # Buscar assinatura do usuário
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription:
            return {
                "can_create": False,
                "forced_type": None,
                "reason": "Sem assinatura ativa",
                "individual_count": 0,
                "total_count": 0,
                "plan_limit": 0
            }

        # Contar workspaces
        individual_count = db.query(Workspace).filter(
            Workspace.owner_id == user_id,
            Workspace.type == WorkspaceType.INDIVIDUAL
        ).count()
        
        total_count = db.query(Workspace).filter(
            Workspace.owner_id == user_id
        ).count()
        
        plan = subscription.plan

        # Aplicar regra de negócio: 1 individual obrigatório + demais colaborativos
        can_create = total_count < plan.max_workspaces
        
        if individual_count == 0:
            # Primeiro workspace deve ser individual
            forced_type = WorkspaceType.INDIVIDUAL
            reason = "Primeiro workspace deve ser individual"
        elif individual_count >= 1:
            # Workspaces subsequentes devem ser colaborativos
            forced_type = WorkspaceType.COLLABORATIVE
            reason = "Workspaces adicionais devem ser colaborativos"
        else:
            forced_type = None
            reason = "Tipo livre"

        return {
            "can_create": can_create,
            "forced_type": forced_type,
            "reason": reason,
            "individual_count": individual_count,
            "total_count": total_count,
            "plan_limit": plan.max_workspaces,
            "plan_name": plan.name,
            "allows_collaborative": plan.allow_collaborative_workspaces
        }

    # ==================== MEMBROS ====================
    
    def invite_member(self, workspace_id: str, invite_data: MemberInvite, inviter_id: str) -> WorkspaceInvitation:
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
        if existing_user and self._is_workspace_member(workspace_id, str(existing_user)):
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
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        self.db.add(invitation)

        # Registrar atividade
        self._log_activity(
            workspace_id=workspace_id,
            user_id=inviter_id,
            action="member_invited",
            resource_type="invitation",
            resource_id=str(invitation.id),
            description=f"Usuário {invite_data.email} foi convidado com role {invite_data.role.value}"
        )

        self.db.commit()
        return invitation

    def accept_invitation(self, token: str, user_id: str) -> WorkspaceMember | None:
        """Aceita um convite para workspace"""
        invitation = self.db.query(WorkspaceInvitation).filter(
            WorkspaceInvitation.token == token,
            WorkspaceInvitation.status == "pending"
        ).first()

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
        member = self._add_member(str(invitation.workspace_id), user_id, invitation.role)

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
            description=f"Usuário aceitou convite e se juntou ao workspace"
        )

        self.db.commit()
        return member

    def remove_member(self, workspace_id: str, member_id: int, remover_id: str) -> bool:
        """Remove um membro do workspace"""
        try:
            # Verificar permissão
            if not self._has_permission(workspace_id, remover_id, "admin"):
                raise PermissionError("Sem permissão para remover membros")

            member = self.db.query(WorkspaceMember).filter(
                WorkspaceMember.id == member_id,
                WorkspaceMember.workspace_id == workspace_id
            ).first()

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
                description=f"Membro foi removido do workspace"
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

            member = self.db.query(WorkspaceMember).filter(
                WorkspaceMember.id == member_id,
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.status == "active"
            ).first()

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
                description=f"Role do membro alterado de {old_role} para {new_role.value}"
            )

            self.db.commit()
            return member

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar role do membro {member_id}: {str(e)}")
            return None

    def get_workspace_members(self, workspace_id: str) -> list[WorkspaceMember]:
        """Lista membros do workspace"""
        return self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.status == "active"
        ).all()

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
                is_active=True
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
            last_edited_at=datetime.now(timezone.utc)
        )

        self.db.add(project)
        self.db.flush()

        # Adicionar criador como colaborador
        self._add_project_collaborator(
            str(project.id), creator_id,
            can_edit=True, can_comment=True, can_share=True, can_delete=True
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
            description=f"Projeto '{project.name}' foi criado"
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
        self, workspace_id: int, user_id: int
    ) -> list[WorkspaceProject]:
        """Obtém projetos do workspace que o usuário tem acesso"""

        # Verificar se é membro do workspace
        if not self._is_workspace_member(workspace_id, user_id):
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
            workspace['project_count'] -= 1

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
    ) -> list[WorkspaceActivity]:
        """Lista atividades do workspace"""
        # Verificar permissão
        if not self._has_permission(workspace_id, user_id, "read"):
            raise PermissionError("Sem permissão para ver atividades")

        return (
            self.db.query(WorkspaceActivity)
            .filter(WorkspaceActivity.workspace_id == workspace_id)
            .order_by(WorkspaceActivity.created_at.desc())
            .limit(limit)
            .all()
        )

    # ==================== MÉTODOS AUXILIARES ====================

    @staticmethod
    def _generate_unique_slug(db: Session, name: str, username: str) -> str:
        """Gera slug único para o workspace"""
        import re
        
        # Limpar nome para slug
        base_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        base_slug = re.sub(r'\s+', '-', base_slug.strip())
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
                "activity_digest": "daily"
            },
            joined_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc)
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
            last_seen_at=datetime.now(timezone.utc)
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
        member = self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.status == "active"
        ).first()

        if not member:
            return False

        # Mapear permissões por role
        permissions_map = {
            WorkspaceRole.ADMIN: ["read", "write", "admin"],
            WorkspaceRole.MEMBER: ["read", "write"],
            WorkspaceRole.VIEWER: ["read"]
        }

        allowed_permissions = permissions_map.get(member.role, [])
        return permission in allowed_permissions

    def _is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
        """Verifica se usuário é membro do workspace"""
        return self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.status == "active"
        ).first() is not None

    def _can_edit_project(self, project_id: str, user_id: str) -> bool:
        """Verifica se usuário pode editar projeto"""
        collaborator = self.db.query(ProjectCollaborator).filter(
            ProjectCollaborator.project_id == project_id,
            ProjectCollaborator.user_id == user_id
        ).first()
        
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
        meta_data: dict | None = None
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
            created_at=datetime.now(timezone.utc)
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
            "last_activity": workspace.last_activity_at
        }

    def _count_individual_workspaces(self, user_id: str) -> int:
        """Conta workspaces individuais do usuário"""
        return (
            self.db.query(Workspace)
            .filter(
                and_(
                    Workspace.owner_id == user_id,
                    Workspace.type == WorkspaceType.INDIVIDUAL
                )
            )
            .count()
        )

    def _count_total_workspaces(self, user_id: str) -> int:
        """Conta total de workspaces do usuário"""
        return (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == user_id)
            .count()
        )

    def change_member_role(
        self, workspace_id: str, user_id: str, role: WorkspaceRole
    ) -> bool:
        """Altera role de um membro"""
        member = self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.status == "active"
        ).first()

        if not member:
            return False

        member.role = role
        self.db.commit()
        return True

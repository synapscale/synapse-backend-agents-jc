"""
Serviço para criar configurações padrão do usuário
"""
from sqlalchemy.orm import Session
from synapse.models.user import User
from synapse.models.workspace import Workspace, WorkspaceType
from synapse.models.workspace_member import WorkspaceMember, WorkspaceRole
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.subscription import Plan, UserSubscription, PlanType, SubscriptionStatus
# from synapse.services.workspace_service import WorkspaceService  # Não usado atualmente
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

def create_user_defaults(db: Session, user: User) -> dict:
    """
    Cria todas as configurações padrão para um novo usuário:
    1. Plano FREE (se não existir)
    2. Assinatura FREE ativa
    3. Workspace individual automático
    4. Membership como OWNER
    5. Atividade inicial registrada
    6. Contadores atualizados
    """
    try:
        logger.info(f"Criando configurações padrão para usuário {user.id}")
        
        # 1. Garantir que existe plano FREE
        free_plan = db.query(Plan).filter(Plan.slug == "free").first()
        
        # Se não encontrou o plano FREE, tentar buscar pelo ID específico conhecido
        if not free_plan:
            logger.info("Plano FREE não encontrado por slug, tentando buscar por ID específico")
            from uuid import UUID
            try:
                known_plan_id = UUID("6f97342b-ab33-469f-bedb-8a73d067588d")
                free_plan = db.query(Plan).filter(Plan.id == known_plan_id).first()
                if free_plan:
                    logger.info(f"Plano encontrado por ID específico: {free_plan.id}")
            except Exception as e:
                logger.warning(f"Erro ao buscar plano por ID específico: {e}")
        
        if not free_plan:
            logger.info("Criando plano FREE padrão")
            from uuid import UUID
            free_plan = Plan(
                id=UUID("6f97342b-ab33-469f-bedb-8a73d067588d"),  # Usar ID específico
                name="Plano Gratuito",
                slug="free",
                type=PlanType.FREE,
                price_monthly=0.0,
                price_yearly=0.0,
                max_workspaces=3,
                max_members_per_workspace=5,
                max_storage_mb=1024,  # 1GB
                max_executions_per_month=100,
                allow_collaborative_workspaces=True,
                allow_custom_domains=False,
                allow_api_access=False,
                allow_advanced_analytics=False,
                allow_priority_support=False,
                is_active=True
            )
            db.add(free_plan)
            db.flush()  # Usar flush em vez de commit
            # Refresh do objeto para garantir que o ID seja populado
            db.refresh(free_plan)
            logger.info(f"Plano FREE criado com ID fixo: {free_plan.id}")
        
        # Garantir que temos um plano válido
        if not free_plan or not free_plan.id:
            raise ValueError(f"Não foi possível obter plano FREE válido. free_plan: {free_plan}, id: {free_plan.id if free_plan else 'N/A'}")

        # 2. Criar assinatura FREE para o usuário
        logger.info(f"Criando assinatura FREE para usuário {user.id}")
        user_subscription = UserSubscription(
            user_id=user.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
            current_workspaces=0,  # Será atualizado após criar workspace
            current_storage_mb=0,
            current_executions_this_month=0,
            subscription_metadata={"created_automatically": True}
        )
        db.add(user_subscription)
        db.flush()
        logger.info(f"Assinatura criada com ID: {user_subscription.id}")

        # 3. Criar workspace individual automático
        logger.info(f"Criando workspace individual para usuário {user.id}")
        
        # Garantir que temos o plan_id válido
        plan_id = free_plan.id
        logger.info(f"Plan ID do free_plan: {plan_id}")
        logger.info(f"Type of plan_id: {type(plan_id)}")
        
        if not plan_id:
            raise ValueError("Plan ID não foi gerado corretamente")
        
        # Garantir que o plan_id não seja None antes de criar o workspace
        if plan_id is None:
            raise ValueError("plan_id não pode ser None ao criar workspace")
            
        logger.info(f"Criando workspace com plan_id: {plan_id}")
        
        # Validação extra antes de criar o workspace
        if plan_id is None:
            raise ValueError("ERRO CRÍTICO: plan_id é None antes de criar workspace")
        
        # Criar workspace com argumentos explícitos
        workspace_args = {
            "id": uuid.uuid4(),
            "name": f"Workspace de {user.full_name}",
            "slug": f"workspace-{user.username}-{uuid.uuid4().hex[:8]}",
            "description": "Seu workspace pessoal para projetos individuais",
            "type": WorkspaceType.INDIVIDUAL,
            "owner_id": user.id,
            "plan_id": plan_id,  # Usar a variável explícita
            "is_public": False,
            "is_template": False,
            "allow_guest_access": False,
            "require_approval": False,
            "max_members": 1,  # Workspace individual = apenas o dono
            "max_projects": 10,
            "max_storage_mb": 512,  # 512MB para workspace individual
            "enable_real_time_editing": True,
            "enable_comments": True,
            "enable_chat": False,  # Chat desabilitado para workspace individual
            "enable_video_calls": False,  # Video calls desabilitado para workspace individual
            "notification_settings": {"email_notifications": True, "push_notifications": False},
            "member_count": 1,  # Será o próprio dono
            "project_count": 0,
            "activity_count": 1,  # Atividade de criação
            "storage_used_mb": 0.0,
            "status": "active",
            "last_activity_at": datetime.now(timezone.utc)
        }
        
        # Log dos argumentos antes de criar
        logger.info(f"Argumentos do workspace - plan_id: {workspace_args['plan_id']}")
        
        individual_workspace = Workspace(**workspace_args)
        
        # Verificar se o plan_id foi preservado no objeto
        logger.info(f"Workspace criado - plan_id no objeto: {individual_workspace.plan_id}")
        
        db.add(individual_workspace)
        db.flush()
        
        # Verificar novamente após flush
        logger.info(f"Após flush - plan_id no objeto: {individual_workspace.plan_id}")
        logger.info(f"Workspace individual criado: {individual_workspace.id}")

        # 4. Criar membership automática como OWNER
        logger.info(f"Criando membership OWNER para usuário {user.id}")
        workspace_member = WorkspaceMember(
            workspace_id=individual_workspace.id,
            user_id=user.id,
            role=WorkspaceRole.OWNER,
            status="active",
            is_favorite=True,  # Workspace individual sempre favorito
            notification_preferences={
                "email_notifications": True,
                "push_notifications": False,
                "activity_digest": "daily"
            },
            last_seen_at=datetime.now(timezone.utc),
            joined_at=datetime.now(timezone.utc)
        )
        db.add(workspace_member)
        db.flush()
        logger.info(f"Membership criada com ID: {workspace_member.id}")

        # 5. Registrar atividade inicial
        logger.info(f"Registrando atividade inicial no workspace {individual_workspace.id}")
        initial_activity = WorkspaceActivity(
            id=uuid.uuid4(),
            workspace_id=individual_workspace.id,
            user_id=user.id,
            action="workspace_created",
            resource_type="workspace",
            resource_id=str(individual_workspace.id),
            description=f"Workspace individual criado automaticamente para {user.full_name}",
            meta_data={
                "workspace_type": "INDIVIDUAL",
                "auto_created": True,
                "user_signup": True
            },
            created_at=datetime.now(timezone.utc)
        )
        db.add(initial_activity)
        db.flush()
        logger.info(f"Atividade inicial registrada com ID: {initial_activity.id}")

        # 6. Atualizar contadores da assinatura
        logger.info("Atualizando contadores da assinatura")
        user_subscription.current_workspaces = 1
        db.add(user_subscription)

        # 7. Commit de todas as operações
        db.commit()
        
        logger.info(f"✅ Configurações padrão criadas com sucesso para usuário {user.id}")
        
        return {
            "success": True,
            "user_id": str(user.id),
            "plan": {
                "id": str(free_plan.id),
                "name": free_plan.name,
                "slug": free_plan.slug,
                "type": free_plan.type.value
            },
            "subscription": {
                "id": str(user_subscription.id),
                "status": user_subscription.status.value,
                "current_workspaces": user_subscription.current_workspaces
            },
            "workspace": {
                "id": str(individual_workspace.id),
                "name": individual_workspace.name,
                "slug": individual_workspace.slug,
                "type": individual_workspace.type.value
            },
            "membership": {
                "id": str(workspace_member.id),
                "role": workspace_member.role.value,
                "status": workspace_member.status
            },
            "activity": {
                "id": str(initial_activity.id),
                "action": initial_activity.action
            }
        }

    except Exception as e:
        logger.error(f"Erro ao criar configurações padrão para usuário {user.id}: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "user_id": str(user.id)
        } 
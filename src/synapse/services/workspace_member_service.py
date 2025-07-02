"""
Serviço de gerenciamento de membros de workspace com sincronização automática
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from synapse.models.workspace import Workspace, WorkspaceType
from synapse.models.workspace_member import WorkspaceMember, WorkspaceRole
from synapse.models.workspace_activity import WorkspaceActivity
from synapse.models.workspace_invitation import WorkspaceInvitation
from synapse.models.user import User
from synapse.models.subscription import UserSubscription, Plan
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class WorkspaceMemberService:
    """Serviço para gerenciamento de membros com sincronização automática"""

    def __init__(self, db: Session):
        self.db = db

    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: WorkspaceRole,
        invited_by_user_id: str,
    ) -> Dict[str, Any]:
        """
        Adiciona membro ao workspace com validações e sincronização automática
        """
        try:
            logger.info(f"Adicionando membro {user_id} ao workspace {workspace_id}")

            # 1. VALIDAÇÕES
            validation = self._validate_member_addition(
                workspace_id, user_id, invited_by_user_id
            )
            if not validation["can_add"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "error_code": validation.get("error_code"),
                }

            workspace = validation["workspace"]
            new_member_user = validation["new_member_user"]
            inviter_user = validation["inviter_user"]

            # 2. VERIFICAR SE JÁ É MEMBRO
            existing_member = (
                self.db.query(WorkspaceMember)
                .filter(
                    and_(
                        WorkspaceMember.workspace_id == workspace_id,
                        WorkspaceMember.user_id == user_id,
                    )
                )
                .first()
            )

            if existing_member:
                return {
                    "success": False,
                    "error": f"Usuário {new_member_user.full_name} já é membro deste workspace",
                    "error_code": "ALREADY_MEMBER",
                }

            # 3. CRIAR MEMBERSHIP
            member = WorkspaceMember(
                workspace_id=workspace_id,
                user_id=user_id,
                role=role,
                status="active",
                is_favorite=False,
                notification_preferences={
                    "email_notifications": True,
                    "push_notifications": False,
                    "activity_digest": "weekly",
                },
                last_seen_at=datetime.now(timezone.utc),
                joined_at=datetime.now(timezone.utc),
            )

            self.db.add(member)
            self.db.flush()

            # 4. ATUALIZAR CONTADOR DO WORKSPACE
            workspace.member_count = (workspace.member_count or 0) + 1
            workspace.last_activity_at = datetime.now(timezone.utc)
            self.db.add(workspace)

            # 5. REGISTRAR ATIVIDADE
            activity = WorkspaceActivity(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                user_id=invited_by_user_id,
                action="member_added",
                resource_type="member",
                resource_id=str(member.id),
                description=f"{new_member_user.full_name} foi adicionado ao workspace por {inviter_user.full_name}",
                meta_data={
                    "new_member_id": str(user_id),
                    "new_member_name": new_member_user.full_name,
                    "new_member_role": role.value,
                    "inviter_id": str(inviter_id),
                    "inviter_name": inviter_user.full_name,
                },
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(activity)
            self.db.commit()

            logger.info(
                f"✅ Membro {user_id} adicionado com sucesso ao workspace {workspace_id}"
            )

            return {
                "success": True,
                "member": {
                    "id": str(member.id),
                    "user_id": str(member.user_id),
                    "user_name": new_member_user.full_name,
                    "role": member.role.value,
                    "status": member.status,
                    "joined_at": member.joined_at.isoformat(),
                },
                "workspace": {
                    "id": str(workspace.id),
                    "name": workspace.name,
                    "member_count": workspace.member_count,
                },
                "activity_id": str(activity.id),
            }

        except Exception as e:
            logger.error(f"Erro ao adicionar membro: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": f"Erro interno: {str(e)}"}

    def remove_member(
        self, workspace_id: str, user_id: str, removed_by_user_id: str
    ) -> Dict[str, Any]:
        """
        Remove membro do workspace com validações e sincronização automática
        """
        try:
            logger.info(f"Removendo membro {user_id} do workspace {workspace_id}")

            # 1. VALIDAÇÕES
            validation = self._validate_member_removal(
                workspace_id, user_id, removed_by_user_id
            )
            if not validation["can_remove"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "error_code": validation.get("error_code"),
                }

            workspace = validation["workspace"]
            member = validation["member"]
            removed_user = validation["removed_user"]
            remover_user = validation["remover_user"]

            # 2. REGISTRAR ATIVIDADE ANTES DE DELETAR
            activity = WorkspaceActivity(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                user_id=removed_by_user_id,
                action="member_removed",
                resource_type="member",
                resource_id=str(member.id),
                description=f"{removed_user.full_name} foi removido do workspace por {remover_user.full_name}",
                meta_data={
                    "removed_member_id": str(user_id),
                    "removed_member_name": removed_user.full_name,
                    "removed_member_role": member.role.value,
                    "remover_id": str(removed_by_user_id),
                    "remover_name": remover_user.full_name,
                },
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(activity)

            # 3. DELETAR MEMBERSHIP
            self.db.delete(member)

            # 4. ATUALIZAR CONTADOR DO WORKSPACE
            workspace.member_count = max((workspace.member_count or 1) - 1, 0)
            workspace.last_activity_at = datetime.now(timezone.utc)
            self.db.add(workspace)

            self.db.commit()

            logger.info(
                f"✅ Membro {user_id} removido com sucesso do workspace {workspace_id}"
            )

            return {
                "success": True,
                "message": f"{removed_user.full_name} foi removido do workspace",
                "workspace": {
                    "id": str(workspace.id),
                    "name": workspace.name,
                    "member_count": workspace.member_count,
                },
                "activity_id": str(activity.id),
            }

        except Exception as e:
            logger.error(f"Erro ao remover membro: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": f"Erro interno: {str(e)}"}

    def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        new_role: WorkspaceRole,
        updated_by_user_id: str,
    ) -> Dict[str, Any]:
        """
        Atualiza role do membro com validações e sincronização automática
        """
        try:
            logger.info(
                f"Atualizando role do membro {user_id} no workspace {workspace_id}"
            )

            # 1. VALIDAÇÕES
            validation = self._validate_role_update(
                workspace_id, user_id, new_role, updated_by_user_id
            )
            if not validation["can_update"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "error_code": validation.get("error_code"),
                }

            workspace = validation["workspace"]
            member = validation["member"]
            member_user = validation["member_user"]
            updater_user = validation["updater_user"]
            old_role = member.role

            # 2. ATUALIZAR ROLE
            member.role = new_role
            self.db.add(member)

            # 3. ATUALIZAR ÚLTIMA ATIVIDADE DO WORKSPACE
            workspace.last_activity_at = datetime.now(timezone.utc)
            self.db.add(workspace)

            # 4. REGISTRAR ATIVIDADE
            activity = WorkspaceActivity(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                user_id=updated_by_user_id,
                action="member_role_updated",
                resource_type="member",
                resource_id=str(member.id),
                description=f"Role de {member_user.full_name} alterado de {old_role.value} para {new_role.value} por {updater_user.full_name}",
                meta_data={
                    "member_id": str(user_id),
                    "member_name": member_user.full_name,
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                    "updater_id": str(updated_by_user_id),
                    "updater_name": updater_user.full_name,
                },
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(activity)
            self.db.commit()

            logger.info(f"✅ Role do membro {user_id} atualizado com sucesso")

            return {
                "success": True,
                "member": {
                    "id": str(member.id),
                    "user_id": str(member.user_id),
                    "user_name": member_user.full_name,
                    "old_role": old_role.value,
                    "new_role": member.role.value,
                    "status": member.status,
                },
                "activity_id": str(activity.id),
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar role do membro: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": f"Erro interno: {str(e)}"}

    def _validate_member_addition(
        self, workspace_id: str, user_id: str, invited_by_user_id: str
    ) -> Dict[str, Any]:
        """Validações para adição de membro"""

        # 1. Verificar se workspace existe
        workspace = (
            self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if not workspace:
            return {
                "can_add": False,
                "reason": "Workspace não encontrado",
                "error_code": "WORKSPACE_NOT_FOUND",
            }

        # 2. Verificar se é workspace individual (não permite membros adicionais)
        if workspace.type == WorkspaceType.INDIVIDUAL:
            return {
                "can_add": False,
                "reason": "Workspaces individuais não permitem membros adicionais",
                "error_code": "INDIVIDUAL_NO_MEMBERS",
            }

        # 3. Verificar se quem está convidando tem permissão
        inviter_member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == invited_by_user_id,
                )
            )
            .first()
        )

        if not inviter_member or inviter_member.role not in [
            WorkspaceRole.OWNER,
            WorkspaceRole.ADMIN,
        ]:
            return {
                "can_add": False,
                "reason": "Apenas owners e admins podem adicionar membros",
                "error_code": "INSUFFICIENT_PERMISSIONS",
            }

        # 4. Verificar limite de membros
        if workspace.member_count >= workspace.max_members:
            return {
                "can_add": False,
                "reason": f"Limite de membros atingido ({workspace.member_count}/{workspace.max_members})",
                "error_code": "MEMBER_LIMIT_REACHED",
            }

        # 5. Verificar se usuários existem
        new_member_user = self.db.query(User).filter(User.id == user_id).first()
        inviter_user = self.db.query(User).filter(User.id == invited_by_user_id).first()

        if not new_member_user or not inviter_user:
            return {
                "can_add": False,
                "reason": "Usuário não encontrado",
                "error_code": "USER_NOT_FOUND",
            }

        return {
            "can_add": True,
            "workspace": workspace,
            "new_member_user": new_member_user,
            "inviter_user": inviter_user,
        }

    def _validate_member_removal(
        self, workspace_id: str, user_id: str, removed_by_user_id: str
    ) -> Dict[str, Any]:
        """Validações para remoção de membro"""

        # 1. Verificar se workspace existe
        workspace = (
            self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if not workspace:
            return {
                "can_remove": False,
                "reason": "Workspace não encontrado",
                "error_code": "WORKSPACE_NOT_FOUND",
            }

        # 2. Verificar se membro existe
        member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
            .first()
        )

        if not member:
            return {
                "can_remove": False,
                "reason": "Membro não encontrado",
                "error_code": "MEMBER_NOT_FOUND",
            }

        # 3. Não permitir remover o owner
        if member.role == WorkspaceRole.OWNER:
            return {
                "can_remove": False,
                "reason": "Não é possível remover o owner do workspace",
                "error_code": "CANNOT_REMOVE_OWNER",
            }

        # 4. Verificar permissões de quem está removendo
        remover_member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == removed_by_user_id,
                )
            )
            .first()
        )

        if not remover_member:
            return {
                "can_remove": False,
                "reason": "Sem permissão para remover membros",
                "error_code": "NO_PERMISSION",
            }

        # Apenas owners e admins podem remover, ou o próprio usuário pode sair
        if (
            remover_member.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]
            and removed_by_user_id != user_id
        ):
            return {
                "can_remove": False,
                "reason": "Apenas owners, admins ou o próprio usuário podem remover membros",
                "error_code": "INSUFFICIENT_PERMISSIONS",
            }

        # 5. Obter dados dos usuários
        removed_user = self.db.query(User).filter(User.id == user_id).first()
        remover_user = self.db.query(User).filter(User.id == removed_by_user_id).first()

        return {
            "can_remove": True,
            "workspace": workspace,
            "member": member,
            "removed_user": removed_user,
            "remover_user": remover_user,
        }

    def _validate_role_update(
        self,
        workspace_id: str,
        user_id: str,
        new_role: WorkspaceRole,
        updated_by_user_id: str,
    ) -> Dict[str, Any]:
        """Validações para atualização de role"""

        # 1. Verificar se workspace existe
        workspace = (
            self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if not workspace:
            return {
                "can_update": False,
                "reason": "Workspace não encontrado",
                "error_code": "WORKSPACE_NOT_FOUND",
            }

        # 2. Verificar se membro existe
        member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id,
                )
            )
            .first()
        )

        if not member:
            return {
                "can_update": False,
                "reason": "Membro não encontrado",
                "error_code": "MEMBER_NOT_FOUND",
            }

        # 3. Não permitir alterar role do owner
        if member.role == WorkspaceRole.OWNER:
            return {
                "can_update": False,
                "reason": "Não é possível alterar o role do owner",
                "error_code": "CANNOT_UPDATE_OWNER",
            }

        # 4. Verificar permissões de quem está atualizando
        updater_member = (
            self.db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == updated_by_user_id,
                )
            )
            .first()
        )

        if not updater_member or updater_member.role != WorkspaceRole.OWNER:
            return {
                "can_update": False,
                "reason": "Apenas o owner pode alterar roles de membros",
                "error_code": "INSUFFICIENT_PERMISSIONS",
            }

        # 5. Obter dados dos usuários
        member_user = self.db.query(User).filter(User.id == user_id).first()
        updater_user = self.db.query(User).filter(User.id == updated_by_user_id).first()

        return {
            "can_update": True,
            "workspace": workspace,
            "member": member,
            "member_user": member_user,
            "updater_user": updater_user,
        }

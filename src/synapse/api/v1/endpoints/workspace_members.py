"""
Endpoints para gerenciamento de membros de workspace com sincronização automática
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user
from synapse.database import get_db
from synapse.models.user import User
from synapse.models.workspace_member import WorkspaceRole
from synapse.services.workspace_member_service import WorkspaceMemberService
from synapse.schemas.workspace_member import (
    WorkspaceMemberResponse,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/{workspace_id}/members",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar membro ao workspace",
    tags=["workspaces"],
)
async def add_workspace_member(
    workspace_id: str,
    member_data: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adiciona um novo membro ao workspace com sincronização automática.
    
    **Validações automáticas:**
    - Workspace deve existir e ser colaborativo
    - Usuário deve ter permissão (OWNER ou ADMIN)
    - Limite de membros não pode ser excedido
    - Usuário a ser adicionado deve existir
    - Não pode adicionar membro duplicado
    
    **Sincronização automática:**
    - Atualiza contador de membros do workspace
    - Registra atividade no workspace
    - Atualiza última atividade do workspace
    """
    try:
        logger.info(f"Adicionando membro ao workspace {workspace_id} por usuário {current_user.id}")
        
        service = WorkspaceMemberService(db)
        result = service.add_member(
            workspace_id=workspace_id,
            user_id=member_data.user_id,
            role=member_data.role,
            invited_by_user_id=str(current_user.id)
        )
        
        if not result["success"]:
            error_codes = {
                "WORKSPACE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "INDIVIDUAL_NO_MEMBERS": status.HTTP_400_BAD_REQUEST,
                "INSUFFICIENT_PERMISSIONS": status.HTTP_403_FORBIDDEN,
                "MEMBER_LIMIT_REACHED": status.HTTP_400_BAD_REQUEST,
                "USER_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "ALREADY_MEMBER": status.HTTP_409_CONFLICT,
            }
            
            status_code = error_codes.get(result.get("error_code"), status.HTTP_400_BAD_REQUEST)
            raise HTTPException(status_code=status_code, detail=result["error"])
        
        logger.info(f"✅ Membro adicionado com sucesso ao workspace {workspace_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar membro ao workspace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete(
    "/{workspace_id}/members/{user_id}",
    response_model=dict,
    summary="Remover membro do workspace",
    tags=["workspaces"],
)
async def remove_workspace_member(
    workspace_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove um membro do workspace com sincronização automática.
    
    **Validações automáticas:**
    - Workspace deve existir
    - Membro deve existir
    - Não pode remover o owner
    - Usuário deve ter permissão ou estar removendo a si mesmo
    
    **Sincronização automática:**
    - Atualiza contador de membros do workspace
    - Registra atividade no workspace
    - Atualiza última atividade do workspace
    """
    try:
        logger.info(f"Removendo membro {user_id} do workspace {workspace_id} por usuário {current_user.id}")
        
        service = WorkspaceMemberService(db)
        result = service.remove_member(
            workspace_id=workspace_id,
            user_id=user_id,
            removed_by_user_id=str(current_user.id)
        )
        
        if not result["success"]:
            error_codes = {
                "WORKSPACE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "MEMBER_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "CANNOT_REMOVE_OWNER": status.HTTP_400_BAD_REQUEST,
                "NO_PERMISSION": status.HTTP_403_FORBIDDEN,
                "INSUFFICIENT_PERMISSIONS": status.HTTP_403_FORBIDDEN,
            }
            
            status_code = error_codes.get(result.get("error_code"), status.HTTP_400_BAD_REQUEST)
            raise HTTPException(status_code=status_code, detail=result["error"])
        
        logger.info(f"✅ Membro {user_id} removido com sucesso do workspace {workspace_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover membro do workspace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put(
    "/{workspace_id}/members/{user_id}/role",
    response_model=dict,
    summary="Atualizar role do membro",
    tags=["workspaces"],
)
async def update_member_role(
    workspace_id: str,
    user_id: str,
    role_data: WorkspaceMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza o role de um membro do workspace com sincronização automática.
    
    **Validações automáticas:**
    - Workspace deve existir
    - Membro deve existir
    - Não pode alterar role do owner
    - Apenas owner pode alterar roles
    
    **Sincronização automática:**
    - Registra atividade no workspace
    - Atualiza última atividade do workspace
    """
    try:
        logger.info(f"Atualizando role do membro {user_id} no workspace {workspace_id} por usuário {current_user.id}")
        
        service = WorkspaceMemberService(db)
        result = service.update_member_role(
            workspace_id=workspace_id,
            user_id=user_id,
            new_role=role_data.role,
            updated_by_user_id=str(current_user.id)
        )
        
        if not result["success"]:
            error_codes = {
                "WORKSPACE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "MEMBER_NOT_FOUND": status.HTTP_404_NOT_FOUND,
                "CANNOT_UPDATE_OWNER": status.HTTP_400_BAD_REQUEST,
                "INSUFFICIENT_PERMISSIONS": status.HTTP_403_FORBIDDEN,
            }
            
            status_code = error_codes.get(result.get("error_code"), status.HTTP_400_BAD_REQUEST)
            raise HTTPException(status_code=status_code, detail=result["error"])
        
        logger.info(f"✅ Role do membro {user_id} atualizado com sucesso no workspace {workspace_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar role do membro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get(
    "/{workspace_id}/members",
    response_model=List[WorkspaceMemberResponse],
    summary="Listar membros do workspace",
    tags=["workspaces"],
)
async def list_workspace_members(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista todos os membros do workspace com informações detalhadas.
    
    **Informações retornadas:**
    - Dados do usuário (nome, email, etc.)
    - Role no workspace
    - Status da membership
    - Data de entrada
    - Última visualização
    """
    try:
        logger.info(f"Listando membros do workspace {workspace_id} para usuário {current_user.id}")
        
        # Verificar se usuário tem acesso ao workspace
        from synapse.models.workspace_member import WorkspaceMember
        from synapse.models.workspace import Workspace
        from synapse.models.user import User as UserModel
        from sqlalchemy import and_
        
        # Verificar se é membro do workspace
        member_check = (
            db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
            .first()
        )
        
        if not member_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem acesso a este workspace"
            )
        
        # Buscar membros com informações do usuário
        members_query = (
            db.query(WorkspaceMember, UserModel)
            .join(UserModel, WorkspaceMember.user_id == UserModel.id)
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .offset(offset)
            .limit(limit)
        )
        
        members_data = members_query.all()
        
        members_response = []
        for member, user in members_data:
            members_response.append(
                WorkspaceMemberResponse(
                    id=str(member.id),
                    workspace_id=str(member.workspace_id),
                    user_id=str(member.user_id),
                    user_name=user.full_name,
                    user_email=user.email,
                    role=member.role.value,
                    status=member.status,
                    is_favorite=member.is_favorite,
                    joined_at=member.joined_at,
                    last_seen_at=member.last_seen_at,
                )
            )
        
        logger.info(f"✅ Retornados {len(members_response)} membros do workspace {workspace_id}")
        return members_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar membros do workspace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceMemberResponse,
    summary="Obter detalhes de um membro específico",
    tags=["workspaces"],
)
async def get_workspace_member(
    workspace_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtém detalhes de um membro específico do workspace.
    """
    try:
        logger.info(f"Obtendo detalhes do membro {user_id} no workspace {workspace_id}")
        
        from synapse.models.workspace_member import WorkspaceMember
        from synapse.models.user import User as UserModel
        from sqlalchemy import and_
        
        # Verificar se usuário atual tem acesso ao workspace
        current_member = (
            db.query(WorkspaceMember)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
            .first()
        )
        
        if not current_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem acesso a este workspace"
            )
        
        # Buscar o membro específico
        member_data = (
            db.query(WorkspaceMember, UserModel)
            .join(UserModel, WorkspaceMember.user_id == UserModel.id)
            .filter(
                and_(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == user_id
                )
            )
            .first()
        )
        
        if not member_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membro não encontrado neste workspace"
            )
        
        member, user = member_data
        
        response = WorkspaceMemberResponse(
            id=str(member.id),
            workspace_id=str(member.workspace_id),
            user_id=str(member.user_id),
            user_name=user.full_name,
            user_email=user.email,
            role=member.role.value,
            status=member.status,
            is_favorite=member.is_favorite,
            joined_at=member.joined_at,
            last_seen_at=member.last_seen_at,
        )
        
        logger.info(f"✅ Detalhes do membro {user_id} obtidos com sucesso")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do membro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        ) 
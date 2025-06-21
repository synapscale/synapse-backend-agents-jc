"""
Endpoints da API para Workspaces
Criado por José - um desenvolvedor Full Stack
API completa para workspaces colaborativos e gerenciamento de projetos
"""

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status, Path
from sqlalchemy.orm import Session

from synapse.database import get_db
from synapse.models.user import User
from synapse.models.workspace_member import WorkspaceRole
from synapse.services.workspace_service import WorkspaceService
from synapse.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceStats,
    MemberInvite,
    MemberResponse,
    MemberUpdate,
    InvitationResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectVersionResponse,
    CollaboratorAdd,
    CollaboratorResponse,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    ActivityResponse,
    VersionCreate,
    WorkspaceSearch,
    ProjectSearch,
    BulkMemberOperation,
    BulkProjectOperation,
    BulkOperationResponse,
    NotificationPreferences,
    WorkspaceIntegration,
    IntegrationResponse,
)
from synapse.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== WORKSPACES ====================

@router.post("/", response_model=Dict[str, Any], summary="Criar workspace", tags=["workspaces"])
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Cria um novo workspace para o usuário autenticado"""
    try:
        logger.info(f"Criando workspace '{workspace_data.name}' para usuário {current_user.id}")
        service = WorkspaceService(db)
        
        # Verificar regras de criação
        rules = service.get_workspace_creation_rules(current_user.id)
        
        # Determinar tipo do workspace baseado nas regras
        if not rules["has_individual_workspace"]:
            workspace_type = "INDIVIDUAL"
        else:
            workspace_type = "COLLABORATIVE"
            if not rules["can_create_collaborative"]:
                raise HTTPException(
                    status_code=403, 
                    detail="Seu plano não permite criar workspaces colaborativos"
                )
        
        result = service.create_workspace(
            user_id=current_user.id,
            name=workspace_data.name,
            description=workspace_data.description,
            workspace_type=workspace_type
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"Workspace '{workspace_data.name}' criado com sucesso como {workspace_type}")
        return {
            "success": True,
            "workspace": result["workspace"],
            "type": workspace_type,
            "message": f"Workspace criado como {workspace_type}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar workspace para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/creation-rules", summary="Obter regras de criação", tags=["workspaces"])
async def get_workspace_creation_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Obtém as regras e limitações para criação de workspaces do usuário"""
    try:
        logger.info(f"Obtendo regras de criação de workspace para usuário {current_user.id}")
        service = WorkspaceService(db)
        rules = service.get_workspace_creation_rules(current_user.id)
        limits = service.get_workspace_limits(current_user.id)
        
        return {
            **rules,
            "limits": limits,
            "message": "Cada usuário pode ter apenas 1 workspace individual. Workspaces adicionais devem ser colaborativos."
        }
    except Exception as e:
        logger.error(f"Erro ao obter regras de criação: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get(
    "/",
    response_model=List[WorkspaceResponse],
    summary="Listar workspaces",
    tags=["workspaces"],
)
async def get_user_workspaces(
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados por página"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """Obtém todos os workspaces do usuário autenticado, com paginação"""
    try:
        logger.info(f"Listando workspaces para usuário {current_user.id} - limit: {limit}, offset: {offset}")
        service = WorkspaceService(db)
        result = service.get_user_workspaces(current_user.id)
        logger.info(f"Retornados {len(result)} workspaces para usuário {current_user.id}")
        return [WorkspaceResponse(**w) for w in result]
    except Exception as e:
        logger.error(f"Erro ao listar workspaces para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/search", response_model=List[WorkspaceResponse], summary="Buscar workspaces", tags=["workspaces"])
async def search_workspaces(
    query: Optional[str] = Query(None, description="Termo de busca"),
    is_public: Optional[bool] = Query(None, description="Apenas workspaces públicos"),
    has_projects: Optional[bool] = Query(None, description="Com projetos"),
    min_members: Optional[int] = Query(None, ge=1, description="Mínimo de membros"),
    max_members: Optional[int] = Query(None, ge=1, description="Máximo de membros"),
    sort_by: str = Query("activity", pattern="^(activity|members|projects|created|name)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkspaceResponse]:
    """Busca workspaces públicos com filtros avançados e paginação"""
    try:
        logger.info(f"Busca de workspaces por usuário {current_user.id} - query: '{query}', público: {is_public}")
        
        search_params = WorkspaceSearch(
            query=query,
            is_public=is_public,
            has_projects=has_projects,
            min_members=min_members,
            max_members=max_members,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )
        service = WorkspaceService(db)
        result = service.search_workspaces(search_params, current_user.id)
        logger.info(f"Busca de workspaces concluída - {len(result)} resultados")
        return result
    except Exception as e:
        logger.error(f"Erro na busca de workspaces: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{workspace_id}", response_model=WorkspaceResponse, summary="Obter workspace", tags=["workspaces"])
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Obtém detalhes de um workspace"""
    service = WorkspaceService(db)
    workspace = service.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    
    # Verificar se usuário tem acesso
    if not service._has_permission(workspace_id, str(current_user.id), "read"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse, summary="Atualizar workspace", tags=["workspaces"])
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    """Atualiza um workspace"""
    service = WorkspaceService(db)
    
    try:
        workspace = service.update_workspace(workspace_id, workspace_data, str(current_user.id))
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace não encontrado")
        return workspace
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workspace_id}", summary="Deletar workspace", tags=["workspaces"])
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Deleta um workspace"""
    service = WorkspaceService(db)
    result = service.delete_workspace(workspace_id, str(current_user.id))
    
    if not result["success"]:
        if "não encontrado" in result["error"]:
            raise HTTPException(status_code=404, detail=result["error"])
        elif "permissão" in result["error"]:
            raise HTTPException(status_code=403, detail=result["error"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": result["message"]}


@router.get("/{workspace_id}/stats", response_model=dict, summary="Obter estatísticas do workspace", tags=["workspaces"])
async def get_workspace_stats(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém estatísticas do workspace"""
    service = WorkspaceService(db)
    
    try:
        stats = service.get_workspace_stats(workspace_id, str(current_user.id))
        return stats
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ==================== MEMBROS ====================


@router.get("/{workspace_id}/members", response_model=List[MemberResponse], summary="Listar membros do workspace", tags=["workspaces"])
async def get_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista membros do workspace"""
    service = WorkspaceService(db)
    
    # Verificar permissão
    if not service._has_permission(workspace_id, str(current_user.id), "read"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    members = service.get_workspace_members(workspace_id)
    return members


@router.post("/{workspace_id}/members/invite", response_model=dict, summary="Convidar membro para workspace", tags=["workspaces"])
async def invite_member(
    workspace_id: str,
    invite_data: MemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Convida um membro para o workspace"""
    service = WorkspaceService(db)
    
    try:
        invitation = service.invite_member(workspace_id, invite_data, str(current_user.id))
        return {"message": "Convite enviado com sucesso", "invitation_id": invitation.id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workspace_id}/members/{member_id}", summary="Remover membro do workspace", tags=["workspaces"])
async def remove_member(
    workspace_id: str,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove um membro do workspace"""
    service = WorkspaceService(db)
    
    try:
        success = service.remove_member(workspace_id, member_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        return {"message": "Membro removido com sucesso"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{workspace_id}/members/{member_id}/role", summary="Atualizar role de membro", tags=["workspaces"])
async def update_member_role(
    workspace_id: str,
    member_id: int,
    role_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza o role de um membro"""
    service = WorkspaceService(db)
    
    try:
        new_role = WorkspaceRole(role_data["role"])
        member = service.update_member_role(workspace_id, member_id, new_role, str(current_user.id))
        if not member:
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        return {"message": "Role atualizado com sucesso"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== PROJETOS ====================

@router.post("/{workspace_id}/projects", response_model=dict, summary="Criar projeto no workspace", tags=["workspaces"])
async def create_project(
    workspace_id: str,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um novo projeto no workspace"""
    service = WorkspaceService(db)
    
    try:
        project = service.create_project(workspace_id, project_data, str(current_user.id))
        return {"message": "Projeto criado com sucesso", "project_id": str(project.id)}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workspace_id}/projects", response_model=List[ProjectResponse], summary="Listar projetos", tags=["workspaces"])
async def get_workspace_projects(
    workspace_id: int,
    status: Optional[str] = Query(None, pattern="^(active|archived|deleted)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """Lista projetos do workspace"""
    try:
        logger.info(f"Listando projetos do workspace {workspace_id} - status: {status}")
        service = WorkspaceService(db)
        projects = service.get_workspace_projects(workspace_id, current_user.id, status, limit, offset)
        logger.info(f"Retornados {len(projects)} projetos do workspace {workspace_id}")
        return projects
    except Exception as e:
        logger.error(f"Erro ao listar projetos do workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/projects/search", response_model=List[ProjectResponse], summary="Buscar projetos", tags=["workspaces"])
async def search_projects(
    query: Optional[str] = Query(None, description="Termo de busca"),
    workspace_id: Optional[int] = Query(None, description="ID do workspace"),
    status: Optional[str] = Query(None, pattern="^(active|archived|deleted)$"),
    has_collaborators: Optional[bool] = Query(None, description="Com colaboradores"),
    sort_by: str = Query("updated", pattern="^(updated|created|name|activity)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """Busca projetos com filtros avançados"""
    try:
        logger.info(f"Busca de projetos por usuário {current_user.id} - query: '{query}', workspace: {workspace_id}")
        
        search_params = ProjectSearch(
            query=query,
            workspace_id=workspace_id,
            status=status,
            has_collaborators=has_collaborators,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )
        service = WorkspaceService(db)
        result = service.search_projects(search_params, current_user.id)
        logger.info(f"Busca de projetos concluída - {len(result)} resultados")
        return result
    except Exception as e:
        logger.error(f"Erro na busca de projetos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/projects/{project_id}", response_model=ProjectResponse, summary="Obter projeto", tags=["workspaces"])
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Obtém detalhes de um projeto"""
    try:
        logger.info(f"Obtendo projeto {project_id} para usuário {current_user.id}")
        service = WorkspaceService(db)
        project = service.get_project(project_id, current_user.id)
        if not project:
            logger.warning(f"Projeto {project_id} não encontrado")
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        logger.info(f"Projeto {project_id} obtido com sucesso")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter projeto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/projects/{project_id}", response_model=ProjectResponse, summary="Atualizar projeto", tags=["workspaces"])
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Atualiza um projeto"""
    try:
        logger.info(f"Atualizando projeto {project_id} por usuário {current_user.id}")
        service = WorkspaceService(db)
        project = service.update_project(project_id, project_data, current_user.id)
        if not project:
            logger.warning(f"Projeto {project_id} não encontrado ou sem permissão")
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        logger.info(f"Projeto {project_id} atualizado com sucesso")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar projeto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/projects/{project_id}", summary="Deletar projeto", tags=["workspaces"])
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Remove um projeto"""
    try:
        logger.info(f"Deletando projeto {project_id} por usuário {current_user.id}")
        service = WorkspaceService(db)
        success = service.delete_project(project_id, current_user.id)
        if not success:
            logger.warning(f"Projeto {project_id} não encontrado ou sem permissão")
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        logger.info(f"Projeto {project_id} deletado com sucesso")
        return {"message": "Projeto removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar projeto {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== CONVITES ====================

@router.get(
    "/invitations",
    response_model=list[InvitationResponse],
    summary="Listar convites recebidos",
    response_description="Lista de convites retornada com sucesso",
    tags=["workspaces"],
)
async def get_user_invitations(
    status: str | None = Query(None, pattern="^(pending|accepted|declined|expired)$", description="Status do convite"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados por página"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InvitationResponse]:
    """
    Lista todos os convites recebidos pelo usuário autenticado, com paginação.
    """
    service = WorkspaceService(db)
    return service.get_user_invitations(current_user.id, status, limit, offset)


@router.post(
    "/invitations/{invitation_id}/accept",
    summary="Aceitar convite de workspace",
    response_description="Convite aceito com sucesso",
    tags=["workspaces"],
)
async def accept_invitation(
    invitation_id: int = Path(..., description="ID do convite"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Aceita um convite de workspace para o usuário autenticado.
    """
    service = WorkspaceService(db)
    success = service.accept_invitation(invitation_id, current_user.id)
    if not success:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Usuário {current_user.id} tentou aceitar convite inexistente: {invitation_id}")
        raise HTTPException(status_code=404, detail="Convite não encontrado")
    logger = logging.getLogger(__name__)
    logger.info(f"Usuário {current_user.id} aceitou convite {invitation_id}")
    return {"message": "Convite aceito com sucesso"}


@router.post(
    "/invitations/{invitation_id}/decline",
    summary="Recusar convite de workspace",
    response_description="Convite recusado com sucesso",
    tags=["workspaces"],
)
async def decline_invitation(
    invitation_id: int = Path(..., description="ID do convite"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Recusa um convite de workspace para o usuário autenticado.
    """
    service = WorkspaceService(db)
    success = service.decline_invitation(invitation_id, current_user.id)
    if not success:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Usuário {current_user.id} tentou recusar convite inexistente: {invitation_id}")
        raise HTTPException(status_code=404, detail="Convite não encontrado")
    logger = logging.getLogger(__name__)
    logger.info(f"Usuário {current_user.id} recusou convite {invitation_id}")
    return {"message": "Convite recusado com sucesso"}


# ==================== VERSÕES ====================

@router.get(
    "/projects/{project_id}/versions", response_model=list[ProjectVersionResponse], summary="Listar versões do projeto", tags=["workspaces"]
)
async def get_project_versions(
    project_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém versões do projeto"""
    service = WorkspaceService(db)
    versions = service.get_project_versions(project_id, current_user.id, limit, offset)
    if versions is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return versions


@router.post("/projects/{project_id}/versions", response_model=ProjectVersionResponse, summary="Criar versão do projeto", tags=["workspaces"])
async def create_project_version(
    project_id: int,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria uma nova versão do projeto"""
    service = WorkspaceService(db)
    return service.create_project_version(project_id, version_data, current_user.id)


@router.post("/projects/{project_id}/versions/{version_id}/restore", summary="Restaurar versão do projeto", tags=["workspaces"])
async def restore_project_version(
    project_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Restaura uma versão do projeto"""
    service = WorkspaceService(db)
    success = service.restore_project_version(project_id, version_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    return {"message": "Versão restaurada com sucesso"}


# ==================== ATIVIDADES ====================

@router.get("/{workspace_id}/activities", response_model=List[dict], summary="Listar atividades do workspace", tags=["workspaces"])
async def get_workspace_activities(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista atividades do workspace"""
    service = WorkspaceService(db)
    
    try:
        activities = service.get_workspace_activities(workspace_id, str(current_user.id), limit)
        return [activity.to_dict() for activity in activities]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/projects/{project_id}/activities", response_model=list[ActivityResponse], summary="Listar atividades do projeto", tags=["workspaces"])
async def get_project_activities(
    project_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém atividades do projeto"""
    service = WorkspaceService(db)
    activities = service.get_project_activities(
        project_id, current_user.id, limit, offset
    )
    if activities is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return activities


# ==================== OPERAÇÕES EM LOTE ====================

@router.post(
    "/workspaces/{workspace_id}/members/bulk", response_model=BulkOperationResponse, summary="Operação em lote com membros", tags=["workspaces"]
)
async def bulk_member_operation(
    workspace_id: int,
    operation: BulkMemberOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Operação em lote em membros"""
    service = WorkspaceService(db)
    return service.bulk_member_operation(workspace_id, operation, current_user.id)


@router.post(
    "/workspaces/{workspace_id}/projects/bulk", response_model=BulkOperationResponse, summary="Operação em lote com projetos", tags=["workspaces"]
)
async def bulk_project_operation(
    workspace_id: int,
    operation: BulkProjectOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Operação em lote em projetos"""
    service = WorkspaceService(db)
    return service.bulk_project_operation(workspace_id, operation, current_user.id)


# ==================== NOTIFICAÇÕES ====================

@router.get("/workspaces/{workspace_id}/notifications", summary="Obter configurações de notificação", tags=["workspaces"])
async def get_workspace_notification_settings(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém configurações de notificação do workspace"""
    service = WorkspaceService(db)
    settings = service.get_notification_settings(workspace_id, current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return settings


@router.put("/workspaces/{workspace_id}/notifications", summary="Atualizar configurações de notificação", tags=["workspaces"])
async def update_workspace_notification_settings(
    workspace_id: int,
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza configurações de notificação do workspace"""
    service = WorkspaceService(db)
    success = service.update_notification_settings(
        workspace_id, preferences, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return {"message": "Configurações de notificação atualizadas"}


# ==================== INTEGRAÇÕES ====================

@router.post(
    "/workspaces/{workspace_id}/integrations", response_model=IntegrationResponse, summary="Criar integração do workspace", tags=["workspaces"]
)
async def create_workspace_integration(
    workspace_id: int,
    integration_data: WorkspaceIntegration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria uma integração no workspace"""
    service = WorkspaceService(db)
    return service.create_integration(workspace_id, integration_data, current_user.id)


@router.get(
    "/workspaces/{workspace_id}/integrations", response_model=list[IntegrationResponse], summary="Listar integrações do workspace", tags=["workspaces"]
)
async def get_workspace_integrations(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém integrações do workspace"""
    service = WorkspaceService(db)
    integrations = service.get_workspace_integrations(workspace_id, current_user.id)
    if integrations is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return integrations


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse, summary="Atualizar integração", tags=["workspaces"])
async def update_integration(
    integration_id: int,
    integration_data: WorkspaceIntegration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza uma integração"""
    service = WorkspaceService(db)
    integration = service.update_integration(
        integration_id, integration_data, current_user.id
    )
    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return integration


@router.delete("/integrations/{integration_id}", summary="Deletar integração", tags=["workspaces"])
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove uma integração"""
    service = WorkspaceService(db)
    success = service.delete_integration(integration_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return {"message": "Integração removida com sucesso"}

"""
Endpoints da API para Workspaces
Criado por José - um desenvolvedor Full Stack
Endpoints para gerenciar workspaces colaborativos
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from src.synapse.database import get_db
from src.synapse.models.user import User
from src.synapse.services.workspace_service import WorkspaceService
from src.synapse.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceStats,
    MemberInvite, MemberResponse, MemberUpdate, InvitationResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectVersionResponse,
    CollaboratorAdd, CollaboratorResponse, CommentCreate, CommentUpdate,
    CommentResponse, ActivityResponse, VersionCreate, WorkspaceSearch,
    ProjectSearch, BulkMemberOperation, BulkProjectOperation,
    BulkOperationResponse, NotificationPreferences, WorkspaceIntegration,
    IntegrationResponse
)
from src.synapse.api.deps import get_current_user

router = APIRouter()

# ==================== WORKSPACES ====================

@router.post("/workspaces", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo workspace"""
    service = WorkspaceService(db)
    return service.create_workspace(workspace_data, current_user.id)

@router.get("/workspaces", response_model=List[WorkspaceResponse])
async def get_user_workspaces(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém workspaces do usuário"""
    service = WorkspaceService(db)
    return service.get_user_workspaces(current_user.id, limit, offset)

@router.get("/workspaces/search", response_model=List[WorkspaceResponse])
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
    db: Session = Depends(get_db)
):
    """Busca workspaces públicos"""
    search_params = WorkspaceSearch(
        query=query,
        is_public=is_public,
        has_projects=has_projects,
        min_members=min_members,
        max_members=max_members,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    service = WorkspaceService(db)
    return service.search_workspaces(search_params, current_user.id)

@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um workspace"""
    service = WorkspaceService(db)
    workspace = service.get_workspace(workspace_id, current_user.id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return workspace

@router.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um workspace"""
    service = WorkspaceService(db)
    workspace = service.update_workspace(workspace_id, workspace_data, current_user.id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return workspace

@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um workspace"""
    service = WorkspaceService(db)
    success = service.delete_workspace(workspace_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return {"message": "Workspace removido com sucesso"}

@router.get("/workspaces/{workspace_id}/stats", response_model=WorkspaceStats)
async def get_workspace_stats(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas do workspace"""
    service = WorkspaceService(db)
    stats = service.get_workspace_stats(workspace_id, current_user.id)
    if not stats:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return stats

# ==================== MEMBROS ====================

@router.post("/workspaces/{workspace_id}/invite")
async def invite_member(
    workspace_id: int,
    invite_data: MemberInvite,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convida um membro para o workspace"""
    service = WorkspaceService(db)
    invitation = service.invite_member(workspace_id, invite_data, current_user.id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    
    # Enviar email de convite em background
    background_tasks.add_task(service.send_invitation_email, invitation)
    
    return {"message": "Convite enviado com sucesso", "invitation_id": invitation.id}

@router.get("/workspaces/{workspace_id}/members", response_model=List[MemberResponse])
async def get_workspace_members(
    workspace_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém membros do workspace"""
    service = WorkspaceService(db)
    members = service.get_workspace_members(workspace_id, current_user.id, limit, offset)
    if members is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return members

@router.put("/workspaces/{workspace_id}/members/{member_id}", response_model=MemberResponse)
async def update_member(
    workspace_id: int,
    member_id: int,
    member_data: MemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um membro do workspace"""
    service = WorkspaceService(db)
    member = service.update_member(workspace_id, member_id, member_data, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return member

@router.delete("/workspaces/{workspace_id}/members/{member_id}")
async def remove_member(
    workspace_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um membro do workspace"""
    service = WorkspaceService(db)
    success = service.remove_member(workspace_id, member_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"message": "Membro removido com sucesso"}

@router.post("/workspaces/{workspace_id}/leave")
async def leave_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sai do workspace"""
    service = WorkspaceService(db)
    success = service.leave_workspace(workspace_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return {"message": "Você saiu do workspace"}

# ==================== CONVITES ====================

@router.get("/invitations", response_model=List[InvitationResponse])
async def get_user_invitations(
    status: Optional[str] = Query(None, pattern="^(pending|accepted|declined|expired)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém convites do usuário"""
    service = WorkspaceService(db)
    return service.get_user_invitations(current_user.email, status, limit, offset)

@router.post("/invitations/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aceita um convite"""
    service = WorkspaceService(db)
    success = service.accept_invitation(invitation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Convite não encontrado")
    return {"message": "Convite aceito com sucesso"}

@router.post("/invitations/{invitation_id}/decline")
async def decline_invitation(
    invitation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recusa um convite"""
    service = WorkspaceService(db)
    success = service.decline_invitation(invitation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Convite não encontrado")
    return {"message": "Convite recusado"}

# ==================== PROJETOS ====================

@router.post("/workspaces/{workspace_id}/projects", response_model=ProjectResponse)
async def create_project(
    workspace_id: int,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um novo projeto no workspace"""
    service = WorkspaceService(db)
    return service.create_project(workspace_id, project_data, current_user.id)

@router.get("/workspaces/{workspace_id}/projects", response_model=List[ProjectResponse])
async def get_workspace_projects(
    workspace_id: int,
    status: Optional[str] = Query(None, pattern="^(active|archived|deleted)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém projetos do workspace"""
    service = WorkspaceService(db)
    projects = service.get_workspace_projects(workspace_id, current_user.id, status, limit, offset)
    if projects is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return projects

@router.get("/projects/search", response_model=List[ProjectResponse])
async def search_projects(
    query: Optional[str] = Query(None, description="Termo de busca"),
    workspace_id: Optional[int] = Query(None, description="ID do workspace"),
    status: Optional[str] = Query(None, pattern="^(active|archived|deleted)$"),
    has_collaborators: Optional[bool] = Query(None, description="Com colaboradores"),
    sort_by: str = Query("updated", pattern="^(updated|created|name|activity)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca projetos"""
    search_params = ProjectSearch(
        query=query,
        workspace_id=workspace_id,
        status=status,
        has_collaborators=has_collaborators,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    service = WorkspaceService(db)
    return service.search_projects(search_params, current_user.id)

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém detalhes de um projeto"""
    service = WorkspaceService(db)
    project = service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um projeto"""
    service = WorkspaceService(db)
    project = service.update_project(project_id, project_data, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um projeto"""
    service = WorkspaceService(db)
    success = service.delete_project(project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto removido com sucesso"}

@router.post("/projects/{project_id}/archive")
async def archive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Arquiva um projeto"""
    service = WorkspaceService(db)
    success = service.archive_project(project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto arquivado com sucesso"}

@router.post("/projects/{project_id}/restore")
async def restore_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restaura um projeto arquivado"""
    service = WorkspaceService(db)
    success = service.restore_project(project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return {"message": "Projeto restaurado com sucesso"}

# ==================== COLABORADORES ====================

@router.post("/projects/{project_id}/collaborators", response_model=CollaboratorResponse)
async def add_collaborator(
    project_id: int,
    collaborator_data: CollaboratorAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adiciona um colaborador ao projeto"""
    service = WorkspaceService(db)
    return service.add_collaborator(project_id, collaborator_data, current_user.id)

@router.get("/projects/{project_id}/collaborators", response_model=List[CollaboratorResponse])
async def get_project_collaborators(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém colaboradores do projeto"""
    service = WorkspaceService(db)
    collaborators = service.get_project_collaborators(project_id, current_user.id)
    if collaborators is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return collaborators

@router.put("/projects/{project_id}/collaborators/{collaborator_id}")
async def update_collaborator_permissions(
    project_id: int,
    collaborator_id: int,
    permissions: CollaboratorAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza permissões de um colaborador"""
    service = WorkspaceService(db)
    success = service.update_collaborator_permissions(
        project_id, collaborator_id, permissions.permissions, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    return {"message": "Permissões atualizadas com sucesso"}

@router.delete("/projects/{project_id}/collaborators/{collaborator_id}")
async def remove_collaborator(
    project_id: int,
    collaborator_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um colaborador do projeto"""
    service = WorkspaceService(db)
    success = service.remove_collaborator(project_id, collaborator_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Colaborador não encontrado")
    return {"message": "Colaborador removido com sucesso"}

# ==================== COMENTÁRIOS ====================

@router.post("/projects/{project_id}/comments", response_model=CommentResponse)
async def create_comment(
    project_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria um comentário no projeto"""
    service = WorkspaceService(db)
    return service.create_comment(project_id, comment_data, current_user.id)

@router.get("/projects/{project_id}/comments", response_model=List[CommentResponse])
async def get_project_comments(
    project_id: int,
    node_id: Optional[str] = Query(None, description="ID do nó específico"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém comentários do projeto"""
    service = WorkspaceService(db)
    comments = service.get_project_comments(project_id, current_user.id, node_id, limit, offset)
    if comments is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return comments

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um comentário"""
    service = WorkspaceService(db)
    comment = service.update_comment(comment_id, comment_data, current_user.id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return comment

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um comentário"""
    service = WorkspaceService(db)
    success = service.delete_comment(comment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return {"message": "Comentário removido com sucesso"}

@router.post("/comments/{comment_id}/resolve")
async def resolve_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca um comentário como resolvido"""
    service = WorkspaceService(db)
    success = service.resolve_comment(comment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return {"message": "Comentário marcado como resolvido"}

# ==================== VERSÕES ====================

@router.get("/projects/{project_id}/versions", response_model=List[ProjectVersionResponse])
async def get_project_versions(
    project_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém versões do projeto"""
    service = WorkspaceService(db)
    versions = service.get_project_versions(project_id, current_user.id, limit, offset)
    if versions is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return versions

@router.post("/projects/{project_id}/versions", response_model=ProjectVersionResponse)
async def create_project_version(
    project_id: int,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova versão do projeto"""
    service = WorkspaceService(db)
    return service.create_project_version(project_id, version_data, current_user.id)

@router.post("/projects/{project_id}/versions/{version_id}/restore")
async def restore_project_version(
    project_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restaura uma versão do projeto"""
    service = WorkspaceService(db)
    success = service.restore_project_version(project_id, version_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    return {"message": "Versão restaurada com sucesso"}

# ==================== ATIVIDADES ====================

@router.get("/workspaces/{workspace_id}/activities", response_model=List[ActivityResponse])
async def get_workspace_activities(
    workspace_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém atividades do workspace"""
    service = WorkspaceService(db)
    activities = service.get_workspace_activities(workspace_id, current_user.id, limit, offset)
    if activities is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return activities

@router.get("/projects/{project_id}/activities", response_model=List[ActivityResponse])
async def get_project_activities(
    project_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém atividades do projeto"""
    service = WorkspaceService(db)
    activities = service.get_project_activities(project_id, current_user.id, limit, offset)
    if activities is None:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return activities

# ==================== OPERAÇÕES EM LOTE ====================

@router.post("/workspaces/{workspace_id}/members/bulk", response_model=BulkOperationResponse)
async def bulk_member_operation(
    workspace_id: int,
    operation: BulkMemberOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Operação em lote em membros"""
    service = WorkspaceService(db)
    return service.bulk_member_operation(workspace_id, operation, current_user.id)

@router.post("/workspaces/{workspace_id}/projects/bulk", response_model=BulkOperationResponse)
async def bulk_project_operation(
    workspace_id: int,
    operation: BulkProjectOperation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Operação em lote em projetos"""
    service = WorkspaceService(db)
    return service.bulk_project_operation(workspace_id, operation, current_user.id)

# ==================== NOTIFICAÇÕES ====================

@router.get("/workspaces/{workspace_id}/notifications")
async def get_workspace_notification_settings(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém configurações de notificação do workspace"""
    service = WorkspaceService(db)
    settings = service.get_notification_settings(workspace_id, current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return settings

@router.put("/workspaces/{workspace_id}/notifications")
async def update_workspace_notification_settings(
    workspace_id: int,
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza configurações de notificação do workspace"""
    service = WorkspaceService(db)
    success = service.update_notification_settings(workspace_id, preferences, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return {"message": "Configurações de notificação atualizadas"}

# ==================== INTEGRAÇÕES ====================

@router.post("/workspaces/{workspace_id}/integrations", response_model=IntegrationResponse)
async def create_workspace_integration(
    workspace_id: int,
    integration_data: WorkspaceIntegration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma integração no workspace"""
    service = WorkspaceService(db)
    return service.create_integration(workspace_id, integration_data, current_user.id)

@router.get("/workspaces/{workspace_id}/integrations", response_model=List[IntegrationResponse])
async def get_workspace_integrations(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém integrações do workspace"""
    service = WorkspaceService(db)
    integrations = service.get_workspace_integrations(workspace_id, current_user.id)
    if integrations is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return integrations

@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_data: WorkspaceIntegration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza uma integração"""
    service = WorkspaceService(db)
    integration = service.update_integration(integration_id, integration_data, current_user.id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return integration

@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove uma integração"""
    service = WorkspaceService(db)
    success = service.delete_integration(integration_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integração não encontrada")
    return {"message": "Integração removida com sucesso"}


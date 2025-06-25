"""
Endpoints da API para Workspaces
Criado por José - um desenvolvedor Full Stack
API completa para workspaces colaborativos e gerenciamento de projetos
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status, Path
from sqlalchemy.orm import Session

from synapse.database import get_db
from synapse.models.user import User
from synapse.models.workspace_member import WorkspaceRole
from synapse.services.workspace_service import WorkspaceService
from synapse.models.workspace import WorkspaceType
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
            workspace_type_enum = WorkspaceType.INDIVIDUAL
        else:
            workspace_type_enum = WorkspaceType.COLLABORATIVE
            if not rules["can_create_collaborative"]:
                raise HTTPException(
                    status_code=403, 
                    detail="Seu plano não permite criar workspaces colaborativos"
                )
        
        # Ajustar o tipo no objeto recebido
        workspace_data.type = workspace_type_enum  # type: ignore

        try:
            # Usar método de instância em vez de método estático
            workspace_obj = service._create_workspace_complete(
                user_id=current_user.id, 
                workspace_data=workspace_data
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        logger.info(f"Workspace '{workspace_obj.name}' criado com sucesso como {workspace_obj.type.value}")

        return {
            "success": True,
            "workspace": WorkspaceResponse.from_orm(workspace_obj),
            "type": workspace_obj.type.value,
            "message": f"Workspace criado como {workspace_obj.type.value}"
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
):
    """Obtém detalhes de um workspace"""
    try:
        logger.info(f"Obtendo workspace {workspace_id} para usuário {current_user.id}")
        service = WorkspaceService(db)
        
        # Verificar se workspace existe e usuário tem acesso
        workspace = service.get_workspace_by_id(workspace_id)
        if not workspace:
            logger.warning(f"Workspace {workspace_id} não encontrado")
            raise HTTPException(status_code=404, detail="Workspace não encontrado")
        
        # Verificar permissão
        if not service._has_permission(workspace_id, str(current_user.id), "read"):
            logger.warning(f"Usuário {current_user.id} sem permissão para workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Converter workspace para dict e depois para WorkspaceResponse
        try:
            workspace_dict = workspace.to_dict()
            response = WorkspaceResponse(**workspace_dict)
            return response
        except Exception as conversion_error:
            logger.error(f"Erro ao converter workspace para response: {str(conversion_error)}")
            raise HTTPException(status_code=500, detail="Erro na conversão dos dados do workspace")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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
):
    """Deleta um workspace"""
    try:
        logger.info(f"Deletando workspace {workspace_id} por usuário {current_user.id}")
        service = WorkspaceService(db)
        
        # Tentar deletar workspace
        try:
            result = service.delete_workspace(workspace_id, str(current_user.id))
            
            if not result.get("success", False):
                error_msg = result.get("error", "Erro desconhecido")
                if "não encontrado" in error_msg.lower():
                    raise HTTPException(status_code=404, detail=error_msg)
                elif "permissão" in error_msg.lower():
                    raise HTTPException(status_code=403, detail=error_msg)
                else:
                    raise HTTPException(status_code=400, detail=error_msg)
            
            return {"message": "Workspace deletado com sucesso"}
            
        except ValueError as ve:
            logger.warning(f"Erro de validação ao deletar workspace: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except PermissionError as pe:
            logger.warning(f"Erro de permissão ao deletar workspace: {str(pe)}")
            raise HTTPException(status_code=403, detail=str(pe))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{workspace_id}/stats", response_model=WorkspaceStats, summary="Obter estatísticas do workspace", tags=["workspaces"])
async def get_workspace_stats(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém estatísticas do workspace"""
    try:
        logger.info(f"Obtendo estatísticas do workspace {workspace_id}")
        service = WorkspaceService(db)
        
        # Verificar permissão
        if not service._has_permission(workspace_id, str(current_user.id), "read"):
            logger.warning(f"Usuário {current_user.id} sem permissão para workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Obter estatísticas
        try:
            stats = service.get_workspace_stats(workspace_id, str(current_user.id))
            return WorkspaceStats(**stats)
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter estatísticas: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro ao obter estatísticas do workspace")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== MEMBROS ====================


@router.get("/{workspace_id}/members", response_model=List[MemberResponse], summary="Listar membros do workspace", tags=["workspaces"])
async def get_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista membros do workspace"""
    try:
        logger.info(f"Listando membros do workspace {workspace_id}")
        service = WorkspaceService(db)
        
        # Verificar permissão
        if not service._has_permission(workspace_id, str(current_user.id), "read"):
            logger.warning(f"Usuário {current_user.id} sem permissão para workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Obter membros
        try:
            members = service.get_workspace_members(workspace_id)
            return members
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter membros: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro ao obter membros do workspace")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar membros do workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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
    try:
        logger.info(f"Atualizando role do membro {member_id} no workspace {workspace_id}")
        service = WorkspaceService(db)
        
        # Validar dados
        if "role" not in role_data:
            raise HTTPException(status_code=422, detail="Campo 'role' é obrigatório")
        
        try:
            new_role = WorkspaceRole(role_data["role"])
        except ValueError:
            raise HTTPException(status_code=422, detail="Role inválido")
        
        member = service.update_member_role(workspace_id, member_id, new_role, str(current_user.id))
        if not member:
            raise HTTPException(status_code=404, detail="Membro não encontrado")
        
        logger.info(f"Role do membro {member_id} atualizado para {new_role.value}")
        return {"message": "Role atualizado com sucesso"}
    except HTTPException:
        raise
    except PermissionError as e:
        logger.warning(f"Permissão negada ao atualizar role: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar role do membro {member_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ==================== PROJETOS ====================

@router.post("/{workspace_id}/projects", response_model=dict, summary="Criar projeto no workspace", tags=["workspaces"])
async def create_project(
    workspace_id: str,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cria um novo projeto no workspace"""
    try:
        logger.info(f"Criando projeto no workspace {workspace_id} por usuário {current_user.id}")
        service = WorkspaceService(db)
        
        # Verificar se usuário tem permissão
        if not service._has_permission(workspace_id, str(current_user.id), "write"):
            logger.warning(f"Usuário {current_user.id} sem permissão para criar projeto no workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Criar projeto usando workspace_id como string
        try:
            project = service.create_project(workspace_id, project_data, str(current_user.id))
            return {
                "message": "Projeto criado com sucesso",
                "project_id": str(project.id),
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "workspace_id": str(project.workspace_id),
                    "workflow_id": str(project.workflow_id) if project.workflow_id else None,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                }
            }
        except ValueError as ve:
            logger.warning(f"Erro de validação ao criar projeto: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except PermissionError as pe:
            logger.warning(f"Erro de permissão ao criar projeto: {str(pe)}")
            raise HTTPException(status_code=403, detail=str(pe))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao criar projeto no workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{workspace_id}/projects", response_model=List[ProjectResponse], summary="Listar projetos", tags=["workspaces"])
async def get_workspace_projects(
    workspace_id: str,
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
        
        # Verificar se usuário tem acesso (usar workspace_id como string)
        if not service._has_permission(workspace_id, str(current_user.id), "read"):
            logger.warning(f"Usuário {current_user.id} sem permissão para workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Usar workspace_id como string diretamente, não converter para int
        projects = service.get_workspace_projects(workspace_id, str(current_user.id))
        
        # Filtrar por status se especificado
        if status:
            projects = [p for p in projects if getattr(p, 'status', 'active') == status]
        
        # Aplicar paginação
        total = len(projects)
        projects = projects[offset:offset + limit]
        
        logger.info(f"Retornados {len(projects)} projetos de {total} total do workspace {workspace_id}")
        
        # Converter para ProjectResponse
        result = []
        for project in projects:
            try:
                project_response = ProjectResponse(
                    id=str(project.id),
                    name=project.name,
                    description=project.description or "",
                    workspace_id=str(project.workspace_id),
                    workflow_id=str(project.workflow_id),
                    collaborator_count=getattr(project, 'collaborator_count', 0),
                    comment_count=getattr(project, 'comment_count', 0),
                    version_count=0,  # Default value as it's not in the model
                    status=getattr(project, 'status', 'active'),
                    last_edited_at=getattr(project, 'last_edited_at', None),
                    created_at=project.created_at,
                    updated_at=project.updated_at
                )
                result.append(project_response)
            except Exception as conversion_error:
                logger.error(f"Erro ao converter projeto {project.id}: {str(conversion_error)}")
                # Continue processing other projects instead of failing completely
                continue
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar projetos do workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/projects/search", response_model=List[ProjectResponse], summary="Buscar projetos", tags=["workspaces"])
async def search_projects(
    query: Optional[str] = Query(None, min_length=1, max_length=100),
    workspace_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None, pattern="^(active|archived|deleted)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Busca projetos em workspaces que o usuário tem acesso"""
    try:
        logger.info(f"Buscando projetos - query: {query}, workspace_id: {workspace_id}")
        service = WorkspaceService(db)
        
        # Criar objeto de parâmetros de busca
        from types import SimpleNamespace
        search_params = SimpleNamespace(
            query=query,
            workspace_id=workspace_id,
            status=status or "active",
            limit=limit,
            offset=offset,
            sort_by="updated"
        )
        
        # Buscar projetos
        try:
            projects_data = service.search_projects(search_params, str(current_user.id))
            
            # Converter para ProjectResponse
            result = []
            for project_dict in projects_data:
                try:
                    project_response = ProjectResponse(
                        id=str(project_dict["id"]),
                        name=project_dict["name"],
                        description=project_dict.get("description", ""),
                        workspace_id=str(project_dict["workspace_id"]),
                        workflow_id=str(project_dict["workflow_id"]),
                        collaborator_count=project_dict.get("collaborator_count", 0),
                        comment_count=project_dict.get("comment_count", 0),
                        version_count=0,  # Default value
                        status=project_dict.get("status", "active"),
                        last_edited_at=datetime.fromisoformat(project_dict["last_edited_at"]) if project_dict.get("last_edited_at") else None,
                        created_at=datetime.fromisoformat(project_dict["created_at"]),
                        updated_at=datetime.fromisoformat(project_dict["updated_at"])
                    )
                    result.append(project_response)
                except Exception as conversion_error:
                    logger.error(f"Erro ao converter projeto na busca: {str(conversion_error)}")
                    continue
            
            return result
        except Exception as service_error:
            logger.error(f"Erro no serviço de busca de projetos: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro na busca de projetos")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar projetos: {str(e)}")
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

@router.get("/invitations", response_model=List[InvitationResponse], summary="Listar convites do usuário", tags=["workspaces"])
async def get_user_invitations(
    status: Optional[str] = Query(None, pattern="^(pending|accepted|declined|expired)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista convites de workspace do usuário"""
    try:
        logger.info(f"Listando convites para usuário {current_user.id}")
        service = WorkspaceService(db)
        
        # Obter convites
        try:
            invitations_data = service.get_user_invitations(str(current_user.id), status, limit, offset)
            
            # Converter para InvitationResponse
            result = []
            for invitation_dict in invitations_data:
                try:
                    invitation_response = InvitationResponse(
                        id=str(invitation_dict["id"]),
                        workspace_id=str(invitation_dict["workspace_id"]),
                        workspace_name=invitation_dict["workspace_name"],
                        inviter_id=str(invitation_dict["inviter_id"]),
                        inviter_name=invitation_dict["inviter_name"],
                        email=invitation_dict["email"],
                        role=invitation_dict["role"],
                        status=invitation_dict["status"],
                        message=invitation_dict.get("message", ""),
                        expires_at=invitation_dict.get("expires_at"),
                        created_at=invitation_dict["created_at"]
                    )
                    result.append(invitation_response)
                except Exception as conversion_error:
                    logger.error(f"Erro ao converter convite: {str(conversion_error)}")
                    continue
            
            return result
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter convites: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro ao obter convites")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar convites do usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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

@router.get("/{workspace_id}/activities", response_model=List[ActivityResponse], summary="Obter atividades do workspace", tags=["workspaces"])
async def get_workspace_activities(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtém atividades recentes do workspace"""
    try:
        logger.info(f"Obtendo atividades do workspace {workspace_id}")
        service = WorkspaceService(db)
        
        # Verificar permissão
        if not service._has_permission(workspace_id, str(current_user.id), "read"):
            logger.warning(f"Usuário {current_user.id} sem permissão para workspace {workspace_id}")
            raise HTTPException(status_code=403, detail="Acesso negado")
        
        # Obter atividades
        try:
            activities = service.get_workspace_activities(workspace_id, str(current_user.id), limit)
            
            # Converter para ActivityResponse
            result = []
            for activity in activities:
                try:
                    activity_response = ActivityResponse(
                        id=str(activity.get("id", "")),
                        workspace_id=str(activity.get("workspace_id", "")),
                        user_id=str(activity.get("user_id", "")),
                        user_name=activity.get("user_name", ""),
                        action=activity.get("action", ""),
                        resource_type=activity.get("resource_type", ""),
                        resource_id=activity.get("resource_id", ""),
                        description=activity.get("description", ""),
                        created_at=activity.get("created_at")
                    )
                    result.append(activity_response)
                except Exception as conversion_error:
                    logger.error(f"Erro ao converter atividade: {str(conversion_error)}")
                    continue
            
            return result
        except Exception as service_error:
            logger.error(f"Erro no serviço ao obter atividades: {str(service_error)}")
            raise HTTPException(status_code=500, detail="Erro ao obter atividades do workspace")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter atividades do workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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

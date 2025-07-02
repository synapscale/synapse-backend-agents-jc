"""
Schemas para WorkspaceMember
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from synapse.models.workspace_member import WorkspaceRole


class WorkspaceMemberBase(BaseModel):
    """Schema base para workspace member"""

    role: WorkspaceRole = Field(..., description="Role do membro no workspace")
    custom_permissions: Optional[dict] = Field(
        None, description="Permissões customizadas"
    )
    notification_preferences: Optional[dict] = Field(
        None, description="Preferências de notificação"
    )
    is_favorite: bool = Field(False, description="Se é workspace favorito do usuário")


class WorkspaceMemberCreate(BaseModel):
    """Schema para criação de workspace member"""

    user_id: str = Field(..., description="ID do usuário a ser adicionado")
    role: WorkspaceRole = Field(..., description="Role do membro no workspace")
    custom_permissions: Optional[dict] = Field(
        None, description="Permissões customizadas"
    )
    notification_preferences: Optional[dict] = Field(
        None, description="Preferências de notificação"
    )


class WorkspaceMemberUpdate(BaseModel):
    """Schema para atualização de workspace member"""

    role: Optional[WorkspaceRole] = Field(None, description="Novo role do membro")
    custom_permissions: Optional[dict] = Field(
        None, description="Novas permissões customizadas"
    )
    notification_preferences: Optional[dict] = Field(
        None, description="Novas preferências de notificação"
    )
    is_favorite: Optional[bool] = Field(None, description="Se é workspace favorito")


class WorkspaceMemberResponse(WorkspaceMemberBase):
    """Schema de resposta para workspace member"""

    id: int = Field(..., description="ID do membro")
    workspace_id: str = Field(..., description="ID do workspace")
    user_id: str = Field(..., description="ID do usuário")
    status: str = Field(..., description="Status do membro")
    last_seen_at: datetime = Field(..., description="Última vez que foi visto")
    joined_at: datetime = Field(..., description="Data de entrada no workspace")
    left_at: Optional[datetime] = Field(None, description="Data de saída do workspace")

    # Informações do usuário (opcional)
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    user_avatar: Optional[str] = Field(None, description="Avatar do usuário")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "MEMBER",
                "status": "active",
                "is_favorite": False,
                "custom_permissions": {},
                "notification_preferences": {
                    "email_notifications": True,
                    "push_notifications": False,
                },
                "last_seen_at": "2024-12-20T15:00:00Z",
                "joined_at": "2024-12-20T10:00:00Z",
                "left_at": None,
                "user_name": "João Silva",
                "user_email": "joao@exemplo.com",
                "user_avatar": None,
            }
        }


class WorkspaceMemberListResponse(BaseModel):
    """Schema de resposta para listagem de membros"""
    
    model_config = ConfigDict(from_attributes=True)
    
    items: List[WorkspaceMemberResponse] = Field(..., description="Lista de membros")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    pages: int = Field(..., description="Total de páginas")
    size: int = Field(..., description="Tamanho da página")

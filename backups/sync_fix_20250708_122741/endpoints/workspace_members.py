"""
Workspace Members endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.api.deps import get_current_active_user, get_db
from synapse.database import get_async_db

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_workspace_members(
    current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_async_db)
):
    """Listar membros do workspace"""
    from sqlalchemy import select
    from synapse.models import WorkspaceMember
    from synapse.schemas.workspace_member import WorkspaceMemberListResponse, WorkspaceMemberResponse

    try:
        query = select(WorkspaceMember).where(WorkspaceMember.tenant_id == current_user.tenant_id)
        result = await db.execute(query)
        members = result.scalars().all()

        member_responses = [
            WorkspaceMemberResponse(
                id=member.id,
                workspace_id=member.workspace_id,
                user_id=member.user_id,
                role=member.role,
                permissions=member.permissions or {},
                joined_at=member.joined_at,
                invited_by=member.invited_by,
                user_name=member.user.full_name if member.user else None,
                user_email=member.user.email if member.user else None,
            )
            for member in members
        ]

        return WorkspaceMemberListResponse(
            items=member_responses, total=len(member_responses), page=1, pages=1, size=len(member_responses)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado em [NOME_DA_FUNCAO]: {str(e)}", extra={"error_type": type(e).__name__})
        raise

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from synapse.database import get_async_db
from synapse.models.llm import LLM
from synapse.models.user import User
from synapse.api.deps import get_current_user

router = APIRouter()


@router.get("/", summary="Listar catálogo de LLMs")
async def list_llms(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(LLM).where(LLM.is_active == True)
    result = await db.execute(stmt)
    llms = result.scalars().all()
    return [llm.to_dict() for llm in llms]


@router.get("/{llm_id}", summary="Detalhe de LLM")
async def get_llm(
    llm_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(LLM).where(LLM.id == llm_id, LLM.is_active == True)
    result = await db.execute(stmt)
    llm = result.scalar_one_or_none()
    if not llm:
        raise HTTPException(status_code=404, detail="LLM não encontrado")
    return llm.to_dict()

"""Endpoints para gerenciamento de arquivos.

Este módulo implementa os endpoints da API para upload, download,
listagem e gerenciamento de arquivos.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from synapse.constants import FILE_CATEGORIES
from synapse.core.auth.jwt import get_current_user
from synapse.db.base import get_db
from synapse.exceptions import file_validation_exception
from synapse.middlewares.rate_limiting import rate_limit
from synapse.schemas.file import (
    FileDownloadResponse,
    FileListResponse,
    FileResponse,
    FileUploadResponse,
)
from synapse.services.file_service import FileService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    category: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _rate_limit=Depends(rate_limit),
):
    """Upload de arquivo."""
    if category not in FILE_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida"
        )

    file_service = FileService(db)
    return await file_service.upload_file(file, category, current_user.id)


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Listar arquivos do usuário."""
    file_service = FileService(db)
    return await file_service.list_user_files(current_user.id, page, size, category)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obter informações de um arquivo."""
    file_service = FileService(db)
    return await file_service.get_file(file_id, current_user.id)


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Download de arquivo."""
    file_service = FileService(db)
    return await file_service.download_file(file_id, current_user.id)


@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Deletar arquivo."""
    file_service = FileService(db)
    await file_service.delete_file(file_id, current_user.id)
    return {"message": "Arquivo deletado com sucesso"}

"""
Files endpoints - Gerenciamento de arquivos e uploads
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid
import os
import aiofiles
import mimetypes
from pathlib import Path

from synapse.api.deps import get_current_active_user
from synapse.schemas.file import (
    FileResponse,
    FileCreate,
    FileUpdate,
    FileListResponse,
    FileStatus,
    ScanStatus,
)
from synapse.models import File as FileModel, User, Workspace
from synapse.database import get_async_db
from synapse.core.config import settings


router = APIRouter()

# Configurações de upload
UPLOAD_DIRECTORY = Path(settings.UPLOAD_DIR)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".tar",
    ".gz",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".svg",
    ".mp3",
    ".wav",
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".py",
    ".js",
    ".html",
    ".css",
    ".md",
    ".yaml",
    ".yml",
}

# Criar diretório de upload se não existir
UPLOAD_DIRECTORY.mkdir(exist_ok=True)


def validate_file(file: UploadFile) -> None:
    """Validar arquivo antes do upload"""

    # Verificar extensão
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Extensões permitidas: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Verificar tamanho
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // 1024 // 1024}MB",
        )


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    workspace_id: Optional[uuid.UUID] = Query(None, description="ID do workspace"),
    description: Optional[str] = Query(None, description="Descrição do arquivo"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upload de arquivo"""

    # Validar arquivo
    validate_file(file)

    # Verificar workspace se especificado
    if workspace_id:
        workspace_result = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.user_id == current_user.id,
                        Workspace.is_public == True,
                        # TODO: Verificar se é membro
                    ),
                )
            )
        )
        workspace = workspace_result.scalar_one_or_none()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado ou sem acesso",
            )

    # Gerar nome único para o arquivo
    file_id = uuid.uuid4()
    file_ext = Path(file.filename or "").suffix.lower()
    unique_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIRECTORY / unique_filename

    try:
        # Salvar arquivo no disco
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Obter informações do arquivo
        file_size = len(content)
        content_type = (
            mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
        )

        # Criar registro no banco
        file_record = FileModel(
            id=file_id,
            filename=file.filename or unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            content_type=content_type,
            description=description,
            user_id=current_user.id,
            workspace_id=workspace_id,
            tenant_id=current_user.tenant_id,
            status=FileStatus.ACTIVE.value,
            scan_status=ScanStatus.PENDING.value,
        )

        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return FileResponse(
            id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            content_type=file_record.content_type,
            description=file_record.description,
            user_id=file_record.user_id,
            workspace_id=file_record.workspace_id,
            tenant_id=file_record.tenant_id,
            status=file_record.status,
            scan_status=file_record.scan_status,
            download_count=file_record.download_count,
            is_public=file_record.is_public,
            metadata=file_record.metadata or {},
            created_at=file_record.created_at,
            updated_at=file_record.updated_at,
            # URL de download
            download_url=f"/api/v1/files/{file_record.id}/download",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado em upload_file: {str(e)}", extra={"error_type": type(e).__name__})
        # Limpar arquivo se erro
        if file_path.exists():
            file_path.unlink()
        raise


@router.get("/", response_model=FileListResponse)
async def list_files(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    workspace_id: Optional[uuid.UUID] = Query(
        None, description="Filtrar por workspace"
    ),
    search: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    content_type: Optional[str] = Query(
        None, description="Filtrar por tipo de conteúdo"
    ),
    status: Optional[FileStatus] = Query(None, description="Filtrar por status"),
):
    """Listar arquivos do usuário"""

    # Query base
    query = select(FileModel).options(
        selectinload(FileModel.user), selectinload(FileModel.workspace)
    )

    conditions = []

    # Filtrar por arquivos do usuário ou públicos
    conditions.append(
        or_(FileModel.user_id == current_user.id, FileModel.is_public == True)
    )

    # Filtrar por workspace se especificado
    if workspace_id:
        conditions.append(FileModel.workspace_id == workspace_id)

    # Aplicar filtros adicionais
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                FileModel.filename.ilike(search_term),
                FileModel.original_filename.ilike(search_term),
                FileModel.description.ilike(search_term),
            )
        )

    if content_type:
        conditions.append(FileModel.content_type.ilike(f"%{content_type}%"))

    if status:
        conditions.append(FileModel.status == status.value)
    else:
        # Por padrão, só mostrar arquivos ativos
        conditions.append(FileModel.status == FileStatus.ACTIVE.value)

    if conditions:
        query = query.where(and_(*conditions))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(FileModel.created_at.desc())

    # Executar query
    result = await db.execute(query)
    files = result.scalars().all()

    # Calcular páginas
    pages = (total + size - 1) // size

    # Converter para response
    file_responses = [
        FileResponse(
            id=file.id,
            filename=file.filename,
            original_filename=file.original_filename,
            file_size=file.file_size,
            content_type=file.content_type,
            description=file.description,
            user_id=file.user_id,
            workspace_id=file.workspace_id,
            tenant_id=file.tenant_id,
            status=file.status,
            scan_status=file.scan_status,
            download_count=file.download_count,
            is_public=file.is_public,
            metadata=file.metadata or {},
            created_at=file.created_at,
            updated_at=file.updated_at,
            download_url=f"/api/v1/files/{file.id}/download",
            # Dados relacionados
            user_name=file.user.full_name if file.user else None,
            workspace_name=file.workspace.name if file.workspace else None,
        )
        for file in files
    ]

    return FileListResponse(
        items=file_responses, total=total, page=page, pages=pages, size=size
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Obter informações do arquivo"""

    result = await db.execute(
        select(FileModel)
        .options(selectinload(FileModel.user), selectinload(FileModel.workspace))
        .where(FileModel.id == file_id)
    )
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
        )

    # Verificar acesso
    has_access = False
    if file.user_id == current_user.id:
        has_access = True
    elif file.is_public:
        has_access = True
    elif file.workspace and file.workspace.is_public:
        has_access = True
    # TODO: Verificar se é membro do workspace

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar este arquivo",
        )

    return FileResponse(
        id=file.id,
        filename=file.filename,
        original_filename=file.original_filename,
        file_size=file.file_size,
        content_type=file.content_type,
        description=file.description,
        user_id=file.user_id,
        workspace_id=file.workspace_id,
        tenant_id=file.tenant_id,
        status=file.status,
        scan_status=file.scan_status,
        download_count=file.download_count,
        is_public=file.is_public,
        metadata=file.metadata or {},
        created_at=file.created_at,
        updated_at=file.updated_at,
        download_url=f"/api/v1/files/{file.id}/download",
        user_name=file.user.full_name if file.user else None,
        workspace_name=file.workspace.name if file.workspace else None,
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download do arquivo"""

    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
        )

    # Verificar acesso (mesmo código do get_file)
    has_access = False
    if file.user_id == current_user.id:
        has_access = True
    elif file.is_public:
        has_access = True
    elif file.workspace and file.workspace.is_public:
        has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a baixar este arquivo",
        )

    # Verificar se arquivo existe no disco
    file_path = Path(file.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo físico não encontrado",
        )

    # Incrementar contador de downloads
    file.download_count += 1
    await db.commit()

    # Retornar arquivo
    async def file_generator():
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                yield chunk

    return StreamingResponse(
        file_generator(),
        media_type=file.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={file.original_filename}",
            "Content-Length": str(file.file_size),
        },
    )


@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: uuid.UUID,
    file_update: FileUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Atualizar metadados do arquivo"""

    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
        )

    # Apenas o proprietário pode atualizar
    if file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode atualizar o arquivo",
        )

    # Atualizar campos
    update_data = file_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file, field, value)

    await db.commit()
    await db.refresh(file)

    return FileResponse(
        id=file.id,
        filename=file.filename,
        original_filename=file.original_filename,
        file_size=file.file_size,
        content_type=file.content_type,
        description=file.description,
        user_id=file.user_id,
        workspace_id=file.workspace_id,
        tenant_id=file.tenant_id,
        status=file.status,
        scan_status=file.scan_status,
        download_count=file.download_count,
        is_public=file.is_public,
        metadata=file.metadata or {},
        created_at=file.created_at,
        updated_at=file.updated_at,
        download_url=f"/api/v1/files/{file.id}/download",
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deletar arquivo"""

    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
        )

    # Apenas o proprietário pode deletar
    if file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o proprietário pode deletar o arquivo",
        )

    # Soft delete
    file.status = FileStatus.DELETED.value

    await db.commit()

    return {"message": "Arquivo deletado com sucesso"}

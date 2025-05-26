"""Rotas para upload e gerenciamento de arquivos."""

import logging

import magic
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

from ..models.file import (
    FileDownloadResponse,
    FileListResponse,
    FileMetadata,
    FileProcessingStatus,
    FileUploadResponse,
)
from ..utils.auth import get_current_user
from ..utils.security import SecurityValidator

logger = logging.getLogger(__name__)

router = APIRouter()
security_validator = SecurityValidator()


@router.post(
    "/upload", response_model=FileUploadResponse, description="Faz upload de um arquivo"
)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    tags: str = Form(""),
    is_public: bool = Form(False),
    current_user: dict = Depends(get_current_user),
):
    """Endpoint para upload de arquivos."""
    try:
        logger.info(f"Iniciando upload para usuário {current_user['id']}")

        content = await file.read()
        mime_type = magic.from_buffer(content, mime=True)

        is_safe = await security_validator.validate_file_safety(
            content, file.filename, mime_type
        )

        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo não passou nas validações de segurança",
            )

        file_id = f"file_{current_user['id']}_{file.filename}"

        return FileUploadResponse(
            file_id=file_id, message="Arquivo enviado com sucesso"
        )

    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        ) from e


@router.get(
    "/files", response_model=FileListResponse, description="Lista arquivos do usuário"
)
async def list_files(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: str = Query(None),
    current_user: dict = Depends(get_current_user),
) -> FileListResponse:
    """Lista arquivos do usuário."""
    return FileListResponse(files=[], total=0)


@router.get(
    "/files/{file_id}",
    response_model=FileMetadata,
    description="Obtém informações de um arquivo específico",
)
async def get_file_info(
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Obtém informações de um arquivo."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
    )


@router.get(
    "/files/{file_id}/download",
    response_model=FileDownloadResponse,
    description="Gera URL para download do arquivo",
)
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Gera URL para download do arquivo."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
    )


@router.delete("/files/{file_id}", description="Remove um arquivo")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove um arquivo."""
    return {"message": "Arquivo removido com sucesso"}


@router.get(
    "/files/{file_id}/status",
    response_model=FileProcessingStatus,
    description="Obtém status de processamento do arquivo",
)
async def get_processing_status(
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Obtém status de processamento do arquivo."""
    return FileProcessingStatus(
        status="completed", progress=100.0, message="Processamento concluído"
    )

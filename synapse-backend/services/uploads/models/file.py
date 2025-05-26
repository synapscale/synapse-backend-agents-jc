"""Modelos de dados para arquivos."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Metadados de arquivo."""

    id: str = Field(..., description="ID único do arquivo")
    original_name: str = Field(..., description="Nome original do arquivo")
    stored_name: str = Field(..., description="Nome do arquivo no armazenamento")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    mime_type: str = Field(..., description="Tipo MIME do arquivo")
    category: str = Field(..., description="Categoria do arquivo")
    upload_date: datetime = Field(..., description="Data de upload")
    user_id: str = Field(..., description="ID do usuário que fez upload")
    checksum: str = Field(..., description="Checksum MD5 do arquivo")
    tags: List[str] = Field(default=[], description="Tags do arquivo")
    is_public: bool = Field(default=False, description="Arquivo público")
    expiry_date: Optional[datetime] = Field(None, description="Data de expiração")


class FileProcessingStatus(BaseModel):
    """Status de processamento de arquivo."""

    status: str = Field(..., description="Status atual")
    progress: float = Field(..., description="Progresso (0-100)")
    message: str = Field(..., description="Mensagem de status")


class FileUploadResponse(BaseModel):
    """Resposta de upload de arquivo."""

    file_id: str = Field(..., description="ID do arquivo")
    message: str = Field(..., description="Mensagem de sucesso")


class FileListResponse(BaseModel):
    """Resposta de listagem de arquivos."""

    files: List[FileMetadata] = Field(..., description="Lista de arquivos")
    total: int = Field(..., description="Total de arquivos")


class FileDownloadResponse(BaseModel):
    """Resposta de download de arquivo."""

    file_url: str = Field(..., description="URL para download")
    expires_at: datetime = Field(..., description="Data de expiração da URL")

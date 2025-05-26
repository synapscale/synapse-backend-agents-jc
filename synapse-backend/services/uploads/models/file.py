from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class FileMetadata(BaseModel):
    id: str = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome original do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    path: str = Field(..., description="Caminho relativo do arquivo no storage")
    category: str = Field(..., description="Categoria do arquivo (image, document, etc.)")
    user_id: str = Field(..., description="ID do usuário que fez o upload")
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")

class UploadResponse(BaseModel):
    file_id: str = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome original do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    url: str = Field(..., description="URL para acessar o arquivo")
    category: str = Field(..., description="Categoria do arquivo")
    created_at: datetime = Field(..., description="Data de criação")

class ShareRequest(BaseModel):
    user_ids: List[str] = Field(..., description="Lista de IDs de usuários com quem compartilhar")

class ShareResponse(BaseModel):
    message: str = Field(..., description="Mensagem de sucesso")
    shared_with: List[str] = Field(..., description="Lista de IDs de usuários com quem o arquivo está compartilhado")

class FileUploadMetadata(BaseModel):
    description: Optional[str] = Field(None, description="Descrição do arquivo")
    tags: Optional[List[str]] = Field(None, description="Tags associadas ao arquivo")
    is_public: Optional[bool] = Field(False, description="Se o arquivo é público ou não")
    expiration: Optional[datetime] = Field(None, description="Data de expiração do arquivo")

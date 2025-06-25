from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class MemoryBase(BaseModel):
    content: str = Field(..., min_length=1, description="Conteúdo da memória")
    content_type: str = Field("text", description="Tipo de conteúdo (text, image, code, etc)")
    title: Optional[str] = Field(None, max_length=255, description="Título opcional da memória")
    description: Optional[str] = Field(None, description="Descrição opcional da memória")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags para categorização")
    importance_score: Optional[int] = Field(1, ge=1, le=10, description="Importância (1-10)")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração (opcional)")

class MemoryCreate(MemoryBase):
    collection_id: str = Field(..., description="ID da coleção onde a memória será armazenada")

class MemoryUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    importance_score: Optional[int] = Field(None, ge=1, le=10)
    expires_at: Optional[datetime] = None

class MemoryResponse(MemoryBase):
    id: str
    collection_id: str
    user_id: str
    access_count: int
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class MemorySearch(BaseModel):
    query: str = Field(..., min_length=1, description="Texto para busca semântica")
    collection_id: Optional[str] = Field(None, description="Filtrar por coleção específica")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de resultados")
    min_score: float = Field(0.7, ge=0, le=1, description="Pontuação mínima de similaridade (0-1)")
    tags: Optional[List[str]] = Field(None, description="Filtrar por tags")

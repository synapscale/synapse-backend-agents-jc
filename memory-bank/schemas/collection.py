from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome da coleção")
    description: Optional[str] = Field(None, description="Descrição da coleção")
    is_private: bool = Field(True, description="Se a coleção é privada ou compartilhada")
    max_memories: Optional[int] = Field(1000, ge=1, description="Número máximo de memórias")
    retention_days: Optional[int] = Field(90, ge=0, description="Dias de retenção (0=sem expiração)")

class CollectionCreate(CollectionBase):
    workspace_id: Optional[str] = Field(None, description="ID do workspace (opcional)")

class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_private: Optional[bool] = None
    max_memories: Optional[int] = Field(None, ge=1)
    retention_days: Optional[int] = Field(None, ge=0)

class CollectionResponse(CollectionBase):
    id: str
    user_id: str
    workspace_id: Optional[str] = None
    memory_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class CollectionStats(BaseModel):
    total_collections: int
    total_memories: int
    total_tokens: int
    avg_memories_per_collection: float
    most_used_collection: Optional[str] = None

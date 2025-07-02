"""
Tag schemas para API endpoints
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class TagCreateSchema(BaseModel):
    """Schema para criação de tags"""
    target_type: str = Field(..., description="Tipo do alvo (conversation, message, user, workspace)")
    target_id: UUID = Field(..., description="ID do alvo")
    tag_name: str = Field(..., min_length=1, max_length=100, description="Nome da tag")
    tag_value: Optional[str] = Field(None, description="Valor da tag (opcional)")
    tag_category: Optional[str] = Field(None, max_length=50, description="Categoria da tag")
    tag_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional")
    
    class Config:
        json_encoders = {UUID: str}


class TagResponseSchema(BaseModel):
    """Schema para resposta de tags"""
    id: UUID
    target_type: str
    target_id: UUID
    tag_name: str
    tag_value: Optional[str]
    tag_category: Optional[str]
    is_system_tag: bool
    is_user_tag: bool
    created_by_user_id: Optional[UUID]
    auto_generated: bool
    confidence_score: Optional[float]
    is_high_confidence: bool
    display_name: str
    tag_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {UUID: str}


class TagUpdateSchema(BaseModel):
    """Schema para atualização de tags"""
    tag_name: Optional[str] = Field(None, min_length=1, max_length=100)
    tag_value: Optional[str] = Field(None)
    tag_category: Optional[str] = Field(None, max_length=50)
    tag_metadata: Optional[Dict[str, Any]] = Field(None)
    
    class Config:
        json_encoders = {UUID: str}


class TagListSchema(BaseModel):
    """Schema para listagem de tags"""
    target_type: Optional[str] = Field(None, description="Filtrar por tipo de alvo")
    target_id: Optional[UUID] = Field(None, description="Filtrar por ID do alvo")
    tag_category: Optional[str] = Field(None, description="Filtrar por categoria")
    is_system_tag: Optional[bool] = Field(None, description="Filtrar por tags do sistema")
    
    class Config:
        json_encoders = {UUID: str}

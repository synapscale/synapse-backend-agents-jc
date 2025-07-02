"""Modelo de arquivo para o banco de dados.

Este módulo contém o modelo de dados para arquivos armazenados no sistema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

# Importar Base do arquivo database.py
from synapse.database import Base


class File(Base):
    """Modelo de dados para arquivos armazenados no sistema."""

    __tablename__ = "files"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos EXATOS da estrutura do banco de dados
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    tags = Column(JSONB, nullable=True)
    description = Column(Text, nullable=True)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True
    )
    status = Column(String(20), default="active")
    scan_status = Column(String(20), default="pending")
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True))

    # Relacionamentos
    user = relationship("User", back_populates="files")
    tenant = relationship("Tenant", back_populates="files")

    def __repr__(self):
        return (
            f"<File(id={self.id}, filename='{self.filename}', size={self.file_size})>"
        )

    def is_image(self) -> bool:
        """Verifica se o arquivo é uma imagem"""
        return self.category == "image" or self.mime_type.startswith("image/")

    def is_document(self) -> bool:
        """Verifica se o arquivo é um documento"""
        return self.category == "document"

    def generate_download_url(self) -> str:
        """Gera URL de download para o arquivo"""
        return f"/api/v1/files/{self.id}/download"

    def to_dict(self) -> dict:
        """Converte o arquivo para dicionário"""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "original_name": self.original_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "category": self.category,
            "is_public": self.is_public,
            "user_id": str(self.user_id) if self.user_id else None,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "status": self.status,
            "scan_status": self.scan_status,
            "access_count": self.access_count,
            "tags": self.tags,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed_at": (
                self.last_accessed_at.isoformat() if self.last_accessed_at else None
            ),
        }

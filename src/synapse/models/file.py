"""Modelo de arquivo para o banco de dados.

Este módulo contém o modelo de dados para arquivos armazenados no sistema.
"""

import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# CORREÇÃO: Importar Base do arquivo correto ao invés de criar um novo
from synapse.db.base import Base


class File(Base):
    """Modelo de dados para arquivos armazenados no sistema."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)
    
    # MUDANÇA: ARRAY → JSON para compatibilidade SQLite
    tags = Column(JSON, nullable=True, default=list)
    
    description = Column(Text, nullable=True)
    
    # MUDANÇA: Boolean → String para compatibilidade SQLite
    is_public = Column(String(10), default="false", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Índices para performance
    __table_args__ = (
        Index('idx_file_filename', 'filename'),
        Index('idx_file_created_at', 'created_at'),
        Index('idx_file_file_hash', 'file_hash'),
    )
    
    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', size={self.file_size})>"

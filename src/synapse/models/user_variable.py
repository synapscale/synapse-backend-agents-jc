"""
Modelo UserVariable para sistema de variáveis personalizado
Criado por José - um desenvolvedor Full Stack
Permite que usuários configurem suas próprias variáveis como .env personalizado
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import os
import uuid
import logging
from typing import ClassVar, Optional
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)

class UserVariable(Base):
    """
    Modelo para variáveis personalizadas do usuário
    Funciona como um .env personalizado para cada usuário
    """

    __tablename__ = "user_variables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_encrypted = Column(Boolean, nullable=False, server_default=text("false"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    # Relacionamento com usuário
    user = relationship("User", back_populates="variables")

    def __repr__(self):
        return f"<UserVariable(user_id={self.user_id}, key='{self.key}')>"

    @staticmethod
    def get_encryption_key() -> str:
        """Função mantida apenas para compatibilidade com código existente."""
        return "dummy_key"

    @classmethod
    def encrypt_value(cls, value: str) -> str:
        """
        Não realiza criptografia - retorna o valor original
        """
        return value or ""

    @classmethod
    def decrypt_value(cls, encrypted_value: str) -> str:
        """
        Não realiza descriptografia - retorna o valor original
        """
        return encrypted_value or ""

    def get_decrypted_value(self) -> str:
        """
        Retorna o valor da variável (sem criptografia)
        """
        return self.value

    def validate_encryption_integrity(self) -> bool:
        """
        Validação de integridade (sempre retorna True)
        """
        return True

    def migrate_to_current_encryption(self) -> bool:
        """
        Função mantida para compatibilidade
        """
        return True

    def set_encrypted_value(self, value: str):
        """
        Define o valor da variável (sem criptografia)
        """
        self.value = value

    @classmethod
    def create_variable(
        cls,
        user_id,  # UUID ou string que será convertida para UUID
        key: str,
        value: str,
        description: str = None,
        category: str = None,
        is_encrypted: bool = False,
    ):
        """
        Cria uma nova variável do usuário
        """
        variable = cls(
            user_id=user_id,
            key=key.upper(),  # Padronizar chaves em maiúsculo
            description=description,
            category=category,
            is_encrypted=False,  # Sempre False agora
        )
        variable.value = value
        return variable

    def to_dict(self, include_value: bool = False) -> dict:
        """
        Converte a variável para dicionário
        """
        data = {
            "id": str(self.id) if self.id else None,
            "key": self.key,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "is_encrypted": self.is_encrypted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_value:
            data["value"] = self.value

        return data

    def to_env_format(self) -> str:
        """
        Retorna a variável no formato .env
        """
        value = self.value
        # Escapar valores que contêm espaços ou caracteres especiais
        if " " in value or any(char in value for char in ["$", '"', "'", "\\", "\n"]):
            value = f'"{value}"'
        return f"{self.key}={value}"

    @classmethod
    def check_and_migrate_user_variables(cls, user_id, db_session) -> dict:
        """
        Função mantida para compatibilidade com código existente
        """
        stats = {
            "total": 0,
            "valid": 0,
            "migrated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            variables = db_session.query(cls).filter(
                cls.user_id == user_id,
                cls.is_encrypted == True
            ).all()
            
            stats["total"] = len(variables)
            stats["valid"] = len(variables)
            
        except Exception as e:
            logger.error(f"Erro ao verificar variáveis: {e}")
            stats["errors"].append(f"Erro geral: {e}")
            
        return stats

    @classmethod
    def get_user_env_dict(cls, user_id: int, db_session) -> dict:
        """
        Retorna todas as variáveis ativas do usuário como dicionário
        Usado para injetar variáveis em execuções de workflows
        """
        variables = (
            db_session.query(cls)
            .filter(
                cls.user_id == user_id,
                cls.is_active == True,
            )
            .all()
        )

        env_dict = {}
        for var in variables:
            env_dict[var.key] = var.value

        return env_dict

    @classmethod
    def get_user_env_string(cls, user_id: int, db_session) -> str:
        """
        Retorna todas as variáveis ativas do usuário como string .env
        """
        variables = (
            db_session.query(cls)
            .filter(
                cls.user_id == user_id,
                cls.is_active == True,
            )
            .all()
        )

        env_lines = []
        for var in variables:
            env_lines.append(var.to_env_format())

        return "\n".join(env_lines)

    def validate_key(self) -> bool:
        """
        Valida se a chave da variável está no formato correto
        """
        import re

        # Chaves devem seguir o padrão de variáveis de ambiente
        pattern = r"^[A-Z][A-Z0-9_]*$"
        return bool(re.match(pattern, self.key))

    def is_sensitive(self) -> bool:
        """
        Verifica se a variável contém dados sensíveis baseado na chave
        """
        sensitive_keywords = [
            "KEY",
            "SECRET",
            "TOKEN",
            "PASSWORD",
            "PASS",
            "AUTH",
            "CREDENTIAL",
            "PRIVATE",
            "API_KEY",
            "ACCESS_TOKEN",
        ]
        return any(keyword in self.key.upper() for keyword in sensitive_keywords)

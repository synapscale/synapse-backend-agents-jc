"""
Modelo UserVariable para sistema de variáveis personalizado
Criado por José - O melhor Full Stack do mundo
Permite que usuários configurem suas próprias variáveis como .env personalizado
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from cryptography.fernet import Fernet
import os
import base64

class UserVariable(Base):
    """
    Modelo para variáveis personalizadas do usuário
    Funciona como um .env personalizado para cada usuário
    """
    __tablename__ = "user_variables"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)  # Valor criptografado
    description = Column(Text, nullable=True)  # Descrição opcional da variável
    is_encrypted = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    category = Column(String(100), nullable=True)  # Ex: "API_KEYS", "CREDENTIALS", "CONFIG"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com usuário
    user = relationship("User", back_populates="variables")

    def __repr__(self):
        return f"<UserVariable(user_id={self.user_id}, key='{self.key}', category='{self.category}')>"

    @staticmethod
    def get_encryption_key():
        """
        Obtém a chave de criptografia das variáveis de ambiente
        """
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            # Gerar uma chave padrão para desenvolvimento (NUNCA usar em produção)
            encryption_key = base64.urlsafe_b64encode(b"synapse-dev-encryption-key-32b").decode()
        return encryption_key

    @classmethod
    def encrypt_value(cls, value: str) -> str:
        """
        Criptografa um valor usando Fernet
        """
        if not value:
            return ""
        
        key = cls.get_encryption_key()
        fernet = Fernet(key.encode() if isinstance(key, str) else key)
        encrypted_value = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted_value).decode()

    @classmethod
    def decrypt_value(cls, encrypted_value: str) -> str:
        """
        Descriptografa um valor usando Fernet
        """
        if not encrypted_value:
            return ""
        
        try:
            key = cls.get_encryption_key()
            fernet = Fernet(key.encode() if isinstance(key, str) else key)
            decoded_value = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_value = fernet.decrypt(decoded_value)
            return decrypted_value.decode()
        except Exception as e:
            # Log do erro em produção
            print(f"Erro ao descriptografar variável: {e}")
            return ""

    def get_decrypted_value(self) -> str:
        """
        Retorna o valor descriptografado da variável
        """
        if self.is_encrypted:
            return self.decrypt_value(self.value)
        return self.value

    def set_encrypted_value(self, value: str):
        """
        Define o valor criptografado da variável
        """
        if self.is_encrypted:
            self.value = self.encrypt_value(value)
        else:
            self.value = value

    @classmethod
    def create_variable(cls, user_id: int, key: str, value: str, 
                       description: str = None, category: str = None, 
                       is_encrypted: bool = True):
        """
        Cria uma nova variável do usuário
        """
        variable = cls(
            user_id=user_id,
            key=key.upper(),  # Padronizar chaves em maiúsculo
            description=description,
            category=category,
            is_encrypted=is_encrypted
        )
        variable.set_encrypted_value(value)
        return variable

    def to_dict(self, include_value: bool = False) -> dict:
        """
        Converte a variável para dicionário
        """
        data = {
            "id": self.id,
            "key": self.key,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_value:
            data["value"] = self.get_decrypted_value()
        
        return data

    def to_env_format(self) -> str:
        """
        Retorna a variável no formato .env
        """
        value = self.get_decrypted_value()
        # Escapar valores que contêm espaços ou caracteres especiais
        if " " in value or any(char in value for char in ['$', '"', "'", '\\', '\n']):
            value = f'"{value}"'
        return f"{self.key}={value}"

    @classmethod
    def get_user_env_dict(cls, user_id: int, db_session) -> dict:
        """
        Retorna todas as variáveis ativas do usuário como dicionário
        Usado para injetar variáveis em execuções de workflows
        """
        variables = db_session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).all()
        
        env_dict = {}
        for var in variables:
            env_dict[var.key] = var.get_decrypted_value()
        
        return env_dict

    @classmethod
    def get_user_env_string(cls, user_id: int, db_session) -> str:
        """
        Retorna todas as variáveis ativas do usuário como string .env
        """
        variables = db_session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).all()
        
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
        pattern = r'^[A-Z][A-Z0-9_]*$'
        return bool(re.match(pattern, self.key))

    def is_sensitive(self) -> bool:
        """
        Verifica se a variável contém dados sensíveis baseado na chave
        """
        sensitive_keywords = [
            'KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PASS', 'AUTH',
            'CREDENTIAL', 'PRIVATE', 'API_KEY', 'ACCESS_TOKEN'
        ]
        return any(keyword in self.key.upper() for keyword in sensitive_keywords)


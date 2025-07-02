"""
Model para tokens de verificação de email
ALINHADO PERFEITAMENTE COM A TABELA email_verification_tokens
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from synapse.database import Base


class EmailVerificationToken(Base):
    """Model para tokens de verificação de email - ALINHADO COM email_verification_tokens TABLE"""

    __tablename__ = "email_verification_tokens"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Campos exatos da tabela
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), nullable=False, index=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False
    )
    email = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )

    # Relacionamentos
    user = relationship("User", back_populates="email_verification_tokens")

    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, email={self.email}, expires_at={self.expires_at})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "email": self.email,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_used": self.is_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # Token não é incluído por questões de segurança
        }

    def is_expired(self):
        """Verifica se o token está expirado"""
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self):
        """Verifica se o token é válido (não usado e não expirado)"""
        return not self.is_used and not self.is_expired()

    def time_until_expiry(self):
        """Retorna o tempo até a expiração"""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - datetime.now(timezone.utc)

    def minutes_until_expiry(self) -> int:
        """Retorna quantos minutos até a expiração"""
        delta = self.time_until_expiry()
        return max(0, int(delta.total_seconds() / 60))

    def use_token(self):
        """Marca o token como usado"""
        self.is_used = True
        self.updated_at = datetime.now(timezone.utc)

    def extend_expiry(self, minutes: int = 1440):  # 24 horas por padrão
        """Estende a validade do token"""
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self.updated_at = datetime.now(timezone.utc)

    def verify_token(self, provided_token: str) -> bool:
        """Verifica se o token fornecido corresponde ao armazenado"""
        if not provided_token or not self.token:
            return False

        # Comparação segura contra timing attacks
        return secrets.compare_digest(self.token, provided_token)

    @classmethod
    def generate_secure_token(cls, length: int = 32) -> str:
        """Gera um token seguro"""
        # Gera bytes aleatórios criptograficamente seguros
        random_bytes = secrets.token_bytes(length)

        # Converte para string hexadecimal
        token = random_bytes.hex()

        # Adiciona timestamp para uniqueness
        timestamp = str(int(datetime.now().timestamp()))

        # Hash final para ofuscar o timestamp
        final_token = hashlib.sha256(f"{token}{timestamp}".encode()).hexdigest()

        return final_token

    @classmethod
    def create_for_user(
        cls,
        user_id: str,
        email: str,
        expires_in_minutes: int = 1440,  # 24 horas por padrão
        token: str = None,
    ):
        """Cria um novo token de verificação para um usuário"""
        if not token:
            token = cls.generate_secure_token()

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        return cls(
            user_id=user_id,
            email=email,
            token=token,
            expires_at=expires_at,
            is_used=False,
        )

    @classmethod
    def find_valid_token(cls, session, token: str):
        """Busca um token válido"""
        verification_token = (
            session.query(cls)
            .filter(
                cls.token == token,
                cls.is_used.isnot(True),  # Não usado
                cls.expires_at > datetime.now(timezone.utc),  # Não expirado
            )
            .first()
        )

        return verification_token

    @classmethod
    def find_by_user(cls, session, user_id: str, valid_only: bool = True):
        """Busca tokens por usuário"""
        query = session.query(cls).filter(cls.user_id == user_id)

        if valid_only:
            query = query.filter(
                cls.is_used.isnot(True), cls.expires_at > datetime.now(timezone.utc)
            )

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def find_by_email(cls, session, email: str, valid_only: bool = True):
        """Busca tokens por email"""
        query = session.query(cls).filter(cls.email == email)

        if valid_only:
            query = query.filter(
                cls.is_used.isnot(True), cls.expires_at > datetime.now(timezone.utc)
            )

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def invalidate_user_tokens(cls, session, user_id: str):
        """Invalida todos os tokens de um usuário"""
        session.query(cls).filter(
            cls.user_id == user_id, cls.is_used.isnot(True)
        ).update({"is_used": True, "updated_at": datetime.now(timezone.utc)})

    @classmethod
    def invalidate_email_tokens(cls, session, email: str):
        """Invalida todos os tokens de um email"""
        session.query(cls).filter(cls.email == email, cls.is_used.isnot(True)).update(
            {"is_used": True, "updated_at": datetime.now(timezone.utc)}
        )

    @classmethod
    def cleanup_expired_tokens(cls, session):
        """Remove tokens expirados do banco"""
        expired_count = (
            session.query(cls)
            .filter(cls.expires_at <= datetime.now(timezone.utc))
            .delete()
        )

        return expired_count

    @classmethod
    def get_expired_tokens(cls, session):
        """Retorna todos os tokens expirados"""
        return (
            session.query(cls)
            .filter(cls.expires_at <= datetime.now(timezone.utc))
            .all()
        )

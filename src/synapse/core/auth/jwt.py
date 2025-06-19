"""
Sistema JWT completo para autenticação e autorização
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from synapse.core.config_new import settings
from synapse.database import get_db
from synapse.models.user import User, RefreshToken
import secrets
import uuid

# HTTPBearer foi movido para deps.py


class JWTManager:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Cria um token de acesso JWT"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "access",
            }
        )
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, db: Session) -> str:
        """Cria um token de refresh e salva no banco"""
        token = secrets.token_urlsafe(32)
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )

        # Criar registro no banco
        refresh_token = RefreshToken(
            token=token,
            user_id=uuid.UUID(user_id),
            expires_at=expire,
        )
        db.add(refresh_token)
        db.commit()

        return token

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verifica e decodifica um token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

    def refresh_access_token(self, refresh_token: str, db: Session) -> str | None:
        """Gera um novo token de acesso usando refresh token"""
        # Buscar refresh token no banco
        token_record = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False,
            )
            .first()
        )

        if not token_record or not token_record.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
            )

        # Buscar usuário
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo",
            )

        # Criar novo access token
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": str(user.id)}
        )
        return access_token

    def revoke_refresh_token(self, refresh_token: str, db: Session):
        """Revoga um refresh token"""
        token_record = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == refresh_token,
            )
            .first()
        )

        if token_record:
            token_record.is_revoked = True
            db.commit()

    def revoke_all_user_tokens(self, user_id: str, db: Session):
        """Revoga todos os refresh tokens de um usuário"""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == uuid.UUID(user_id),
        ).update({"is_revoked": True})
        db.commit()


# Instância global do gerenciador JWT
jwt_manager = JWTManager()


# NOTA: As funções get_current_user, get_current_active_user, get_current_verified_user
# foram movidas para src/synapse/api/deps.py para evitar dependências circulares
# e manter uma arquitetura mais limpa. Use as importações de deps.py nos endpoints.


# Funções utilitárias
def create_access_token(data: dict[str, Any]) -> str:
    """Função utilitária para criar token de acesso"""
    return jwt_manager.create_access_token(data)


def create_refresh_token(user_id: str, db: Session) -> str:
    """Função utilitária para criar refresh token"""
    return jwt_manager.create_refresh_token(user_id, db)


def verify_token(token: str) -> dict[str, Any]:
    """Função utilitária para verificar token"""
    return jwt_manager.verify_token(token)


def decode_token(token: str) -> dict[str, Any]:
    """Decodifica um token JWT e retorna o payload"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

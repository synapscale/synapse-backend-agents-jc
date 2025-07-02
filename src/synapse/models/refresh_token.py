"""Refresh Token Model"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone

from synapse.database import Base


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    token = Column(String(500), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, nullable=True, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __str__(self):
        return f"RefreshToken(user_id={self.user_id}, expires_at={self.expires_at})"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return self.expires_at < datetime.now(timezone.utc)

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)"""
        return not self.is_revoked and not self.is_expired

    def revoke(self):
        """Revoke the refresh token"""
        self.is_revoked = True
        self.updated_at = func.current_timestamp()

    @classmethod
    def get_valid_token(cls, session, token_string):
        """Get valid refresh token by token string"""
        token = session.query(cls).filter(
            cls.token == token_string,
            cls.is_revoked.is_(False),
            cls.expires_at > func.now()
        ).first()
        return token

    @classmethod
    def revoke_all_for_user(cls, session, user_id):
        """Revoke all refresh tokens for a user"""
        session.query(cls).filter(cls.user_id == user_id).update({
            "is_revoked": True,
            "updated_at": func.current_timestamp()
        })

    @classmethod
    def cleanup_expired(cls, session):
        """Remove expired tokens from database"""
        session.query(cls).filter(cls.expires_at < func.now()).delete()

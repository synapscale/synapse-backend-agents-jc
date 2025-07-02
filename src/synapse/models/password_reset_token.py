"""Password Reset Token Model"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class PasswordResetToken(Base):
    """Password reset tokens for user authentication"""
    
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    token = Column(String(500), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, nullable=True, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    def __str__(self):
        return f"PasswordResetToken(user_id={self.user_id}, expires_at={self.expires_at})"

    @property
    def is_expired(self):
        """Check if token is expired"""
        return self.expires_at < func.now()

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.updated_at = func.current_timestamp()

    @classmethod
    def get_valid_token(cls, session, token_string):
        """Get valid password reset token by token string"""
        token = session.query(cls).filter(
            cls.token == token_string,
            cls.is_used.is_(False),
            cls.expires_at > func.now()
        ).first()
        return token

    @classmethod
    def invalidate_all_for_user(cls, session, user_id):
        """Invalidate all password reset tokens for a user"""
        session.query(cls).filter(cls.user_id == user_id).update({
            "is_used": True,
            "updated_at": func.current_timestamp()
        })

    @classmethod
    def cleanup_expired(cls, session):
        """Remove expired tokens from database"""
        session.query(cls).filter(cls.expires_at < func.now()).delete()

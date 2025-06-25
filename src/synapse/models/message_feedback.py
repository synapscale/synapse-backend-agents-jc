"""
Modelo MessageFeedback para feedback de mensagens
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class MessageFeedback(Base):
    __tablename__ = "llms_message_feedbacks"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.llms_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Tipo e valor do rating
    rating_type = Column(String(20), nullable=False, index=True)  # thumbs_up, thumbs_down, star_rating
    rating_value = Column(Integer, nullable=True)  # 1-5 para stars, 1/-1 para thumbs

    # Feedback textual
    feedback_text = Column(Text, nullable=True)
    feedback_category = Column(String(50), nullable=True, index=True)  # helpful, accurate, creative, etc
    improvement_suggestions = Column(Text, nullable=True)

    # Configurações
    is_public = Column(Boolean, server_default=text('false'))
    feedback_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relacionamentos
    message = relationship("Message", back_populates="message_feedbacks")
    user = relationship("User", back_populates="message_feedbacks")

    def __repr__(self):
        return f"<MessageFeedback(message_id={self.message_id}, rating_type={self.rating_type}, rating_value={self.rating_value})>"

    @property
    def is_positive(self):
        """Verifica se o feedback é positivo"""
        if self.rating_type == "thumbs_up":
            return self.rating_value == 1
        elif self.rating_type == "star_rating":
            return self.rating_value >= 4
        return False

    @property
    def is_negative(self):
        """Verifica se o feedback é negativo"""
        if self.rating_type == "thumbs_down":
            return self.rating_value == -1
        elif self.rating_type == "star_rating":
            return self.rating_value <= 2
        return False

    @property
    def is_neutral(self):
        """Verifica se o feedback é neutro"""
        if self.rating_type == "star_rating":
            return self.rating_value == 3
        return False

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "message_id": str(self.message_id),
            "user_id": str(self.user_id),
            "rating_type": self.rating_type,
            "rating_value": self.rating_value,
            "feedback_text": self.feedback_text,
            "feedback_category": self.feedback_category,
            "improvement_suggestions": self.improvement_suggestions,
            "is_public": self.is_public,
            "feedback_metadata": self.feedback_metadata,
            "is_positive": self.is_positive,
            "is_negative": self.is_negative,
            "is_neutral": self.is_neutral,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 
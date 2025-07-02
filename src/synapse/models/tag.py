"""
Modelo Tag para sistema de tagging flexível
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    Float,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

from synapse.database import Base


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_type = Column(
        String(50), nullable=False, index=True
    )  # conversation, message, user, workspace
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Dados da tag
    tag_name = Column(String(100), nullable=False, index=True)
    tag_value = Column(Text, nullable=True)  # Opcional: valor da tag
    tag_category = Column(String(50), nullable=True, index=True)  # categoria da tag

    # Configurações
    is_system_tag = Column(
        Boolean, server_default=text("false"), index=True
    )  # tag do sistema vs usuário
    created_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    auto_generated = Column(Boolean, server_default=text("false"))
    confidence_score = Column(Float, nullable=True)  # Para tags automáticas

    # Metadata adicional
    tag_metadata = Column("metadata", JSON, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relacionamentos
    created_by_user = relationship("User", back_populates="created_tags")

    def __repr__(self):
        return f"<Tag(target_type={self.target_type}, target_id={self.target_id}, tag_name={self.tag_name})>"

    @property
    def is_user_tag(self):
        """Verifica se a tag foi criada por usuário"""
        return not self.is_system_tag

    @property
    def is_high_confidence(self):
        """Verifica se a tag automática tem alta confiança"""
        if self.confidence_score is not None:
            return self.confidence_score >= 0.8
        return False

    @property
    def display_name(self):
        """Nome para exibição"""
        if self.tag_value:
            return f"{self.tag_name}: {self.tag_value}"
        return self.tag_name

    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "target_type": self.target_type,
            "target_id": str(self.target_id),
            "tag_name": self.tag_name,
            "tag_value": self.tag_value,
            "tag_category": self.tag_category,
            "is_system_tag": self.is_system_tag,
            "is_user_tag": self.is_user_tag,
            "created_by_user_id": (
                str(self.created_by_user_id) if self.created_by_user_id else None
            ),
            "auto_generated": self.auto_generated,
            "confidence_score": self.confidence_score,
            "is_high_confidence": self.is_high_confidence,
            "display_name": self.display_name,
            "tag_metadata": self.tag_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

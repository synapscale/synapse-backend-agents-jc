"""
Modelo de convites de workspace
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from synapse.database import Base
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import secrets

class InvitationStatus(Enum):
    """Status do convite"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class WorkspaceInvitation(Base):
    """
    Modelo de convite para workspace
    """
    __tablename__ = "workspace_invitations"
    __table_args__ = {"schema": "synapscale_db"}

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE"), nullable=False)
    invited_user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id", ondelete="CASCADE"), nullable=True)  # Pode ser null se convidado por email
    
    # Dados do convite
    email = Column(String(255), nullable=False, index=True)  # Email do convidado
    token = Column(String(255), nullable=False, unique=True, index=True)  # Token único para aceitar convite
    role = Column(String(20), nullable=False, default="member")  # Role que será atribuído
    message = Column(String(500), nullable=True)  # Mensagem personalizada
    
    # Status e controle
    status = Column(SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING, index=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="workspace_invitations_sent")
    invited_user = relationship("User", foreign_keys=[invited_user_id], back_populates="workspace_invitations_received")

    def __repr__(self):
        return f"<WorkspaceInvitation(id={self.id}, email={self.email}, status={self.status.value})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "inviter_id": str(self.inviter_id),
            "invited_user_id": str(self.invited_user_id) if self.invited_user_id else None,
            "email": self.email,
            "token": self.token,
            "role": self.role,
            "message": self.message,
            "status": self.status.value,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def is_expired(self) -> bool:
        """Verifica se o convite está expirado"""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def can_be_accepted(self) -> bool:
        """Verifica se o convite pode ser aceito"""
        return (
            self.status == InvitationStatus.PENDING and
            self.is_active and
            not self.is_expired
        )

    def mark_as_expired(self):
        """Marca o convite como expirado"""
        self.status = InvitationStatus.EXPIRED
        self.is_active = False

    def accept(self, user_id: str = None):
        """Aceita o convite"""
        if not self.can_be_accepted:
            raise ValueError("Convite não pode ser aceito")
        
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = datetime.now(timezone.utc)
        if user_id:
            self.invited_user_id = user_id

    def decline(self):
        """Recusa o convite"""
        if self.status != InvitationStatus.PENDING:
            raise ValueError("Apenas convites pendentes podem ser recusados")
        
        self.status = InvitationStatus.DECLINED
        self.is_active = False

    def cancel(self):
        """Cancela o convite"""
        if self.status not in [InvitationStatus.PENDING]:
            raise ValueError("Apenas convites pendentes podem ser cancelados")
        
        self.status = InvitationStatus.CANCELLED
        self.is_active = False

    @classmethod
    def create_invitation(
        cls,
        workspace_id: str,
        inviter_id: str,
        email: str,
        role: str = "member",
        message: str = None,
        expires_in_days: int = 7
    ):
        """Cria um novo convite"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        return cls(
            workspace_id=workspace_id,
            inviter_id=inviter_id,
            email=email.lower(),
            token=token,
            role=role,
            message=message,
            expires_at=expires_at
        )

    @classmethod
    def find_by_token(cls, db_session, token: str):
        """Encontra convite pelo token"""
        return db_session.query(cls).filter(cls.token == token).first()

    @classmethod
    def find_pending_by_email(cls, db_session, email: str, workspace_id: str = None):
        """Encontra convites pendentes por email"""
        query = db_session.query(cls).filter(
            cls.email == email.lower(),
            cls.status == InvitationStatus.PENDING,
            cls.is_active == True
        )
        
        if workspace_id:
            query = query.filter(cls.workspace_id == workspace_id)
        
        return query.all()

    def generate_invitation_url(self, base_url: str) -> str:
        """Gera URL de convite"""
        return f"{base_url}/invite/accept?token={self.token}" 
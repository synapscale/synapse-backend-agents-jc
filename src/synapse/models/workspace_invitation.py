"""Workspace Invitation Model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkspaceInvitation(Base):
    """Workspace invitation management"""
    
    __tablename__ = "workspace_invitations"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    invited_user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    token = Column(String(100), nullable=False, unique=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="workspace_invitations_sent")
    invited_user = relationship("User", foreign_keys=[invited_user_id], back_populates="workspace_invitations_received")
    tenant = relationship("Tenant", back_populates="workspace_invitations")

    def __str__(self):
        return f"WorkspaceInvitation(email={self.email}, status={self.status})"

    @property
    def is_expired(self):
        """Check if invitation is expired"""
        return self.expires_at < func.now()

    @property
    def is_pending(self):
        """Check if invitation is pending"""
        return self.status == "pending" and not self.is_expired

    @property
    def can_accept(self):
        """Check if invitation can be accepted"""
        return self.status == "pending" and not self.is_expired

    @property
    def status_display(self):
        """Get human-readable status"""
        status_map = {
            "pending": "Pending Response",
            "accepted": "Accepted",
            "declined": "Declined",
            "expired": "Expired",
            "cancelled": "Cancelled"
        }
        if self.status == "pending" and self.is_expired:
            return "Expired"
        return status_map.get(self.status, self.status.title())

    def accept(self):
        """Accept the invitation"""
        if not self.can_accept:
            raise ValueError("Invitation cannot be accepted")
        
        self.status = "accepted"
        self.responded_at = func.current_timestamp()
        self.updated_at = func.current_timestamp()

    def decline(self):
        """Decline the invitation"""
        if not self.can_accept:
            raise ValueError("Invitation cannot be declined")
        
        self.status = "declined"
        self.responded_at = func.current_timestamp()
        self.updated_at = func.current_timestamp()

    def cancel(self):
        """Cancel the invitation"""
        if self.status in ["accepted", "declined"]:
            raise ValueError("Cannot cancel responded invitation")
        
        self.status = "cancelled"
        self.updated_at = func.current_timestamp()

    def resend(self, new_token, new_expires_at):
        """Resend the invitation with new token"""
        if self.status != "pending":
            raise ValueError("Can only resend pending invitations")
        
        self.token = new_token
        self.expires_at = new_expires_at
        self.updated_at = func.current_timestamp()

    @classmethod
    def get_by_token(cls, session, token):
        """Get invitation by token"""
        return session.query(cls).filter(cls.token == token).first()

    @classmethod
    def get_workspace_invitations(cls, session, workspace_id, status=None):
        """Get invitations for a workspace"""
        query = session.query(cls).filter(cls.workspace_id == workspace_id)
        if status:
            query = query.filter(cls.status == status)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_invitations(cls, session, email=None, user_id=None, status=None):
        """Get invitations for a user"""
        query = session.query(cls)
        
        if email:
            query = query.filter(cls.email == email)
        if user_id:
            query = query.filter(cls.invited_user_id == user_id)
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def cleanup_expired(cls, session):
        """Update expired invitations status"""
        expired_invitations = session.query(cls).filter(
            cls.status == "pending",
            cls.expires_at < func.now()
        ).all()
        
        for invitation in expired_invitations:
            invitation.status = "expired"
            invitation.updated_at = func.current_timestamp()
        
        return len(expired_invitations)

    @classmethod
    def get_pending_for_email(cls, session, email):
        """Get pending invitations for an email"""
        return session.query(cls).filter(
            cls.email == email,
            cls.status == "pending",
            cls.expires_at > func.now()
        ).all()

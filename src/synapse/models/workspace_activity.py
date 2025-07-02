"""Workspace Activity Model"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkspaceActivity(Base):
    """Activity tracking within workspaces"""
    
    __tablename__ = "workspace_activities"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    description = Column(String(500), nullable=False)
    activity_metadata = Column("metadata", JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    meta_data = Column(JSONB, nullable=True, server_default="{}")

    # Relationships
    workspace = relationship("Workspace", back_populates="activities")
    user = relationship("User", back_populates="workspace_activities")
    tenant = relationship("Tenant", back_populates="workspace_activities")

    def __str__(self):
        return f"WorkspaceActivity(action={self.action}, resource={self.resource_type})"

    @property
    def action_display(self):
        """Get human-readable action description"""
        action_map = {
            "create": "Created",
            "update": "Updated", 
            "delete": "Deleted",
            "view": "Viewed",
            "share": "Shared",
            "invite": "Invited",
            "join": "Joined",
            "leave": "Left",
            "export": "Exported",
            "import": "Imported"
        }
        return action_map.get(self.action, self.action.title())

    @classmethod
    def log_activity(cls, session, workspace_id, user_id, action, resource_type, 
                    description, resource_id=None, metadata=None, ip_address=None, 
                    user_agent=None, tenant_id=None):
        """Log a new workspace activity"""
        activity = cls(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            activity_metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            tenant_id=tenant_id,
            created_at=func.now()
        )
        session.add(activity)
        return activity

    @classmethod
    def get_workspace_timeline(cls, session, workspace_id, limit=50, offset=0):
        """Get timeline of workspace activities"""
        return session.query(cls).filter(
            cls.workspace_id == workspace_id
        ).order_by(cls.created_at.desc()).limit(limit).offset(offset).all()

    @classmethod
    def get_user_activities(cls, session, user_id, workspace_id=None, limit=50):
        """Get activities for a specific user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        if workspace_id:
            query = query.filter(cls.workspace_id == workspace_id)
        return query.order_by(cls.created_at.desc()).limit(limit).all()

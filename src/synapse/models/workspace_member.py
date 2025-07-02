"""Workspace Member Model"""

from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkspaceRole(PyEnum):
    """Workspace member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceMember(Base):
    """Workspace membership and permissions"""
    
    __tablename__ = "workspace_members"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    custom_permissions = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False, server_default="active")
    is_favorite = Column(Boolean, nullable=False, server_default="false")
    notification_preferences = Column(JSONB, nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=False)
    left_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)
    role = Column(String(50), nullable=False, server_default="member")

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")
    tenant = relationship("Tenant", back_populates="workspace_members")

    def __str__(self):
        return f"WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role})"

    @property
    def is_active(self):
        """Check if membership is active"""
        return self.status == "active" and self.left_at is None

    @property
    def is_owner(self):
        """Check if member is workspace owner"""
        return self.role == "owner"

    @property
    def is_admin(self):
        """Check if member is admin or owner"""
        return self.role in ["owner", "admin"]

    @property
    def can_manage_members(self):
        """Check if member can manage other members"""
        return self.role in ["owner", "admin"]

    @property
    def can_invite_members(self):
        """Check if member can invite new members"""
        return self.role in ["owner", "admin", "moderator"]

    def has_permission(self, permission):
        """Check if member has specific permission"""
        # Check role-based permissions first
        role_permissions = {
            "owner": ["*"],  # All permissions
            "admin": ["manage_workspace", "manage_members", "invite_members", "manage_projects", "view_analytics"],
            "moderator": ["invite_members", "manage_projects", "view_projects"],
            "member": ["view_projects", "create_projects"],
            "viewer": ["view_projects"]
        }
        
        default_perms = role_permissions.get(self.role, [])
        if "*" in default_perms or permission in default_perms:
            return True
        
        # Check custom permissions
        if self.custom_permissions:
            custom_perms = self.custom_permissions.get("permissions", [])
            if permission in custom_perms:
                return True
            
            # Check denied permissions
            denied_perms = self.custom_permissions.get("denied_permissions", [])
            if permission in denied_perms:
                return False
        
        return False

    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen_at = func.current_timestamp()
        self.updated_at = func.current_timestamp()

    def leave_workspace(self):
        """Leave the workspace"""
        self.status = "left"
        self.left_at = func.current_timestamp()
        self.updated_at = func.current_timestamp()

    def change_role(self, new_role):
        """Change member role"""
        valid_roles = ["owner", "admin", "moderator", "member", "viewer"]
        if new_role in valid_roles:
            self.role = new_role
            self.updated_at = func.current_timestamp()
            return True
        return False

    def set_custom_permissions(self, permissions, denied_permissions=None):
        """Set custom permissions for member"""
        self.custom_permissions = {
            "permissions": permissions or [],
            "denied_permissions": denied_permissions or []
        }
        self.updated_at = func.current_timestamp()

    @classmethod
    def get_workspace_members(cls, session, workspace_id, status="active"):
        """Get all members of a workspace"""
        query = session.query(cls).filter(cls.workspace_id == workspace_id)
        if status:
            query = query.filter(cls.status == status)
        return query.all()

    @classmethod
    def get_user_workspaces(cls, session, user_id, status="active"):
        """Get all workspaces for a user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        if status:
            query = query.filter(cls.status == status)
        return query.all()

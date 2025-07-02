"""Workspace Project Model"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkspaceProject(Base):
    """Projects within workspaces"""
    
    __tablename__ = "workspace_projects"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    allow_concurrent_editing = Column(Boolean, nullable=False)
    auto_save_interval = Column(Integer, nullable=True)  # seconds
    version_control_enabled = Column(Boolean, nullable=False)
    status = Column(String(20), nullable=False)
    is_template = Column(Boolean, nullable=False)
    is_public = Column(Boolean, nullable=False)
    collaborator_count = Column(Integer, nullable=False)
    edit_count = Column(Integer, nullable=False)
    comment_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    last_edited_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    workflow = relationship("Workflow", back_populates="projects")
    tenant = relationship("Tenant", back_populates="workspace_projects")
    collaborators = relationship("ProjectCollaborator", back_populates="project")
    comments = relationship("ProjectComment", back_populates="project")
    versions = relationship("ProjectVersion", back_populates="project")
    analytics_events = relationship("AnalyticsEvent", back_populates="project", cascade="all, delete-orphan")

    def __str__(self):
        return f"WorkspaceProject(name={self.name}, status={self.status})"

    @property
    def is_active(self):
        """Check if project is active"""
        return self.status == "active"

    @property
    def is_archived(self):
        """Check if project is archived"""
        return self.status == "archived"

    @property
    def can_edit(self):
        """Check if project can be edited"""
        return self.status in ["active", "draft"]

    @property
    def color_hex(self):
        """Get color as hex code"""
        return self.color or "#007bff"  # Default blue

    @property
    def auto_save_enabled(self):
        """Check if auto-save is enabled"""
        return self.auto_save_interval is not None and self.auto_save_interval > 0

    def update_edit_count(self):
        """Increment edit count and update last edited time"""
        self.edit_count += 1
        self.last_edited_at = func.now()
        self.updated_at = func.now()

    def update_collaborator_count(self, session):
        """Update collaborator count based on active collaborators"""
        from synapse.models.project_collaborator import ProjectCollaborator
        count = session.query(ProjectCollaborator).filter(
            ProjectCollaborator.project_id == self.id,
            ProjectCollaborator.status == "active"
        ).count()
        self.collaborator_count = count
        self.updated_at = func.now()

    def update_comment_count(self, session):
        """Update comment count"""
        from synapse.models.project_comment import ProjectComment
        count = session.query(ProjectComment).filter(
            ProjectComment.project_id == self.id
        ).count()
        self.comment_count = count
        self.updated_at = func.now()

    def archive(self):
        """Archive the project"""
        self.status = "archived"
        self.updated_at = func.now()

    def activate(self):
        """Activate the project"""
        self.status = "active"
        self.updated_at = func.now()

    def make_template(self):
        """Convert project to template"""
        self.is_template = True
        self.updated_at = func.now()

    def make_public(self):
        """Make project public"""
        self.is_public = True
        self.updated_at = func.now()

    def make_private(self):
        """Make project private"""
        self.is_public = False
        self.updated_at = func.now()

    def update_settings(self, allow_concurrent=None, auto_save_interval=None, 
                       version_control=None, color=None):
        """Update project settings"""
        if allow_concurrent is not None:
            self.allow_concurrent_editing = allow_concurrent
        if auto_save_interval is not None:
            self.auto_save_interval = auto_save_interval
        if version_control is not None:
            self.version_control_enabled = version_control
        if color is not None:
            self.color = color
        
        self.updated_at = func.now()

    @classmethod
    def get_workspace_projects(cls, session, workspace_id, status=None, include_templates=True):
        """Get projects for a workspace"""
        query = session.query(cls).filter(cls.workspace_id == workspace_id)
        
        if status:
            query = query.filter(cls.status == status)
        if not include_templates:
            query = query.filter(cls.is_template.is_(False))
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def get_public_projects(cls, session, limit=20, offset=0):
        """Get public projects"""
        return session.query(cls).filter(
            cls.is_public.is_(True),
            cls.status == "active"
        ).order_by(cls.updated_at.desc()).limit(limit).offset(offset).all()

    @classmethod
    def get_templates(cls, session, workspace_id=None, limit=20):
        """Get project templates"""
        query = session.query(cls).filter(
            cls.is_template.is_(True),
            cls.status == "active"
        )
        
        if workspace_id:
            query = query.filter(cls.workspace_id == workspace_id)
        
        return query.order_by(cls.updated_at.desc()).limit(limit).all()

    @classmethod
    def search_projects(cls, session, workspace_id, search_term, status=None):
        """Search projects by name or description"""
        query = session.query(cls).filter(
            cls.workspace_id == workspace_id
        ).filter(
            cls.name.ilike(f"%{search_term}%") |
            cls.description.ilike(f"%{search_term}%")
        )
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def get_recent_projects(cls, session, workspace_id, limit=10):
        """Get recently edited projects"""
        return session.query(cls).filter(
            cls.workspace_id == workspace_id,
            cls.status == "active"
        ).order_by(cls.last_edited_at.desc()).limit(limit).all()

"""Project Version Model"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class ProjectVersion(Base):
    """Version control for workspace projects"""
    
    __tablename__ = "project_versions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspace_projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    workflow_data = Column(JSONB, nullable=False)
    changes_summary = Column(JSONB, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    is_major = Column(Boolean, nullable=False)
    is_auto_save = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    project = relationship("WorkspaceProject", back_populates="versions")
    user = relationship("User", back_populates="project_versions")
    tenant = relationship("Tenant", back_populates="project_versions")

    def __str__(self):
        return f"ProjectVersion(v{self.version_number}, project_id={self.project_id})"

    @property
    def version_display(self):
        """Get version display string"""
        if self.version_name:
            return f"v{self.version_number} ({self.version_name})"
        return f"v{self.version_number}"

    @property
    def size_display(self):
        """Get human-readable file size"""
        if not self.file_size:
            return "Unknown"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def is_latest(self):
        """Check if this is the latest version (computed property)"""
        # This would need to be computed in the query or business logic
        return False

    @property
    def version_type(self):
        """Get version type"""
        if self.is_auto_save:
            return "Auto-save"
        elif self.is_major:
            return "Major Release"
        else:
            return "Minor Update"

    def calculate_checksum(self):
        """Calculate SHA-256 checksum of workflow data"""
        import hashlib
        import json
        
        data_string = json.dumps(self.workflow_data, sort_keys=True)
        checksum = hashlib.sha256(data_string.encode()).hexdigest()
        self.checksum = checksum
        return checksum

    def calculate_file_size(self):
        """Calculate size of workflow data in bytes"""
        import json
        
        data_string = json.dumps(self.workflow_data)
        self.file_size = len(data_string.encode('utf-8'))
        return self.file_size

    def add_change_summary(self, change_type, description, details=None):
        """Add a change to the summary"""
        if not self.changes_summary:
            self.changes_summary = {"changes": []}
        
        change = {
            "type": change_type,
            "description": description,
            "timestamp": func.now().isoformat(),
            "details": details or {}
        }
        
        self.changes_summary["changes"].append(change)

    def get_changes_by_type(self, change_type):
        """Get changes of specific type"""
        if not self.changes_summary or "changes" not in self.changes_summary:
            return []
        
        return [
            change for change in self.changes_summary["changes"]
            if change.get("type") == change_type
        ]

    @classmethod
    def get_project_versions(cls, session, project_id, limit=20, include_auto_save=True):
        """Get versions for a project"""
        query = session.query(cls).filter(cls.project_id == project_id)
        
        if not include_auto_save:
            query = query.filter(cls.is_auto_save.is_(False))
        
        return query.order_by(cls.version_number.desc()).limit(limit).all()

    @classmethod
    def get_latest_version(cls, session, project_id):
        """Get the latest version for a project"""
        return session.query(cls).filter(
            cls.project_id == project_id
        ).order_by(cls.version_number.desc()).first()

    @classmethod
    def get_version_by_number(cls, session, project_id, version_number):
        """Get specific version by number"""
        return session.query(cls).filter(
            cls.project_id == project_id,
            cls.version_number == version_number
        ).first()

    @classmethod
    def get_major_versions(cls, session, project_id):
        """Get only major versions"""
        return session.query(cls).filter(
            cls.project_id == project_id,
            cls.is_major.is_(True)
        ).order_by(cls.version_number.desc()).all()

    @classmethod
    def cleanup_auto_saves(cls, session, project_id, keep_count=10):
        """Clean up old auto-save versions, keeping only the most recent"""
        auto_saves = session.query(cls).filter(
            cls.project_id == project_id,
            cls.is_auto_save.is_(True)
        ).order_by(cls.created_at.desc()).all()
        
        if len(auto_saves) > keep_count:
            to_delete = auto_saves[keep_count:]
            for version in to_delete:
                session.delete(version)
            return len(to_delete)
        return 0

    @classmethod
    def create_version(cls, session, project_id, user_id, workflow_data, 
                      version_name=None, description=None, is_major=False, 
                      is_auto_save=False, tenant_id=None):
        """Create a new version"""
        # Get next version number
        latest = cls.get_latest_version(session, project_id)
        next_version = 1 if not latest else latest.version_number + 1
        
        version = cls(
            project_id=project_id,
            user_id=user_id,
            version_number=next_version,
            version_name=version_name,
            description=description,
            workflow_data=workflow_data,
            is_major=is_major,
            is_auto_save=is_auto_save,
            created_at=func.now(),
            tenant_id=tenant_id
        )
        
        # Calculate size and checksum
        version.calculate_file_size()
        version.calculate_checksum()
        
        session.add(version)
        return version

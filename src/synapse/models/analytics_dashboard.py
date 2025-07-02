"""Analytics Dashboard Model"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsDashboard(Base):
    """Analytics dashboards and visualizations"""
    
    __tablename__ = "analytics_dashboards"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    layout = Column(JSONB, nullable=False)
    widgets = Column(JSONB, nullable=False)
    filters = Column(JSONB, nullable=True)
    auto_refresh = Column(Boolean, nullable=False)
    refresh_interval = Column(Integer, nullable=True)  # seconds
    is_public = Column(Boolean, nullable=False, server_default="false")
    shared_with = Column(JSONB, nullable=True)
    is_default = Column(Boolean, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workspaces.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="analytics_dashboards")
    workspace = relationship("Workspace", back_populates="analytics_dashboards")
    tenant = relationship("Tenant", back_populates="analytics_dashboards")

    def __str__(self):
        return f"AnalyticsDashboard(name={self.name}, status={self.status})"

    @property
    def is_active(self):
        """Check if dashboard is active"""
        return self.status == "active"

    @property
    def widget_count(self):
        """Get number of widgets in dashboard"""
        if not self.widgets or not isinstance(self.widgets, list):
            return 0
        return len(self.widgets)

    @property
    def layout_type(self):
        """Get dashboard layout type"""
        if not self.layout:
            return "grid"
        return self.layout.get("type", "grid")

    @property
    def refresh_interval_display(self):
        """Get human-readable refresh interval"""
        if not self.auto_refresh or not self.refresh_interval:
            return "Manual"
        
        seconds = self.refresh_interval
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        else:
            return f"{seconds // 3600}h"

    @property
    def sharing_info(self):
        """Get dashboard sharing information"""
        info = {"type": "private"}
        
        if self.is_public:
            info["type"] = "public"
        elif self.shared_with:
            info["type"] = "shared"
            info["shared_count"] = len(self.shared_with.get("users", []))
        
        return info

    def add_widget(self, widget_config):
        """Add a widget to the dashboard"""
        if not self.widgets:
            self.widgets = []
        
        # Generate widget ID
        widget_id = f"widget_{len(self.widgets) + 1}"
        widget_config["id"] = widget_id
        widget_config["created_at"] = func.now().isoformat()
        
        self.widgets.append(widget_config)
        self.updated_at = func.now()
        return widget_id

    def remove_widget(self, widget_id):
        """Remove a widget from the dashboard"""
        if not self.widgets:
            return False
        
        original_count = len(self.widgets)
        self.widgets = [w for w in self.widgets if w.get("id") != widget_id]
        
        if len(self.widgets) < original_count:
            self.updated_at = func.now()
            return True
        return False

    def update_widget(self, widget_id, new_config):
        """Update a specific widget"""
        if not self.widgets:
            return False
        
        for i, widget in enumerate(self.widgets):
            if widget.get("id") == widget_id:
                # Preserve id and created_at
                new_config["id"] = widget_id
                new_config["created_at"] = widget.get("created_at")
                new_config["updated_at"] = func.now().isoformat()
                
                self.widgets[i] = new_config
                self.updated_at = func.now()
                return True
        return False

    def update_layout(self, new_layout):
        """Update dashboard layout"""
        self.layout = new_layout
        self.updated_at = func.now()

    def set_filters(self, filters):
        """Set dashboard filters"""
        self.filters = filters
        self.updated_at = func.now()

    def share_with_users(self, user_ids, permissions=None):
        """Share dashboard with specific users"""
        if not self.shared_with:
            self.shared_with = {"users": [], "permissions": {}}
        
        for user_id in user_ids:
            if user_id not in self.shared_with["users"]:
                self.shared_with["users"].append(user_id)
            
            if permissions:
                self.shared_with["permissions"][user_id] = permissions
        
        self.updated_at = func.now()

    def unshare_with_user(self, user_id):
        """Remove user from shared list"""
        if not self.shared_with:
            return False
        
        users = self.shared_with.get("users", [])
        if user_id in users:
            users.remove(user_id)
            
            # Remove permissions
            permissions = self.shared_with.get("permissions", {})
            if user_id in permissions:
                del permissions[user_id]
            
            self.updated_at = func.now()
            return True
        return False

    def make_public(self):
        """Make dashboard public"""
        self.is_public = True
        self.updated_at = func.now()

    def make_private(self):
        """Make dashboard private"""
        self.is_public = False
        self.shared_with = None
        self.updated_at = func.now()

    def activate(self):
        """Activate dashboard"""
        self.status = "active"
        self.updated_at = func.now()

    def archive(self):
        """Archive dashboard"""
        self.status = "archived"
        self.updated_at = func.now()

    def set_as_default(self):
        """Set as default dashboard"""
        self.is_default = True
        self.updated_at = func.now()

    def record_view(self):
        """Record that dashboard was viewed"""
        self.last_viewed_at = func.now()

    def configure_auto_refresh(self, enabled, interval=None):
        """Configure auto-refresh settings"""
        self.auto_refresh = enabled
        if enabled and interval:
            self.refresh_interval = interval
        elif not enabled:
            self.refresh_interval = None
        self.updated_at = func.now()

    @classmethod
    def get_user_dashboards(cls, session, user_id, status="active", include_shared=True):
        """Get dashboards for a user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        dashboards = query.order_by(cls.updated_at.desc()).all()
        
        if include_shared:
            # Add shared dashboards
            shared_dashboards = session.query(cls).filter(
                cls.shared_with.op('?')('users'),
                cls.shared_with.op('@>')([user_id])
            ).all()
            dashboards.extend(shared_dashboards)
        
        return dashboards

    @classmethod
    def get_public_dashboards(cls, session, limit=20):
        """Get public dashboards"""
        return session.query(cls).filter(
            cls.is_public.is_(True),
            cls.status == "active"
        ).order_by(cls.updated_at.desc()).limit(limit).all()

    @classmethod
    def get_workspace_dashboards(cls, session, workspace_id, status="active"):
        """Get dashboards for a workspace"""
        query = session.query(cls).filter(cls.workspace_id == workspace_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def get_default_dashboard(cls, session, user_id):
        """Get user's default dashboard"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default.is_(True),
            cls.status == "active"
        ).first()

    @classmethod
    def search_dashboards(cls, session, search_term, user_id=None):
        """Search dashboards by name or description"""
        query = session.query(cls).filter(
            cls.name.ilike(f"%{search_term}%") |
            cls.description.ilike(f"%{search_term}%")
        ).filter(cls.status == "active")
        
        if user_id:
            query = query.filter(
                (cls.user_id == user_id) |
                (cls.is_public.is_(True)) |
                (cls.shared_with.op('?')('users') & cls.shared_with.op('@>')([user_id]))
            )
        
        return query.order_by(cls.updated_at.desc()).all()

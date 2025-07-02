"""Workflow Template Model"""

from sqlalchemy import Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkflowTemplate(Base):
    """Templates for creating workflows"""
    
    __tablename__ = "workflow_templates"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    tags = Column(JSONB, nullable=True)
    workflow_definition = Column(JSONB, nullable=False)
    preview_image = Column(String(500), nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    version = Column(String(50), nullable=False, server_default="1.0.0")
    is_public = Column(Boolean, nullable=False, server_default="false")
    is_featured = Column(Boolean, nullable=False, server_default="false")
    downloads_count = Column(Integer, nullable=False, server_default="0")
    rating_average = Column(Numeric, nullable=False, server_default="0.00")
    rating_count = Column(Integer, nullable=False, server_default="0")
    price = Column(Numeric, nullable=False, server_default="0.00")
    is_free = Column(Boolean, nullable=False, server_default="true")
    license = Column(String(50), nullable=False, server_default="MIT")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    title = Column(String(255), nullable=False)
    short_description = Column(String(500), nullable=True)
    original_workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=True)
    status = Column(String(20), nullable=True)
    is_verified = Column(Boolean, nullable=True)
    license_type = Column(String(20), nullable=True)
    workflow_data = Column(JSONB, nullable=False)
    nodes_data = Column(JSONB, nullable=False)
    connections_data = Column(JSONB, nullable=True)
    required_variables = Column(JSONB, nullable=True)
    optional_variables = Column(JSONB, nullable=True)
    default_config = Column(JSONB, nullable=True)
    compatibility_version = Column(String(20), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutes
    complexity_level = Column(Integer, nullable=True)  # 1-5
    download_count = Column(Integer, nullable=True)
    usage_count = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    keywords = Column(JSONB, nullable=True)
    use_cases = Column(JSONB, nullable=True)
    industries = Column(JSONB, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    preview_images = Column(JSONB, nullable=True)
    demo_video_url = Column(String(500), nullable=True)
    documentation = Column(Text, nullable=True)
    setup_instructions = Column(Text, nullable=True)
    changelog = Column(JSONB, nullable=True)
    support_email = Column(String(255), nullable=True)
    repository_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)

    # Relationships
    author = relationship("User", back_populates="created_templates")
    original_workflow = relationship("Workflow", back_populates="templates")
    tenant = relationship("Tenant", back_populates="workflow_templates")
    
    # Relacionamentos com as classes de template do arquivo template.py
    reviews = relationship("TemplateReview", back_populates="template", cascade="all, delete-orphan")
    downloads = relationship("TemplateDownload", back_populates="template", cascade="all, delete-orphan")
    favorites = relationship("TemplateFavorite", back_populates="template", cascade="all, delete-orphan")

    def __str__(self):
        return f"WorkflowTemplate(name={self.name}, version={self.version})"

    @property
    def is_active(self):
        """Check if template is active"""
        return self.status == "active"

    @property
    def is_published(self):
        """Check if template is published"""
        return self.published_at is not None

    @property
    def complexity_display(self):
        """Get human-readable complexity level"""
        levels = {1: "Beginner", 2: "Easy", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
        return levels.get(self.complexity_level, "Unknown")

    @property
    def duration_display(self):
        """Get human-readable estimated duration"""
        if not self.estimated_duration:
            return "Unknown"
        
        minutes = self.estimated_duration
        if minutes < 60:
            return f"{minutes}m"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"

    @property
    def price_display(self):
        """Get formatted price"""
        if self.is_free:
            return "Free"
        return f"${float(self.price):.2f}"

    @property
    def rating_display(self):
        """Get formatted rating"""
        if self.rating_count == 0:
            return "No ratings"
        return f"{float(self.rating_average):.1f}/5.0 ({self.rating_count} reviews)"

    def increment_download(self):
        """Increment download count"""
        self.downloads_count += 1
        self.download_count = (self.download_count or 0) + 1
        self.updated_at = func.now()

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count = (self.usage_count or 0) + 1
        self.last_used_at = func.now()
        self.updated_at = func.now()

    def increment_view(self):
        """Increment view count"""
        self.view_count = (self.view_count or 0) + 1
        self.updated_at = func.now()

    def add_rating(self, rating, count=1):
        """Add a new rating"""
        current_total = float(self.rating_average) * self.rating_count
        new_total = current_total + (rating * count)
        self.rating_count += count
        self.rating_average = new_total / self.rating_count
        self.updated_at = func.now()

    def publish(self):
        """Publish the template"""
        self.status = "active"
        self.published_at = func.now()
        self.updated_at = func.now()

    def unpublish(self):
        """Unpublish the template"""
        self.status = "draft"
        self.updated_at = func.now()

    def feature(self):
        """Mark template as featured"""
        self.is_featured = True
        self.updated_at = func.now()

    def unfeature(self):
        """Remove featured status"""
        self.is_featured = False
        self.updated_at = func.now()

    def add_keyword(self, keyword):
        """Add a keyword"""
        if not self.keywords:
            self.keywords = []
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            self.updated_at = func.now()

    def remove_keyword(self, keyword):
        """Remove a keyword"""
        if self.keywords and keyword in self.keywords:
            self.keywords.remove(keyword)
            self.updated_at = func.now()

    def get_variable_info(self):
        """Get information about template variables"""
        info = {
            "required_count": len(self.required_variables) if self.required_variables else 0,
            "optional_count": len(self.optional_variables) if self.optional_variables else 0,
            "required_variables": self.required_variables or [],
            "optional_variables": self.optional_variables or []
        }
        return info

    @classmethod
    def create_template(cls, session, name, workflow_data, nodes_data, author_id, **kwargs):
        """Create a new workflow template"""
        template = cls(
            name=name,
            title=kwargs.get('title', name),
            workflow_data=workflow_data,
            nodes_data=nodes_data,
            author_id=author_id,
            status="draft",
            created_at=func.now(),
            updated_at=func.now(),
            **{k: v for k, v in kwargs.items() if k != 'title'}
        )
        
        session.add(template)
        return template

    @classmethod
    def get_public_templates(cls, session, category=None, featured_only=False, limit=20, offset=0):
        """Get public templates"""
        query = session.query(cls).filter(
            cls.is_public.is_(True),
            cls.status == "active"
        )
        
        if category:
            query = query.filter(cls.category == category)
        if featured_only:
            query = query.filter(cls.is_featured.is_(True))
        
        return query.order_by(cls.downloads_count.desc()).limit(limit).offset(offset).all()

    @classmethod
    def get_featured_templates(cls, session, limit=10):
        """Get featured templates"""
        return session.query(cls).filter(
            cls.is_featured.is_(True),
            cls.is_public.is_(True),
            cls.status == "active"
        ).order_by(cls.rating_average.desc()).limit(limit).all()

    @classmethod
    def get_popular_templates(cls, session, days=30, limit=10):
        """Get popular templates based on recent downloads"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return session.query(cls).filter(
            cls.is_public.is_(True),
            cls.status == "active",
            cls.updated_at >= cutoff_date
        ).order_by(cls.downloads_count.desc()).limit(limit).all()

    @classmethod
    def search_templates(cls, session, search_term, category=None, limit=20):
        """Search templates by name, description, or keywords"""
        query = session.query(cls).filter(
            cls.is_public.is_(True),
            cls.status == "active"
        ).filter(
            cls.name.ilike(f"%{search_term}%") |
            cls.description.ilike(f"%{search_term}%") |
            cls.keywords.op('@>')([search_term])
        )
        
        if category:
            query = query.filter(cls.category == category)
        
        return query.order_by(cls.rating_average.desc()).limit(limit).all()

    @classmethod
    def get_by_author(cls, session, author_id, include_private=False):
        """Get templates by author"""
        query = session.query(cls).filter(cls.author_id == author_id)
        
        if not include_private:
            query = query.filter(cls.is_public.is_(True))
        
        return query.order_by(cls.updated_at.desc()).all()

    @classmethod
    def get_categories(cls, session):
        """Get available template categories"""
        return session.query(cls.category).filter(
            cls.is_public.is_(True),
            cls.status == "active"
        ).distinct().all()

    @classmethod
    def get_template_stats(cls, session, template_id=None, author_id=None):
        """Get template statistics"""
        query = session.query(cls)
        
        if template_id:
            query = query.filter(cls.id == template_id)
        elif author_id:
            query = query.filter(cls.author_id == author_id)
        
        templates = query.all()
        
        if not templates:
            return {}
        
        stats = {
            "total_templates": len(templates),
            "total_downloads": sum(t.downloads_count for t in templates),
            "total_views": sum(t.view_count or 0 for t in templates),
            "avg_rating": 0,
            "featured_count": len([t for t in templates if t.is_featured]),
            "published_count": len([t for t in templates if t.is_published]),
        }
        
        # Calculate average rating
        rated_templates = [t for t in templates if t.rating_count > 0]
        if rated_templates:
            total_rating = sum(float(t.rating_average) * t.rating_count for t in rated_templates)
            total_ratings = sum(t.rating_count for t in rated_templates)
            stats["avg_rating"] = total_rating / total_ratings
        
        return stats

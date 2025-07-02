"""Analytics Export Model"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class AnalyticsExport(Base):
    """Analytics data export management"""
    
    __tablename__ = "analytics_exports"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    export_type = Column(String(50), nullable=False)  # csv, json, pdf, xlsx
    export_query = Column("query", JSONB, nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, server_default="pending")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    owner = relationship("User", back_populates="analytics_exports")
    tenant = relationship("Tenant", back_populates="analytics_exports")

    def __str__(self):
        return f"AnalyticsExport(name={self.name}, type={self.export_type}, status={self.status})"

    @property
    def is_completed(self):
        """Check if export is completed"""
        return self.status == "completed"

    @property
    def is_processing(self):
        """Check if export is currently processing"""
        return self.status == "processing"

    @property
    def is_failed(self):
        """Check if export failed"""
        return self.status == "failed"

    @property
    def is_pending(self):
        """Check if export is pending"""
        return self.status == "pending"

    @property
    def duration_seconds(self):
        """Get export duration in seconds"""
        if not self.completed_at:
            return None
        return (self.completed_at - self.created_at).total_seconds()

    @property
    def query_summary(self):
        """Get a summary of the export query"""
        if not self.query:
            return "No query defined"
        
        summary_parts = []
        
        # Extract key information from query
        if "table" in self.query:
            summary_parts.append(f"Table: {self.query['table']}")
        
        if "date_range" in self.query:
            date_range = self.query["date_range"]
            summary_parts.append(f"Period: {date_range.get('start')} to {date_range.get('end')}")
        
        if "filters" in self.query:
            filter_count = len(self.query["filters"])
            summary_parts.append(f"Filters: {filter_count}")
        
        if "columns" in self.query:
            column_count = len(self.query["columns"])
            summary_parts.append(f"Columns: {column_count}")
        
        return " | ".join(summary_parts) if summary_parts else "Custom query"

    @property
    def file_extension(self):
        """Get file extension based on export type"""
        extensions = {
            "csv": ".csv",
            "json": ".json", 
            "pdf": ".pdf",
            "xlsx": ".xlsx",
            "xml": ".xml"
        }
        return extensions.get(self.export_type, ".txt")

    def start_processing(self):
        """Mark export as processing"""
        self.status = "processing"
        self.updated_at = func.current_timestamp()

    def mark_completed(self, file_path=None):
        """Mark export as completed"""
        self.status = "completed"
        self.completed_at = func.now()
        if file_path:
            self.file_path = file_path
        self.updated_at = func.current_timestamp()

    def mark_failed(self, error_message=None):
        """Mark export as failed"""
        self.status = "failed"
        self.completed_at = func.now()
        
        # Store error in query metadata
        if error_message and self.query:
            self.query["error"] = error_message
        
        self.updated_at = func.current_timestamp()

    def cancel(self):
        """Cancel pending export"""
        if self.status == "pending":
            self.status = "cancelled"
            self.updated_at = func.current_timestamp()
            return True
        return False

    def retry(self):
        """Retry failed export"""
        if self.status == "failed":
            self.status = "pending"
            self.completed_at = None
            self.file_path = None
            
            # Clear error from query
            if self.query and "error" in self.query:
                del self.query["error"]
            
            self.updated_at = func.current_timestamp()
            return True
        return False

    def update_query(self, new_query):
        """Update export query"""
        self.query = new_query
        self.updated_at = func.current_timestamp()

    def get_download_url(self, base_url=""):
        """Get download URL for completed export"""
        if not self.is_completed or not self.file_path:
            return None
        
        return f"{base_url}/exports/download/{self.id}"

    @classmethod
    def create_export(cls, session, name, export_type, query, owner_id, tenant_id=None):
        """Create a new analytics export"""
        export = cls(
            name=name,
            export_type=export_type,
            query=query,
            owner_id=owner_id,
            tenant_id=tenant_id,
            status="pending",
            created_at=func.now()
        )
        
        session.add(export)
        return export

    @classmethod
    def get_user_exports(cls, session, user_id, status=None, limit=50):
        """Get exports for a user"""
        query = session.query(cls).filter(cls.owner_id == user_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_pending_exports(cls, session, tenant_id=None):
        """Get pending exports for processing"""
        query = session.query(cls).filter(cls.status == "pending")
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.created_at.asc()).all()

    @classmethod
    def get_export_stats(cls, session, tenant_id=None, days=30):
        """Get export statistics"""
        cutoff_date = func.now() - func.interval(f'{days} days')
        
        query = session.query(cls).filter(cls.created_at >= cutoff_date)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        exports = query.all()
        
        stats = {
            "total": len(exports),
            "completed": len([e for e in exports if e.status == "completed"]),
            "failed": len([e for e in exports if e.status == "failed"]),
            "pending": len([e for e in exports if e.status == "pending"]),
            "processing": len([e for e in exports if e.status == "processing"]),
            "by_type": {}
        }
        
        # Count by export type
        for export in exports:
            export_type = export.export_type
            if export_type not in stats["by_type"]:
                stats["by_type"][export_type] = 0
            stats["by_type"][export_type] += 1
        
        # Calculate success rate
        if stats["total"] > 0:
            stats["success_rate"] = (stats["completed"] / stats["total"]) * 100
        else:
            stats["success_rate"] = 0
        
        return stats

    @classmethod
    def cleanup_old_exports(cls, session, days=90, tenant_id=None):
        """Clean up old completed exports"""
        cutoff_date = func.now() - func.interval(f'{days} days')
        
        query = session.query(cls).filter(
            cls.status.in_(["completed", "failed"]),
            cls.created_at < cutoff_date
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        old_exports = query.all()
        
        # Delete the exports
        for export in old_exports:
            session.delete(export)
        
        return len(old_exports)

    @classmethod
    def get_exports_by_type(cls, session, export_type, tenant_id=None, limit=50):
        """Get exports by type"""
        query = session.query(cls).filter(cls.export_type == export_type)
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()

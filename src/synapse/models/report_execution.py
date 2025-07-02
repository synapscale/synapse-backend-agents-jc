"""Report Execution Model"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class ReportExecution(Base):
    """Report execution tracking and results"""
    
    __tablename__ = "report_executions"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.custom_reports.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.users.id"), nullable=True)
    execution_type = Column(String(20), nullable=False)  # manual, scheduled, api
    parameters = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False)  # running, completed, failed
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    rows_processed = Column(Integer, nullable=True)
    data_size_bytes = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    report = relationship("CustomReport", back_populates="executions")
    user = relationship("User", back_populates="report_executions")
    tenant = relationship("Tenant", back_populates="report_executions")

    def __str__(self):
        return f"ReportExecution(report_id={self.report_id}, status={self.status})"

    @property
    def is_completed(self):
        """Check if execution is completed"""
        return self.status == "completed"

    @property
    def is_running(self):
        """Check if execution is still running"""
        return self.status == "running"

    @property
    def is_failed(self):
        """Check if execution failed"""
        return self.status == "failed"

    @property
    def duration_seconds(self):
        """Get execution duration in seconds"""
        if self.execution_time_ms:
            return self.execution_time_ms / 1000
        elif self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def formatted_duration(self):
        """Get human-readable duration"""
        duration = self.duration_seconds
        if not duration:
            return "N/A"
        
        if duration < 1:
            return f"{duration*1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.1f}s"
        else:
            return f"{duration/60:.1f}m"

    @property
    def data_size_display(self):
        """Get human-readable data size"""
        if not self.data_size_bytes:
            return "N/A"
        
        size = self.data_size_bytes
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def mark_completed(self, result_data=None, rows_processed=None, data_size_bytes=None):
        """Mark execution as completed"""
        self.status = "completed"
        self.completed_at = func.now()
        
        if result_data is not None:
            self.result_data = result_data
        if rows_processed is not None:
            self.rows_processed = rows_processed
        if data_size_bytes is not None:
            self.data_size_bytes = data_size_bytes
        
        # Calculate execution time
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.execution_time_ms = int(duration * 1000)
        
        self.updated_at = func.current_timestamp()

    def mark_failed(self, error_message=None):
        """Mark execution as failed"""
        self.status = "failed"
        self.completed_at = func.now()
        
        if error_message:
            self.error_message = error_message
        
        # Calculate execution time even for failed executions
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.execution_time_ms = int(duration * 1000)
        
        self.updated_at = func.current_timestamp()

    @classmethod
    def start_execution(cls, session, report_id, execution_type="manual", 
                       user_id=None, parameters=None, tenant_id=None):
        """Start a new report execution"""
        execution = cls(
            report_id=report_id,
            user_id=user_id,
            execution_type=execution_type,
            parameters=parameters,
            status="running",
            started_at=func.now(),
            tenant_id=tenant_id
        )
        
        session.add(execution)
        return execution

    @classmethod
    def get_report_executions(cls, session, report_id, limit=50):
        """Get executions for a specific report"""
        return session.query(cls).filter(
            cls.report_id == report_id
        ).order_by(cls.started_at.desc()).limit(limit).all()

    @classmethod
    def get_user_executions(cls, session, user_id, limit=50, status=None):
        """Get executions for a user"""
        query = session.query(cls).filter(cls.user_id == user_id)
        
        if status:
            query = query.filter(cls.status == status)
        
        return query.order_by(cls.started_at.desc()).limit(limit).all()

    @classmethod
    def get_execution_stats(cls, session, report_id=None, tenant_id=None, days=30):
        """Get execution statistics"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = session.query(cls).filter(cls.started_at >= cutoff_date)
        
        if report_id:
            query = query.filter(cls.report_id == report_id)
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        executions = query.all()
        
        stats = {
            "total": len(executions),
            "completed": len([e for e in executions if e.status == "completed"]),
            "failed": len([e for e in executions if e.status == "failed"]),
            "running": len([e for e in executions if e.status == "running"]),
            "avg_duration": 0,
            "total_rows_processed": 0
        }
        
        # Calculate averages for completed executions
        completed_executions = [e for e in executions if e.status == "completed"]
        if completed_executions:
            durations = [e.execution_time_ms for e in completed_executions if e.execution_time_ms]
            if durations:
                stats["avg_duration"] = sum(durations) / len(durations) / 1000  # Convert to seconds
            
            rows = [e.rows_processed for e in completed_executions if e.rows_processed]
            if rows:
                stats["total_rows_processed"] = sum(rows)
        
        # Calculate success rate
        if stats["total"] > 0:
            stats["success_rate"] = (stats["completed"] / stats["total"]) * 100
        else:
            stats["success_rate"] = 0
        
        return stats

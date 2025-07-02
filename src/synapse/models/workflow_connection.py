"""Workflow Connection Model"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkflowConnection(Base):
    """Connections between workflow nodes"""
    
    __tablename__ = "workflow_connections"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=False)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_nodes.id"), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflow_nodes.id"), nullable=False)
    source_port = Column(String(100), nullable=True)
    target_port = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    workflow = relationship("Workflow", back_populates="connections")
    source_node = relationship("WorkflowNode", foreign_keys=[source_node_id], back_populates="outgoing_connections")
    target_node = relationship("WorkflowNode", foreign_keys=[target_node_id], back_populates="incoming_connections")
    tenant = relationship("Tenant", back_populates="workflow_connections")

    def __str__(self):
        return f"WorkflowConnection({self.source_node_id} -> {self.target_node_id})"

    @property
    def connection_display(self):
        """Get human-readable connection display"""
        source_port = f":{self.source_port}" if self.source_port else ""
        target_port = f":{self.target_port}" if self.target_port else ""
        return f"{self.source_node_id}{source_port} -> {self.target_node_id}{target_port}"

    @property
    def has_ports(self):
        """Check if connection uses specific ports"""
        return self.source_port is not None or self.target_port is not None

    def update_ports(self, source_port=None, target_port=None):
        """Update connection ports"""
        if source_port is not None:
            self.source_port = source_port
        if target_port is not None:
            self.target_port = target_port
        self.updated_at = func.current_timestamp()

    @classmethod
    def create_connection(cls, session, workflow_id, source_node_id, target_node_id,
                         source_port=None, target_port=None, tenant_id=None):
        """Create a new workflow connection"""
        connection = cls(
            workflow_id=workflow_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            source_port=source_port,
            target_port=target_port,
            tenant_id=tenant_id,
            created_at=func.now()
        )
        
        session.add(connection)
        return connection

    @classmethod
    def get_workflow_connections(cls, session, workflow_id):
        """Get all connections for a workflow"""
        return session.query(cls).filter(cls.workflow_id == workflow_id).all()

    @classmethod
    def get_node_connections(cls, session, node_id):
        """Get all connections involving a specific node"""
        return session.query(cls).filter(
            (cls.source_node_id == node_id) |
            (cls.target_node_id == node_id)
        ).all()

    @classmethod
    def get_outgoing_connections(cls, session, node_id):
        """Get outgoing connections from a node"""
        return session.query(cls).filter(cls.source_node_id == node_id).all()

    @classmethod
    def get_incoming_connections(cls, session, node_id):
        """Get incoming connections to a node"""
        return session.query(cls).filter(cls.target_node_id == node_id).all()

    @classmethod
    def validate_connection(cls, session, workflow_id, source_node_id, target_node_id):
        """Validate if a connection can be created (no cycles, etc.)"""
        # Check if connection already exists
        existing = session.query(cls).filter(
            cls.workflow_id == workflow_id,
            cls.source_node_id == source_node_id,
            cls.target_node_id == target_node_id
        ).first()
        
        if existing:
            return False, "Connection already exists"
        
        # Check for direct self-connection
        if source_node_id == target_node_id:
            return False, "Cannot connect node to itself"
        
        # Check for cycles (simplified check)
        # This is a basic cycle detection - in production, you'd want more sophisticated cycle detection
        paths = cls._find_paths(session, workflow_id, target_node_id, source_node_id)
        if paths:
            return False, "Connection would create a cycle"
        
        return True, "Connection is valid"

    @classmethod
    def _find_paths(cls, session, workflow_id, start_node, end_node, visited=None, max_depth=10):
        """Find paths between nodes to detect cycles"""
        if visited is None:
            visited = set()
        
        if max_depth <= 0 or start_node in visited:
            return []
        
        if start_node == end_node:
            return [[start_node]]
        
        visited.add(start_node)
        paths = []
        
        # Get outgoing connections from start_node
        connections = session.query(cls).filter(
            cls.workflow_id == workflow_id,
            cls.source_node_id == start_node
        ).all()
        
        for conn in connections:
            sub_paths = cls._find_paths(session, workflow_id, conn.target_node_id, 
                                      end_node, visited.copy(), max_depth - 1)
            for path in sub_paths:
                paths.append([start_node] + path)
        
        return paths

    @classmethod
    def delete_node_connections(cls, session, node_id):
        """Delete all connections involving a node"""
        connections = cls.get_node_connections(session, node_id)
        for connection in connections:
            session.delete(connection)
        return len(connections)

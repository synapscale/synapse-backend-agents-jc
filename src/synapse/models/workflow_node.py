"""Workflow Node Model"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class WorkflowNode(Base):
    """Nodes within workflows"""
    
    __tablename__ = "workflow_nodes"
    __table_args__ = {"schema": "synapscale_db"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.workflows.id"), nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.nodes.id"), nullable=False)
    instance_name = Column(String(200), nullable=True)
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    configuration = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    workflow = relationship("Workflow", back_populates="workflow_nodes")
    # node = relationship("Node", back_populates="workflow_instances") # REMOVIDO - sem FK
    tenant = relationship("Tenant", back_populates="workflow_nodes")
    outgoing_connections = relationship("WorkflowConnection", foreign_keys="WorkflowConnection.source_node_id", back_populates="source_node")
    incoming_connections = relationship("WorkflowConnection", foreign_keys="WorkflowConnection.target_node_id", back_populates="target_node")

    def __str__(self):
        display_name = self.instance_name or f"Node-{self.node_id}"
        return f"WorkflowNode({display_name} at {self.position_x},{self.position_y})"

    @property
    def display_name(self):
        """Get display name for the node"""
        return self.instance_name or f"Node-{str(self.node_id)[:8]}"

    @property
    def position(self):
        """Get position as tuple"""
        return (self.position_x, self.position_y)

    @property
    def has_configuration(self):
        """Check if node has custom configuration"""
        return self.configuration is not None and bool(self.configuration)

    @property
    def input_count(self):
        """Get count of incoming connections"""
        return len(self.incoming_connections) if self.incoming_connections else 0

    @property
    def output_count(self):
        """Get count of outgoing connections"""
        return len(self.outgoing_connections) if self.outgoing_connections else 0

    @property
    def is_start_node(self):
        """Check if this is a start node (no incoming connections)"""
        return self.input_count == 0

    @property
    def is_end_node(self):
        """Check if this is an end node (no outgoing connections)"""
        return self.output_count == 0

    def move_to(self, x, y):
        """Move node to new position"""
        self.position_x = x
        self.position_y = y
        self.updated_at = func.current_timestamp()

    def update_configuration(self, config):
        """Update node configuration"""
        self.configuration = config
        self.updated_at = func.current_timestamp()

    def get_config_value(self, key, default=None):
        """Get configuration value"""
        if not self.configuration:
            return default
        return self.configuration.get(key, default)

    def set_config_value(self, key, value):
        """Set configuration value"""
        if not self.configuration:
            self.configuration = {}
        self.configuration[key] = value
        self.updated_at = func.current_timestamp()

    def rename(self, new_name):
        """Rename the node instance"""
        self.instance_name = new_name
        self.updated_at = func.current_timestamp()

    def get_connected_nodes(self, direction="both"):
        """Get connected nodes"""
        connected = []
        
        if direction in ["both", "incoming"]:
            for conn in self.incoming_connections:
                connected.append(conn.source_node)
        
        if direction in ["both", "outgoing"]:
            for conn in self.outgoing_connections:
                connected.append(conn.target_node)
        
        return connected

    def get_execution_order(self):
        """Calculate execution order based on connections (simplified)"""
        # This is a simplified version - in practice, you'd need topological sorting
        if self.is_start_node:
            return 0
        
        # Find the maximum order of incoming nodes + 1
        max_order = 0
        for conn in self.incoming_connections:
            source_order = conn.source_node.get_execution_order()
            max_order = max(max_order, source_order)
        
        return max_order + 1

    @classmethod
    def create_node(cls, session, workflow_id, node_id, position_x, position_y,
                   instance_name=None, configuration=None, tenant_id=None):
        """Create a new workflow node"""
        workflow_node = cls(
            workflow_id=workflow_id,
            node_id=node_id,
            instance_name=instance_name,
            position_x=position_x,
            position_y=position_y,
            configuration=configuration,
            tenant_id=tenant_id,
            created_at=func.now()
        )
        
        session.add(workflow_node)
        return workflow_node

    @classmethod
    def get_workflow_nodes(cls, session, workflow_id):
        """Get all nodes for a workflow"""
        return session.query(cls).filter(
            cls.workflow_id == workflow_id
        ).order_by(cls.position_y.asc(), cls.position_x.asc()).all()

    @classmethod
    def get_nodes_by_type(cls, session, workflow_id, node_type):
        """Get nodes of specific type in a workflow"""
        return session.query(cls).join(cls.node).filter(
            cls.workflow_id == workflow_id,
            cls.node.has(type=node_type)
        ).all()

    @classmethod
    def get_start_nodes(cls, session, workflow_id):
        """Get start nodes (nodes with no incoming connections)"""
        from synapse.models.workflow_connection import WorkflowConnection
        
        # Subquery to find nodes with incoming connections
        connected_nodes = session.query(WorkflowConnection.target_node_id).filter(
            WorkflowConnection.workflow_id == workflow_id
        ).subquery()
        
        # Find nodes not in the connected nodes list
        return session.query(cls).filter(
            cls.workflow_id == workflow_id,
            ~cls.id.in_(connected_nodes)
        ).all()

    @classmethod
    def get_end_nodes(cls, session, workflow_id):
        """Get end nodes (nodes with no outgoing connections)"""
        from synapse.models.workflow_connection import WorkflowConnection
        
        # Subquery to find nodes with outgoing connections
        source_nodes = session.query(WorkflowConnection.source_node_id).filter(
            WorkflowConnection.workflow_id == workflow_id
        ).subquery()
        
        # Find nodes not in the source nodes list
        return session.query(cls).filter(
            cls.workflow_id == workflow_id,
            ~cls.id.in_(source_nodes)
        ).all()

    @classmethod
    def get_execution_sequence(cls, session, workflow_id):
        """Get nodes in execution order"""
        nodes = cls.get_workflow_nodes(session, workflow_id)
        
        # Simple ordering by position for now
        # In practice, you'd implement proper topological sorting
        return sorted(nodes, key=lambda n: (n.get_execution_order(), n.position_y, n.position_x))

    @classmethod
    def validate_position(cls, session, workflow_id, position_x, position_y, exclude_node_id=None):
        """Validate if position is available"""
        query = session.query(cls).filter(
            cls.workflow_id == workflow_id,
            cls.position_x == position_x,
            cls.position_y == position_y
        )
        
        if exclude_node_id:
            query = query.filter(cls.id != exclude_node_id)
        
        existing = query.first()
        return existing is None

    @classmethod
    def find_available_position(cls, session, workflow_id, preferred_x=0, preferred_y=0):
        """Find an available position near the preferred location"""
        grid_size = 100  # Grid spacing
        
        # Start with preferred position
        if cls.validate_position(session, workflow_id, preferred_x, preferred_y):
            return preferred_x, preferred_y
        
        # Search in expanding rings around preferred position
        for radius in range(1, 20):  # Max search radius
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue  # Only check the perimeter of each ring
                    
                    x = preferred_x + (dx * grid_size)
                    y = preferred_y + (dy * grid_size)
                    
                    if cls.validate_position(session, workflow_id, x, y):
                        return x, y
        
        # Fallback: use timestamp-based position
        import time
        return int(time.time() % 1000) * grid_size, int(time.time() % 100) * grid_size

    @classmethod
    def get_node_statistics(cls, session, workflow_id):
        """Get statistics about nodes in workflow"""
        nodes = cls.get_workflow_nodes(session, workflow_id)
        
        if not nodes:
            return {}
        
        # Calculate bounding box
        min_x = min(node.position_x for node in nodes)
        max_x = max(node.position_x for node in nodes)
        min_y = min(node.position_y for node in nodes)
        max_y = max(node.position_y for node in nodes)
        
        # Count node types
        node_types = {}
        for node in nodes:
            if hasattr(node.node, 'type'):
                node_type = node.node.type
                node_types[node_type] = node_types.get(node_type, 0) + 1
        
        return {
            "total_nodes": len(nodes),
            "start_nodes": len(cls.get_start_nodes(session, workflow_id)),
            "end_nodes": len(cls.get_end_nodes(session, workflow_id)),
            "bounding_box": {
                "min_x": min_x, "max_x": max_x,
                "min_y": min_y, "max_y": max_y,
                "width": max_x - min_x,
                "height": max_y - min_y
            },
            "node_types": node_types
        }

"""Node Category Model"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from synapse.database import Base


class NodeCategory(Base):
    """Categories for organizing workflow nodes"""
    
    __tablename__ = "node_categories"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)  # Icon identifier or emoji
    color = Column(String(7), nullable=True)  # Hex color code
    parent_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.node_categories.id"), nullable=True)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.current_timestamp())

    # Relationships
    parent = relationship("NodeCategory", remote_side=[id], back_populates="children")
    children = relationship("NodeCategory", back_populates="parent")
    tenant = relationship("Tenant", back_populates="node_categories")
    nodes = relationship("Node", primaryjoin="NodeCategory.name == foreign(Node.category)", viewonly=True)

    def __str__(self):
        return f"NodeCategory(name={self.name}, parent={self.parent.name if self.parent else 'None'})"

    @property
    def full_path(self):
        """Get full category path"""
        path = [self.name]
        current = self.parent
        while current:
            path.append(current.name)
            current = current.parent
        return " > ".join(reversed(path))

    @property
    def depth_level(self):
        """Get depth level in hierarchy"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

    @property
    def is_root_category(self):
        """Check if this is a root category"""
        return self.parent_id is None

    @property
    def is_leaf_category(self):
        """Check if this is a leaf category (no children)"""
        return len(self.children) == 0

    @property
    def has_nodes(self):
        """Check if category has nodes"""
        return len(self.nodes) > 0 if self.nodes else False

    @property
    def node_count(self):
        """Get count of nodes in this category"""
        return len(self.nodes) if self.nodes else 0

    @property
    def total_node_count(self):
        """Get total count including child categories"""
        total = self.node_count
        for child in self.children:
            total += child.total_node_count
        return total

    def activate(self):
        """Activate the category"""
        self.is_active = True
        self.updated_at = func.current_timestamp()

    def deactivate(self):
        """Deactivate the category"""
        self.is_active = False
        self.updated_at = func.current_timestamp()

    def move_to_parent(self, new_parent_id):
        """Move category to a new parent"""
        # Validate that this wouldn't create a cycle
        if new_parent_id and self._would_create_cycle(new_parent_id):
            raise ValueError("Moving category would create a cycle")
        
        self.parent_id = new_parent_id
        self.updated_at = func.current_timestamp()

    def _would_create_cycle(self, new_parent_id):
        """Check if moving to new parent would create a cycle"""
        if new_parent_id == self.id:
            return True
        
        # Check if new_parent_id is in our descendant tree
        descendants = self.get_all_descendants()
        return any(desc.id == new_parent_id for desc in descendants)

    def get_all_descendants(self):
        """Get all descendant categories"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def get_all_ancestors(self):
        """Get all ancestor categories"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_siblings(self):
        """Get sibling categories"""
        if not self.parent:
            # Root categories
            return [cat for cat in self.parent.children if cat.id != self.id] if self.parent else []
        return [cat for cat in self.parent.children if cat.id != self.id]

    @classmethod
    def create_category(cls, session, name, description=None, parent_id=None, 
                       icon=None, color=None, tenant_id=None):
        """Create a new node category"""
        # Calculate sort order
        if parent_id:
            max_order = session.query(func.max(cls.sort_order)).filter(
                cls.parent_id == parent_id
            ).scalar() or 0
        else:
            max_order = session.query(func.max(cls.sort_order)).filter(
                cls.parent_id.is_(None)
            ).scalar() or 0
        
        category = cls(
            name=name,
            description=description,
            parent_id=parent_id,
            icon=icon,
            color=color,
            sort_order=max_order + 1,
            is_active=True,
            tenant_id=tenant_id,
            created_at=func.now()
        )
        
        session.add(category)
        return category

    @classmethod
    def get_root_categories(cls, session, tenant_id=None, active_only=True):
        """Get root categories"""
        query = session.query(cls).filter(cls.parent_id.is_(None))
        
        if active_only:
            query = query.filter(cls.is_active.is_(True))
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.sort_order.asc()).all()

    @classmethod
    def get_category_tree(cls, session, tenant_id=None, active_only=True):
        """Get complete category tree"""
        root_categories = cls.get_root_categories(session, tenant_id, active_only)
        
        def build_tree(categories):
            tree = []
            for category in categories:
                children = [child for child in category.children 
                          if not active_only or child.is_active]
                category_dict = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "icon": category.icon,
                    "color": category.color,
                    "node_count": category.node_count,
                    "children": build_tree(children) if children else []
                }
                tree.append(category_dict)
            return tree
        
        return build_tree(root_categories)

    @classmethod
    def get_category_breadcrumbs(cls, session, category_id):
        """Get breadcrumb trail for a category"""
        category = session.query(cls).filter(cls.id == category_id).first()
        if not category:
            return []
        
        breadcrumbs = []
        current = category
        while current:
            breadcrumbs.append({
                "id": current.id,
                "name": current.name
            })
            current = current.parent
        
        return list(reversed(breadcrumbs))

    @classmethod
    def search_categories(cls, session, search_term, tenant_id=None):
        """Search categories by name or description"""
        query = session.query(cls).filter(
            cls.is_active.is_(True)
        ).filter(
            cls.name.ilike(f"%{search_term}%") |
            cls.description.ilike(f"%{search_term}%")
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.order_by(cls.name.asc()).all()

    @classmethod
    def get_popular_categories(cls, session, limit=10, tenant_id=None):
        """Get categories with most nodes"""
        from synapse.models.node import Node
        
        query = session.query(cls, func.count(Node.id).label('node_count')).outerjoin(Node).filter(
            cls.is_active.is_(True)
        )
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        return query.group_by(cls.id).order_by(func.count(Node.id).desc()).limit(limit).all()

    @classmethod
    def reorder_categories(cls, session, category_ids, parent_id=None):
        """Reorder categories"""
        for index, category_id in enumerate(category_ids):
            session.query(cls).filter(cls.id == category_id).update({
                "sort_order": index + 1,
                "parent_id": parent_id,
                "updated_at": func.current_timestamp()
            })

    @classmethod
    def delete_category(cls, session, category_id, move_nodes_to=None, move_children_to=None):
        """Delete category with proper cleanup"""
        category = session.query(cls).filter(cls.id == category_id).first()
        if not category:
            return False
        
        # Handle child categories
        if category.children:
            if move_children_to:
                for child in category.children:
                    child.parent_id = move_children_to
            else:
                # Move children to category's parent
                for child in category.children:
                    child.parent_id = category.parent_id
        
        # Handle nodes in this category
        if category.nodes:
            if move_nodes_to:
                for node in category.nodes:
                    node.category_id = move_nodes_to
            else:
                # Set nodes to uncategorized
                for node in category.nodes:
                    node.category_id = None
        
        session.delete(category)
        return True

    @classmethod
    def get_category_statistics(cls, session, tenant_id=None):
        """Get category usage statistics"""
        query = session.query(cls).filter(cls.is_active.is_(True))
        
        if tenant_id:
            query = query.filter(cls.tenant_id == tenant_id)
        
        categories = query.all()
        
        stats = {
            "total_categories": len(categories),
            "root_categories": len([c for c in categories if c.is_root_category]),
            "leaf_categories": len([c for c in categories if c.is_leaf_category]),
            "max_depth": max((c.depth_level for c in categories), default=0),
            "categories_with_nodes": len([c for c in categories if c.has_nodes]),
            "total_nodes": sum(c.node_count for c in categories),
            "avg_nodes_per_category": 0
        }
        
        if stats["categories_with_nodes"] > 0:
            stats["avg_nodes_per_category"] = stats["total_nodes"] / stats["categories_with_nodes"]
        
        return stats

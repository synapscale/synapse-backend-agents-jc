"""
Modelo para hierarquia de agentes usando closure table design
ALINHADO PERFEITAMENTE COM A TABELA agent_hierarchy
"""

from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from synapse.database import Base


class AgentHierarchy(Base):
    """Model para hierarquia de agentes - ALINHADO COM agent_hierarchy TABLE (Closure Table)"""
    
    __tablename__ = "agent_hierarchy"
    __table_args__ = (
        PrimaryKeyConstraint("ancestor", "descendant"),
        {"schema": "synapscale_db", "extend_existing": True}
    )

    # Campos exatos da tabela (closure table design)
    ancestor = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    descendant = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.agents.id"), nullable=False)
    depth = Column(Integer, nullable=False)

    # Relacionamentos
    ancestor_agent = relationship("Agent", foreign_keys=[ancestor], back_populates="descendants")
    descendant_agent = relationship("Agent", foreign_keys=[descendant], back_populates="ancestors")

    def __repr__(self):
        return f"<AgentHierarchy(ancestor={self.ancestor}, descendant={self.descendant}, depth={self.depth})>"

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            "ancestor": str(self.ancestor),
            "descendant": str(self.descendant),
            "depth": self.depth,
        }

    def is_direct_parent_child(self) -> bool:
        """Verifica se é uma relação direta pai-filho"""
        return self.depth == 1

    def is_self_reference(self) -> bool:
        """Verifica se é uma autoreferência"""
        return self.depth == 0 and self.ancestor == self.descendant

    @classmethod
    def create_self_reference(cls, agent_id: str):
        """Cria autoreferência (depth 0) para um agente"""
        return cls(
            ancestor=agent_id,
            descendant=agent_id,
            depth=0
        )

    @classmethod
    def create_parent_child(cls, parent_id: str, child_id: str):
        """Cria relação direta pai-filho (depth 1)"""
        return cls(
            ancestor=parent_id,
            descendant=child_id,
            depth=1
        )

    @classmethod
    def get_children(cls, session, agent_id: str, direct_only: bool = True):
        """Retorna filhos de um agente"""
        query = session.query(cls).filter(cls.ancestor == agent_id)
        
        if direct_only:
            query = query.filter(cls.depth == 1)
        else:
            query = query.filter(cls.depth > 0)  # Exclui autoreferência
            
        return query.all()

    @classmethod
    def get_parents(cls, session, agent_id: str, direct_only: bool = True):
        """Retorna pais de um agente"""
        query = session.query(cls).filter(cls.descendant == agent_id)
        
        if direct_only:
            query = query.filter(cls.depth == 1)
        else:
            query = query.filter(cls.depth > 0)  # Exclui autoreferência
            
        return query.all()

    @classmethod
    def get_descendants(cls, session, agent_id: str, max_depth: int = None):
        """Retorna todos os descendentes de um agente"""
        query = session.query(cls).filter(
            cls.ancestor == agent_id,
            cls.depth > 0  # Exclui autoreferência
        )
        
        if max_depth:
            query = query.filter(cls.depth <= max_depth)
            
        return query.order_by(cls.depth).all()

    @classmethod
    def get_ancestors(cls, session, agent_id: str, max_depth: int = None):
        """Retorna todos os ancestrais de um agente"""
        query = session.query(cls).filter(
            cls.descendant == agent_id,
            cls.depth > 0  # Exclui autoreferência
        )
        
        if max_depth:
            query = query.filter(cls.depth <= max_depth)
            
        return query.order_by(cls.depth).all()

    @classmethod
    def add_agent_to_hierarchy(cls, session, agent_id: str, parent_id: str = None):
        """Adiciona um agente à hierarquia"""
        relationships = []
        
        # Sempre criar autoreferência
        relationships.append(cls.create_self_reference(agent_id))
        
        if parent_id:
            # Criar relação direta com o pai
            relationships.append(cls.create_parent_child(parent_id, agent_id))
            
            # Criar relações transitivas com todos os ancestrais do pai
            parent_ancestors = cls.get_ancestors(session, parent_id)
            for ancestor in parent_ancestors:
                relationships.append(cls(
                    ancestor=ancestor.ancestor,
                    descendant=agent_id,
                    depth=ancestor.depth + 1
                ))
        
        # Adicionar todas as relações
        for rel in relationships:
            session.add(rel)
            
        return relationships

    @classmethod
    def remove_agent_from_hierarchy(cls, session, agent_id: str):
        """Remove um agente da hierarquia (e todos os relacionamentos)"""
        removed_count = session.query(cls).filter(
            (cls.ancestor == agent_id) | (cls.descendant == agent_id)
        ).delete()
        
        return removed_count

    @classmethod
    def is_ancestor(cls, session, ancestor_id: str, descendant_id: str) -> bool:
        """Verifica se um agente é ancestral de outro"""
        relationship = session.query(cls).filter(
            cls.ancestor == ancestor_id,
            cls.descendant == descendant_id,
            cls.depth > 0
        ).first()
        
        return relationship is not None

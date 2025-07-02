"""
Modelo Component para Marketplace
Sistema avançado de componentes reutilizáveis - SINCRONIZADO COM BANCO REAL
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    DECIMAL,
    text,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
from synapse.database import Base
import uuid


class MarketplaceComponent(Base):
    """
    Modelo para componentes do marketplace
    Representa componentes reutilizáveis que podem ser compartilhados
    SINCRONIZADO COM ESTRUTURA REAL DO BANCO
    """

    __tablename__ = "marketplace_components"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    # Identificação básica - EXATA do banco
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    component_type = Column(String, nullable=False)
    tags = Column(ARRAY(String))  # PostgreSQL Array - tipo correto!
    price = Column(DECIMAL(10, 2), nullable=False, server_default=text("0.00"))
    is_free = Column(Boolean, nullable=False, server_default=text("true"))
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(String, nullable=False, server_default=text("'1.0.0'"))
    content = Column(Text)
    component_metadata = Column(Text)  # Campo exato do banco
    downloads_count = Column(Integer, nullable=False, server_default=text("0"))
    rating_average = Column(Float, nullable=False)  # Única definição!
    rating_count = Column(Integer, nullable=False)  # Única definição!
    is_featured = Column(Boolean, nullable=False, server_default=text("false"))
    is_approved = Column(Boolean, nullable=False, server_default=text("false"))
    status = Column(String, nullable=False, server_default=text("'pending'"))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Campos adicionais - EXATOS do banco
    title = Column(String, nullable=False)
    short_description = Column(String)
    subcategory = Column(String)
    organization = Column(String)
    configuration_schema = Column(JSONB)
    dependencies = Column(JSONB)
    compatibility = Column(JSONB)
    documentation = Column(Text)
    readme = Column(Text)
    changelog = Column(Text)
    examples = Column(JSONB)
    icon_url = Column(String)
    screenshots = Column(JSONB)
    demo_url = Column(String)
    video_url = Column(String)
    currency = Column(String)
    license_type = Column(String)
    install_count = Column(Integer, nullable=False)
    view_count = Column(Integer, nullable=False)
    like_count = Column(Integer, nullable=False)
    is_verified = Column(Boolean, nullable=False)
    moderation_notes = Column(Text)
    keywords = Column(JSONB)
    search_vector = Column(Text)
    popularity_score = Column(Float, nullable=False)
    published_at = Column(DateTime(timezone=True))
    last_download_at = Column(DateTime(timezone=True))
    
    # Campo OBRIGATÓRIO presente no banco!
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"))

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="marketplace_components")
    author = relationship("User", back_populates="marketplace_components")
    ratings = relationship(
        "ComponentRating", back_populates="component", cascade="all, delete-orphan"
    )
    downloads = relationship(
        "ComponentDownload", back_populates="component", cascade="all, delete-orphan"
    )
    purchases = relationship(
        "ComponentPurchase", back_populates="component", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MarketplaceComponent(id={self.id}, name='{self.name}', version='{self.version}')>"

    @property
    def full_name(self):
        """Nome completo do componente"""
        return f"{self.name}@{self.version}"

    @property
    def is_premium(self):
        """Verifica se é um componente premium"""
        return not self.is_free and self.price > 0

    @property
    def rating_stars(self):
        """Retorna rating em formato de estrelas (0-5)"""
        return round(float(self.rating_average), 1)


class ComponentRating(Base):
    """
    Modelo para avaliações de componentes
    SINCRONIZADO COM ESTRUTURA REAL DO BANCO
    """

    __tablename__ = "component_ratings"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.marketplace_components.id"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
    )

    # Avaliação principal
    rating = Column(Integer, nullable=False)
    title = Column(String)
    review = Column(Text)

    # Aspectos específicos (1-5)
    ease_of_use = Column(Integer)
    documentation_quality = Column(Integer)
    performance = Column(Integer)
    reliability = Column(Integer)
    support_quality = Column(Integer)

    # Contexto
    version_used = Column(String)
    use_case = Column(String)
    experience_level = Column(String)

    # Interação
    helpful_count = Column(Integer, nullable=False)
    reported_count = Column(Integer, nullable=False)

    # Status
    is_verified_purchase = Column(Boolean, nullable=False)
    is_featured = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    
    # Campo obrigatório do banco
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"))

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="component_ratings")
    component = relationship("MarketplaceComponent", back_populates="ratings")
    user = relationship("User")

    def __repr__(self):
        return f"<ComponentRating(id={self.id}, component_id={self.component_id}, rating={self.rating})>"


class ComponentDownload(Base):
    """
    Modelo para downloads de componentes
    SINCRONIZADO COM ESTRUTURA REAL DO BANCO
    """

    __tablename__ = "component_downloads"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.marketplace_components.id"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
    )

    # Informações do download
    version = Column(String, nullable=False)
    download_type = Column(String, nullable=False)

    # Contexto
    ip_address = Column(String)
    user_agent = Column(String)
    referrer = Column(String)

    # Status
    status = Column(String, nullable=False)
    file_size = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    # Campo obrigatório do banco
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"))

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="component_downloads")
    component = relationship("MarketplaceComponent", back_populates="downloads")
    user = relationship("User")

    def __repr__(self):
        return f"<ComponentDownload(id={self.id}, component_id={self.component_id}, status='{self.status}')>"


class ComponentPurchase(Base):
    """
    Modelo para compras de componentes premium
    SINCRONIZADO COM ESTRUTURA REAL DO BANCO
    """

    __tablename__ = "component_purchases"
    __table_args__ = {"schema": "synapscale_db", "extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.marketplace_components.id"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("synapscale_db.users.id"),
        nullable=False,
    )

    # Informações da compra - EXATAS do banco
    amount = Column(Float, nullable=False)  # double precision
    currency = Column(String, nullable=False)
    payment_method = Column(String)

    # Processamento
    transaction_id = Column(String, nullable=False)
    payment_provider = Column(String)
    provider_transaction_id = Column(String)

    # Status
    status = Column(String, nullable=False)

    # Licença
    license_key = Column(String)
    license_expires_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    # Campo obrigatório do banco
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("synapscale_db.tenants.id"))

    # Relacionamentos
    tenant = relationship("Tenant", back_populates="component_purchases")
    component = relationship("MarketplaceComponent", back_populates="purchases")
    user = relationship("User")

    def __repr__(self):
        return f"<ComponentPurchase(id={self.id}, component_id={self.component_id}, amount={self.amount}, status='{self.status}')>"

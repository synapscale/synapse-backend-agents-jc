"""
Schemas Pydantic para Marketplace
Criado por José - O melhor Full Stack do mundo
Validação e serialização para marketplace
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class ComponentType(str, Enum):
    WORKFLOW_TEMPLATE = "workflow_template"
    NODE_COMPONENT = "node_component"
    INTEGRATION = "integration"
    PLUGIN = "plugin"
    THEME = "theme"
    WIDGET = "widget"

class ComponentCategory(str, Enum):
    AI_ML = "ai_ml"
    DATA_PROCESSING = "data_processing"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    UTILITIES = "utilities"

class ComponentStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class LicenseType(str, Enum):
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    BSD_3 = "BSD-3-Clause"
    COMMERCIAL = "Commercial"
    PROPRIETARY = "Proprietary"

# ==================== BASE SCHEMAS ====================

class ComponentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=200)
    category: ComponentCategory
    subcategory: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(default_factory=list)
    organization: Optional[str] = Field(None, max_length=100)
    component_type: ComponentType
    component_data: Dict[str, Any]
    configuration_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = Field(default_factory=list)
    compatibility: Optional[Dict[str, Any]] = Field(default_factory=dict)
    documentation: Optional[str] = None
    readme: Optional[str] = None
    changelog: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    icon_url: Optional[str] = None
    screenshots: Optional[List[str]] = Field(default_factory=list)
    demo_url: Optional[str] = None
    video_url: Optional[str] = None
    is_free: bool = True
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=3)
    license_type: Optional[LicenseType] = LicenseType.MIT
    keywords: Optional[List[str]] = Field(default_factory=list)
    version: Optional[str] = Field("1.0.0", max_length=20)

    @validator('price')
    def validate_price(cls, v, values):
        if not values.get('is_free') and (v is None or v <= 0):
            raise ValueError('Componentes pagos devem ter preço maior que zero')
        return v

    @validator('tags', 'keywords')
    def validate_lists(cls, v):
        if v and len(v) > 20:
            raise ValueError('Máximo de 20 itens permitidos')
        return v

class ComponentCreate(ComponentBase):
    pass

class ComponentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=200)
    category: Optional[ComponentCategory] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    organization: Optional[str] = Field(None, max_length=100)
    component_data: Optional[Dict[str, Any]] = None
    configuration_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    compatibility: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    readme: Optional[str] = None
    changelog: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    icon_url: Optional[str] = None
    screenshots: Optional[List[str]] = None
    demo_url: Optional[str] = None
    video_url: Optional[str] = None
    is_free: Optional[bool] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    license_type: Optional[LicenseType] = None
    keywords: Optional[List[str]] = None

class ComponentResponse(ComponentBase):
    id: int
    slug: str
    author_id: int
    author_name: str
    status: ComponentStatus
    download_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    popularity_score: float = 0.0
    is_featured: bool = False
    last_download_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== SEARCH SCHEMAS ====================

class ComponentSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[ComponentCategory] = None
    component_type: Optional[ComponentType] = None
    tags: Optional[List[str]] = None
    is_free: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_price: Optional[float] = Field(None, ge=0)
    sort_by: Optional[str] = Field("popularity", pattern="^(popularity|rating|downloads|newest|price_low|price_high)$")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class ComponentSearchResponse(BaseModel):
    components: List[ComponentResponse]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool

# ==================== RATING SCHEMAS ====================

class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    review: Optional[str] = Field(None, max_length=2000)
    ease_of_use: Optional[int] = Field(None, ge=1, le=5)
    documentation_quality: Optional[int] = Field(None, ge=1, le=5)
    performance: Optional[int] = Field(None, ge=1, le=5)
    reliability: Optional[int] = Field(None, ge=1, le=5)
    support_quality: Optional[int] = Field(None, ge=1, le=5)
    version_used: Optional[str] = Field(None, max_length=20)
    use_case: Optional[str] = Field(None, max_length=500)
    experience_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced|expert)$")

class RatingCreate(RatingBase):
    component_id: int

class RatingResponse(RatingBase):
    id: int
    component_id: int
    user_id: int
    user_name: str
    is_verified_purchase: bool = False
    helpful_count: int = 0
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RatingStats(BaseModel):
    average_rating: float
    total_ratings: int
    rating_distribution: Dict[int, int]
    aspects: Dict[str, float]

# ==================== DOWNLOAD SCHEMAS ====================

class DownloadResponse(BaseModel):
    id: int
    component_id: int
    user_id: int
    version: str
    download_type: str = "manual"
    status: str = "completed"
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== PURCHASE SCHEMAS ====================

class PurchaseCreate(BaseModel):
    component_id: int
    payment_method: str = Field(..., max_length=50)
    payment_provider: str = Field(..., max_length=50)

class PurchaseResponse(BaseModel):
    id: int
    component_id: int
    user_id: int
    amount: float
    currency: str
    payment_method: str
    transaction_id: str
    provider_transaction_id: Optional[str] = None
    status: str
    license_key: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== VERSION SCHEMAS ====================

class ComponentVersionResponse(BaseModel):
    id: int
    component_id: int
    version: str
    is_latest: bool = False
    is_stable: bool = True
    component_data: Dict[str, Any]
    dependencies: List[str]
    file_hash: str
    download_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== MARKETPLACE STATS ====================

class MarketplaceStats(BaseModel):
    total_components: int
    total_downloads: int
    total_revenue: float
    average_rating: float
    active_developers: int
    categories: Dict[str, int]

# ==================== BULK OPERATIONS ====================

class BulkComponentOperation(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|suspend|feature|unfeature)$")
    component_ids: List[int] = Field(..., min_items=1, max_items=100)
    reason: Optional[str] = Field(None, max_length=500)

class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]

# ==================== ADMIN SCHEMAS ====================

class ComponentModerationResponse(BaseModel):
    id: int
    name: str
    author_name: str
    status: ComponentStatus
    submitted_at: datetime
    review_notes: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ModerationAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|request_changes)$")
    notes: Optional[str] = Field(None, max_length=1000)
    feedback: Optional[Dict[str, Any]] = None


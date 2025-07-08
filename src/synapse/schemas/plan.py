"""
Schemas for Plan - a model for managing subscription plans.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from enum import Enum


class PlanStatus(str, Enum):
    """Enum for the status of a plan."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class PlanPeriod(str, Enum):
    """Enum for the billing period of a plan."""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PlanMigrationType(str, Enum):
    """Enum for the type of plan migration."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"


class PlanBase(BaseModel):
    """Base schema for Plan attributes."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    name: str = Field(..., description="The name of the plan.")
    description: Optional[str] = Field(None, description="A detailed description of the plan.")
    plan_code: str = Field(..., description="A unique code for the plan.")
    monthly_price: Decimal = Field(..., ge=0, description="The monthly price of the plan.")
    yearly_price: Optional[Decimal] = Field(None, ge=0, description="The yearly price of the plan.")
    is_active: bool = Field(True, description="Indicates if the plan is currently active.")
    is_public: bool = Field(True, description="Indicates if the plan is visible to the public.")
    is_featured: bool = Field(False, description="Indicates if the plan is featured on the pricing page.")
    user_limit: Optional[int] = Field(None, ge=0, description="The maximum number of users allowed on this plan.")
    workspace_limit: Optional[int] = Field(None, ge=0, description="The maximum number of workspaces allowed on this plan.")
    agent_limit: Optional[int] = Field(None, ge=0, description="The maximum number of agents allowed on this plan.")
    storage_limit_gb: Optional[int] = Field(None, ge=0, description="The maximum storage allowed in GB.")
    features_config: Dict[str, Any] = Field(default_factory=dict, description="A dictionary defining the features included in this plan.")
    trial_days: Optional[int] = Field(None, ge=0, description="The number of trial days offered with this plan.")
    tenant_id: Optional[UUID] = Field(None, description="The tenant to which this plan belongs (null for global plans).")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the plan.")
    color: Optional[str] = Field(None, description="A hex color code for UI representation.")
    icon: Optional[str] = Field(None, description="An icon for UI representation.")


class PlanCreate(PlanBase):
    """Schema for creating a new Plan."""
    pass


class PlanUpdate(BaseModel):
    """Schema for updating an existing Plan. All fields are optional."""
    name: Optional[str] = Field(None, description="New name for the plan.")
    description: Optional[str] = Field(None, description="New description.")
    monthly_price: Optional[Decimal] = Field(None, ge=0, description="New monthly price.")
    yearly_price: Optional[Decimal] = Field(None, ge=0, description="New yearly price.")
    is_active: Optional[bool] = Field(None, description="New active status.")
    is_public: Optional[bool] = Field(None, description="New public status.")
    is_featured: Optional[bool] = Field(None, description="New featured status.")
    user_limit: Optional[int] = Field(None, ge=0, description="New user limit.")
    workspace_limit: Optional[int] = Field(None, ge=0, description="New workspace limit.")
    agent_limit: Optional[int] = Field(None, ge=0, description="New agent limit.")
    storage_limit_gb: Optional[int] = Field(None, ge=0, description="New storage limit.")
    features_config: Optional[Dict[str, Any]] = Field(None, description="New features configuration.")
    trial_days: Optional[int] = Field(None, ge=0, description="New trial days.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata.")
    color: Optional[str] = Field(None, description="New color.")
    icon: Optional[str] = Field(None, description="New icon.")


class PlanResponse(PlanBase):
    """Response schema for a Plan, including database-generated fields and related data."""
    id: UUID = Field(..., description="Unique identifier for the plan.")
    created_at: datetime = Field(..., description="Timestamp of when the plan was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update.")
    subscribers_count: Optional[int] = Field(None, description="The number of active subscribers to this plan.")
    revenue_monthly: Optional[Decimal] = Field(None, description="Estimated monthly revenue from this plan.")
    revenue_yearly: Optional[Decimal] = Field(None, description="Estimated yearly revenue from this plan.")
    features: Optional[List[Dict[str, Any]]] = Field(None, description="A list of detailed features included in this plan.")


class PlanListResponse(BaseModel):
    """Paginated list of Plans."""
    items: List[PlanResponse] = Field(..., description="List of plans for the current page.")
    total: int = Field(..., description="Total number of plans.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")


class PlanComparison(BaseModel):
    """Schema for comparing multiple plans."""
    model_config = ConfigDict(from_attributes=True)

    plans: List[PlanResponse] = Field(..., description="The list of plans being compared.")
    feature_comparison: Dict[str, Dict[str, Any]] = Field(..., description="A detailed comparison of features across plans.")
    limits_comparison: Dict[str, Dict[str, Any]] = Field(..., description="A detailed comparison of limits across plans.")


class PlanUsage(BaseModel):
    """Schema for tracking usage against a plan's limits."""
    model_config = ConfigDict(from_attributes=True)

    plan_id: UUID = Field(..., description="The ID of the plan.")
    subscription_id: UUID = Field(..., description="The ID of the subscription.")
    users_used: int = Field(..., ge=0, description="Number of users currently utilizing the plan.")
    workspaces_used: int = Field(..., ge=0, description="Number of workspaces currently utilizing the plan.")
    agents_used: int = Field(..., ge=0, description="Number of agents currently utilizing the plan.")
    storage_used_gb: float = Field(..., ge=0, description="Storage utilized in GB.")
    user_limit: Optional[int] = Field(None, ge=0, description="The user limit defined by the plan.")
    workspace_limit: Optional[int] = Field(None, ge=0, description="The workspace limit defined by the plan.")
    agent_limit: Optional[int] = Field(None, ge=0, description="The agent limit defined by the plan.")
    storage_limit_gb: Optional[int] = Field(None, ge=0, description="The storage limit defined by the plan.")
    users_usage_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of user limit used.")
    workspaces_usage_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of workspace limit used.")
    agents_usage_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of agent limit used.")
    storage_usage_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of storage limit used.")


class PlanRecommendation(BaseModel):
    """Schema for recommending a plan to a user."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID = Field(..., description="The ID of the user for whom the recommendation is made.")
    recommended_plan_id: UUID = Field(..., description="The ID of the recommended plan.")
    recommended_plan_name: str = Field(..., description="The name of the recommended plan.")
    reason: str = Field(..., description="The reason for the recommendation.")
    confidence_score: float = Field(..., ge=0, le=1, description="The confidence score of the recommendation (0-1).")
    usage_analysis: Dict[str, Any] = Field(..., description="An analysis of the user's current usage patterns.")
    benefits: List[str] = Field(..., description="A list of benefits the user will gain by migrating to the recommended plan.")


class PlanMigration(BaseModel):
    """Schema for initiating a plan migration for a subscription."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    from_plan_id: UUID = Field(..., description="The ID of the current plan.")
    to_plan_id: UUID = Field(..., description="The ID of the target plan.")
    subscription_id: UUID = Field(..., description="The ID of the subscription to migrate.")
    migration_type: PlanMigrationType = Field(..., description="The type of migration (immediate or scheduled).")
    scheduled_date: Optional[datetime] = Field(None, description="The date for a scheduled migration.")
    prorated_amount: Optional[Decimal] = Field(None, description="The prorated amount for the migration.")
    new_monthly_amount: Decimal = Field(..., ge=0, description="The new monthly amount after migration.")


class PlanStatistics(BaseModel):
    """Schema for aggregated plan statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_plans: int = Field(..., description="Total number of plans.")
    active_plans: int = Field(..., description="Number of active plans.")
    public_plans: int = Field(..., description="Number of public plans.")
    total_subscribers: int = Field(..., description="Total number of subscribers across all plans.")
    subscribers_by_plan: Dict[str, int] = Field(..., description="Count of subscribers per plan.")
    total_monthly_revenue: Decimal = Field(..., description="Total estimated monthly revenue from all plans.")
    total_yearly_revenue: Decimal = Field(..., description="Total estimated yearly revenue from all plans.")
    revenue_by_plan: Dict[str, Decimal] = Field(..., description="Revenue breakdown per plan.")
    monthly_growth_rate: float = Field(..., description="Monthly growth rate of subscribers.")
    churn_rate: float = Field(..., description="Overall churn rate across all plans.")


class PlanPricing(BaseModel):
    """Schema for detailed plan pricing information."""
    model_config = ConfigDict(from_attributes=True)

    plan_id: UUID = Field(..., description="The ID of the plan.")
    base_monthly_price: Decimal = Field(..., ge=0, description="The base monthly price.")
    base_yearly_price: Optional[Decimal] = Field(None, ge=0, description="The base yearly price.")
    monthly_discount_percentage: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage for monthly billing.")
    yearly_discount_percentage: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage for yearly billing.")
    final_monthly_price: Decimal = Field(..., ge=0, description="The final monthly price after discounts.")
    final_yearly_price: Optional[Decimal] = Field(None, ge=0, description="The final yearly price after discounts.")
    valid_until: Optional[datetime] = Field(None, description="The date until which this pricing is valid.")

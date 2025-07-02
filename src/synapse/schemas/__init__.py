"""
Centralized import for all Pydantic schemas.

This file re-exports schemas from their resource-specific files,
making them accessible from a single import path.
"""

# Import from resource-specific schema files
from .base import (
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)
from .auth import (
    Token,
    TokenResponse,
    UserLogin,
    UserRegister,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    PasswordChangeRequest,
    TwoFactorSetup,
    TwoFactorVerify,
    TwoFactorDisable,
    UserPreferences,
    UserProfile,
    UserStats,
    SessionInfo,
    AuthProvider,
)
from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserStatus,
)
from .tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
    TenantStatus,
)
from .workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceListResponse,
    WorkspaceType,
    WorkspaceStatus,
)
from .node import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    NodeListResponse,
    NodeType,
    NodeStatus,
)
from .workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowStatus,
)
from .agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse,
    AgentStatus,
    AgentEnvironment,
    AgentScope,
    TriggerType,
)
from .file import (
    FileCreate,
    FileUpdate,
    FileResponse,
    FileListResponse,
    FileStatus,
    ScanStatus,
)
from .rbac import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    RolePermissionCreate,
    RolePermissionResponse,
    UserPermissionCheck,
    UserPermissionResult,
)
from .audit import (
    AuditLogCreate,
    AuditLogResponse,
    AuditOperation,
    AuditSeverity,
    AuditCategory,
    AuditReport,
    SecurityAuditEvent,
    APIAuditEvent,
)
from .user_analytics import (
    UserBehaviorMetricsCreate,
    UserBehaviorMetricsResponse,
    UserInsightCreate,
    UserInsightResponse,
    PeriodType,
    InsightType,
    InsightCategory,
    InsightPriority,
    UserEngagementSummary,
    UserProductivityMetrics,
)
from .user_features import (
    UserSubscriptionCreate,
    UserSubscriptionResponse,
    UserVariableCreate,
    UserVariableResponse,
    UserVariableSecureResponse,
    SubscriptionStatus,
    BillingCycle,
    VariableCategory,
    UserSubscriptionWithPlan,
    UserSubscriptionUsage,
)

# It's recommended to eventually refactor the code to import directly
# from the specific files (e.g., from synapse.schemas.user import UserCreate)
# instead of relying on this central __init__.py.

__all__ = [
    # Base
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    # Auth
    "Token",
    "TokenResponse",
    "UserLogin",
    "UserRegister",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "EmailVerificationRequest",
    "PasswordChangeRequest",
    "TwoFactorSetup",
    "TwoFactorVerify",
    "TwoFactorDisable",
    "UserPreferences",
    "UserProfile",
    "UserStats",
    "SessionInfo",
    "AuthProvider",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "UserStatus",
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "TenantListResponse",
    "TenantStatus",
    # Workspace
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceResponse",
    "WorkspaceListResponse",
    "WorkspaceType",
    "WorkspaceStatus",
    # Node
    "NodeCreate",
    "NodeUpdate",
    "NodeResponse",
    "NodeListResponse",
    "NodeType",
    "NodeStatus",
    # Workflow
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "WorkflowListResponse",
    "WorkflowStatus",
    # Agent
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentListResponse",
    "AgentStatus",
    "AgentEnvironment",
    "AgentScope",
    "TriggerType",
    # File
    "FileCreate",
    "FileUpdate",
    "FileResponse",
    "FileListResponse",
    "FileStatus",
    "ScanStatus",
    # RBAC
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "RolePermissionCreate",
    "RolePermissionResponse",
    "UserPermissionCheck",
    "UserPermissionResult",
    # Audit
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditOperation",
    "AuditSeverity",
    "AuditCategory",
    "AuditReport",
    "SecurityAuditEvent",
    "APIAuditEvent",
    # User Analytics
    "UserBehaviorMetricsCreate",
    "UserBehaviorMetricsResponse",
    "UserInsightCreate",
    "UserInsightResponse",
    "PeriodType",
    "InsightType",
    "InsightCategory",
    "InsightPriority",
    "UserEngagementSummary",
    "UserProductivityMetrics",
    # User Features
    "UserSubscriptionCreate",
    "UserSubscriptionResponse",
    "UserVariableCreate",
    "UserVariableResponse",
    "UserVariableSecureResponse",
    "SubscriptionStatus",
    "BillingCycle",
    "VariableCategory",
    "UserSubscriptionWithPlan",
    "UserSubscriptionUsage",
]

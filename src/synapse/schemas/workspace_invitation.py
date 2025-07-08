from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class InvitationStatus(str, Enum):
    """Enum for invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REVOKED = "revoked"


class WorkspaceInvitationBase(BaseModel):
    """Base schema for WorkspaceInvitation"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    inviter_id: UUID = Field(..., description="Inviter user ID")
    invited_user_id: Optional[UUID] = Field(None, description="Invited user ID (if user exists)")
    email: EmailStr = Field(..., description="Recipient email address")
    message: Optional[str] = Field(None, description="Invitation message")
    token: str = Field(..., description="Invitation token")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING, description="Invitation status")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class WorkspaceInvitationCreate(BaseModel):
    """Schema for creating a new workspace invitation"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    email: EmailStr = Field(..., description="Recipient email address")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_in_hours: int = Field(default=168, description="Expiration time in hours (default: 7 days)")
    send_email: bool = Field(default=True, description="Whether to send invitation email")


class WorkspaceInvitationUpdate(BaseModel):
    """Schema for updating an existing workspace invitation"""
    message: Optional[str] = Field(None, description="Invitation message")
    status: Optional[InvitationStatus] = Field(None, description="Invitation status")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class WorkspaceInvitationInDB(WorkspaceInvitationBase):
    """Schema for workspace invitation in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Invitation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    responded_at: Optional[datetime] = Field(None, description="Response timestamp")


class WorkspaceInvitationResponse(WorkspaceInvitationInDB):
    """Schema for workspace invitation response"""
    inviter_name: Optional[str] = Field(None, description="Inviter name")
    inviter_email: Optional[str] = Field(None, description="Inviter email")
    workspace_name: Optional[str] = Field(None, description="Workspace name")
    is_expired: bool = Field(..., description="Whether invitation is expired")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiry")


class WorkspaceInvitationListResponse(BaseModel):
    """Schema for workspace invitation list response"""
    model_config = ConfigDict(from_attributes=True)
    
    invitations: list[WorkspaceInvitationResponse] = Field(..., description="List of invitations")
    total: int = Field(..., description="Total number of invitations")
    pending_count: int = Field(..., description="Number of pending invitations")
    accepted_count: int = Field(..., description="Number of accepted invitations")
    expired_count: int = Field(..., description="Number of expired invitations")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of invitations per page")
    pages: int = Field(..., description="Total number of pages")


class WorkspaceInvitationAccept(BaseModel):
    """Schema for accepting a workspace invitation"""
    token: str = Field(..., description="Invitation token")
    accept_message: Optional[str] = Field(None, description="Acceptance message")


class WorkspaceInvitationDecline(BaseModel):
    """Schema for declining a workspace invitation"""
    token: str = Field(..., description="Invitation token")
    decline_reason: Optional[str] = Field(None, description="Decline reason")


class WorkspaceInvitationResend(BaseModel):
    """Schema for resending a workspace invitation"""
    invitation_id: UUID = Field(..., description="Invitation ID")
    new_message: Optional[str] = Field(None, description="New invitation message")
    extend_expiry: bool = Field(default=False, description="Whether to extend expiry time")


class WorkspaceInvitationBatch(BaseModel):
    """Schema for batch invitation operations"""
    invitation_ids: list[UUID] = Field(..., description="List of invitation IDs")
    action: str = Field(..., description="Batch action (resend, cancel, etc.)")
    action_data: Optional[dict] = Field(None, description="Action-specific data")


class WorkspaceInvitationStatistics(BaseModel):
    """Schema for workspace invitation statistics"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    total_invitations: int = Field(..., description="Total invitations sent")
    pending_invitations: int = Field(..., description="Pending invitations")
    accepted_invitations: int = Field(..., description="Accepted invitations")
    declined_invitations: int = Field(..., description="Declined invitations")
    expired_invitations: int = Field(..., description="Expired invitations")
    acceptance_rate: float = Field(..., description="Acceptance rate percentage")
    average_response_time_hours: Optional[float] = Field(None, description="Average response time in hours")
    recent_invitations: list[WorkspaceInvitationResponse] = Field(..., description="Recent invitations")


class WorkspaceInvitationBulkCreate(BaseModel):
    """Schema for bulk invitation creation"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    emails: list[EmailStr] = Field(..., description="List of email addresses")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_in_hours: int = Field(default=168, description="Expiration time in hours")
    send_emails: bool = Field(default=True, description="Whether to send invitation emails")


class WorkspaceInvitationBulkCreateResponse(BaseModel):
    """Schema for bulk invitation creation response"""
    total_sent: int = Field(..., description="Total invitations sent")
    successful: int = Field(..., description="Successful invitations")
    failed: int = Field(..., description="Failed invitations")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    invitation_ids: list[UUID] = Field(..., description="Created invitation IDs")


class WorkspaceInvitationFilter(BaseModel):
    """Schema for invitation filtering"""
    workspace_id: Optional[UUID] = Field(None, description="Filter by workspace")
    inviter_id: Optional[UUID] = Field(None, description="Filter by inviter")
    status: Optional[InvitationStatus] = Field(None, description="Filter by status")
    email: Optional[str] = Field(None, description="Filter by email")
    date_range: Optional[dict] = Field(None, description="Date range filter")
    is_expired: Optional[bool] = Field(None, description="Filter by expiry status")


class WorkspaceInvitationExport(BaseModel):
    """Schema for invitation export"""
    workspace_id: UUID = Field(..., description="Workspace ID")
    filters: Optional[WorkspaceInvitationFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_personal_data: bool = Field(default=False, description="Include personal data")
    date_range: Optional[dict] = Field(None, description="Date range for export")

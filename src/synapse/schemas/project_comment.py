from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class CommentContentType(str, Enum):
    """Enum for comment content types"""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    RICH_TEXT = "rich_text"
    CODE = "code"
    MENTION = "mention"
    ATTACHMENT = "attachment"


class CommentStatus(str, Enum):
    """Enum for comment status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectCommentBase(BaseModel):
    """Base schema for ProjectComment"""
    project_id: UUID = Field(..., description="Project ID")
    user_id: UUID = Field(..., description="User ID")
    parent_id: Optional[UUID] = Field(None, description="Parent comment ID for replies")
    content: str = Field(..., description="Comment content")
    content_type: CommentContentType = Field(default=CommentContentType.TEXT, description="Content type")
    node_id: Optional[str] = Field(None, description="Related node ID")
    position_x: Optional[float] = Field(None, description="X coordinate position")
    position_y: Optional[float] = Field(None, description="Y coordinate position")
    is_resolved: bool = Field(default=False, description="Whether comment is resolved")
    is_edited: bool = Field(default=False, description="Whether comment has been edited")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID")


class ProjectCommentCreate(ProjectCommentBase):
    """Schema for creating a new project comment"""
    pass


class ProjectCommentUpdate(BaseModel):
    """Schema for updating an existing project comment"""
    content: Optional[str] = Field(None, description="Comment content")
    content_type: Optional[CommentContentType] = Field(None, description="Content type")
    node_id: Optional[str] = Field(None, description="Related node ID")
    position_x: Optional[float] = Field(None, description="X coordinate position")
    position_y: Optional[float] = Field(None, description="Y coordinate position")
    is_resolved: Optional[bool] = Field(None, description="Whether comment is resolved")
    is_edited: Optional[bool] = Field(None, description="Whether comment has been edited")


class ProjectCommentInDB(ProjectCommentBase):
    """Schema for project comment in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Comment ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")


class ProjectCommentResponse(ProjectCommentInDB):
    """Schema for project comment response"""
    replies: Optional[List["ProjectCommentResponse"]] = Field(None, description="Nested replies")
    reply_count: int = Field(default=0, description="Number of replies")
    author_name: Optional[str] = Field(None, description="Author name")
    author_avatar: Optional[str] = Field(None, description="Author avatar URL")


class ProjectCommentListResponse(BaseModel):
    """Schema for project comment list response"""
    model_config = ConfigDict(from_attributes=True)
    
    comments: List[ProjectCommentResponse] = Field(..., description="List of comments")
    total: int = Field(..., description="Total number of comments")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of comments per page")
    pages: int = Field(..., description="Total number of pages")


class ProjectCommentThread(BaseModel):
    """Schema for comment thread"""
    root_comment: ProjectCommentResponse = Field(..., description="Root comment")
    replies: List[ProjectCommentResponse] = Field(..., description="All replies in thread")
    participants: List[str] = Field(..., description="Thread participants")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    is_active: bool = Field(..., description="Whether thread is active")


class ProjectCommentStatistics(BaseModel):
    """Schema for project comment statistics"""
    project_id: UUID = Field(..., description="Project ID")
    total_comments: int = Field(..., description="Total number of comments")
    resolved_comments: int = Field(..., description="Number of resolved comments")
    active_comments: int = Field(..., description="Number of active comments")
    recent_comments: List[ProjectCommentResponse] = Field(..., description="Recent comments")
    top_commenters: List[dict] = Field(..., description="Top commenters")
    comments_by_node: dict = Field(..., description="Comments grouped by node")
    resolution_rate: float = Field(..., description="Comment resolution rate")


class ProjectCommentResolve(BaseModel):
    """Schema for resolving a comment"""
    comment_id: UUID = Field(..., description="Comment ID")
    resolution_note: Optional[str] = Field(None, description="Resolution note")
    resolve_thread: bool = Field(default=True, description="Resolve entire thread")


class ProjectCommentResolveResponse(BaseModel):
    """Schema for comment resolution response"""
    success: bool = Field(..., description="Resolution success")
    resolved_comment: ProjectCommentResponse = Field(..., description="Resolved comment")
    resolved_thread: Optional[List[ProjectCommentResponse]] = Field(None, description="Resolved thread")
    message: str = Field(..., description="Response message")


class ProjectCommentMention(BaseModel):
    """Schema for comment mentions"""
    comment_id: UUID = Field(..., description="Comment ID")
    mentioned_user_id: UUID = Field(..., description="Mentioned user ID")
    mention_type: str = Field(default="user", description="Mention type")
    position: int = Field(..., description="Position in comment")
    length: int = Field(..., description="Length of mention")


class ProjectCommentReaction(BaseModel):
    """Schema for comment reactions"""
    comment_id: UUID = Field(..., description="Comment ID")
    user_id: UUID = Field(..., description="User ID")
    reaction_type: str = Field(..., description="Reaction type (like, love, laugh, etc.)")
    created_at: datetime = Field(..., description="Reaction timestamp")


class ProjectCommentFilter(BaseModel):
    """Schema for comment filtering"""
    project_id: Optional[UUID] = Field(None, description="Filter by project")
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    node_id: Optional[str] = Field(None, description="Filter by node")
    is_resolved: Optional[bool] = Field(None, description="Filter by resolution status")
    content_type: Optional[CommentContentType] = Field(None, description="Filter by content type")
    date_range: Optional[dict] = Field(None, description="Date range filter")
    has_replies: Optional[bool] = Field(None, description="Filter by replies existence")


class ProjectCommentBatch(BaseModel):
    """Schema for batch comment operations"""
    comment_ids: List[UUID] = Field(..., description="List of comment IDs")
    action: str = Field(..., description="Batch action (resolve, archive, delete)")
    bulk_data: Optional[dict] = Field(None, description="Additional bulk operation data")


class ProjectCommentExport(BaseModel):
    """Schema for comment export"""
    project_id: UUID = Field(..., description="Project ID")
    filters: Optional[ProjectCommentFilter] = Field(None, description="Export filters")
    format: str = Field(default="csv", description="Export format")
    include_replies: bool = Field(default=True, description="Include replies in export")
    include_metadata: bool = Field(default=False, description="Include metadata in export")

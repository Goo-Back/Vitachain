# Pydantic models for Account Blocking functionality

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class AccountBlockRequest(BaseModel):
    """Request model for blocking a user account"""
    block_reason: str = Field(..., min_length=1, max_length=500, 
                              description="Reason for blocking the user account")
    duration_hours: int = Field(..., ge=1, le=8760,  # Max 1 year
                               description="Duration of block in hours")
    auto_block: bool = Field(default=False, 
                           description="Whether this is an automatic security block")
    metadata: Optional[Dict[str, Any]] = Field(default=None,
                                            description="Additional metadata for the block")

class AccountUnblockRequest(BaseModel):
    """Request model for unblocking a user account"""
    unblock_reason: str = Field(..., min_length=1, max_length=500,
                                description="Reason for unblocking the user account")

class BlockExtensionRequest(BaseModel):
    """Request model for extending a block duration"""
    additional_hours: int = Field(..., ge=1, le=8760,  # Max 1 year
                                 description="Additional hours to extend the block")
    extension_reason: str = Field(..., min_length=1, max_length=500,
                                 description="Reason for extending the block")

class BlockResponse(BaseModel):
    """Response model for block operations"""
    block_id: str = Field(..., description="ID of the created block")
    user_id: str = Field(..., description="ID of the blocked user")
    blocked_until: str = Field(..., description="ISO datetime when block expires")
    block_reason: str = Field(..., description="Reason for the block")
    auto_block: bool = Field(..., description="Whether this was an automatic block")

class UnblockResponse(BaseModel):
    """Response model for unblock operations"""
    user_id: str = Field(..., description="ID of the unblocked user")
    unblocked_at: str = Field(..., description="ISO datetime when unblocked")
    unblock_reason: str = Field(..., description="Reason for unblocking")
    previous_block_id: str = Field(..., description="ID of the block that was lifted")

class BlockExtensionResponse(BaseModel):
    """Response model for block extension operations"""
    block_id: str = Field(..., description="ID of the extended block")
    user_id: str = Field(..., description="ID of the user whose block was extended")
    new_blocked_until: str = Field(..., description="New ISO datetime when block expires")
    additional_hours: int = Field(..., description="Additional hours that were added")
    total_duration_hours: int = Field(..., description="Total block duration in hours")

class BlockStatusResponse(BaseModel):
    """Response model for block status checks"""
    is_blocked: bool = Field(..., description="Whether the user is currently blocked")
    block_reason: Optional[str] = Field(None, description="Reason for the block")
    blocked_at: Optional[str] = Field(None, description="ISO datetime when block was applied")
    blocked_until: Optional[str] = Field(None, description="ISO datetime when block expires")
    auto_block: bool = Field(default=False, description="Whether this was an automatic block")

class BlockedUserView(BaseModel):
    """View model for blocked users in admin dashboard"""
    id: str = Field(..., description="Block ID")
    user_id: str = Field(..., description="ID of the blocked user")
    block_reason: str = Field(..., description="Reason for the block")
    block_duration_hours: int = Field(..., description="Total block duration in hours")
    blocked_at: str = Field(..., description="ISO datetime when block was applied")
    blocked_until: str = Field(..., description="ISO datetime when block expires")
    auto_block: bool = Field(..., description="Whether this was an automatic block")
    time_remaining_hours: float = Field(..., description="Hours remaining until block expires")
    time_remaining_minutes: float = Field(..., description="Minutes remaining until block expires")
    user: Dict[str, Any] = Field(..., description="User details")

class BlockedUsersListResponse(BaseModel):
    """Response model for blocked users list"""
    blocks: list[BlockedUserView] = Field(..., description="List of blocked users")
    total: int = Field(..., description="Total number of blocked users")
    limit: int = Field(..., description="Maximum number of users returned")
    offset: int = Field(..., description="Number of users skipped")

class BlockCleanupResponse(BaseModel):
    """Response model for block cleanup operations"""
    cleaned_blocks: int = Field(..., description="Number of blocks that were cleaned up")
    timestamp: str = Field(..., description="ISO timestamp when cleanup was performed")

# Validation validators
@validator('duration_hours', 'additional_hours')
def validate_duration_hours(cls, v):
    if v <= 0:
        raise ValueError('Duration must be positive')
    return v

@validator('block_reason', 'unblock_reason', 'extension_reason')
def validate_text_fields(cls, v):
    if not v or not v.strip():
        raise ValueError('Text fields cannot be empty')
    return v.strip()

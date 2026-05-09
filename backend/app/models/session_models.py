"""
Session management models and schemas for VitaChain
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class SessionCreateRequest(BaseModel):
    """Request model for creating a new session"""
    user_id: str = Field(..., description="User UUID")
    session_id: str = Field(..., description="JWT jti claim")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device fingerprint and details")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Browser user agent string")


class LogoutRequest(BaseModel):
    """Request model for user logout"""
    logout_all: bool = Field(False, description="Whether to logout from all devices")
    session_id: Optional[str] = Field(None, description="Specific session ID to logout (if not all)")


class LogoutResponse(BaseModel):
    """Response model for logout operations"""
    success: bool = Field(..., description="Whether logout was successful")
    message: str = Field(..., description="Logout confirmation message")
    sessions_terminated: int = Field(0, description="Number of sessions terminated")


class ForceLogoutRequest(BaseModel):
    """Request model for admin force logout"""
    reason: str = Field(..., description="Reason for force logout")
    notify_user: bool = Field(True, description="Whether to notify the user")


class SessionInfo(BaseModel):
    """Response model for session information"""
    id: str = Field(..., description="Session database ID")
    session_id: str = Field(..., description="JWT jti claim")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    created_at: datetime = Field(..., description="Session creation time")
    last_accessed: datetime = Field(..., description="Last access time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_active: bool = Field(..., description="Whether session is currently active")
    logout_reason: Optional[str] = Field(None, description="Reason for logout")
    logged_out_at: Optional[datetime] = Field(None, description="Logout timestamp")
    force_logout: bool = Field(False, description="Whether session was force-logged out")

    @validator('device_info', pre=True)
    def parse_device_info(cls, v):
        """Parse device_info from JSON string if needed"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}


class UserSessionsResponse(BaseModel):
    """Response model for user sessions list"""
    sessions: List[SessionInfo] = Field(..., description="List of active sessions")
    total: int = Field(..., description="Total number of sessions")


class SessionValidationRequest(BaseModel):
    """Request model for session validation"""
    session_id: str = Field(..., description="JWT jti claim")
    user_id: str = Field(..., description="User UUID from JWT")


class SessionValidationResponse(BaseModel):
    """Response model for session validation"""
    valid: bool = Field(..., description="Whether session is valid")
    session_info: Optional[SessionInfo] = Field(None, description="Session details if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")


class SessionCleanupResponse(BaseModel):
    """Response model for session cleanup operations"""
    cleaned_sessions: int = Field(..., description="Number of sessions cleaned up")
    timestamp: datetime = Field(..., description="Cleanup operation timestamp")


# Error response models
class SessionNotFoundResponse(BaseModel):
    """Response when session is not found"""
    error: str = Field("Session not found", description="Error message")
    code: str = Field("SESSION_NOT_FOUND", description="Error code")


class SessionExpiredResponse(BaseModel):
    """Response when session is expired"""
    error: str = Field("Session has expired", description="Error message")
    code: str = Field("SESSION_EXPIRED", description="Error code")


class UnauthorizedSessionResponse(BaseModel):
    """Response for unauthorized session access"""
    error: str = Field("Unauthorized session access", description="Error message")
    code: str = Field("UNAUTHORIZED_SESSION", description="Error code")


class SessionLimitExceededResponse(BaseModel):
    """Response when session limit is exceeded"""
    error: str = Field("Maximum sessions exceeded", description="Error message")
    code: str = Field("SESSION_LIMIT_EXCEEDED", description="Error code")
    max_sessions: int = Field(5, description="Maximum allowed sessions")

# Security Schemas for VitaChain
# Pydantic models for security monitoring and suspicious login detection

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class SecurityEventType(str, Enum):
    FAILED_LOGIN = "failed_login"
    LOCATION_ANOMALY = "location_anomaly"
    DEVICE_ANOMALY = "device_anomaly"
    VELOCITY_ANOMALY = "velocity_anomaly"

class SecuritySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LoginAnalysisRequest(BaseModel):
    """Request for login analysis"""
    user_id: str
    ip_address: str
    user_agent: str
    success: bool = False
    location_data: Optional[Dict[str, Any]] = None

class LoginAnalysisResponse(BaseModel):
    """Response from login analysis"""
    timestamp: datetime
    user_id: str
    ip_address: str
    user_agent: str
    success: bool
    risk_score: int = Field(ge=0, le=100, description="Risk score from 0-100")
    anomalies: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    should_block: bool = False
    should_notify: bool = False

class SecurityEventCreate(BaseModel):
    """Create security event"""
    event_type: SecurityEventType
    severity: SecuritySeverity
    user_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityAlertCreate(BaseModel):
    """Create security alert"""
    alert_type: str
    severity: SecuritySeverity
    title: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    requires_action: bool = True
    metadata: Optional[Dict[str, Any]] = None

class SecurityAlertResponse(BaseModel):
    """Security alert response"""
    id: str
    alert_type: str
    severity: SecuritySeverity
    title: str
    description: Optional[str]
    user_id: Optional[str]
    ip_address: Optional[str]
    requires_action: bool
    is_read: bool = False
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class IPBlockRequest(BaseModel):
    """Request to block IP address"""
    duration_hours: int = Field(ge=1, le=24, description="Block duration in hours")
    reason: str = Field(..., description="Reason for blocking IP")

class IPBlockResponse(BaseModel):
    """Response from IP blocking"""
    ip_address: str
    blocked: bool
    blocked_until: datetime
    reason: str

class IPReputationResponse(BaseModel):
    """IP reputation response"""
    ip_address: str
    reputation_score: int = Field(ge=0, le=100, description="Reputation score from 0-100")
    reputation: str  # good, suspicious, poor
    failed_attempts: int
    successful_logins: int
    is_blocked: bool
    last_activity: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityMetricsResponse(BaseModel):
    """Security metrics for admin dashboard"""
    failed_auth_attempts_24h: int
    rate_violations_24h: int
    suspicious_patterns_24h: int
    currently_blocked_ips: int
    active_failed_auth_sessions: int
    active_rate_violations: int
    top_suspicious_patterns: Dict[str, int]
    recent_alerts: List[SecurityAlertResponse] = []

class AlertResolutionRequest(BaseModel):
    """Request to resolve security alert"""
    action_taken: str = Field(..., description="Action taken to resolve alert")
    notes: Optional[str] = None

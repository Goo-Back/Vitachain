# Security API Routes for VitaChain
# Provides endpoints for security monitoring, alerts, and IP management

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request
from supabase import create_client, Client

from app.core.database import get_supabase_client
from app.core.security_monitoring import security_monitor
from app.core.geo_ip_service import geo_ip_service
from app.models.security_schemas import (
    LoginAnalysisRequest, LoginAnalysisResponse, SecurityEventCreate,
    SecurityAlertResponse, SecurityMetricsResponse, IPBlockRequest, IPBlockResponse,
    IPReputationResponse, AlertResolutionRequest
)
from app.models.schemas import ValidationErrorResponse, RateLimitResponse
from app.core.logging import logger

router = APIRouter(prefix="/api/security", tags=["security"])

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_current_user(request: Request) -> dict:
    """Get current user from JWT token"""
    # This would use the existing JWT validation from security.py
    # For now, return None to avoid circular imports
    return None

@router.post("/analyze-login", response_model=LoginAnalysisResponse)
async def analyze_login_attempt(
    request: LoginAnalysisRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Analyze login attempt for suspicious patterns
    Called during login process before authentication succeeds
    """
    try:
        # Get IP geolocation data
        location_data = await geo_ip_service.get_ip_location(request.ip_address)
        
        # Analyze login attempt
        analysis_result = security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success,
            location_data=location_data
        )
        
        # Update user login patterns if successful
        if request.success:
            security_monitor.update_user_login_pattern(
                user_id=request.user_id,
                ip=request.ip_address,
                user_agent=request.user_agent,
                location_data=location_data
            )
        
        # Log security event if suspicious
        if analysis_result["anomalies"] or analysis_result["risk_score"] > 20:
            await _log_security_event(supabase, {
                "event_type": "login_analysis",
                "severity": "high" if analysis_result["risk_score"] >= 50 else "medium",
                "user_id": request.user_id,
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
                "device_fingerprint": security_monitor._generate_device_fingerprint(request.user_agent),
                "location_country": location_data.get("country_code") if location_data else None,
                "location_city": location_data.get("city") if location_data else None,
                "metadata": {
                    "analysis_result": analysis_result,
                    "success": request.success
                }
            })
        
        # Create security alert if needed
        if analysis_result["should_notify"] or analysis_result["should_block"]:
            await _create_security_alert(supabase, {
                "alert_type": "suspicious_login",
                "severity": "high" if analysis_result["risk_score"] >= 50 else "medium",
                "title": "Suspicious Login Activity Detected",
                "description": _generate_alert_description(analysis_result),
                "user_id": request.user_id,
                "ip_address": request.ip_address,
                "metadata": analysis_result
            })
        
        # Block IP if necessary
        if analysis_result["should_block"]:
            security_monitor.block_ip_temporarily(
                ip=request.ip_address,
                hours=1
            )
            logger.warning("ip_blocked_after_analysis", 
                       ip=request.ip_address,
                       risk_score=analysis_result["risk_score"],
                       reason="suspicious_login_pattern")
        
        return LoginAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error("login_analysis_error", 
                   error=str(e),
                   user_id=request.user_id,
                   ip=request.ip_address)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ANALYSIS_ERROR",
                "message": "Failed to analyze login attempt"
            }
        )

@router.get("/dashboard/metrics", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get security metrics for admin dashboard
    Requires ADMIN role
    """
    try:
        # Check admin permissions
        if not current_user or current_user.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Admin access required"
                }
            )
        
        # Get security metrics from monitor
        metrics = security_monitor.get_security_metrics()
        
        # Get recent alerts from database
        recent_alerts = await _get_recent_alerts(supabase, limit=10)
        
        return SecurityMetricsResponse(
            failed_auth_attempts_24h=metrics["failed_auth_attempts_24h"],
            rate_violations_24h=metrics["rate_violations_24h"],
            suspicious_patterns_24h=metrics["suspicious_patterns_24h"],
            currently_blocked_ips=metrics["currently_blocked_ips"],
            active_failed_auth_sessions=metrics["active_failed_auth_sessions"],
            active_rate_violations=metrics["active_rate_violations"],
            top_suspicious_patterns=metrics["top_suspicious_patterns"],
            recent_alerts=recent_alerts
        )
        
    except Exception as e:
        logger.error("security_metrics_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "METRICS_ERROR",
                "message": "Failed to retrieve security metrics"
            }
        )

@router.get("/alerts", response_model=List[SecurityAlertResponse])
async def get_security_alerts(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    limit: int = 50,
    offset: int = 0
):
    """
    Get security alerts for admin or user
    Filtered by user role
    """
    try:
        # Get alerts based on user role
        if current_user.get("role") == "ADMIN":
            # Admins can see all alerts
            query = supabase.table("security_alerts")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
        else:
            # Users can only see their own alerts
            query = supabase.table("security_alerts")\
                .select("*")\
                .eq("user_id", current_user.get("id"))\
                .order("created_at", desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
        
        alerts = []
        for alert_data in query.data:
            alerts.append(SecurityAlertResponse(
                id=alert_data["id"],
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                title=alert_data["title"],
                description=alert_data["description"],
                user_id=alert_data.get("user_id"),
                ip_address=alert_data.get("ip_address"),
                requires_action=alert_data["requires_action"],
                is_read=alert_data["is_read"],
                created_at=alert_data["created_at"],
                metadata=alert_data.get("metadata")
            ))
        
        return alerts
        
    except Exception as e:
        logger.error("security_alerts_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ALERTS_ERROR",
                "message": "Failed to retrieve security alerts"
            }
        )

@router.post("/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    resolution: AlertResolutionRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resolve a security alert with action taken
    Requires ADMIN role
    """
    try:
        # Check admin permissions
        if not current_user or current_user.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Admin access required"
                }
            )
        
        # Update alert
        update_data = {
            "is_resolved": True,
            "resolved_by": current_user.get("id"),
            "resolved_at": datetime.utcnow().isoformat(),
            "action_taken": resolution.action_taken,
            "metadata": {"resolution_notes": resolution.notes} if resolution.notes else {}
        }
        
        result = supabase.table("security_alerts")\
            .update(update_data)\
            .eq("id", alert_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "ALERT_NOT_FOUND",
                    "message": "Security alert not found"
                }
            )
        
        logger.info("security_alert_resolved", 
                   alert_id=alert_id,
                   resolved_by=current_user.get("id"),
                   action=resolution.action_taken)
        
        return {"message": "Alert resolved successfully"}
        
    except Exception as e:
        logger.error("alert_resolution_error", 
                   alert_id=alert_id,
                   error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "RESOLUTION_ERROR",
                "message": "Failed to resolve security alert"
            }
        )

@router.post("/ip/{ip_address}/block", response_model=IPBlockResponse)
async def block_ip_address(
    ip_address: str,
    block_request: IPBlockRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Manually block an IP address
    Requires ADMIN role
    """
    try:
        # Check admin permissions
        if not current_user or current_user.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Admin access required"
                }
            )
        
        # Block IP using security monitor
        security_monitor.block_ip_temporarily(
            ip=ip_address,
            hours=block_request.duration_hours
        )
        
        # Update IP reputation in database
        blocked_until = datetime.utcnow() + timedelta(hours=block_request.duration_hours)
        update_data = {
            "is_blocked": True,
            "blocked_until": blocked_until.isoformat(),
            "block_reason": block_request.reason,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("ip_reputation")\
            .update(update_data)\
            .eq("ip_address", ip_address)\
            .execute()
        
        logger.warning("ip_blocked_manually", 
                   ip=ip_address,
                   duration_hours=block_request.duration_hours,
                   reason=block_request.reason,
                   blocked_by=current_user.get("id"))
        
        return IPBlockResponse(
            ip_address=ip_address,
            blocked=True,
            blocked_until=blocked_until,
            reason=block_request.reason
        )
        
    except Exception as e:
        logger.error("ip_block_error", 
                   ip=ip_address,
                   error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "BLOCK_ERROR",
                "message": "Failed to block IP address"
            }
        )

@router.get("/ip/{ip_address}/reputation", response_model=IPReputationResponse)
async def get_ip_reputation(
    ip_address: str,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get detailed reputation data for IP address
    Requires ADMIN role
    """
    try:
        # Check admin permissions
        if not current_user or current_user.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Admin access required"
                }
            )
        
        # Get IP reputation from security monitor
        reputation_data = security_monitor.get_ip_reputation(ip_address)
        
        # Get additional data from database if available
        try:
            db_result = supabase.table("ip_reputation")\
                .select("*")\
                .eq("ip_address", ip_address)\
                .execute()
            
            if db_result.data:
                db_data = db_result.data[0]
                reputation_data.update({
                    "failed_attempts": db_data.get("failed_attempts", 0),
                    "successful_logins": db_data.get("successful_logins", 0),
                    "last_activity": db_data.get("last_activity"),
                    "metadata": db_data.get("metadata", {})
                })
        except Exception as e:
            logger.warning("ip_reputation_db_error", 
                        ip=ip_address, 
                        error=str(e))
        
        return IPReputationResponse(**reputation_data)
        
    except Exception as e:
        logger.error("ip_reputation_error", 
                   ip=ip_address,
                   error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "REPUTATION_ERROR",
                "message": "Failed to get IP reputation"
            }
        )

# Helper functions
async def _log_security_event(supabase: Client, event_data: dict):
    """Log security event to database"""
    try:
        supabase.table("security_events").insert({
            "event_type": event_data["event_type"],
            "severity": event_data["severity"],
            "user_id": event_data.get("user_id"),
            "ip_address": event_data["ip_address"],
            "user_agent": event_data.get("user_agent"),
            "device_fingerprint": event_data.get("device_fingerprint"),
            "location_country": event_data.get("location_country"),
            "location_city": event_data.get("location_city"),
            "metadata": event_data.get("metadata")
        }).execute()
    except Exception as e:
        logger.error("security_event_log_error", error=str(e))

async def _create_security_alert(supabase: Client, alert_data: dict):
    """Create security alert in database"""
    try:
        supabase.table("security_alerts").insert({
            "alert_type": alert_data["alert_type"],
            "severity": alert_data["severity"],
            "title": alert_data["title"],
            "description": alert_data["description"],
            "user_id": alert_data.get("user_id"),
            "ip_address": alert_data.get("ip_address"),
            "requires_action": alert_data.get("requires_action", True),
            "metadata": alert_data.get("metadata")
        }).execute()
    except Exception as e:
        logger.error("security_alert_create_error", error=str(e))

async def _get_recent_alerts(supabase: Client, limit: int = 10) -> List[dict]:
    """Get recent security alerts from database"""
    try:
        result = supabase.table("security_alerts")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data
    except Exception as e:
        logger.error("recent_alerts_error", error=str(e))
        return []

def _generate_alert_description(analysis_result: dict) -> str:
    """Generate alert description based on analysis results"""
    descriptions = []
    
    for anomaly in analysis_result.get("anomalies", []):
        anomaly_type = anomaly.get("type", "")
        
        if anomaly_type == "new_country":
            descriptions.append(f"Login from new country: {anomaly.get('country')}")
        elif anomaly_type == "new_device":
            descriptions.append(f"Login from new device: {anomaly.get('device')}")
        elif anomaly_type == "high_velocity":
            descriptions.append(f"Unusual login frequency: {anomaly.get('count')} logins in {anomaly.get('timeframe_minutes')} minutes")
        elif anomaly_type == "credential_stuffing":
            descriptions.append(f"Credential stuffing detected: {anomaly.get('unique_accounts')} accounts targeted")
        elif anomaly_type == "impossible_travel":
            descriptions.append(f"Impossible travel: {anomaly.get('from')} to {anomaly.get('to')} in {anomaly.get('time_diff_hours')} hours")
        else:
            descriptions.append(f"Suspicious activity: {anomaly_type}")
    
    return " | ".join(descriptions)

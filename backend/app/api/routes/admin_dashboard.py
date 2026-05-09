# Admin Dashboard Routes for VitaChain
# Provides admin dashboard endpoints for security monitoring

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from supabase import create_client, Client

from app.core.database import get_supabase_client
from app.core.security_monitoring import security_monitor
from app.models.security_schemas import SecurityMetricsResponse, SecurityAlertResponse
from app.core.logging import logger

router = APIRouter(prefix="/api/admin/dashboard", tags=["admin-dashboard"])

def get_current_user(request) -> dict:
    """Get current user from JWT token"""
    # This would use the existing JWT validation from security.py
    # For now, return None to avoid circular imports
    return None

@router.get("/security/overview", response_model=SecurityMetricsResponse)
async def get_security_overview(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30)
):
    """
    Get security overview for admin dashboard
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
        recent_alerts = await _get_recent_alerts(supabase, limit=20)
        
        # Get trend data for specified period
        trend_data = await _get_security_trends(supabase, days=days)
        
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
        logger.error("security_overview_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "OVERVIEW_ERROR",
                "message": "Failed to retrieve security overview"
            }
        )

@router.get("/security/alerts", response_model=List[SecurityAlertResponse])
async def get_dashboard_alerts(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(50, description="Number of alerts to return", ge=1, le=100),
    offset: int = Query(0, description="Number of alerts to skip", ge=0)
):
    """
    Get security alerts for admin dashboard
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
        
        # Build query
        query = supabase.table("security_alerts")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)
        
        # Apply severity filter if provided
        if severity:
            query = query.eq("severity", severity)
        
        result = query.execute()
        
        alerts = []
        for alert_data in result.data:
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
        logger.error("dashboard_alerts_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ALERTS_ERROR",
                "message": "Failed to retrieve security alerts"
            }
        )

@router.get("/security/ip-reputation")
async def get_ip_reputation_overview(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(20, description="Number of IPs to return", ge=1, le=50),
    risk_threshold: int = Query(50, description="Risk score threshold", ge=0, le=100)
):
    """
    Get IP reputation overview for admin dashboard
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
        
        # Get IPs with high risk or blocked status
        query = supabase.table("ip_reputation")\
            .select("*")\
            .or_(
                ("reputation_score", "lt", risk_threshold),
                ("is_blocked", "eq", True)
            )\
            .order("reputation_score", asc=False)\
            .limit(limit)\
            .execute()
        
        ip_list = []
        for ip_data in query.data:
            ip_list.append({
                "ip_address": ip_data["ip_address"],
                "reputation_score": ip_data["reputation_score"],
                "reputation": "good" if ip_data["reputation_score"] >= 70 else "suspicious" if ip_data["reputation_score"] >= 30 else "poor",
                "failed_attempts": ip_data["failed_attempts"],
                "successful_logins": ip_data["successful_logins"],
                "is_blocked": ip_data["is_blocked"],
                "blocked_until": ip_data.get("blocked_until"),
                "block_reason": ip_data.get("block_reason"),
                "last_activity": ip_data["last_activity"],
                "metadata": ip_data.get("metadata", {})
            })
        
        return {
            "ips": ip_list,
            "total_count": len(ip_list),
            "risk_threshold": risk_threshold
        }
        
    except Exception as e:
        logger.error("ip_reputation_overview_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "IP_REPUTATION_ERROR",
                "message": "Failed to retrieve IP reputation overview"
            }
        )

@router.get("/security/trends")
async def get_security_trends(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30)
):
    """
    Get security trends for admin dashboard
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
        
        return await _get_security_trends(supabase, days)
        
    except Exception as e:
        logger.error("security_trends_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "TRENDS_ERROR",
                "message": "Failed to retrieve security trends"
            }
        )

# Helper functions
async def _get_recent_alerts(supabase: Client, limit: int = 20) -> List[dict]:
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

async def _get_security_trends(supabase: Client, days: int) -> dict:
    """Get security trend data for specified period"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get security events trend
        events_result = supabase.table("security_events")\
            .select("event_type, severity, created_at")\
            .gte("created_at", cutoff_date.isoformat())\
            .execute()
        
        # Get alerts trend
        alerts_result = supabase.table("security_alerts")\
            .select("severity, created_at")\
            .gte("created_at", cutoff_date.isoformat())\
            .execute()
        
        # Analyze trends
        event_trends = {}
        alert_trends = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for event in events_result.data:
            event_type = event.get("event_type", "unknown")
            event_trends[event_type] = event_trends.get(event_type, 0) + 1
        
        for alert in alerts_result.data:
            severity = alert.get("severity", "low")
            if severity in alert_trends:
                alert_trends[severity] += 1
        
        return {
            "period_days": days,
            "event_trends": event_trends,
            "alert_trends": alert_trends,
            "total_events": len(events_result.data),
            "total_alerts": len(alerts_result.data)
        }
        
    except Exception as e:
        logger.error("security_trends_error", error=str(e))
        return {
            "period_days": days,
            "event_trends": {},
            "alert_trends": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "total_events": 0,
            "total_alerts": 0
        }

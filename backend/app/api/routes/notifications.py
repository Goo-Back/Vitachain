"""
Notifications API Routes
Handles alerts and notifications for VitaChain
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, List, Optional
import structlog

from app.core.config import settings
from app.core.database import get_supabase_client
from app.api.dependencies import get_current_user
from app.models.schemas import ErrorResponse

logger = structlog.get_logger("notifications_routes")

# Initialize router
router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/alerts")
async def get_alerts(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get alerts for the current user
    
    Args:
        request: FastAPI request object
        limit: Maximum number of alerts
        offset: Number of alerts to skip
        unread_only: Only return unread alerts
        current_user: Current user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        List of alerts
    """
    try:
        user_id = current_user["user_id"]
        logger.info("Fetching alerts", user_id=user_id, ip=request.client.host)
        
        # Build query
        query = supabase_client.table('alerts').select('*')
        
        # Filter by user (or get system alerts for all users)
        query = query.or_(f"user_id.eq.{user_id},user_id.is.null")
        
        if unread_only:
            query = query.eq('is_read', False)
        
        # Order and paginate
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error fetching alerts", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to fetch alerts"}
            )
        
        alerts = result.data or []
        
        # Count unread alerts
        unread_count_result = supabase_client.table('alerts').select('id', count='exact').eq('is_read', False).or_(f"user_id.eq.{user_id},user_id.is.null").execute()
        unread_count = unread_count_result.count if hasattr(unread_count_result, 'count') else 0
        
        logger.info("Alerts retrieved successfully", user_id=user_id, count=len(alerts))
        return {
            "alerts": alerts,
            "total": len(alerts),
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
            "message": "Alerts retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_alerts", user_id=current_user.get("user_id"), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve alerts"}
        )


@router.post("/alerts")
async def create_alert(
    request: Request,
    alert_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Create a new alert
    
    Args:
        request: FastAPI request object
        alert_data: Alert creation data
        current_user: Current user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Created alert data
    """
    try:
        user_id = current_user["user_id"]
        logger.info("Creating alert", user_id=user_id, ip=request.client.host)
        
        # Validate required fields
        if not alert_data.get('title') or not alert_data.get('message'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": "Title and message are required"}
            )
        
        # Prepare alert data
        new_alert = {
            'user_id': user_id,
            'type': alert_data.get('type', 'system'),
            'title': alert_data['title'],
            'message': alert_data['message'],
            'severity': alert_data.get('severity', 'medium'),
            'is_read': False,
            'metadata': alert_data.get('metadata', {}),
            'expires_at': alert_data.get('expires_at')
        }
        
        # Create alert
        result = supabase_client.table('alerts').insert(new_alert).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error creating alert", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to create alert"}
            )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "INTERNAL_ERROR", "message": "Failed to create alert"}
            )
        
        alert = result.data[0]
        
        logger.info("Alert created successfully", user_id=user_id, alert_id=alert['id'])
        return {
            "message": "Alert created successfully",
            "alert": alert
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in create_alert", user_id=current_user.get("user_id"), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to create alert"}
        )


@router.get("/stats")
async def get_notification_stats(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get notification statistics for the current user
    
    Args:
        request: FastAPI request object
        current_user: Current user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Notification statistics
    """
    try:
        user_id = current_user["user_id"]
        logger.info("Fetching notification stats", user_id=user_id, ip=request.client.host)
        
        # Get alert stats
        alert_stats = {}
        for alert_type in ['system', 'telemetry', 'order', 'reservation', 'security']:
            result = supabase_client.table('alerts').select('id', count='exact').eq('user_id', user_id).eq('type', alert_type).execute()
            alert_stats[alert_type] = result.count if hasattr(result, 'count') else 0
        
        # Get unread counts
        unread_alerts_result = supabase_client.table('alerts').select('id', count='exact').eq('user_id', user_id).eq('is_read', False).execute()
        unread_alerts = unread_alerts_result.count if hasattr(unread_alerts_result, 'count') else 0
        
        unread_notifications_result = supabase_client.table('in_app_notifications').select('id', count='exact').eq('user_id', user_id).eq('is_read', False).execute()
        unread_notifications = unread_notifications_result.count if hasattr(unread_notifications_result, 'count') else 0
        
        stats = {
            "total_alerts": sum(alert_stats.values()),
            "unread_alerts": unread_alerts,
            "alerts_by_type": alert_stats,
            "unread_in_app_notifications": unread_notifications,
            "total_unread": unread_alerts + unread_notifications
        }
        
        logger.info("Notification stats retrieved successfully", user_id=user_id)
        return {
            "stats": stats,
            "message": "Notification statistics retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_notification_stats", user_id=current_user.get("user_id"), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve notification statistics"}
        )

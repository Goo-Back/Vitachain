"""
Notifications API Routes
Handles alerts and notifications for VitaChain
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
import structlog
from jose import JWTError

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.security import JWTManager
from app.api.dependencies import get_current_user
from app.models.schemas import ErrorResponse

logger = structlog.get_logger("notifications_routes")

# Initialize router
router = APIRouter(prefix="/api/notifications", tags=["notifications"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate user ID from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User ID from JWT token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        user_info = JWTManager.validate_jwt_token(token)
        return user_info["user_id"]
    except JWTError as e:
        logger.warning("Invalid JWT token in notification request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid authentication token"}
        )
    except Exception as e:
        logger.error("Unexpected error during JWT validation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.get("/alerts")
async def get_alerts(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get alerts for the current user
    
    Args:
        request: FastAPI request object
        limit: Maximum number of alerts
        offset: Number of alerts to skip
        unread_only: Only return unread alerts
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        List of alerts
    """
    try:
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
        logger.error("Error in get_alerts", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve alerts"}
        )


@router.post("/alerts")
async def create_alert(
    request: Request,
    alert_data: Dict[str, Any],
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Create a new alert
    
    Args:
        request: FastAPI request object
        alert_data: Alert creation data
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Created alert data
    """
    try:
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
        logger.error("Error in create_alert", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to create alert"}
        )


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Mark an alert as read
    
    Args:
        alert_id: Alert ID
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success message
    """
    try:
        logger.info("Marking alert as read", user_id=user_id, alert_id=alert_id)
        
        # Update alert
        result = supabase_client.table('alerts').update({'is_read': True}).eq('id', alert_id).or_(f"user_id.eq.{user_id},user_id.is.null").execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error updating alert", user_id=user_id, alert_id=alert_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to update alert"}
            )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ALERT_NOT_FOUND", "message": "Alert not found"}
            )
        
        logger.info("Alert marked as read successfully", user_id=user_id, alert_id=alert_id)
        return {
            "message": "Alert marked as read successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in mark_alert_as_read", user_id=user_id, alert_id=alert_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to update alert"}
        )


@router.patch("/alerts/mark-all-read")
async def mark_all_alerts_as_read(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Mark all user alerts as read
    
    Args:
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success message with count
    """
    try:
        logger.info("Marking all alerts as read", user_id=user_id)
        
        # Update all unread alerts for user
        result = supabase_client.table('alerts').update({'is_read': True}).eq('is_read', False).eq('user_id', user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error updating alerts", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to update alerts"}
            )
        
        updated_count = len(result.data) if result.data else 0
        
        logger.info("All alerts marked as read successfully", user_id=user_id, count=updated_count)
        return {
            "message": f"Marked {updated_count} alerts as read",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in mark_all_alerts_as_read", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to update alerts"}
        )


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Delete an alert
    
    Args:
        alert_id: Alert ID
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success message
    """
    try:
        logger.info("Deleting alert", user_id=user_id, alert_id=alert_id)
        
        # Delete alert
        result = supabase_client.table('alerts').delete().eq('id', alert_id).eq('user_id', user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error deleting alert", user_id=user_id, alert_id=alert_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to delete alert"}
            )
        
        logger.info("Alert deleted successfully", user_id=user_id, alert_id=alert_id)
        return {
            "message": "Alert deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in delete_alert", user_id=user_id, alert_id=alert_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to delete alert"}
        )


@router.get("/in-app")
async def get_in_app_notifications(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get in-app notifications for the current user
    
    Args:
        request: FastAPI request object
        limit: Maximum number of notifications
        offset: Number of notifications to skip
        unread_only: Only return unread notifications
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        List of in-app notifications
    """
    try:
        logger.info("Fetching in-app notifications", user_id=user_id, ip=request.client.host)
        
        # Build query
        query = supabase_client.table('in_app_notifications').select('*').eq('user_id', user_id)
        
        if unread_only:
            query = query.eq('is_read', False)
        
        # Order and paginate
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error fetching in-app notifications", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to fetch notifications"}
            )
        
        notifications = result.data or []
        
        # Count unread notifications
        unread_count_result = supabase_client.table('in_app_notifications').select('id', count='exact').eq('user_id', user_id).eq('is_read', False).execute()
        unread_count = unread_count_result.count if hasattr(unread_count_result, 'count') else 0
        
        logger.info("In-app notifications retrieved successfully", user_id=user_id, count=len(notifications))
        return {
            "notifications": notifications,
            "total": len(notifications),
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
            "message": "Notifications retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_in_app_notifications", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve notifications"}
        )


@router.get("/stats")
async def get_notification_stats(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get notification statistics for the current user
    
    Args:
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Notification statistics
    """
    try:
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
        logger.error("Error in get_notification_stats", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve notification statistics"}
        )

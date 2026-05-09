"""
Device Management API Routes
Handles IoT device management for VitaChain
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, List, Optional
import structlog

from app.core.config import settings
from app.core.database import get_supabase_client
from app.api.dependencies import get_current_user
from app.models.schemas import ErrorResponse

logger = structlog.get_logger("device_routes")

# Initialize router
router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("/")
async def get_devices(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get all devices for the current user
    
    Args:
        request: FastAPI request object
        current_user: Current user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        List of user's devices
    """
    try:
        user_id = current_user["user_id"]
        logger.info("Fetching devices", user_id=user_id, ip=request.client.host)
        
        # Get devices for user
        result = supabase_client.table('devices').select('*').eq('user_id', user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error fetching devices", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to fetch devices"}
            )
        
        devices = result.data or []
        
        logger.info("Devices retrieved successfully", user_id=user_id, count=len(devices))
        return {
            "devices": devices,
            "total": len(devices),
            "message": "Devices retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_devices", user_id=current_user.get("user_id"), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve devices"}
        )


@router.post("/")
async def create_device(
    request: Request,
    device_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Create a new IoT device
    
    Args:
        request: FastAPI request object
        device_data: Device creation data
        current_user: Current user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Created device data
    """
    try:
        user_id = current_user["user_id"]
        logger.info("Creating device", user_id=user_id, ip=request.client.host)
        
        # Validate required fields
        if not device_data.get('name'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": "Device name is required"}
            )
        
        # Generate API key for device
        import secrets
        api_key = f"vc_{secrets.token_urlsafe(32)}"
        
        # Prepare device data
        new_device = {
            'user_id': user_id,
            'name': device_data['name'],
            'type': device_data.get('type', 'esp32'),
            'status': 'active',
            'location_lat': device_data.get('location_lat'),
            'location_lng': device_data.get('location_lng'),
            'api_key': api_key,
            'configuration': device_data.get('configuration', {})
        }
        
        # Create device
        result = supabase_client.table('devices').insert(new_device).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error creating device", user_id=user_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to create device"}
            )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "INTERNAL_ERROR", "message": "Failed to create device"}
            )
        
        device = result.data[0]
        
        logger.info("Device created successfully", user_id=user_id, device_id=device['id'])
        return {
            "message": "Device created successfully",
            "device": device
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in create_device", user_id=current_user.get("user_id"), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to create device"}
        )

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
        user_id: Current user ID from JWT
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
        logger.error("Error in get_devices", user_id=user_id, error=str(e))
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
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Created device data
    """
    try:
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
        logger.error("Error in create_device", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to create device"}
        )


@router.get("/{device_id}")
async def get_device(
    device_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get a specific device by ID
    
    Args:
        device_id: Device ID
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Device data
    """
    try:
        logger.info("Fetching device", user_id=user_id, device_id=device_id)
        
        # Get device
        result = supabase_client.table('devices').select('*').eq('id', device_id).eq('user_id', user_id).single()
        
        if hasattr(result, 'error') and result.error:
            if result.error.get('code') == 'PGRST116':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
                )
            logger.error("Database error fetching device", user_id=user_id, device_id=device_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to fetch device"}
            )
        
        device = result.data
        
        logger.info("Device retrieved successfully", user_id=user_id, device_id=device_id)
        return {
            "device": device,
            "message": "Device retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_device", user_id=user_id, device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve device"}
        )


@router.patch("/{device_id}")
async def update_device(
    device_id: str,
    request: Request,
    device_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Update a device
    
    Args:
        device_id: Device ID
        request: FastAPI request object
        device_data: Device update data
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Updated device data
    """
    try:
        logger.info("Updating device", user_id=user_id, device_id=device_id)
        
        # Remove protected fields
        protected_fields = ['id', 'user_id', 'api_key', 'created_at']
        for field in protected_fields:
            device_data.pop(field, None)
        
        # Update device
        result = supabase_client.table('devices').update(device_data).eq('id', device_id).eq('user_id', user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error updating device", user_id=user_id, device_id=device_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to update device"}
            )
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
            )
        
        device = result.data[0]
        
        logger.info("Device updated successfully", user_id=user_id, device_id=device_id)
        return {
            "message": "Device updated successfully",
            "device": device
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in update_device", user_id=user_id, device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to update device"}
        )


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Delete a device
    
    Args:
        device_id: Device ID
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success message
    """
    try:
        logger.info("Deleting device", user_id=user_id, device_id=device_id)
        
        # Delete device
        result = supabase_client.table('devices').delete().eq('id', device_id).eq('user_id', user_id).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error deleting device", user_id=user_id, device_id=device_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to delete device"}
            )
        
        logger.info("Device deleted successfully", user_id=user_id, device_id=device_id)
        return {
            "message": "Device deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in delete_device", user_id=user_id, device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to delete device"}
        )


@router.get("/{device_id}/telemetry")
async def get_device_telemetry(
    device_id: str,
    request: Request,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get telemetry data for a device
    
    Args:
        device_id: Device ID
        request: FastAPI request object
        limit: Maximum number of records
        offset: Number of records to skip
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Telemetry data
    """
    try:
        logger.info("Fetching device telemetry", user_id=user_id, device_id=device_id)
        
        # Verify device ownership
        device_result = supabase_client.table('devices').select('id').eq('id', device_id).eq('user_id', user_id).single()
        if hasattr(device_result, 'error') and device_result.error or not device_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
            )
        
        # Get telemetry data
        result = supabase_client.table('telemetry').select('*').eq('device_id', device_id).order('timestamp', desc=True).range(offset, offset + limit - 1).execute()
        
        if hasattr(result, 'error') and result.error:
            logger.error("Database error fetching telemetry", user_id=user_id, device_id=device_id, error=result.error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATABASE_ERROR", "message": "Failed to fetch telemetry data"}
            )
        
        telemetry = result.data or []
        
        logger.info("Telemetry retrieved successfully", user_id=user_id, device_id=device_id, count=len(telemetry))
        return {
            "telemetry": telemetry,
            "total": len(telemetry),
            "limit": limit,
            "offset": offset,
            "message": "Telemetry data retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_device_telemetry", user_id=user_id, device_id=device_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve telemetry data"}
        )

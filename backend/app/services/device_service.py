"""
Device Service for VitaChain KATARA
Handles IoT device registration and management business logic
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
import structlog
from fastapi import HTTPException, status
from app.models.schemas import DeviceCreate, DeviceResponse, DeviceListResponse

logger = structlog.get_logger("device_service")


class DeviceService:
    """Service for managing IoT devices"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def register_device(self, device_data: DeviceCreate, farmer_id: uuid.UUID) -> DeviceResponse:
        """
        Register a new IoT device for a farmer
        
        Args:
            device_data: Device registration data
            farmer_id: Farmer ID from JWT token
            
        Returns:
            Device response with registration details
            
        Raises:
            HTTPException: If device ID already exists or validation fails
        """
        try:
            logger.info("Registering device", device_id=device_data.device_id, farmer_id=str(farmer_id))
            
            # Check if device_id already exists
            existing_device = self.supabase.table('iot_devices').select('id').eq('device_id', device_data.device_id).execute()
            
            if existing_device.data:
                logger.warning("Device ID already exists", device_id=device_data.device_id)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "DEVICE_ALREADY_EXISTS",
                        "message": "Device with this ID already exists"
                    }
                )
            
            # Prepare device record
            device_record = {
                "device_id": device_data.device_id,
                "farmer_id": str(farmer_id),
                "name": device_data.name,
                "location_lat": device_data.location_lat,
                "location_lng": device_data.location_lng,
                "registered_at": datetime.utcnow().isoformat()
            }
            
            # Insert device
            result = self.supabase.table('iot_devices').insert(device_record).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error inserting device", device_id=device_data.device_id, error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to register device"
                    }
                )
            
            device_data = result.data[0]
            logger.info("Device registered successfully", device_id=device_data.device_id, db_id=device_data['id'])
            
            return DeviceResponse(
                id=uuid.UUID(device_data['id']),
                device_id=device_data['device_id'],
                farmer_id=uuid.UUID(device_data['farmer_id']),
                name=device_data.get('name'),
                location_lat=device_data.get('location_lat'),
                location_lng=device_data.get('location_lng'),
                registered_at=datetime.fromisoformat(device_data['registered_at'].replace('Z', '+00:00'))
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error registering device", device_id=device_data.device_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def get_farmer_devices(self, farmer_id: uuid.UUID) -> DeviceListResponse:
        """
        Get all devices for a specific farmer
        
        Args:
            farmer_id: Farmer ID from JWT token
            
        Returns:
            List of devices belonging to the farmer
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            logger.info("Fetching devices for farmer", farmer_id=str(farmer_id))
            
            # Get all devices for this farmer
            result = self.supabase.table('iot_devices').select('*').eq('farmer_id', str(farmer_id)).order('registered_at', desc=True).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error fetching devices", farmer_id=str(farmer_id), error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to fetch devices"
                    }
                )
            
            devices = []
            for device_data in result.data or []:
                devices.append(DeviceResponse(
                    id=uuid.UUID(device_data['id']),
                    device_id=device_data['device_id'],
                    farmer_id=uuid.UUID(device_data['farmer_id']),
                    name=device_data.get('name'),
                    location_lat=device_data.get('location_lat'),
                    location_lng=device_data.get('location_lng'),
                    registered_at=datetime.fromisoformat(device_data['registered_at'].replace('Z', '+00:00'))
                ))
            
            logger.info("Devices fetched successfully", farmer_id=str(farmer_id), device_count=len(devices))
            
            return DeviceListResponse(
                devices=devices,
                total=len(devices)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error fetching devices", farmer_id=str(farmer_id), error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def get_device_by_id(self, device_id: str, farmer_id: uuid.UUID) -> DeviceResponse:
        """
        Get a specific device by ID (farmer-scoped)
        
        Args:
            device_id: Device unique identifier
            farmer_id: Farmer ID from JWT token
            
        Returns:
            Device details
            
        Raises:
            HTTPException: If device not found or access denied
        """
        try:
            logger.info("Fetching device", device_id=device_id, farmer_id=str(farmer_id))
            
            # Get device (RLS will ensure farmer can only access their own devices)
            result = self.supabase.table('iot_devices').select('*').eq('device_id', device_id).eq('farmer_id', str(farmer_id)).single().execute()
            
            if hasattr(result, 'error') and result.error:
                if result.error.get('code') == 'PGRST116':
                    logger.warning("Device not found", device_id=device_id, farmer_id=str(farmer_id))
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "code": "DEVICE_NOT_FOUND",
                            "message": "Device not found"
                        }
                    )
                else:
                    logger.error("Database error fetching device", device_id=device_id, error=result.error)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "code": "DATABASE_ERROR",
                            "message": "Failed to fetch device"
                        }
                    )
            
            device_data = result.data
            logger.info("Device fetched successfully", device_id=device_id)
            
            return DeviceResponse(
                id=uuid.UUID(device_data['id']),
                device_id=device_data['device_id'],
                farmer_id=uuid.UUID(device_data['farmer_id']),
                name=device_data.get('name'),
                location_lat=device_data.get('location_lat'),
                location_lng=device_data.get('location_lng'),
                registered_at=datetime.fromisoformat(device_data['registered_at'].replace('Z', '+00:00'))
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error fetching device", device_id=device_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def update_device(self, device_id: str, farmer_id: uuid.UUID, update_data: Dict[str, Any]) -> DeviceResponse:
        """
        Update device information (name, location)
        
        Args:
            device_id: Device unique identifier
            farmer_id: Farmer ID from JWT token
            update_data: Fields to update
            
        Returns:
            Updated device details
            
        Raises:
            HTTPException: If device not found or access denied
        """
        try:
            logger.info("Updating device", device_id=device_id, farmer_id=str(farmer_id))
            
            # Filter allowed fields
            allowed_fields = {'name', 'location_lat', 'location_lng'}
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}
            
            if not filtered_data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": "VALIDATION_ERROR",
                        "message": "No valid fields to update"
                    }
                )
            
            # Update device (RLS will ensure farmer can only update their own devices)
            result = self.supabase.table('iot_devices').update(filtered_data).eq('device_id', device_id).eq('farmer_id', str(farmer_id)).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error updating device", device_id=device_id, error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to update device"
                    }
                )
            
            if not result.data:
                logger.warning("Device not found for update", device_id=device_id, farmer_id=str(farmer_id))
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DEVICE_NOT_FOUND",
                        "message": "Device not found"
                    }
                )
            
            device_data = result.data[0]
            logger.info("Device updated successfully", device_id=device_id)
            
            return DeviceResponse(
                id=uuid.UUID(device_data['id']),
                device_id=device_data['device_id'],
                farmer_id=uuid.UUID(device_data['farmer_id']),
                name=device_data.get('name'),
                location_lat=device_data.get('location_lat'),
                location_lng=device_data.get('location_lng'),
                registered_at=datetime.fromisoformat(device_data['registered_at'].replace('Z', '+00:00'))
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error updating device", device_id=device_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def delete_device(self, device_id: str, farmer_id: uuid.UUID) -> bool:
        """
        Delete a device (soft delete by setting status)
        
        Args:
            device_id: Device unique identifier
            farmer_id: Farmer ID from JWT token
            
        Returns:
            True if device deleted successfully
            
        Raises:
            HTTPException: If device not found or access denied
        """
        try:
            logger.info("Deleting device", device_id=device_id, farmer_id=str(farmer_id))
            
            # For now, we'll do a hard delete. In production, consider soft delete
            result = self.supabase.table('iot_devices').delete().eq('device_id', device_id).eq('farmer_id', str(farmer_id)).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error("Database error deleting device", device_id=device_id, error=result.error)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "DATABASE_ERROR",
                        "message": "Failed to delete device"
                    }
                )
            
            if not result.data:
                logger.warning("Device not found for deletion", device_id=device_id, farmer_id=str(farmer_id))
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "DEVICE_NOT_FOUND",
                        "message": "Device not found"
                    }
                )
            
            logger.info("Device deleted successfully", device_id=device_id)
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error deleting device", device_id=device_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )

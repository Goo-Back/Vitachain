"""
Telemetry API Routes for KATARA IoT data ingestion
High-performance endpoint for ESP32 device telemetry with < 50ms response time
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader
from typing import Dict, Any

from app.core.logging import get_logger
from app.core.database import get_supabase_client
from app.services.telemetry_service import TelemetryService
from app.models.schemas import (
    TelemetryCreate, TelemetryResponse,
    TelemetryUnauthorizedResponse, TelemetryForbiddenResponse,
    TelemetryValidationErrorResponse, TelemetryDeviceNotFoundResponse
)

logger = get_logger(__name__)

# Initialize router
router = APIRouter(tags=["telemetry"])

# API Key header authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(request: Request, api_key: str = Depends(api_key_header)) -> str:
    """
    Extract and validate API key from request header.
    
    Args:
        request: FastAPI request object
        api_key: API key from X-API-Key header
        
    Returns:
        Validated API key string
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("missing_api_key", ip=request.client.host)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TelemetryUnauthorizedResponse().error
        )
    
    return api_key


@router.post("/api/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_200_OK)
async def ingest_telemetry(
    request: Request,
    telemetry_data: TelemetryCreate,
    api_key: str = Depends(get_api_key),
    supabase_client = Depends(get_supabase_client)
):
    """
    Ingest telemetry data from ESP32 IoT devices.
    
    This endpoint provides high-performance telemetry data ingestion with:
    - API key authentication for device security
    - < 50ms response time requirement
    - Automatic threshold-based alert triggering
    - Device ownership validation
    - Comprehensive data validation
    
    Args:
        request: FastAPI request object
        telemetry_data: Telemetry data from ESP32 device
        api_key: Device API key for authentication
        supabase_client: Supabase client instance
        
    Returns:
        TelemetryResponse with processing metrics
        
    Raises:
        HTTPException: For authentication, validation, or processing errors
        
    Example:
        POST /api/telemetry
        Headers:
            X-API-Key: vc_abc123def456...
        Body:
        {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 36.8,
            "humidity": 55.2,
            "ndvi": 0.42,
            "battery_level": 78.5,
            "timestamp": "2026-05-03T14:30:00Z"
        }
    """
    try:
        # Initialize telemetry service
        telemetry_service = TelemetryService(supabase_client)
        
        # Log incoming telemetry request
        logger.info(
            "telemetry_ingestion_request",
            device_id=telemetry_data.device_id,
            ip=request.client.host,
            temperature=telemetry_data.temperature,
            humidity=telemetry_data.humidity,
            ndvi=telemetry_data.ndvi
        )
        
        # Process telemetry ingestion
        result = await telemetry_service.ingest_telemetry(telemetry_data, api_key)
        
        # Log successful processing
        logger.info(
            "telemetry_ingestion_success",
            device_id=telemetry_data.device_id,
            reading_id=str(result.reading_id),
            processing_time_ms=result.processing_time_ms,
            alerts_triggered=result.alerts_triggered
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        logger.error(
            "telemetry_ingestion_unexpected_error",
            device_id=telemetry_data.device_id,
            ip=request.client.host,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during telemetry ingestion"
            }
        )


@router.get("/api/telemetry/health")
async def telemetry_health():
    """
    Health check endpoint for telemetry service.
    
    Returns:
        Health status of telemetry ingestion system
    """
    return {
        "status": "healthy",
        "service": "telemetry",
        "version": "1.0.0",
        "performance_target_ms": 50,
        "thresholds": {
            "temperature_high_c": 40.0,
            "humidity_low_percent": 20.0,
            "ndvi_low": 0.3
        }
    }


@router.get("/api/telemetry/device/{device_id}")
async def get_device_telemetry(
    device_id: str,
    request: Request,
    limit: int = 100,
    hours: int = 24,
    api_key: str = Depends(get_api_key),
    supabase_client = Depends(get_supabase_client)
):
    """
    Get telemetry data for a specific device.
    
    This endpoint allows devices to retrieve their own telemetry history
    for dashboard and analysis purposes.
    
    Args:
        device_id: Device ID to fetch telemetry for
        request: FastAPI request object
        limit: Maximum number of readings to return (1-10000)
        hours: Time window in hours (1-720)
        api_key: Device API key for authentication
        supabase_client: Supabase client instance
        
    Returns:
        Dictionary with telemetry data and metadata
        
    Raises:
        HTTPException: For authentication or authorization errors
        
    Example:
        GET /api/telemetry/device/katara-550e8400-e29b-41d4-a716-446655440000?limit=50&hours=24
        Headers:
            X-API-Key: vc_abc123def456...
    """
    try:
        # Initialize telemetry service
        telemetry_service = TelemetryService(supabase_client)
        
        # Validate API key and get device info
        device = await telemetry_service.validate_device_api_key(api_key)
        
        # Verify device ownership
        if device_id != device["device_id"]:
            logger.warning(
                "telemetry_device_access_denied",
                authenticated_device=device["device_id"],
                requested_device=device_id,
                ip=request.client.host
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=TelemetryForbiddenResponse().error
            )
        
        # Get telemetry data
        result = await telemetry_service.get_device_telemetry(
            device_id=device_id,
            farmer_id=device["farmer_id"],
            limit=limit,
            hours=hours
        )
        
        logger.info(
            "telemetry_retrieved",
            device_id=device_id,
            readings_count=result["total"],
            limit=limit,
            hours=hours
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_device_telemetry_error",
            device_id=device_id,
            ip=request.client.host,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve telemetry data"
            }
        )


# Note: Exception handlers should be defined at the app level in main.py
# The above handlers have been removed from router level

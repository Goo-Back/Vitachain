"""KATARA module API routes - Smart Farming with IoT."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.core.logging import get_logger
from app.core.database import get_supabase_client
from app.api.dependencies import get_current_user, require_farmer
from app.services.device_service import DeviceService
from app.services.dashboard_service import DashboardService
from app.services.history_service import HistoryService
from app.services.ai_service import AIService
from app.services.weather_service import weather_service, WeatherServiceError, WeatherServiceTimeout, WeatherServiceRateLimit
from app.services.ndvi_service import NDVIService, NDVIServiceError
from app.services.alert_service import get_alert_service
from app.services.auto_analysis_service import get_auto_analysis_service
from app.models.schemas import (
    DeviceCreate, DeviceResponse, DeviceListResponse,
    DeviceAlreadyExistsResponse, DeviceNotFoundResponse,
    DeviceValidationErrorResponse, DeviceForbiddenResponse,
    DashboardResponse, DashboardNotFoundResponse, DashboardAccessDeniedResponse,
    HistoryParams, HistoryResponse, HistoryNotFoundResponse, 
    HistoryAccessDeniedResponse, HistoryValidationErrorResponse,
    AIAnalysisRequest, AIAnalysisJob, AIRecommendationsResponse,
    AIAnalysisTimeoutResponse, AIAnalysisFailedResponse,
    AIRecommendationNotFoundResponse, AIRecommendationForbiddenResponse,
    AIAnalysisValidationErrorResponse,
    WeatherDataResponse, WeatherErrorResponse, WeatherValidationErrorResponse,
    WeatherTimeoutErrorResponse, WeatherRateLimitErrorResponse,
    NDVIDataResponse, NDVIHistoryResponse, NDVISummaryResponse,
    NDVIErrorResponse, NDVIValidationErrorResponse, NDVITimeoutErrorResponse, NDVIRateLimitErrorResponse,
    AlertListResponse, AlertListParams, AlertUpdateRequest, AlertUpdateResponse,
    AlertNotFoundResponse, AlertForbiddenResponse, AlertValidationErrorResponse,
    DeviceSettingsUpdate, DeviceSettingsResponse,
    DeviceSettingsNotFoundResponse, DeviceSettingsValidationErrorResponse,
    DeviceSettingsUpdateFailedResponse, AutoAnalysisStats
)
import uuid
from datetime import datetime

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/katara", tags=["katara"])

@router.get("/")
async def katara_root():
    """KATARA module root endpoint"""
    return {
        "message": "KATARA API - Smart Farming with IoT",
        "version": "1.0.0",
        "module": "katara",
        "endpoints": [
            "/api/katara/",
            "/api/katara/devices",
            "/api/katara/dashboard",
            "/api/katara/history",
            "/api/katara/analyze/{device_id}",
            "/api/katara/recommendations/{device_id}",
            "/api/katara/weather/{device_id}",
            "/api/katara/weather/{device_id}/history",
            "/api/katara/ndvi/{device_id}",
            "/api/katara/ndvi/{device_id}/history",
            "/api/katara/ndvi/summary",
            "/api/katara/telemetry",
            "/api/katara/alerts"
        ]
    }

@router.get("/health")
async def katara_health():
    """KATARA module health check"""
    return {
        "status": "healthy",
        "module": "katara",
        "version": "1.0.0"
    }

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: DeviceCreate,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Register a new IoT device
    
    Args:
        device_data: Device registration information
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Device registration details
        
    Raises:
        HTTPException: If validation fails or device already exists
    """
    try:
        device_service = DeviceService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await device_service.register_device(device_data, farmer_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in device registration", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/devices", response_model=DeviceListResponse)
async def get_farmer_devices(
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get all devices for the authenticated farmer
    
    Args:
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        List of devices belonging to the farmer
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        device_service = DeviceService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await device_service.get_farmer_devices(farmer_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching devices", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get a specific device by ID
    
    Args:
        device_id: Device unique identifier
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Device details
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        device_service = DeviceService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await device_service.get_device_by_id(device_id, farmer_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching device", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.patch("/devices/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    update_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Update device information (name, location)
    
    Args:
        device_id: Device unique identifier
        update_data: Fields to update
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Updated device details
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        device_service = DeviceService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await device_service.update_device(device_id, farmer_id, update_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error updating device", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Delete a device
    
    Args:
        device_id: Device unique identifier
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        No content on success
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        device_service = DeviceService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        await device_service.delete_device(device_id, farmer_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error deleting device", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get KATARA dashboard data with real-time telemetry and alerts
    
    Args:
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Complete dashboard data including devices, stats, alerts, and trends
        
    Raises:
        HTTPException: If dashboard data cannot be retrieved
    """
    try:
        dashboard_service = DashboardService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await dashboard_service.get_dashboard_data(farmer_id)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Dashboard data validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DashboardNotFoundResponse().error
        )
    except Exception as e:
        logger.error("Unexpected error in dashboard endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/dashboard/device/{device_id}")
async def get_device_dashboard_status(
    device_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get detailed status for a specific device
    
    Args:
        device_id: Device unique identifier
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Detailed device status information
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        dashboard_service = DashboardService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await dashboard_service.get_device_status(farmer_id, device_id)
        
    except ValueError as e:
        logger.error(f"Device not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DashboardNotFoundResponse().error
        )
    except Exception as e:
        logger.error("Unexpected error getting device status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/history", response_model=HistoryResponse)
async def get_telemetry_history(
    start_date: str,
    end_date: str,
    device_id: str = None,
    aggregation: str = "hour",
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get historical telemetry data with trend analysis
    
    Args:
        start_date: Start date for historical analysis (ISO 8601 format)
        end_date: End date for historical analysis (ISO 8601 format)
        device_id: Optional specific device ID to analyze
        aggregation: Aggregation level ('hour' or 'day')
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Comprehensive historical analysis including chart data, statistics, trends, and alert patterns
        
    Raises:
        HTTPException: If validation fails, access denied, or data not found
    """
    try:
        from datetime import datetime
        
        # Parse and validate date parameters
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=HistoryValidationErrorResponse().error
            )
        
        # Create history parameters
        history_params = HistoryParams(
            start_date=start_dt,
            end_date=end_dt,
            device_id=device_id,
            aggregation=aggregation
        )
        
        # Get historical data
        history_service = HistoryService()
        farmer_id = uuid.UUID(current_user["user_id"])
        
        return await history_service.get_historical_telemetry(farmer_id, history_params)
        
    except ValueError as e:
        logger.error(f"History validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=HistoryValidationErrorResponse().error
        )
    except PermissionError as e:
        logger.error(f"History access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=HistoryAccessDeniedResponse().error
        )
    except Exception as e:
        if "No historical data found" in str(e) or "No data found" in str(e):
            logger.error(f"History data not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=HistoryNotFoundResponse().error
            )
        
        logger.error("Unexpected error in history endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.post("/analyze/{device_id}", response_model=AIAnalysisJob, status_code=status.HTTP_202_ACCEPTED)
async def analyze_device_ai(
    device_id: str,
    analysis_request: AIAnalysisRequest,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Trigger AI analysis for device telemetry data
    
    Args:
        device_id: Device unique identifier
        analysis_request: Analysis parameters
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Analysis job information
        
    Raises:
        HTTPException: If device not found, access denied, or analysis fails
    """
    try:
        ai_service = AIService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Get device location for weather data
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user["user_id"])
        
        weather_data = None
        if device and device.get('location_lat') and device.get('location_lng'):
            try:
                # Fetch weather data for AI enhancement
                weather_data = await weather_service.get_weather_data(
                    device['location_lat'], 
                    device['location_lng'], 
                    device_id
                )
                weather_data = weather_data.model_dump()
            except Exception as e:
                logger.warning(f"Failed to fetch weather data for AI analysis: {str(e)}")
                # Continue without weather data - AI analysis should still work
        
        # Try to get NDVI data for AI enhancement
        ndvi_data = None
        try:
            ndvi_service = NDVIService(supabase)
            ndvi_data = await ndvi_service.get_ndvi_data(device_id, farmer_id)
        except Exception as e:
            logger.warning(f"Failed to fetch NDVI data for AI analysis: {str(e)}")
            # Continue without NDVI data - AI analysis should still work
        
        result = await ai_service.analyze_device_telemetry(
            device_id, 
            farmer_id, 
            analysis_request,
            weather_data,
            ndvi_data
        )
        
        return AIAnalysisJob(
            analysis_id=result["analysis_id"],
            status=result["status"],
            estimated_completion=result["estimated_completion"]
        )
        
    except HTTPException as e:
        if e.status_code == 408:  # Timeout
            logger.error("AI analysis timeout", device_id=device_id)
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=AIAnalysisTimeoutResponse().error
            )
        elif e.status_code == 500 and "AI_ANALYSIS" in str(e.detail):
            logger.error("AI analysis failed", device_id=device_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=AIAnalysisFailedResponse().error
            )
        raise
    except Exception as e:
        logger.error("Unexpected error in AI analysis endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/recommendations/{device_id}", response_model=AIRecommendationsResponse)
async def get_ai_recommendations(
    device_id: str,
    start_date: str = None,
    end_date: str = None,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get AI recommendations for a device
    
    Args:
        device_id: Device unique identifier
        start_date: Optional start date filter (ISO 8601)
        end_date: Optional end date filter (ISO 8601)
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        List of AI recommendations
        
    Raises:
        HTTPException: If device not found, access denied, or validation fails
    """
    try:
        from datetime import datetime
        
        ai_service = AIService(supabase)
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Parse optional date filters
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=AIAnalysisValidationErrorResponse().error
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=AIAnalysisValidationErrorResponse().error
                )
        
        recommendations = await ai_service.get_recommendations(
            device_id, 
            farmer_id, 
            start_dt, 
            end_dt
        )
        
        return AIRecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations)
        )
        
    except ValueError as e:
        logger.error(f"AI recommendations validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=AIAnalysisValidationErrorResponse().error
        )
    except PermissionError as e:
        logger.error(f"AI recommendations access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AIRecommendationForbiddenResponse().error
        )
    except Exception as e:
        if "No recommendations found" in str(e) or "not found" in str(e):
            logger.error(f"AI recommendations not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AIRecommendationNotFoundResponse().error
            )
        
        logger.error("Unexpected error in AI recommendations endpoint", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/weather/{device_id}", response_model=WeatherDataResponse)
async def get_weather_data(
    device_id: str,
    current_user = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get weather data for a specific device location.
    Integrates OpenWeatherMap API with 15-minute caching.
    """
    try:
        # Validate device_id format
        if not device_id.startswith('katara-') or len(device_id) != 42:  # katara- + 36 char UUID
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=WeatherValidationErrorResponse().error
            )
        
        # Get device information to verify ownership and get location
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user.id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": f"Device {device_id} not found",
                    "details": {"device_id": device_id}
                }
            )
        
        # Extract location from device with type validation
        try:
            lat = float(device.get('location_lat'))
            lng = float(device.get('location_lng'))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid device coordinates format",
                    "details": {"device_id": device_id, "missing": "numeric location_lat, location_lng"}
                }
            )
        
        if lat is None or lng is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device location not configured",
                    "details": {"device_id": device_id, "missing": "location_lat, location_lng"}
                }
            )
        
        # Validate coordinates (Morocco bounds)
        if not (21 <= lat <= 36 and -17 <= lng <= -1):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device coordinates outside Morocco",
                    "details": {"lat": lat, "lng": lng, "expected_bounds": "21-36°N, 17-1°W"}
                }
            )
        
        # Get weather data
        weather_data = await weather_service.get_weather_data(lat, lng, device_id)
        
        # Store weather reading in database
        await _store_weather_reading(supabase, device_id, current_user.id, weather_data)
        
        # Generate weather risk alerts if needed
        await _generate_weather_alerts(supabase, current_user.id, device_id, weather_data.alerts)
        
        return WeatherDataResponse(
            current=weather_data.current,
            forecast=weather_data.forecast,
            alerts=weather_data.alerts,
            cached_at=weather_data.cached_at,
            cache_expires=weather_data.cache_expires
        )
        
    except WeatherServiceTimeout:
        logger.error(f"Weather service timeout for device {device_id}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=WeatherTimeoutErrorResponse().error
        )
    
    except WeatherServiceRateLimit:
        logger.error(f"Weather service rate limit exceeded for device {device_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=WeatherRateLimitErrorResponse().error
        )
    
    except WeatherServiceError as e:
        logger.error(f"Weather service error for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=WeatherErrorResponse().error
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in weather endpoint for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.get("/weather/{device_id}/history")
async def get_weather_history(
    device_id: str,
    days: int = 7,
    current_user = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get historical weather data for a device (past 7 days by default).
    """
    try:
        # Validate device_id format
        if not device_id.startswith('katara-') or len(device_id) != 42:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=WeatherValidationErrorResponse().error
            )
        
        # Validate days parameter
        if not 1 <= days <= 30:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Days parameter must be between 1 and 30",
                    "details": {"days": days}
                }
            )
        
        # Get device information to verify ownership
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user["user_id"])
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": f"Device {device_id} not found",
                    "details": {"device_id": device_id}
                }
            )
        
        # Query historical weather data
        from datetime import datetime, timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = supabase.table("weather_readings").select("*").eq("device_id", device_id).eq("farmer_id", current_user["user_id"]).gte("created_at", start_date.isoformat()).order("created_at", desc=True).execute()
        
        if not result.data:
            return {"history": [], "total_count": 0}
        
        return {
            "history": result.data,
            "total_count": len(result.data),
            "query_params": {"device_id": device_id, "days": days}
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in weather history endpoint for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )
    """
    Get weather data for a specific device location.
    Integrates OpenWeatherMap API with 15-minute caching.
    """
    try:
        # Validate device_id format
        if not device_id.startswith('katara-') or len(device_id) != 42:  # katara- + 36 char UUID
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=WeatherValidationErrorResponse().error
            )
        
        # Get device information to verify ownership and get location
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user.id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": f"Device {device_id} not found",
                    "details": {"device_id": device_id}
                }
            )
        
        # Extract location from device
        lat = device.get('location_lat')
        lng = device.get('location_lng')
        
        if lat is None or lng is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device location not configured",
                    "details": {"device_id": device_id, "missing": "location_lat, location_lng"}
                }
            )
        
        # Validate coordinates (Morocco bounds)
        if not (21 <= lat <= 36 and -17 <= lng <= -1):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device coordinates outside Morocco",
                    "details": {"lat": lat, "lng": lng, "expected_bounds": "21-36°N, 17-1°W"}
                }
            )
        
        # Get weather data
        weather_data = await weather_service.get_weather_data(lat, lng, device_id)
        
        # Store weather reading in database
        await _store_weather_reading(supabase, device_id, current_user.id, weather_data)
        
        # Generate weather risk alerts if needed
        await _generate_weather_alerts(supabase, current_user.id, device_id, weather_data.alerts)
        
        return WeatherDataResponse(
            current=weather_data.current,
            forecast=weather_data.forecast,
            alerts=weather_data.alerts,
            cached_at=weather_data.cached_at,
            cache_expires=weather_data.cache_expires
        )
        
    except WeatherServiceTimeout:
        logger.error(f"Weather service timeout for device {device_id}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=WeatherTimeoutErrorResponse().error
        )
    
    except WeatherServiceRateLimit:
        logger.error(f"Weather service rate limit exceeded for device {device_id}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=WeatherRateLimitErrorResponse().error
        )
    
    except WeatherServiceError as e:
        logger.error(f"Weather service error for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=WeatherErrorResponse().error
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in weather endpoint for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


async def _store_weather_reading(supabase, device_id: str, farmer_id: str, weather_data):
    """Store weather reading in database."""
    try:
        current = weather_data.current
        
        weather_reading = {
            "device_id": device_id,
            "farmer_id": farmer_id,
            "location_lat": current.location.lat,
            "location_lng": current.location.lng,
            "temperature": current.temperature,
            "humidity": current.humidity,
            "pressure": current.pressure,
            "wind_speed": current.wind_speed,
            "wind_direction": current.wind_direction,
            "rainfall_1h": current.rainfall_1h,
            "rainfall_24h": current.rainfall_24h,
            "weather_main": current.weather_main,
            "weather_description": current.weather_description,
            "visibility": current.visibility,
            "uv_index": current.uv_index,
            "forecast_data": [point.model_dump() for point in weather_data.forecast],
            "api_source": "openweathermap"
        }
        
        result = supabase.table("weather_readings").insert(weather_reading).execute()
        
        if len(result.data) == 0:
            logger.error(f"Failed to store weather reading for device {device_id}")
        
    except Exception as e:
        logger.error(f"Error storing weather reading: {str(e)}")
        # Don't raise - weather data is still useful even if storage fails


async def _generate_weather_alerts(supabase, farmer_id: str, device_id: str, alerts):
    """Generate weather risk alerts in katara_alerts table."""
    try:
        for alert in alerts:
            alert_data = {
                "farmer_id": farmer_id,
                "device_id": device_id,
                "type": "weather_risk",
                "severity": alert.severity,
                "message": f"Alerte météo: {alert.message}",
                "is_read": False
            }
            
            result = supabase.table("katara_alerts").insert(alert_data).execute()
            
            if len(result.data) == 0:
                logger.error(f"Failed to create weather alert for device {device_id}")
        
    except Exception as e:
        logger.error(f"Error generating weather alerts: {str(e)}")
        # Don't raise - weather data is still useful even if alert creation fails


@router.get("/ndvi/{device_id}", response_model=NDVIDataResponse)
async def get_ndvi_data(
    device_id: str,
    current_user = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get NDVI satellite imagery data for a specific device location.
    Integrates Sentinel Hub API with 24-hour caching for cost optimization.
    """
    try:
        # Validate device_id format
        if not device_id.startswith('katara-') or len(device_id) != 42:  # katara- + 36 char UUID
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=NDVIValidationErrorResponse().error
            )
        
        # Get device information to verify ownership and get location
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user.id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": f"Device {device_id} not found",
                    "details": {"device_id": device_id}
                }
            )
        
        # Extract location from device with type validation
        try:
            lat = float(device.get('location_lat'))
            lng = float(device.get('location_lng'))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid device coordinates format",
                    "details": {"device_id": device_id, "missing": "numeric location_lat, location_lng"}
                }
            )
        
        if lat is None or lng is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device location not configured",
                    "details": {"device_id": device_id, "missing": "location_lat, location_lng"}
                }
            )
        
        # Validate coordinates (Morocco bounds)
        if not (21 <= lat <= 36 and -17 <= lng <= -1):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Device coordinates outside Morocco",
                    "details": {"lat": lat, "lng": lng, "expected_bounds": "21-36°N, 17-1°W"}
                }
            )
        
        # Get NDVI data using NDVI service
        ndvi_service = NDVIService(supabase)
        ndvi_data = await ndvi_service.get_ndvi_data(device_id, current_user.id)
        
        return NDVIDataResponse(
            current=ndvi_data["current"],
            trend=ndvi_data["trend"],
            historical=ndvi_data["historical"],
            alerts=ndvi_data["alerts"],
            cached_at=ndvi_data["cached_at"],
            cache_expires=ndvi_data["cache_expires"]
        )
        
    except NDVIServiceError as e:
        if "timeout" in str(e).lower():
            logger.error(f"NDVI service timeout for device {device_id}")
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=NDVITimeoutErrorResponse().error
            )
        elif "rate limit" in str(e).lower():
            logger.error(f"NDVI service rate limit exceeded for device {device_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=NDVIRateLimitErrorResponse().error
            )
        logger.error(f"NDVI service error for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=NDVIErrorResponse().error
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in NDVI endpoint for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.get("/ndvi/{device_id}/history")
async def get_ndvi_history(
    device_id: str,
    days: int = 30,
    current_user = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get historical NDVI data for a device (past 30 days by default).
    """
    try:
        # Validate device_id format
        if not device_id.startswith('katara-') or len(device_id) != 42:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=NDVIValidationErrorResponse().error
            )
        
        # Validate days parameter
        if not 1 <= days <= 90:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "Days parameter must be between 1 and 90",
                    "details": {"days": days}
                }
            )
        
        # Get device information to verify ownership
        device_service = DeviceService(supabase)
        device = await device_service.get_device(device_id, current_user["user_id"])
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "DEVICE_NOT_FOUND",
                    "message": f"Device {device_id} not found",
                    "details": {"device_id": device_id}
                }
            )
        
        # Get historical NDVI data
        ndvi_service = NDVIService(supabase)
        history_data = await ndvi_service.get_ndvi_history(device_id, current_user["user_id"], days)
        
        return NDVIHistoryResponse(
            history=history_data["history"],
            total_count=history_data["total_count"],
            query_params=history_data["query_params"],
            trend_analysis=history_data.get("trend_analysis")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in NDVI history endpoint for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.get("/ndvi/summary", response_model=NDVISummaryResponse)
async def get_ndvi_summary(
    current_user = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get NDVI summary for all devices of the authenticated farmer.
    """
    try:
        # Get NDVI summary using NDVI service
        ndvi_service = NDVIService(supabase)
        summary_data = await ndvi_service.get_ndvi_summary(current_user["user_id"])
        
        return NDVISummaryResponse(
            devices=summary_data["devices"],
            summary=summary_data["summary"]
        )
        
    except NDVIServiceError as e:
        logger.error(f"NDVI service error in summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=NDVIErrorResponse().error
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in NDVI summary endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


# Placeholder endpoints for future stories
@router.get("/telemetry")
async def get_telemetry():
    """Get telemetry data for KATARA module (placeholder for story 3-2)"""
    return {
        "message": "KATARA telemetry endpoint - to be implemented in story 3-2",
        "data": []
    }

@router.get("/alerts", response_model=AlertListResponse)
async def get_farmer_alerts(
    limit: int = 20,
    offset: int = 0,
    severity: Optional[str] = None,
    read_status: Optional[bool] = None,
    device_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get alerts for the authenticated farmer with filtering and pagination.
    
    Args:
        limit: Number of alerts to return (1-100)
        offset: Number of alerts to skip
        severity: Optional severity filter (low, medium, high, critical)
        read_status: Optional read status filter (true=read, false=unread)
        device_id: Optional device ID filter
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Paginated list of alerts with unread count
        
    Raises:
        HTTPException: For validation or database errors
    """
    try:
        # Validate parameters
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=AlertValidationErrorResponse().error
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=AlertValidationErrorResponse().error
            )
        
        # Get alert service
        alert_service = get_alert_service()
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Parse severity filter if provided
        severity_filter = None
        if severity:
            try:
                from app.models.schemas import AlertSeverity
                severity_filter = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=AlertValidationErrorResponse().error
                )
        
        # Get alerts
        alerts = await alert_service.get_farmer_alerts(
            farmer_id=farmer_id,
            limit=limit,
            offset=offset,
            severity=severity_filter,
            is_read=read_status,
            device_id=device_id
        )
        
        # Get unread count
        unread_count = await alert_service.get_unread_alerts_count(farmer_id)
        
        # Check if there are more alerts
        has_more = len(alerts) == limit
        
        # Create pagination info
        pagination = {
            "limit": limit,
            "offset": offset,
            "has_more": has_more
        }
        
        return AlertListResponse(
            alerts=alerts,
            unread_count=unread_count,
            total=len(alerts),  # This would need to be calculated properly in production
            pagination=pagination
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_farmer_alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.patch("/alerts/{alert_id}/status", response_model=AlertUpdateResponse)
async def update_alert_status(
    alert_id: str,
    status_update: AlertUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Update alert read status (read or unread) for the authenticated farmer.
    
    Args:
        alert_id: Alert UUID to update
        status_update: New read status (true=read, false=unread)
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Updated alert information
        
    Raises:
        HTTPException: For validation, authorization, or database errors
    """
    try:
        # Validate alert ID format
        try:
            alert_uuid = uuid.UUID(alert_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "Invalid alert ID format"}
            )
        
        # Get alert service
        alert_service = get_alert_service()
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Update alert status
        updated_alert = await alert_service.update_alert_status(alert_uuid, farmer_id, status_update.read_status)
        
        return AlertUpdateResponse(
            id=updated_alert.id,
            read_status=updated_alert.read_status,
            read_at=updated_alert.read_at,
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_alert_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.patch("/alerts/bulk-status", response_model=dict)
async def bulk_update_alert_status(
    bulk_update: dict,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Update multiple alerts' read status for the authenticated farmer.
    
    Args:
        bulk_update: Dictionary containing alert_ids and read_status
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Bulk update results
        
    Raises:
        HTTPException: For validation, authorization, or database errors
    """
    try:
        # Validate request body
        alert_ids = bulk_update.get("alert_ids", [])
        read_status = bulk_update.get("read_status")
        
        if not isinstance(alert_ids, list) or len(alert_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=AlertValidationErrorResponse().error
            )
        
        if len(alert_ids) > 100:  # Prevent DoS attacks
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "Maximum 100 alerts can be updated at once"}
            )
        
        if not isinstance(read_status, bool):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=AlertValidationErrorResponse().error
            )
        
        # Convert alert IDs to UUIDs
        alert_uuids = []
        for alert_id in alert_ids:
            try:
                alert_uuids.append(uuid.UUID(alert_id))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=AlertValidationErrorResponse().error
                )
        
        # Get alert service
        alert_service = get_alert_service()
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Bulk update alerts
        result = await alert_service.bulk_update_alert_status(alert_uuids, farmer_id, read_status)
        
        return {
            "updated_count": result["updated_count"],
            "failed_updates": result["failed_updates"],
            "updated_alerts": result["updated_alerts"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_update_alert_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.patch("/alerts/{alert_id}/read", response_model=AlertUpdateResponse)
async def mark_alert_as_read(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Mark an alert as read for the authenticated farmer (legacy endpoint).
    
    Args:
        alert_id: Alert UUID to mark as read
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Updated alert information
        
    Raises:
        HTTPException: For validation, authorization, or database errors
    """
    try:
        # Validate alert ID format
        try:
            alert_uuid = uuid.UUID(alert_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "Invalid alert ID format"}
            )
        
        # Get alert service
        alert_service = get_alert_service()
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Mark alert as read
        updated_alert = await alert_service.mark_alert_as_read(alert_uuid, farmer_id)
        
        return AlertUpdateResponse(
            id=updated_alert.id,
            read_status=updated_alert.read_status,
            read_at=updated_alert.read_at,
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in mark_alert_as_read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


# Device Settings and Auto Analysis Endpoints

@router.get("/devices/{device_id}/settings", response_model=DeviceSettingsResponse)
async def get_device_settings(
    device_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get automatic analysis settings for a device.
    
    Args:
        device_id: Device identifier
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Device analysis settings
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Get device settings
        result = supabase.table("iot_devices").select(
            "device_id", "auto_analysis_enabled", "analysis_frequency_hours", 
            "last_auto_analysis"
        ).eq("device_id", device_id).eq("farmer_id", farmer_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DeviceSettingsNotFoundResponse().error
            )
        
        device = result.data[0]
        
        return DeviceSettingsResponse(
            device_id=device["device_id"],
            auto_analysis_enabled=device.get("auto_analysis_enabled", True),
            analysis_frequency_hours=device.get("analysis_frequency_hours", 6),
            last_auto_analysis=device.get("last_auto_analysis"),
            critical_threshold_only=False  # Default value for now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_device_settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve device settings"
            }
        )


@router.patch("/devices/{device_id}/settings", response_model=DeviceSettingsResponse)
async def update_device_settings(
    device_id: str,
    settings: DeviceSettingsUpdate,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Update automatic analysis settings for a device.
    
    Args:
        device_id: Device identifier
        settings: Device settings update
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Updated device settings
        
    Raises:
        HTTPException: If device not found, access denied, or validation fails
    """
    try:
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Get auto analysis service
        auto_analysis_service = get_auto_analysis_service(supabase)
        
        # Update device settings
        updated_device = await auto_analysis_service.update_device_analysis_settings(
            device_id=device_id,
            farmer_id=farmer_id,
            auto_analysis_enabled=settings.auto_analysis_enabled,
            analysis_frequency_hours=settings.analysis_frequency_hours
        )
        
        return DeviceSettingsResponse(
            device_id=updated_device["device_id"],
            auto_analysis_enabled=updated_device.get("auto_analysis_enabled", True),
            analysis_frequency_hours=updated_device.get("analysis_frequency_hours", 6),
            last_auto_analysis=updated_device.get("last_auto_analysis"),
            critical_threshold_only=settings.critical_threshold_only
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_device_settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=DeviceSettingsUpdateFailedResponse().error
        )


@router.get("/devices/{device_id}/auto-analysis-stats", response_model=AutoAnalysisStats)
async def get_auto_analysis_stats(
    device_id: str,
    current_user: Dict[str, Any] = Depends(require_farmer),
    supabase = Depends(get_supabase_client)
):
    """
    Get automatic analysis statistics for a device.
    
    Args:
        device_id: Device identifier
        current_user: Authenticated farmer user
        supabase: Supabase client
        
    Returns:
        Automatic analysis statistics
        
    Raises:
        HTTPException: If device not found or access denied
    """
    try:
        farmer_id = uuid.UUID(current_user["user_id"])
        
        # Verify device ownership
        device_result = supabase.table("iot_devices").select("id").eq(
            "device_id", device_id
        ).eq("farmer_id", farmer_id).execute()
        
        if not device_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DeviceSettingsNotFoundResponse().error
            )
        
        # Get analysis statistics
        stats_result = supabase.table("ai_recommendations").select(
            "trigger_type", "created_at"
        ).eq("device_id", device_id).in_("trigger_type", ["automatic_critical", "automatic_periodic"]).execute()
        
        analyses = stats_result.data or []
        
        # Calculate statistics
        total_analyses = len(analyses)
        critical_triggers = len([a for a in analyses if a["trigger_type"] == "automatic_critical"])
        periodic_triggers = len([a for a in analyses if a["trigger_type"] == "automatic_periodic"])
        
        # Calculate success rate (assuming all stored analyses were successful)
        success_rate = 100.0 if total_analyses > 0 else 0.0
        
        # Get last analysis timestamp
        last_analysis = None
        if analyses:
            latest = max(analyses, key=lambda x: x["created_at"])
            last_analysis = datetime.fromisoformat(latest["created_at"].replace('Z', '+00:00'))
        
        # For now, use placeholder values for response time and success rate
        # In a real implementation, you'd track actual metrics
        avg_response_time = 15.5  # seconds placeholder
        
        return AutoAnalysisStats(
            total_analyses=total_analyses,
            critical_triggers=critical_triggers,
            periodic_triggers=periodic_triggers,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            last_analysis=last_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_auto_analysis_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve analysis statistics"
            }
        )

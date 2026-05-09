"""
Telemetry Service for KATARA IoT data ingestion
Handles high-performance telemetry data processing with < 50ms response time
"""

import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import HTTPException
from app.core.logging import get_logger
from app.core.database import get_supabase_client
from app.models.schemas import (
    TelemetryCreate, TelemetryResponse,
    TelemetryUnauthorizedResponse, TelemetryForbiddenResponse,
    TelemetryDeviceNotFoundResponse, TelemetryValidationErrorResponse
)
from app.services.alert_service import get_alert_service
from app.services.auto_analysis_service import get_auto_analysis_service
from app.core.auto_analysis_config import AutoAnalysisConfig

logger = get_logger(__name__)


class TelemetryService:
    """Service for handling telemetry data ingestion with high performance."""
    
    def __init__(self, supabase_client):
        """Initialize telemetry service with Supabase client."""
        self.supabase = supabase_client
        self.logger = get_logger(f"{__name__}.TelemetryService")
    
    async def validate_device_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate API key and return device information.
        
        Args:
            api_key: Device API key from X-API-Key header
            
        Returns:
            Device information dictionary
            
        Raises:
            HTTPException: If API key is invalid
        """
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail=TelemetryUnauthorizedResponse().error
            )
        
        try:
            # Query device by API key
            result = self.supabase.table("iot_devices").select("*").eq("api_key", api_key).execute()
            
            if not result.data:
                self.logger.warning("invalid_api_key", api_key_prefix=api_key[:8] + "...")
                raise HTTPException(
                    status_code=401,
                    detail=TelemetryUnauthorizedResponse().error
                )
            
            device = result.data[0]
            
            # Check if device is active (add status check if needed)
            if device.get("status") == "inactive":
                self.logger.warning("inactive_device_attempt", device_id=device["device_id"])
                raise HTTPException(
                    status_code=403,
                    detail=TelemetryDeviceNotFoundResponse().error
                )
            
            self.logger.debug("api_key_validated", device_id=device["device_id"])
            return device
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("api_key_validation_error", error=str(e))
            raise HTTPException(
                status_code=500,
                detail={"code": "INTERNAL_ERROR", "message": "API key validation failed"}
            )
    
    async def ingest_telemetry(self, telemetry_data: TelemetryCreate, api_key: str) -> TelemetryResponse:
        """
        Ingest telemetry data with high-performance processing.
        
        Args:
            telemetry_data: Validated telemetry data
            api_key: Device API key for authentication
            
        Returns:
            Telemetry response with processing metrics
            
        Raises:
            HTTPException: If validation fails or device mismatch
        """
        start_time = time.time()
        
        try:
            # Validate API key and get device
            device = await self.validate_device_api_key(api_key)
            
            # Verify device ownership (device_id must match authenticated device)
            if telemetry_data.device_id != device["device_id"]:
                self.logger.warning(
                    "device_id_mismatch",
                    authenticated_device=device["device_id"],
                    requested_device=telemetry_data.device_id
                )
                raise HTTPException(
                    status_code=403,
                    detail=TelemetryForbiddenResponse().error
                )
            
            # Get service role client for bypassing RLS
            service_supabase = get_supabase_client(service_role=True)
            
            # Prepare telemetry record
            reading_data = {
                "device_id": telemetry_data.device_id,
                "farmer_id": device["farmer_id"],
                "temperature": telemetry_data.temperature,
                "humidity": telemetry_data.humidity,
                "ndvi": telemetry_data.ndvi,
                "battery_level": telemetry_data.battery_level,
                "timestamp": telemetry_data.timestamp or datetime.utcnow().isoformat()
            }
            
            # Insert telemetry data using service role (bypasses RLS)
            result = service_supabase.table("telemetry_readings").insert(reading_data).execute()
            
            if not result.data:
                self.logger.error("telemetry_insert_failed", device_id=telemetry_data.device_id)
                raise HTTPException(
                    status_code=500,
                    detail={"code": "INTERNAL_ERROR", "message": "Failed to store telemetry data"}
                )
            
            reading_id = result.data[0]["id"]
            
            # Check for threshold alerts using the enhanced alert service
            alert_service = get_alert_service()
            alert_result = await alert_service.check_thresholds_and_create_alerts(
                device_id=telemetry_data.device_id,
                farmer_id=uuid.UUID(device["farmer_id"]),
                temperature=telemetry_data.temperature,
                humidity=telemetry_data.humidity,
                ndvi=telemetry_data.ndvi
            )
            alerts_triggered = alert_result.alerts_created
            
            # Trigger automatic AI analysis if critical conditions detected
            auto_analysis_service = get_auto_analysis_service(self.supabase)
            telemetry_dict = {
                "temperature": telemetry_data.temperature,
                "humidity": telemetry_data.humidity,
                "ndvi": telemetry_data.ndvi,
                "battery_level": telemetry_data.battery_level,
                "timestamp": telemetry_data.timestamp or datetime.utcnow().isoformat()
            }
            
            # Check if critical thresholds are exceeded for auto-analysis trigger
            critical_conditions = self._check_critical_thresholds(telemetry_dict)
            if critical_conditions:
                # Trigger automatic analysis asynchronously to avoid blocking telemetry ingestion
                asyncio.create_task(
                    auto_analysis_service.handle_automatic_analysis_trigger(
                        device_id=telemetry_data.device_id,
                        farmer_id=uuid.UUID(device["farmer_id"]),
                        telemetry_reading=telemetry_dict,
                        trigger_type="critical_threshold"
                    )
                )
                self.logger.info(
                    "auto_analysis_triggered",
                    device_id=telemetry_data.device_id,
                    critical_conditions=critical_conditions
                )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Log performance metric
            if processing_time_ms > 50:
                self.logger.warning(
                    "telemetry_processing_slow",
                    device_id=telemetry_data.device_id,
                    processing_time_ms=processing_time_ms,
                    threshold_ms=50
                )
            else:
                self.logger.debug(
                    "telemetry_processed",
                    device_id=telemetry_data.device_id,
                    reading_id=str(reading_id),
                    processing_time_ms=processing_time_ms,
                    alerts_triggered=alerts_triggered
                )
            
            return TelemetryResponse(
                reading_id=reading_id,
                alerts_triggered=alerts_triggered,
                alert_ids=alert_result.alert_ids,
                processing_time_ms=processing_time_ms
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "telemetry_ingestion_error",
                device_id=telemetry_data.device_id,
                error=str(e),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            raise HTTPException(
                status_code=500,
                detail={"code": "INTERNAL_ERROR", "message": "Telemetry ingestion failed"}
            )
    
        
    def _check_critical_thresholds(self, telemetry_dict: Dict[str, Any]) -> List[str]:
        """
        Check if telemetry readings exceed critical thresholds for auto-analysis trigger
        
        Args:
            telemetry_dict: Dictionary with telemetry readings
            
        Returns:
            List of exceeded threshold names
        """
        exceeded = []
        
        temperature = telemetry_dict.get("temperature", 0)
        humidity = telemetry_dict.get("humidity", 100)
        ndvi = telemetry_dict.get("ndvi")
        
        if temperature > AutoAnalysisConfig.CRITICAL_TEMPERATURE_THRESHOLD:
            exceeded.append("temperature")
        
        if humidity < AutoAnalysisConfig.CRITICAL_HUMIDITY_THRESHOLD:
            exceeded.append("humidity")
        
        if ndvi is not None and ndvi < AutoAnalysisConfig.CRITICAL_NDVI_THRESHOLD:
            exceeded.append("ndvi")
        
        return exceeded
        
    async def get_device_telemetry(
        self, 
        device_id: str, 
        farmer_id: str, 
        limit: int = 100, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get telemetry data for a specific device.
        
        Args:
            device_id: Device ID to fetch data for
            farmer_id: Farmer ID for authorization
            limit: Maximum number of readings to return
            hours: Time window in hours
            
        Returns:
            Dictionary with telemetry data
        """
        try:
            # Validate inputs
            if limit <= 0 or limit > 10000:
                raise ValueError("Invalid limit")
            if hours <= 0 or hours > 720:  # Max 30 days
                raise ValueError("Invalid hours")
            
            # Query telemetry data with time filter
            result = self.supabase.table("telemetry_readings") \
                .select("*") \
                .eq("device_id", device_id) \
                .eq("farmer_id", farmer_id) \
                .order("timestamp", desc=True) \
                .limit(limit) \
                .execute()
            
            if not result.data:
                return {
                    "device_id": device_id,
                    "readings": [],
                    "total": 0,
                    "limit": limit,
                    "hours": hours
                }
            
            # Filter by time window (additional safety check)
            cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
            filtered_readings = [
                reading for reading in result.data
                if datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00')).timestamp() >= cutoff_time
            ]
            
            return {
                "device_id": device_id,
                "readings": filtered_readings[:limit],
                "total": len(filtered_readings),
                "limit": limit,
                "hours": hours
            }
            
        except Exception as e:
            self.logger.error(
                "get_device_telemetry_error",
                device_id=device_id,
                farmer_id=farmer_id,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail={"code": "INTERNAL_ERROR", "message": "Failed to retrieve telemetry data"}
            )



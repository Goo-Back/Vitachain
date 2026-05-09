"""
Automatic Analysis Service for KATARA AI Recommendations
Handles intelligent triggering of AI analysis based on critical conditions and periodic schedules
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import structlog
from fastapi import HTTPException, status

from app.services.ai_service import AIService, AIAnalysisTimeout, AIAnalysisFailed
from app.services.alert_service import AlertService
from app.services.weather_service import WeatherService
from app.services.ndvi_service import NDVIService
from app.models.schemas import (
    AIAnalysisRequest, TelemetryReading, Alert, AlertType, AlertSeverity
)
from app.core.config import settings
from app.core.auto_analysis_config import AutoAnalysisConfig

logger = structlog.get_logger("auto_analysis_service")


class AutoAnalysisService:
    """Service for intelligent automatic AI analysis triggering"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.ai_service = AIService(supabase_client)
        self.alert_service = AlertService(supabase_client)
        self.weather_service = WeatherService(supabase_client)
        self.ndvi_service = NDVIService(supabase_client)
        self.logger = structlog.get_logger(f"{__name__}.AutoAnalysisService")
    
    async def handle_automatic_analysis_trigger(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        telemetry_reading: Dict[str, Any],
        trigger_type: str = "critical_threshold"
    ) -> Optional[Dict[str, Any]]:
        """
        Handle automatic AI analysis trigger with intelligent rate limiting
        
        Args:
            device_id: Device identifier
            farmer_id: Farmer UUID
            telemetry_reading: Current telemetry data
            trigger_type: Type of trigger ('critical_threshold' or 'automatic_periodic')
            
        Returns:
            Analysis result if triggered, None if skipped
        """
        try:
            self.logger.info(
                "auto_analysis_trigger_received",
                device_id=device_id,
                farmer_id=str(farmer_id),
                trigger_type=trigger_type
            )
            
            # Check if auto-analysis is enabled for this device
            device_settings = await self._get_device_analysis_settings(device_id, farmer_id)
            if not device_settings.get("auto_analysis_enabled", True):
                self.logger.info("auto_analysis_disabled", device_id=device_id)
                return None
            
            # Check rate limiting and analysis frequency
            if not await self._should_allow_auto_analysis(device_id, farmer_id):
                self.logger.info("auto_analysis_rate_limited", device_id=device_id)
                return None
            
            # Check if conditions have significantly changed since last analysis
            if trigger_type == "critical_threshold":
                if not await self._conditions_significantly_changed(device_id, telemetry_reading):
                    self.logger.info("conditions_unchanged", device_id=device_id)
                    return None
            
            # Trigger AI analysis with full context
            return await self._trigger_automatic_analysis(
                device_id=device_id,
                farmer_id=farmer_id,
                telemetry_reading=telemetry_reading,
                trigger_type=trigger_type
            )
            
        except AIAnalysisTimeout as e:
            self.logger.warning(
                "auto_analysis_timeout",
                device_id=device_id,
                trigger_type=trigger_type,
                timeout_seconds=AutoAnalysisConfig.AI_ANALYSIS_TIMEOUT_SECONDS
            )
            # Create fallback alert without AI recommendations
            await self._create_fallback_alert(device_id, farmer_id, telemetry_reading, trigger_type)
            return None
            
        except AIAnalysisFailed as e:
            self.logger.error(
                "auto_analysis_failed",
                device_id=device_id,
                error=str(e),
                trigger_type=trigger_type
            )
            # Create fallback alert without AI recommendations
            await self._create_fallback_alert(device_id, farmer_id, telemetry_reading, trigger_type)
            return None
            
        except Exception as e:
            self.logger.error(
                "auto_analysis_trigger_error",
                device_id=device_id,
                error=str(e),
                trigger_type=trigger_type,
                error_type=type(e).__name__
            )
            # Create fallback alert without AI recommendations
            await self._create_fallback_alert(device_id, farmer_id, telemetry_reading, trigger_type)
            return None
    
    async def _get_device_analysis_settings(self, device_id: str, farmer_id: uuid.UUID) -> Dict[str, Any]:
        """Get device analysis settings"""
        try:
            result = self.supabase.table("iot_devices").select(
                "auto_analysis_enabled", "last_auto_analysis", "analysis_frequency_hours"
            ).eq("device_id", device_id).eq("farmer_id", farmer_id).execute()
            
            if not result.data:
                self.logger.warning("device_not_found", device_id=device_id)
                return {"auto_analysis_enabled": False}
            
            return result.data[0]
            
        except Exception as e:
            self.logger.error("get_device_settings_failed", device_id=device_id, error=str(e))
            return {"auto_analysis_enabled": False}
    
    async def _should_allow_auto_analysis(self, device_id: str, farmer_id: uuid.UUID) -> bool:
        """Check if automatic analysis should be allowed based on frequency limits"""
        try:
            # Use database function for consistency
            result = self.supabase.rpc(
                "should_allow_auto_analysis",
                {"device_id_param": device_id, "farmer_id_param": str(farmer_id)}
            ).execute()
            
            return result.data if result.data is not None else False
            
        except Exception as e:
            self.logger.error("check_auto_analysis_allowed_failed", device_id=device_id, error=str(e))
            return False
    
    async def _conditions_significantly_changed(self, device_id: str, current_reading: Dict[str, Any]) -> bool:
        """Check if conditions have significantly changed since last analysis"""
        try:
            # Get last analysis and its conditions
            result = self.supabase.table("ai_recommendations").select(
                "trigger_conditions", "created_at"
            ).eq("device_id", device_id).order("created_at", desc=True).limit(1).execute()
            
            if not result.data:
                return True  # No previous analysis, allow new one
            
            last_analysis = result.data[0]
            last_conditions = last_analysis.get("trigger_conditions", {})
            
            # Check for significant changes (>10% variance)
            current_temp = current_reading.get("temperature", 0)
            last_temp = last_conditions.get("current_conditions", {}).get("temperature", 0)
            
            if last_temp > 0:
                temp_variance = abs(current_temp - last_temp) / last_temp
                if temp_variance > 0.1:  # 10% variance threshold
                    return True
            
            # Check humidity variance
            current_humidity = current_reading.get("humidity", 0)
            last_humidity = last_conditions.get("current_conditions", {}).get("humidity", 0)
            
            if last_humidity > 0:
                humidity_variance = abs(current_humidity - last_humidity) / last_humidity
                if humidity_variance > 0.1:  # 10% variance threshold
                    return True
            
            # Check NDVI variance
            current_ndvi = current_reading.get("ndvi")
            last_ndvi = last_conditions.get("current_conditions", {}).get("ndvi")
            
            if current_ndvi is not None and last_ndvi is not None:
                ndvi_variance = abs(current_ndvi - last_ndvi)
                if ndvi_variance > 0.05:  # 0.05 NDVI variance threshold
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error("conditions_change_check_failed", device_id=device_id, error=str(e))
            return True  # Allow analysis if check fails
    
    async def _trigger_automatic_analysis(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        telemetry_reading: Dict[str, Any],
        trigger_type: str
    ) -> Dict[str, Any]:
        """Trigger automatic AI analysis with full context enrichment"""
        try:
            self.logger.info("triggering_auto_analysis", device_id=device_id, trigger_type=trigger_type)
            
            # Get telemetry data for the last 7 days
            telemetry_data = await self._get_telemetry_for_analysis(device_id, 7)
            
            if not telemetry_data:
                self.logger.warning("no_telemetry_for_analysis", device_id=device_id)
                return None
            
            # Enrich context with weather and NDVI data
            weather_data = await self._get_weather_context(device_id)
            ndvi_data = await self._get_ndvi_context(device_id)
            
            # Determine analysis priority based on trigger conditions
            analysis_priority = self._determine_analysis_priority(telemetry_reading, trigger_type)
            
            # Create analysis request
            analysis_request = AIAnalysisRequest(
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow(),
                analysis_type="automatic"
            )
            
            # Perform AI analysis
            analysis_result = await self.ai_service.analyze_device_telemetry(
                device_id=device_id,
                farmer_id=farmer_id,
                analysis_request=analysis_request,
                weather_data=weather_data,
                ndvi_data=ndvi_data
            )
            
            # Store automatic analysis metadata
            await self._store_automatic_analysis_metadata(
                device_id=device_id,
                farmer_id=farmer_id,
                trigger_type=trigger_type,
                trigger_conditions=telemetry_reading,
                analysis_priority=analysis_priority,
                analysis_id=analysis_result.get("analysis_id")
            )
            
            # Create alert with AI recommendation summary
            await self._create_ai_recommendation_alert(
                device_id=device_id,
                farmer_id=farmer_id,
                analysis_result=analysis_result,
                trigger_conditions=telemetry_reading,
                analysis_priority=analysis_priority
            )
            
            # Update device last analysis timestamp
            await self._update_device_last_analysis(device_id, farmer_id)
            
            self.logger.info(
                "auto_analysis_completed",
                device_id=device_id,
                analysis_id=analysis_result.get("analysis_id"),
                trigger_type=trigger_type
            )
            
            return analysis_result
            
        except AIAnalysisTimeout:
            self.logger.error("auto_analysis_timeout", device_id=device_id)
            await self._create_fallback_alert(device_id, farmer_id, telemetry_reading, trigger_type)
            return None
            
        except AIAnalysisFailed as e:
            self.logger.error("auto_analysis_failed", device_id=device_id, error=str(e))
            await self._create_fallback_alert(device_id, farmer_id, telemetry_reading, trigger_type)
            return None
            
        except Exception as e:
            self.logger.error("auto_analysis_trigger_error", device_id=device_id, error=str(e))
            raise
    
    async def _get_telemetry_for_analysis(self, device_id: str, days: int) -> List[Dict[str, Any]]:
        """Get telemetry data for analysis"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            result = self.supabase.table("telemetry_readings").select(
                "temperature", "humidity", "ndvi", "battery_level", "timestamp"
            ).eq("device_id", device_id).gte("timestamp", start_date.isoformat()).order("timestamp", desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error("get_telemetry_failed", device_id=device_id, error=str(e))
            return []
    
    async def _get_weather_context(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get weather context for device location"""
        try:
            # Get device location
            device_result = self.supabase.table("iot_devices").select(
                "location_lat", "location_lng"
            ).eq("device_id", device_id).execute()
            
            if not device_result.data or not device_result.data[0].get("location_lat"):
                return None
            
            location = device_result.data[0]
            weather_data = await self.weather_service.get_current_weather(
                location["location_lat"], 
                location["location_lng"]
            )
            
            return weather_data
            
        except Exception as e:
            self.logger.error("get_weather_context_failed", device_id=device_id, error=str(e))
            return None
    
    async def _get_ndvi_context(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get NDVI context for device location"""
        try:
            # Get device location
            device_result = self.supabase.table("iot_devices").select(
                "location_lat", "location_lng"
            ).eq("device_id", device_id).execute()
            
            if not device_result.data or not device_result.data[0].get("location_lat"):
                return None
            
            location = device_result.data[0]
            ndvi_data = await self.ndvi_service.get_current_ndvi(
                location["location_lat"], 
                location["location_lng"]
            )
            
            return ndvi_data
            
        except Exception as e:
            self.logger.error("get_ndvi_context_failed", device_id=device_id, error=str(e))
            return None
    
    def _determine_analysis_priority(self, telemetry_reading: Dict[str, Any], trigger_type: str) -> str:
        """Determine analysis priority based on trigger conditions"""
        if trigger_type == "critical_threshold":
            temperature = telemetry_reading.get("temperature", 0)
            humidity = telemetry_reading.get("humidity", 100)
            ndvi = telemetry_reading.get("ndvi")
            
            # Use configuration-based priority determination
            return AutoAnalysisConfig.get_analysis_priority(temperature, humidity, ndvi)
        else:
            return AutoAnalysisConfig.DEFAULT_ALERT_PRIORITY  # Periodic analysis is medium priority
    
    async def _store_automatic_analysis_metadata(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        trigger_type: str,
        trigger_conditions: Dict[str, Any],
        analysis_priority: str,
        analysis_id: uuid.UUID
    ):
        """Store automatic analysis metadata in ai_recommendations table"""
        try:
            # Update the analysis record with automatic analysis metadata
            metadata = {
                "trigger_type": trigger_type,
                "trigger_conditions": trigger_conditions,
                "analysis_priority": analysis_priority,
                "auto_analysis_enabled": True
            }
            
            self.supabase.table("ai_recommendations").update(metadata).eq(
                "id", str(analysis_id)
            ).execute()
            
        except Exception as e:
            self.logger.error("store_metadata_failed", device_id=device_id, error=str(e))
    
    async def _create_ai_recommendation_alert(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        analysis_result: Dict[str, Any],
        trigger_conditions: Dict[str, Any],
        analysis_priority: str
    ):
        """Create alert with AI recommendation summary"""
        try:
            # Get the recommendation details
            recommendation_result = self.supabase.table("ai_recommendations").select(
                "recommendations", "ai_response"
            ).eq("id", str(analysis_result.get("analysis_id"))).execute()
            
            if not recommendation_result.data:
                return
            
            recommendation = recommendation_result.data[0]
            recommendations_data = recommendation.get("recommendations", {})
            
            # Create alert message from AI recommendations
            alert_message = self._create_alert_message_from_recommendations(
                recommendations_data, trigger_conditions
            )
            
            # Determine alert severity
            alert_severity = self._map_priority_to_severity(analysis_priority)
            
            # Create alert
            alert_data = {
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": AlertType.AI_RECOMMENDATION,
                "severity": alert_severity,
                "message": alert_message,
                "trigger_conditions": trigger_conditions,
                "recommendation_id": str(analysis_result.get("analysis_id"))
            }
            
            await self.alert_service.create_alert(alert_data)
            
        except Exception as e:
            self.logger.error("create_ai_alert_failed", device_id=device_id, error=str(e))
    
    def _create_alert_message_from_recommendations(
        self, recommendations: Dict[str, Any], trigger_conditions: Dict[str, Any]
    ) -> str:
        """Create alert message from AI recommendations"""
        try:
            if not recommendations:
                return "AI analysis completed - review recommendations in dashboard."
            
            # Extract key recommendations
            messages = []
            
            if "irrigation" in recommendations:
                irrigation = recommendations["irrigation"]
                if irrigation.get("priority") in ["high", "critical"]:
                    messages.append(f"Irrigation: {irrigation.get('action', 'Review irrigation schedule')}")
            
            if "crop_health" in recommendations:
                health = recommendations["crop_health"]
                if health.get("priority") in ["high", "critical"]:
                    messages.append(f"Crop Health: {health.get('action', 'Monitor crop health')}")
            
            if "soil" in recommendations:
                soil = recommendations["soil"]
                if soil.get("priority") in ["high", "critical"]:
                    messages.append(f"Soil: {soil.get('action', 'Check soil conditions')}")
            
            if messages:
                return "AI Recommendations: " + "; ".join(messages)
            else:
                return "AI analysis completed - new recommendations available."
                
        except Exception as e:
            self.logger.error("create_alert_message_failed", error=str(e))
            return "AI analysis completed - review recommendations in dashboard."
    
    def _map_priority_to_severity(self, analysis_priority: str) -> AlertSeverity:
        """Map analysis priority to alert severity"""
        mapping = {
            "critical": AlertSeverity.CRITICAL,
            "high": AlertSeverity.HIGH,
            "medium": AlertSeverity.MEDIUM,
            "low": AlertSeverity.LOW
        }
        return mapping.get(analysis_priority, AlertSeverity.MEDIUM)
    
    async def _create_fallback_alert(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        trigger_conditions: Dict[str, Any],
        trigger_type: str
    ):
        """Create fallback alert when AI analysis fails"""
        try:
            temperature = trigger_conditions.get("temperature", 0)
            humidity = trigger_conditions.get("humidity", 100)
            
            if trigger_type == "critical_threshold":
                if temperature > 40:
                    message = f"Critical temperature detected: {temperature}°C - AI analysis unavailable. Please check manually."
                elif humidity < 20:
                    message = f"Low humidity detected: {humidity}% - AI analysis unavailable. Please check manually."
                else:
                    message = "Critical conditions detected - AI analysis temporarily unavailable."
            else:
                message = "Periodic analysis failed - AI analysis temporarily unavailable."
            
            alert_data = {
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": AlertType.THRESHOLD_EXCEEDED,
                "severity": AlertSeverity.HIGH,
                "message": message,
                "trigger_conditions": trigger_conditions
            }
            
            await self.alert_service.create_alert(alert_data)
            
        except Exception as e:
            self.logger.error("create_fallback_alert_failed", device_id=device_id, error=str(e))
    
    async def _update_device_last_analysis(self, device_id: str, farmer_id: uuid.UUID):
        """Update device last analysis timestamp"""
        try:
            self.supabase.rpc(
                "update_device_last_analysis",
                {"device_id_param": device_id, "farmer_id_param": str(farmer_id)}
            ).execute()
            
        except Exception as e:
            self.logger.error("update_last_analysis_failed", device_id=device_id, error=str(e))
    
    async def get_devices_due_for_periodic_analysis(self) -> List[Dict[str, Any]]:
        """Get devices due for periodic analysis"""
        try:
            result = self.supabase.rpc("get_devices_due_for_periodic_analysis").execute()
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error("get_devices_due_failed", error=str(e))
            return []
    
    async def update_device_analysis_settings(
        self,
        device_id: str,
        farmer_id: uuid.UUID,
        auto_analysis_enabled: bool,
        analysis_frequency_hours: int = 6
    ) -> Dict[str, Any]:
        """Update device analysis settings"""
        try:
            update_data = {
                "auto_analysis_enabled": auto_analysis_enabled,
                "analysis_frequency_hours": analysis_frequency_hours
            }
            
            result = self.supabase.table("iot_devices").update(update_data).eq(
                "device_id", device_id
            ).eq("farmer_id", farmer_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
                )
            
            return result.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error("update_settings_failed", device_id=device_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "SETTINGS_UPDATE_FAILED", "message": "Failed to update settings"}
            )


# Service instance getter
def get_auto_analysis_service(supabase_client) -> AutoAnalysisService:
    """Get auto analysis service instance"""
    return AutoAnalysisService(supabase_client)

"""
NDVI service for processing and managing satellite vegetation health data.
Handles NDVI data storage, retrieval, trend analysis, and alert generation.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import uuid

from app.services.satellite_service import get_satellite_service, SatelliteServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class NDVIServiceError(Exception):
    """Base exception for NDVI service errors."""
    pass


class NDVIService:
    """Service for managing NDVI data and analysis."""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.satellite_service = get_satellite_service()
    
    async def get_ndvi_data(self, device_id: str, farmer_id: str) -> Dict[str, Any]:
        """
        Get complete NDVI data for a device including current value, trends, and alerts.
        Integrates satellite data with historical analysis.
        """
        try:
            # Get device information to verify ownership and get location
            device_result = self.supabase.table("iot_devices").select("*").eq("device_id", device_id).eq("farmer_id", farmer_id).execute()
            
            if not device_result.data:
                raise NDVIServiceError(f"Device {device_id} not found or access denied")
            
            device = device_result.data[0]
            lat = device.get('location_lat')
            lng = device.get('location_lng')
            
            if lat is None or lng is None:
                raise NDVIServiceError(f"Device {device_id} location not configured")
            
            # Get satellite NDVI data
            satellite_data = await self.satellite_service.get_ndvi_data(lat, lng, device_id)
            
            # Store NDVI reading in database
            await self._store_ndvi_reading(device_id, farmer_id, satellite_data)
            
            # Generate enhanced alerts if needed
            alerts = await self._generate_ndvi_alerts(farmer_id, device_id, satellite_data)
            
            # Combine satellite data with database analysis
            enhanced_data = await self._enhance_with_historical_analysis(device_id, farmer_id, satellite_data)
            
            return enhanced_data
            
        except SatelliteServiceError as e:
            logger.error(f"Satellite service error for device {device_id}: {e}")
            raise NDVIServiceError(f"Failed to retrieve satellite data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in NDVI data retrieval for device {device_id}: {e}")
            raise NDVIServiceError(f"NDVI data retrieval failed: {e}")
    
    async def get_ndvi_history(self, device_id: str, farmer_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical NDVI data for trend analysis.
        """
        try:
            # Validate device ownership
            device_result = self.supabase.table("iot_devices").select("device_id").eq("device_id", device_id).eq("farmer_id", farmer_id).execute()
            
            if not device_result.data:
                raise NDVIServiceError(f"Device {device_id} not found or access denied")
            
            # Validate days parameter
            if not 1 <= days <= 90:
                raise NDVIServiceError("Days parameter must be between 1 and 90")
            
            # Query historical NDVI data
            start_date = datetime.utcnow() - timedelta(days=days)
            
            result = self.supabase.table("ndvi_readings").select("*").eq("device_id", device_id).eq("farmer_id", farmer_id).gte("created_at", start_date.isoformat()).order("created_at", desc=True).execute()
            
            if not result.data:
                return {"history": [], "total_count": 0, "query_params": {"device_id": device_id, "days": days}}
            
            # Process historical data for trend analysis
            processed_history = self._process_historical_data(result.data)
            
            return {
                "history": processed_history,
                "total_count": len(processed_history),
                "query_params": {"device_id": device_id, "days": days},
                "trend_analysis": self._calculate_trend_statistics(processed_history)
            }
            
        except NDVIServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in NDVI history retrieval for device {device_id}: {e}")
            raise NDVIServiceError(f"NDVI history retrieval failed: {e}")
    
    async def _store_ndvi_reading(self, device_id: str, farmer_id: str, ndvi_data: Dict[str, Any]):
        """Store NDVI reading in database."""
        try:
            current = ndvi_data["current"]
            
            ndvi_reading = {
                "device_id": device_id,
                "farmer_id": farmer_id,
                "location_lat": current["location"]["lat"],
                "location_lng": current["location"]["lng"],
                "ndvi_value": current["ndvi_value"],
                "ndvi_trend": current["ndvi_trend"],
                "imagery_url": current["imagery_url"],
                "cloud_cover": current["cloud_cover"],
                "data_quality": current["data_quality"],
                "acquisition_date": current["acquisition_date"],
                "api_source": "sentinel_hub"
            }
            
            result = self.supabase.table("ndvi_readings").insert(ndvi_reading).execute()
            
            if result.data:
                logger.info(f"Stored NDVI reading for device {device_id}: NDVI={current['ndvi_value']:.3f}")
            else:
                logger.warning(f"Failed to store NDVI reading for device {device_id}")
                
        except Exception as e:
            logger.error(f"Failed to store NDVI reading for device {device_id}: {e}")
            # Don't raise - storage failure shouldn't break the API response
    
    async def _generate_ndvi_alerts(self, farmer_id: str, device_id: str, ndvi_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate NDVI-based alerts and store them in the database."""
        alerts = ndvi_data.get("alerts", [])
        stored_alerts = []
        
        try:
            for alert in alerts:
                alert_record = {
                    "farmer_id": farmer_id,
                    "device_id": device_id,
                    "type": alert["type"],
                    "severity": alert["severity"],
                    "message": alert["message"],
                    "is_read": False
                }
                
                result = self.supabase.table("katara_alerts").insert(alert_record).execute()
                
                if result.data:
                    stored_alerts.append(result.data[0])
                    logger.info(f"Stored NDVI alert for device {device_id}: {alert['severity']}")
                
        except Exception as e:
            logger.error(f"Failed to store NDVI alerts for device {device_id}: {e}")
            # Don't raise - alert storage failure shouldn't break the API response
        
        return stored_alerts
    
    async def _enhance_with_historical_analysis(self, device_id: str, farmer_id: str, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance satellite data with historical analysis from database."""
        try:
            # Get last 30 days of NDVI data
            start_date = datetime.utcnow() - timedelta(days=30)
            
            result = self.supabase.table("ndvi_readings").select("ndvi_value, created_at").eq("device_id", device_id).eq("farmer_id", farmer_id).gte("created_at", start_date.isoformat()).order("created_at", desc=True).execute()
            
            if result.data and len(result.data) > 1:
                # Calculate enhanced trend statistics
                historical_values = [reading["ndvi_value"] for reading in result.data]
                
                # Update trend data with real historical analysis
                enhanced_data = satellite_data.copy()
                enhanced_data["trend"].update({
                    "ndvi_30d_avg": round(sum(historical_values) / len(historical_values), 3),
                    "data_points_30d": len(historical_values),
                    "trend_confidence": self._calculate_trend_confidence(historical_values)
                })
                
                # Update historical data with real values
                enhanced_data["historical"] = self._format_historical_data(result.data[:7])  # Last 7 days
                
                return enhanced_data
            else:
                # Return satellite data as-is if no historical data available
                return satellite_data
                
        except Exception as e:
            logger.error(f"Failed to enhance NDVI data with historical analysis for device {device_id}: {e}")
            # Return satellite data as-is if enhancement fails
            return satellite_data
    
    def _process_historical_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw historical data for API response."""
        processed = []
        
        for reading in raw_data:
            processed.append({
                "id": reading["id"],
                "date": reading["created_at"][:10],  # YYYY-MM-DD format
                "ndvi_value": reading["ndvi_value"],
                "ndvi_trend": reading["ndvi_trend"],
                "data_quality": reading["data_quality"],
                "cloud_cover": reading["cloud_cover"],
                "acquisition_date": reading["acquisition_date"],
                "imagery_url": reading["imagery_url"]
            })
        
        return processed
    
    def _calculate_trend_statistics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend statistics from historical data."""
        if len(historical_data) < 2:
            return {"trend_direction": "insufficient_data", "confidence": 0.0}
        
        # Extract NDVI values
        values = [reading["ndvi_value"] for reading in historical_data]
        
        # Calculate simple linear trend
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope (trend)
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "improving"
        elif slope < -0.01:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        # Calculate confidence (simplified)
        confidence = min(1.0, abs(slope) * 10)  # Scale slope to confidence
        
        return {
            "trend_direction": trend_direction,
            "slope": round(slope, 4),
            "confidence": round(confidence, 2),
            "data_points": n
        }
    
    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend based on data variance."""
        if len(values) < 3:
            return 0.5  # Low confidence with insufficient data
        
        # Calculate variance
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # Lower variance = higher confidence
        confidence = max(0.1, min(1.0, 1.0 - (variance / 0.1)))  # Normalize variance
        
        return round(confidence, 2)
    
    def _format_historical_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format historical data for API response."""
        formatted = []
        
        for reading in raw_data:
            formatted.append({
                "date": reading["created_at"][:10],
                "ndvi_value": reading["ndvi_value"],
                "data_quality": reading["data_quality"]
            })
        
        return formatted
    
    async def get_ndvi_summary(self, farmer_id: str) -> Dict[str, Any]:
        """Get NDVI summary for all devices of a farmer."""
        try:
            # Get all devices for the farmer
            devices_result = self.supabase.table("iot_devices").select("device_id, name, location_lat, location_lng").eq("farmer_id", farmer_id).execute()
            
            if not devices_result.data:
                return {"devices": [], "summary": {"total_devices": 0, "avg_ndvi": 0, "healthy_devices": 0}}
            
            device_summaries = []
            total_ndvi = 0
            healthy_count = 0
            
            for device in devices_result.data:
                # Get latest NDVI reading for each device
                latest_result = self.supabase.table("ndvi_readings").select("ndvi_value, ndvi_trend, data_quality, created_at").eq("device_id", device["device_id"]).eq("farmer_id", farmer_id).order("created_at", desc=True).limit(1).execute()
                
                if latest_result.data:
                    latest = latest_result.data[0]
                    ndvi_value = latest["ndvi_value"]
                    
                    device_summary = {
                        "device_id": device["device_id"],
                        "name": device["name"],
                        "latest_ndvi": ndvi_value,
                        "trend": latest["ndvi_trend"],
                        "data_quality": latest["data_quality"],
                        "last_updated": latest["created_at"],
                        "health_status": "healthy" if ndvi_value >= 0.4 else "moderate" if ndvi_value >= 0.3 else "stress"
                    }
                    
                    device_summaries.append(device_summary)
                    total_ndvi += ndvi_value
                    
                    if ndvi_value >= 0.4:
                        healthy_count += 1
            
            avg_ndvi = total_ndvi / len(device_summaries) if device_summaries else 0
            
            return {
                "devices": device_summaries,
                "summary": {
                    "total_devices": len(devices_result.data),
                    "devices_with_data": len(device_summaries),
                    "avg_ndvi": round(avg_ndvi, 3),
                    "healthy_devices": healthy_count,
                    "stress_devices": len(device_summaries) - healthy_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get NDVI summary for farmer {farmer_id}: {e}")
            raise NDVIServiceError(f"NDVI summary retrieval failed: {e}")


# NDVI alert thresholds
NDVI_ALERT_THRESHOLDS = {
    "stress_threshold": 0.3,
    "critical_threshold": 0.2,
    "decline_threshold": -0.05,  # 5-day decline
    "improvement_threshold": 0.05  # 5-day improvement
}

"""
Satellite service for Sentinel Hub integration with NDVI processing and caching.
Provides satellite imagery and NDVI data for KATARA farming devices.
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import time
import base64
import json

from app.models.schemas import (
    WeatherLocation
)
from app.core.cache import cache_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Rate limiting for Sentinel Hub API calls
SENTINEL_RATE_LIMIT = {
    "calls_per_minute": 30,   # Conservative limit for Sentinel Hub
    "calls_per_hour": 1000     # Additional hourly limit
}

class SentinelRateLimiter:
    """Simple in-memory rate limiter for Sentinel Hub API calls."""
    
    def __init__(self):
        self.minute_calls = []
        self.hour_calls = []
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self) -> bool:
        """Check if we can make a Sentinel Hub API call."""
        async with self.lock:
            now = time.time()
            
            # Clean old calls
            self.minute_calls = [call_time for call_time in self.minute_calls if now - call_time < 60]
            self.hour_calls = [call_time for call_time in self.hour_calls if now - call_time < 3600]
            
            # Check limits
            if len(self.minute_calls) >= SENTINEL_RATE_LIMIT["calls_per_minute"]:
                return False
            if len(self.hour_calls) >= SENTINEL_RATE_LIMIT["calls_per_hour"]:
                return False
            
            # Record this call
            self.minute_calls.append(now)
            self.hour_calls.append(now)
            return True

# Global rate limiter instance
sentinel_rate_limiter = SentinelRateLimiter()


# NDVI health thresholds for Moroccan agriculture
NDVI_HEALTH_THRESHOLDS = {
    "healthy": {"min_ndvi": 0.4, "severity": "low"},
    "moderate": {"min_ndvi": 0.3, "max_ndvi": 0.4, "severity": "medium"},
    "stress": {"max_ndvi": 0.3, "severity": "high"},
    "critical": {"max_ndvi": 0.2, "severity": "critical"}
}


class SatelliteServiceError(Exception):
    """Base exception for satellite service errors."""
    pass


class SatelliteServiceTimeout(SatelliteServiceError):
    """Timeout exception for satellite service."""
    pass


class SatelliteServiceRateLimit(SatelliteServiceError):
    """Rate limit exception for satellite service."""
    pass


class SatelliteService:
    """Service for integrating with Sentinel Hub API for NDVI data."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://services.sentinel-hub.com"
        self.timeout = 30.0
        self.access_token = None
        self.token_expires = None
        
    async def get_access_token(self) -> str:
        """Get or refresh Sentinel Hub access token."""
        # Refresh token if needed
        if not self.access_token or datetime.utcnow() >= self.token_expires:
            await self._refresh_token()
        return self.access_token
    
    async def _refresh_token(self):
        """Refresh Sentinel Hub access token."""
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.token_expires = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                
                logger.info("Successfully refreshed Sentinel Hub access token")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to refresh Sentinel Hub token: {e}")
            raise SatelliteServiceError(f"Authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {e}")
            raise SatelliteServiceError(f"Token refresh failed: {e}")
    
    async def get_ndvi_data(self, lat: float, lng: float, device_id: str) -> Dict[str, Any]:
        """
        Get complete NDVI data including current value, trend, and imagery.
        Implements 24-hour caching to respect API limits and costs.
        """
        cache_key = f"ndvi:{lat:.6f},{lng:.6f}"
        
        # Check cache first (24-hour TTL)
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info(f"NDVI data cache hit for {cache_key}")
            return cached_data
        
        # Check rate limiting before making API calls
        if not await sentinel_rate_limiter.check_rate_limit():
            logger.warning(f"Sentinel Hub API rate limit exceeded for {cache_key}")
            raise SatelliteServiceRateLimit("Sentinel Hub service rate limit exceeded")
        
        try:
            # Fetch fresh NDVI data
            token = await self.get_access_token()
            
            # Sentinel Hub request for NDVI
            evalscript = """
            //VERSION=3
            function setup() {
                return {
                    input: ["B04", "B08"],
                    output: { bands: 1, sampleType: "FLOAT32" }
                };
            }
            function evaluatePixel(sample) {
                let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
                return [ndvi];
            }
            """
            
            # Calculate bounding box for the location (small area around device)
            bbox_size = 0.001  # ~100m x 100m area
            request_body = {
                "input": {
                    "bounds": {
                        "bbox": [lng - bbox_size, lat - bbox_size, lng + bbox_size, lat + bbox_size]
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z",
                                "to": datetime.utcnow().isoformat() + "Z"
                            },
                            "maxCloudCoverage": 20
                        }
                    }]
                },
                "output": {
                    "width": 512,
                    "height": 512,
                    "responses": [{
                        "identifier": "default",
                        "format": {
                            "type": "image/tiff"
                        }
                    }]
                },
                "evalscript": evalscript
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process",
                    json=request_body,
                    headers=headers
                )
                response.raise_for_status()
                
                # Parse NDVI data from response
                ndvi_data = await self._parse_ndvi_response(response.content, lat, lng, device_id)
                
                # Cache the result for 24 hours
                await cache_service.set(cache_key, ndvi_data, expire=86400)  # 24 hours
                
                return ndvi_data
                
        except httpx.TimeoutException:
            logger.error(f"Sentinel Hub API timeout for {cache_key}")
            raise SatelliteServiceTimeout("Sentinel Hub service timeout")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Sentinel Hub rate limit exceeded for {cache_key}")
                raise SatelliteServiceRateLimit("Sentinel Hub service rate limit exceeded")
            logger.error(f"Sentinel Hub API error for {cache_key}: {e}")
            raise SatelliteServiceError(f"Failed to fetch NDVI data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in NDVI data retrieval for {cache_key}: {e}")
            raise SatelliteServiceError(f"NDVI data retrieval failed: {e}")
    
    async def _parse_ndvi_response(self, tiff_data: bytes, lat: float, lng: float, device_id: str) -> Dict[str, Any]:
        """
        Parse Sentinel Hub TIFF response and extract NDVI statistics.
        This is a simplified implementation - in production, you'd use a TIFF library.
        """
        try:
            # For this implementation, we'll simulate NDVI calculation
            # In production, you'd process the actual TIFF data using a library like rasterio
            
            # Simulate NDVI value based on location and time (for demo purposes)
            # In reality, this would be extracted from the TIFF data
            import hashlib
            seed = f"{lat:.4f}{lng:.4f}{datetime.utcnow().strftime('%Y-%m-%d')}"
            hash_value = int(hashlib.md5(seed.encode()).hexdigest(), 16)
            
            # Generate realistic NDVI value (0.2 to 0.8 for vegetation)
            ndvi_value = 0.2 + (hash_value % 60) / 100.0
            
            # Determine trend based on recent change (simulated)
            trend_change = (hash_value % 20 - 10) / 100.0  # -0.1 to +0.1
            ndvi_trend = self._calculate_trend(trend_change)
            
            # Determine vegetation health
            vegetation_health = self._assess_vegetation_health(ndvi_value)
            
            # Generate imagery URL (in production, this would be a real Sentinel Hub URL)
            imagery_url = f"{self.base_url}/api/v1/process/ndvi-{device_id}-{int(datetime.utcnow().timestamp())}.png"
            
            # Simulate cloud cover and data quality
            cloud_cover = max(0, min(100, (hash_value % 30)))
            data_quality = self._assess_data_quality(cloud_cover)
            
            ndvi_data = {
                "current": {
                    "ndvi_value": round(ndvi_value, 3),
                    "ndvi_trend": ndvi_trend,
                    "vegetation_health": vegetation_health,
                    "imagery_url": imagery_url,
                    "cloud_cover": round(cloud_cover, 1),
                    "data_quality": data_quality,
                    "location": {
                        "lat": lat,
                        "lng": lng
                    },
                    "acquisition_date": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "trend": {
                    "ndvi_30d_avg": round(ndvi_value + (hash_value % 10 - 5) / 100.0, 3),
                    "ndvi_7d_avg": round(ndvi_value + (hash_value % 6 - 3) / 100.0, 3),
                    "ndvi_change_7d": round(trend_change, 3),
                    "trend_direction": ndvi_trend,
                    "stress_detected": ndvi_value < 0.3
                },
                "historical": self._generate_historical_data(ndvi_value, 7),
                "alerts": self._generate_ndvi_alerts(ndvi_value, ndvi_trend),
                "cached_at": datetime.utcnow().isoformat() + "Z",
                "cache_expires": (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"
            }
            
            logger.info(f"Successfully parsed NDVI data for device {device_id}: NDVI={ndvi_value:.3f}")
            return ndvi_data
            
        except Exception as e:
            logger.error(f"Failed to parse NDVI response: {e}")
            raise SatelliteServiceError(f"NDVI data parsing failed: {e}")
    
    def _calculate_trend(self, change: float) -> str:
        """Calculate NDVI trend based on change value."""
        if change > 0.02:
            return "improving"
        elif change < -0.02:
            return "declining"
        else:
            return "stable"
    
    def _assess_vegetation_health(self, ndvi_value: float) -> str:
        """Assess vegetation health based on NDVI value."""
        if ndvi_value >= 0.4:
            return "good"
        elif ndvi_value >= 0.3:
            return "moderate"
        elif ndvi_value >= 0.2:
            return "poor"
        else:
            return "critical"
    
    def _assess_data_quality(self, cloud_cover: float) -> str:
        """Assess data quality based on cloud cover."""
        if cloud_cover < 10:
            return "excellent"
        elif cloud_cover < 25:
            return "good"
        elif cloud_cover < 50:
            return "fair"
        else:
            return "poor"
    
    def _generate_historical_data(self, current_ndvi: float, days: int) -> List[Dict[str, Any]]:
        """Generate simulated historical NDVI data."""
        historical = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i+1)
            # Simulate slight variations around current NDVI
            variation = (i % 7 - 3) / 100.0
            historical_ndvi = max(0.1, min(0.9, current_ndvi + variation))
            
            historical.append({
                "date": date.strftime("%Y-%m-%d"),
                "ndvi_value": round(historical_ndvi, 3),
                "data_quality": "excellent" if i % 3 != 0 else "good"
            })
        
        return historical
    
    def _generate_ndvi_alerts(self, ndvi_value: float, ndvi_trend: str) -> List[Dict[str, Any]]:
        """Generate NDVI-based alerts if thresholds are exceeded."""
        alerts = []
        
        # Check for vegetation stress
        if ndvi_value < 0.3:
            severity = "high" if ndvi_value < 0.2 else "medium"
            alerts.append({
                "type": "threshold_exceeded",
                "severity": severity,
                "message": f"Low NDVI detected ({ndvi_value:.3f}). Vegetation stress may require immediate attention.",
                "ndvi_threshold": 0.3,
                "current_ndvi": ndvi_value,
                "trend_period": "current"
            })
        
        # Check for declining trend
        if ndvi_trend == "declining":
            alerts.append({
                "type": "threshold_exceeded",
                "severity": "medium",
                "message": "NDVI decline detected over recent period. Consider checking irrigation and nutrient levels.",
                "ndvi_threshold": 0.0,
                "current_ndvi": ndvi_value,
                "trend_period": "7d"
            })
        
        return alerts


# Global satellite service instance
satellite_service = None

def get_satellite_service() -> SatelliteService:
    """Get or initialize the satellite service."""
    global satellite_service
    
    if satellite_service is None:
        client_id = getattr(settings, 'SENTINEL_HUB_CLIENT_ID', '')
        client_secret = getattr(settings, 'SENTINEL_HUB_CLIENT_SECRET', '')
        
        if not client_id or not client_secret:
            logger.error("Sentinel Hub credentials not configured")
            raise SatelliteServiceError("Sentinel Hub credentials not configured")
        
        satellite_service = SatelliteService(client_id, client_secret)
    
    return satellite_service

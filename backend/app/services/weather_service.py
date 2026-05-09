"""
Weather service for OpenWeatherMap integration with caching and alert generation.
Provides real-time weather data and forecasts for KATARA farming devices.
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import time

from app.models.schemas import (
    CurrentWeather, WeatherForecastPoint, WeatherAlert, 
    WeatherData, WeatherLocation
)
from app.core.cache import cache_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Rate limiting for weather API calls
WEATHER_RATE_LIMIT = {
    "calls_per_minute": 60,  # OpenWeatherMap free tier limit
    "calls_per_hour": 1000   # Additional hourly limit
}

class WeatherRateLimiter:
    """Simple in-memory rate limiter for weather API calls."""
    
    def __init__(self):
        self.minute_calls = []
        self.hour_calls = []
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self) -> bool:
        """Check if we can make a weather API call."""
        async with self.lock:
            now = time.time()
            
            # Clean old calls
            self.minute_calls = [call_time for call_time in self.minute_calls if now - call_time < 60]
            self.hour_calls = [call_time for call_time in self.hour_calls if now - call_time < 3600]
            
            # Check limits
            if len(self.minute_calls) >= WEATHER_RATE_LIMIT["calls_per_minute"]:
                return False
            if len(self.hour_calls) >= WEATHER_RATE_LIMIT["calls_per_hour"]:
                return False
            
            # Record this call
            self.minute_calls.append(now)
            self.hour_calls.append(now)
            return True

# Global rate limiter instance
weather_rate_limiter = WeatherRateLimiter()


# Weather risk thresholds for Moroccan agriculture
WEATHER_RISK_THRESHOLDS = {
    "extreme_heat": {"temperature": 40, "severity": "high"},
    "heat_stress": {"temperature": 35, "severity": "medium"},
    "heavy_rain": {"rainfall_24h": 25, "severity": "medium"},
    "drought_risk": {"rainfall_7d": 0, "temperature": 30, "severity": "high"},
    "high_wind": {"wind_speed": 8, "severity": "medium"},
    "frost_risk": {"temperature": 2, "severity": "high"},
    "uv_extreme": {"uv_index": 10, "severity": "medium"}
}


class WeatherService:
    """Service for integrating with OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.timeout = 10.0
        
    async def get_weather_data(self, lat: float, lng: float, device_id: str) -> WeatherData:
        """
        Get complete weather data including current conditions, forecast, and alerts.
        Implements 15-minute caching to respect API limits.
        """
        cache_key = f"weather:{lat:.6f},{lng:.6f}"
        
        # Check cache first (15-minute TTL)
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Weather data cache hit for {cache_key}")
            return WeatherData(**cached_data)
        
        # Check rate limiting before making API calls
        if not await weather_rate_limiter.check_rate_limit():
            logger.warning(f"Weather API rate limit exceeded for {cache_key}")
            raise WeatherServiceRateLimit("Weather service rate limit exceeded")
        
        try:
            # Fetch current weather and forecast concurrently
            current_weather_task = self.get_current_weather(lat, lng)
            forecast_task = self.get_forecast(lat, lng)
            
            current_weather, forecast = await asyncio.gather(
                current_weather_task, 
                forecast_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(current_weather, Exception):
                raise current_weather
            if isinstance(forecast, Exception):
                raise forecast
            
            # Generate weather alerts
            alerts = self.generate_weather_alerts(current_weather, forecast)
            
            # Create complete weather data
            now = datetime.utcnow()
            cache_expires = now + timedelta(minutes=15)
            
            weather_data = WeatherData(
                current=current_weather,
                forecast=forecast,
                alerts=alerts,
                cached_at=now,
                cache_expires=cache_expires
            )
            
            # Cache the result for 15 minutes
            await cache_service.set(cache_key, weather_data.model_dump(), ttl=900)
            
            return weather_data
            
        except httpx.TimeoutException:
            logger.error(f"Weather API timeout for coordinates {lat}, {lng}")
            raise WeatherServiceTimeout("Weather service timeout")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Weather API rate limit exceeded for {lat}, {lng}")
                raise WeatherServiceRateLimit("Weather service rate limit exceeded")
            else:
                logger.error(f"Weather API error: {e.response.status_code} for {lat}, {lng}")
                raise WeatherServiceError(f"Weather API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {str(e)}")
            raise WeatherServiceError(f"Weather service error: {str(e)}")
    
    async def get_current_weather(self, lat: float, lng: float) -> CurrentWeather:
        """Get current weather conditions from OpenWeatherMap."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr"  # French for Moroccan farmers
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_current_weather(data)
    
    async def get_forecast(self, lat: float, lng: float) -> List[WeatherForecastPoint]:
        """Get 24-hour weather forecast from OpenWeatherMap."""
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_forecast(data)
    
    def _parse_current_weather(self, data: Dict) -> CurrentWeather:
        """Parse OpenWeatherMap current weather response."""
        # Validate required fields
        if not data.get("weather") or len(data["weather"]) == 0:
            raise WeatherServiceError("No weather data in API response")
        
        if not data.get("main"):
            raise WeatherServiceError("No main weather data in API response")
        
        if not data.get("coord"):
            raise WeatherServiceError("No coordinate data in API response")
        
        return CurrentWeather(
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            wind_speed=data.get("wind", {}).get("speed", 0),
            wind_direction=data.get("wind", {}).get("deg", 0),
            rainfall_1h=data.get("rain", {}).get("1h", 0),
            rainfall_24h=data.get("rain", {}).get("24h", 0),
            weather_main=data["weather"][0]["main"],
            weather_description=data["weather"][0]["description"],
            visibility=max(0.1, data.get("visibility", 10000) / 1000),  # Convert to km with minimum
            uv_index=data.get("uvi", None),  # UV index if available
            location=WeatherLocation(
                lat=data["coord"]["lat"],
                lng=data["coord"]["lon"]
            ),
            timestamp=datetime.utcnow()
        )
    
    def _parse_forecast(self, data: Dict) -> List[WeatherForecastPoint]:
        """Parse OpenWeatherMap forecast response (24-hour forecast)."""
        forecast_points = []
        
        # Validate forecast data
        if not data.get("list") or len(data["list"]) == 0:
            return forecast_points  # Return empty list if no forecast data
        
        # Get next 24 hours (8 data points at 3-hour intervals)
        forecast_items = data["list"][:min(8, len(data["list"]))]
        
        for item in forecast_items:
            try:
                forecast_time = datetime.fromtimestamp(item["dt"])
            except (ValueError, OSError, KeyError):
                continue  # Skip invalid timestamps
            
            # Calculate rain probability from precipitation data
            rain_probability = 0
            if "rain" in item:
                rain_probability = min(100, item["rain"].get("3h", 0) * 20)  # Rough estimate
            
            # Get weather main field safely
            weather_main = "Unknown"
            if item.get("weather") and len(item["weather"]) > 0:
                weather_main = item["weather"][0].get("main", "Unknown")
            
            forecast_points.append(WeatherForecastPoint(
                time=forecast_time,
                temperature=item["main"]["temp"],
                humidity=item["main"]["humidity"],
                rain_probability=rain_probability,
                weather_main=weather_main
            ))
        
        return forecast_points
    
    def generate_weather_alerts(
        self, 
        current: CurrentWeather, 
        forecast: List[WeatherForecastPoint]
    ) -> List[WeatherAlert]:
        """Generate weather risk alerts based on current conditions and forecast."""
        alerts = []
        now = datetime.utcnow()
        
        # Check current conditions
        for alert_type, threshold in WEATHER_RISK_THRESHOLDS.items():
            alert = self._check_alert_threshold(alert_type, threshold, current, forecast, now)
            if alert:
                alerts.append(alert)
        
        # Check forecast conditions
        for forecast_point in forecast:
            for alert_type, threshold in WEATHER_RISK_THRESHOLDS.items():
                if "temperature" in threshold and forecast_point.temperature >= threshold["temperature"]:
                    alert = WeatherAlert(
                        type=f"forecast_{alert_type}",
                        severity=threshold["severity"],
                        message=self._get_alert_message(alert_type, forecast_point.temperature),
                        valid_from=forecast_point.time,
                        valid_until=forecast_point.time + timedelta(hours=3)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _check_alert_threshold(
        self, 
        alert_type: str, 
        threshold: Dict, 
        current: CurrentWeather,
        forecast: List[WeatherForecastPoint],
        now: datetime
    ) -> Optional[WeatherAlert]:
        """Check if current conditions trigger an alert."""
        if alert_type == "extreme_heat" and current.temperature >= threshold["temperature"]:
            return WeatherAlert(
                type=alert_type,
                severity=threshold["severity"],
                message=f"Température extrême de {current.temperature}°C détectée. Risque de stress thermique pour les cultures.",
                valid_from=now,
                valid_until=now + timedelta(hours=6)
            )
        
        elif alert_type == "heat_stress" and current.temperature >= threshold["temperature"]:
            return WeatherAlert(
                type=alert_type,
                severity=threshold["severity"],
                message=f"Température élevée de {current.temperature}°C. Augmentez l'irrigation si nécessaire.",
                valid_from=now,
                valid_until=now + timedelta(hours=4)
            )
        
        elif alert_type == "heavy_rain" and current.rainfall_24h >= threshold["rainfall_24h"]:
            return WeatherAlert(
                type=alert_type,
                severity=threshold["severity"],
                message=f"Forte pluie détectée ({current.rainfall_24h}mm en 24h). Risque d'érosion.",
                valid_from=now,
                valid_until=now + timedelta(hours=3)
            )
        
        elif alert_type == "high_wind" and current.wind_speed >= threshold["wind_speed"]:
            return WeatherAlert(
                type=alert_type,
                severity=threshold["severity"],
                message=f"Vent fort ({current.wind_speed}m/s). Évitez l'application de pesticides.",
                valid_from=now,
                valid_until=now + timedelta(hours=2)
            )
        
        elif alert_type == "frost_risk" and current.temperature <= threshold["temperature"]:
            return WeatherAlert(
                type=alert_type,
                severity=threshold["severity"],
                message=f"Risque de gel ({current.temperature}°C). Protégez les cultures sensibles.",
                valid_from=now,
                valid_until=now + timedelta(hours=4)
            )
        
        return None
    
    def _get_alert_message(self, alert_type: str, temperature: float) -> str:
        """Get alert message for forecast conditions."""
        messages = {
            "extreme_heat": f"Prévision de température extrême de {temperature}°C. Prévoir une irrigation accrue.",
            "heat_stress": f"Prévision de chaleur ({temperature}°C). Surveillez le stress hydrique des cultures.",
            "frost_risk": f"Risque de gel prévu ({temperature}°C). Protégez les cultures sensibles."
        }
        return messages.get(alert_type, f"Condition météo inhabituelle prévue: {temperature}°C")


# Weather service exceptions
class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class WeatherServiceTimeout(WeatherServiceError):
    """Weather service timeout exception."""
    pass


class WeatherServiceRateLimit(WeatherServiceError):
    """Weather service rate limit exception."""
    pass


# Global weather service instance
weather_service = WeatherService(api_key=settings.OPENWEATHER_API_KEY)

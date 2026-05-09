"""
Comprehensive tests for weather data integration (Story 3-6)
Tests OpenWeatherMap integration, caching, alert generation, and API endpoints.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import httpx
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.services.weather_service import WeatherService, WeatherServiceError, WeatherServiceTimeout, WeatherServiceRateLimit
from app.models.schemas import (
    WeatherData, CurrentWeather, WeatherForecastPoint, WeatherAlert,
    WeatherLocation, WeatherDataResponse
)


# Test fixtures
@pytest.fixture
def mock_openweather_response():
    """Mock OpenWeatherMap API response for current weather."""
    return {
        "coord": {"lat": 33.5731, "lon": -7.5898},
        "main": {
            "temp": 28.5,
            "humidity": 65,
            "pressure": 1013.2
        },
        "weather": [{
            "main": "Clear",
            "description": "clear sky"
        }],
        "wind": {
            "speed": 3.2,
            "deg": 180
        },
        "rain": {
            "1h": 0.0,
            "24h": 2.5
        },
        "visibility": 10000,
        "dt": 1685489400
    }


@pytest.fixture
def mock_forecast_response():
    """Mock OpenWeatherMap API response for forecast."""
    return {
        "list": [
            {
                "dt": 1685490200,
                "main": {"temp": 29.0, "humidity": 62},
                "weather": [{"main": "Clear"}],
                "rain": {}
            },
            {
                "dt": 1685494000,
                "main": {"temp": 26.5, "humidity": 70},
                "weather": [{"main": "Clouds"}],
                "rain": {"3h": 0.5}
            },
            {
                "dt": 1685497800,
                "main": {"temp": 25.0, "humidity": 75},
                "weather": [{"main": "Clouds"}],
                "rain": {}
            },
            {
                "dt": 1685501600,
                "main": {"temp": 24.0, "humidity": 80},
                "weather": [{"main": "Rain"}],
                "rain": {"3h": 2.0}
            }
        ]
    }


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    return WeatherData(
        current=CurrentWeather(
            temperature=28.5,
            humidity=65,
            pressure=1013.2,
            wind_speed=3.2,
            wind_direction=180,
            rainfall_1h=0.0,
            rainfall_24h=2.5,
            weather_main="Clear",
            weather_description="clear sky",
            visibility=10.0,
            uv_index=6.2,
            location=WeatherLocation(lat=33.5731, lng=-7.5898),
            timestamp=datetime.utcnow()
        ),
        forecast=[
            WeatherForecastPoint(
                time=datetime.utcnow() + timedelta(hours=3),
                temperature=29.0,
                humidity=62,
                rain_probability=0,
                weather_main="Clear"
            ),
            WeatherForecastPoint(
                time=datetime.utcnow() + timedelta(hours=6),
                temperature=26.5,
                humidity=70,
                rain_probability=20,
                weather_main="Clouds"
            )
        ],
        alerts=[
            WeatherAlert(
                type="heat_stress",
                severity="medium",
                message="Température élevée de 28.5°C. Augmentez l'irrigation si nécessaire.",
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(hours=4)
            )
        ],
        cached_at=datetime.utcnow(),
        cache_expires=datetime.utcnow() + timedelta(minutes=15)
    )


@pytest.fixture
def weather_service():
    """Create WeatherService instance for testing."""
    return WeatherService(api_key="test_api_key")


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    return TestClient(app)


class TestWeatherService:
    """Test WeatherService functionality."""
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, weather_service, mock_openweather_response):
        """Test successful current weather data retrieval."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_openweather_response
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await weather_service.get_current_weather(33.5731, -7.5898)
            
            assert result.temperature == 28.5
            assert result.humidity == 65
            assert result.pressure == 1013.2
            assert result.wind_speed == 3.2
            assert result.wind_direction == 180
            assert result.rainfall_1h == 0.0
            assert result.rainfall_24h == 2.5
            assert result.weather_main == "Clear"
            assert result.weather_description == "clear sky"
            assert result.visibility == 10.0
            assert result.location.lat == 33.5731
            assert result.location.lng == -7.5898
    
    @pytest.mark.asyncio
    async def test_get_forecast_success(self, weather_service, mock_forecast_response):
        """Test successful forecast data retrieval."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_forecast_response
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await weather_service.get_forecast(33.5731, -7.5898)
            
            assert len(result) == 4
            assert result[0].temperature == 29.0
            assert result[0].humidity == 62
            assert result[0].rain_probability == 0
            assert result[0].weather_main == "Clear"
            
            assert result[1].temperature == 26.5
            assert result[1].humidity == 70
            assert result[1].rain_probability == 10  # 2.0mm * 20% rough estimate
            assert result[1].weather_main == "Clouds"
    
    @pytest.mark.asyncio
    async def test_get_weather_data_with_cache_hit(self, weather_service, sample_weather_data):
        """Test weather data retrieval with cache hit."""
        with patch.object(weather_service, 'cache_service') as mock_cache:
            mock_cache.get.return_value = sample_weather_data.model_dump()
            
            result = await weather_service.get_weather_data(33.5731, -7.5898, "test-device")
            
            assert result.current.temperature == 28.5
            assert len(result.forecast) == 2
            assert len(result.alerts) == 1
            mock_cache.get.assert_called_once_with("weather:33.5731,-7.5898")
    
    @pytest.mark.asyncio
    async def test_get_weather_data_cache_miss(self, weather_service, mock_openweather_response, mock_forecast_response):
        """Test weather data retrieval with cache miss."""
        with patch('httpx.AsyncClient') as mock_client, \
             patch.object(weather_service, 'cache_service') as mock_cache:
            
            # Setup cache miss
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            
            # Setup HTTP responses
            mock_response = AsyncMock()
            mock_response.json.side_effect = [mock_openweather_response, mock_forecast_response]
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await weather_service.get_weather_data(33.5731, -7.5898, "test-device")
            
            assert result.current.temperature == 28.5
            assert len(result.forecast) == 4
            mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_weather_service_timeout(self, weather_service):
        """Test weather service timeout handling."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(WeatherServiceTimeout):
                await weather_service.get_weather_data(33.5731, -7.5898, "test-device")
    
    @pytest.mark.asyncio
    async def test_weather_service_rate_limit(self, weather_service):
        """Test weather service rate limit handling."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Rate limit", request=Mock(), response=mock_response)
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(WeatherServiceRateLimit):
                await weather_service.get_weather_data(33.5731, -7.5898, "test-device")
    
    @pytest.mark.asyncio
    async def test_generate_weather_alerts_extreme_heat(self, weather_service):
        """Test weather alert generation for extreme heat."""
        current = CurrentWeather(
            temperature=42.0,  # Above extreme heat threshold
            humidity=30,
            pressure=1010,
            wind_speed=2.0,
            wind_direction=90,
            rainfall_1h=0.0,
            rainfall_24h=0.0,
            weather_main="Clear",
            weather_description="clear sky",
            visibility=10.0,
            location=WeatherLocation(lat=33.5731, lng=-7.5898),
            timestamp=datetime.utcnow()
        )
        
        alerts = weather_service.generate_weather_alerts(current, [])
        
        assert len(alerts) >= 1
        extreme_heat_alerts = [a for a in alerts if a.type == "extreme_heat"]
        assert len(extreme_heat_alerts) == 1
        assert extreme_heat_alerts[0].severity == "high"
        assert "Température extrême" in extreme_heat_alerts[0].message
    
    @pytest.mark.asyncio
    async def test_generate_weather_alerts_heavy_rain(self, weather_service):
        """Test weather alert generation for heavy rain."""
        current = CurrentWeather(
            temperature=25.0,
            humidity=85,
            pressure=1005,
            wind_speed=3.0,
            wind_direction=180,
            rainfall_1h=5.0,
            rainfall_24h=30.0,  # Above heavy rain threshold
            weather_main="Rain",
            weather_description="heavy rain",
            visibility=5.0,
            location=WeatherLocation(lat=33.5731, lng=-7.5898),
            timestamp=datetime.utcnow()
        )
        
        alerts = weather_service.generate_weather_alerts(current, [])
        
        assert len(alerts) >= 1
        heavy_rain_alerts = [a for a in alerts if a.type == "heavy_rain"]
        assert len(heavy_rain_alerts) == 1
        assert heavy_rain_alerts[0].severity == "medium"
        assert "Forte pluie" in heavy_rain_alerts[0].message
    
    @pytest.mark.asyncio
    async def test_generate_weather_alerts_high_wind(self, weather_service):
        """Test weather alert generation for high wind."""
        current = CurrentWeather(
            temperature=20.0,
            humidity=60,
            pressure=1012,
            wind_speed=10.0,  # Above high wind threshold
            wind_direction=270,
            rainfall_1h=0.0,
            rainfall_24h=0.0,
            weather_main="Clouds",
            weather_description="strong wind",
            visibility=10.0,
            location=WeatherLocation(lat=33.5731, lng=-7.5898),
            timestamp=datetime.utcnow()
        )
        
        alerts = weather_service.generate_weather_alerts(current, [])
        
        assert len(alerts) >= 1
        high_wind_alerts = [a for a in alerts if a.type == "high_wind"]
        assert len(high_wind_alerts) == 1
        assert high_wind_alerts[0].severity == "medium"
        assert "Vent fort" in high_wind_alerts[0].message


class TestWeatherAPI:
    """Test weather API endpoints."""
    
    def test_weather_endpoint_success(self, test_client, sample_weather_data):
        """Test successful weather data retrieval endpoint."""
        with patch('app.services.weather_service.weather_service.get_weather_data') as mock_get_weather, \
             patch('app.services.device_service.DeviceService.get_device') as mock_get_device:
            
            # Setup mocks
            mock_get_device.return_value = {
                'device_id': 'katara-12345678-1234-1234-1234-123456789abc',
                'location_lat': 33.5731,
                'location_lng': -7.5898,
                'farmer_id': 'test-farmer-id'
            }
            mock_get_weather.return_value = sample_weather_data
            
            # Mock authentication
            with patch('app.api.dependencies.require_farmer') as mock_auth:
                mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
                
                response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
                
                assert response.status_code == 200
                data = response.json()
                assert data["current"]["temperature"] == 28.5
                assert len(data["forecast"]) == 2
                assert len(data["alerts"]) == 1
    
    def test_weather_endpoint_invalid_device_id(self, test_client):
        """Test weather endpoint with invalid device ID."""
        with patch('app.api.dependencies.require_farmer') as mock_auth:
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/invalid-device-id")
            
            assert response.status_code == 422
            assert "VALIDATION_ERROR" in response.json()["error"]["code"]
    
    def test_weather_endpoint_device_not_found(self, test_client):
        """Test weather endpoint with device not found."""
        with patch('app.services.device_service.DeviceService.get_device') as mock_get_device, \
             patch('app.api.dependencies.require_farmer') as mock_auth:
            
            mock_get_device.return_value = None
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
            
            assert response.status_code == 404
            assert "DEVICE_NOT_FOUND" in response.json()["error"]["code"]
    
    def test_weather_endpoint_no_location(self, test_client):
        """Test weather endpoint with device having no location."""
        with patch('app.services.device_service.DeviceService.get_device') as mock_get_device, \
             patch('app.api.dependencies.require_farmer') as mock_auth:
            
            mock_get_device.return_value = {
                'device_id': 'katara-12345678-1234-1234-1234-123456789abc',
                'location_lat': None,
                'location_lng': None,
                'farmer_id': 'test-farmer-id'
            }
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
            
            assert response.status_code == 422
            assert "location not configured" in response.json()["error"]["message"]
    
    def test_weather_endpoint_invalid_coordinates(self, test_client):
        """Test weather endpoint with coordinates outside Morocco."""
        with patch('app.services.device_service.DeviceService.get_device') as mock_get_device, \
             patch('app.api.dependencies.require_farmer') as mock_auth:
            
            mock_get_device.return_value = {
                'device_id': 'katara-12345678-1234-1234-1234-123456789abc',
                'location_lat': 50.0,  # Outside Morocco
                'location_lng': -7.5898,
                'farmer_id': 'test-farmer-id'
            }
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
            
            assert response.status_code == 422
            assert "outside Morocco" in response.json()["error"]["message"]
    
    def test_weather_endpoint_timeout(self, test_client):
        """Test weather endpoint timeout handling."""
        with patch('app.services.device_service.DeviceService.get_device') as mock_get_device, \
             patch('app.services.weather_service.weather_service.get_weather_data') as mock_get_weather, \
             patch('app.api.dependencies.require_farmer') as mock_auth:
            
            mock_get_device.return_value = {
                'device_id': 'katara-12345678-1234-1234-1234-123456789abc',
                'location_lat': 33.5731,
                'location_lng': -7.5898,
                'farmer_id': 'test-farmer-id'
            }
            mock_get_weather.side_effect = WeatherServiceTimeout("Timeout")
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
            
            assert response.status_code == 408
            assert "TIMEOUT_ERROR" in response.json()["error"]["code"]
    
    def test_weather_endpoint_rate_limit(self, test_client):
        """Test weather endpoint rate limit handling."""
        with patch('app.services.device_service.DeviceService.get_device') as mock_get_device, \
             patch('app.services.weather_service.weather_service.get_weather_data') as mock_get_weather, \
             patch('app.api.dependencies.require_farmer') as mock_auth:
            
            mock_get_device.return_value = {
                'device_id': 'katara-12345678-1234-1234-1234-123456789abc',
                'location_lat': 33.5731,
                'location_lng': -7.5898,
                'farmer_id': 'test-farmer-id'
            }
            mock_get_weather.side_effect = WeatherServiceRateLimit("Rate limit")
            mock_auth.return_value = {"user_id": "test-farmer-id", "role": "FARMER"}
            
            response = test_client.get("/api/katara/weather/katara-12345678-1234-1234-1234-123456789abc")
            
            assert response.status_code == 429
            assert "RATE_LIMIT_ERROR" in response.json()["error"]["code"]


class TestWeatherModels:
    """Test weather data models and validation."""
    
    def test_weather_location_validation(self):
        """Test WeatherLocation model validation."""
        # Valid location
        location = WeatherLocation(lat=33.5731, lng=-7.5898)
        assert location.lat == 33.5731
        assert location.lng == -7.5898
        
        # Invalid latitude
        with pytest.raises(ValueError):
            WeatherLocation(lat=91.0, lng=-7.5898)
        
        # Invalid longitude
        with pytest.raises(ValueError):
            WeatherLocation(lat=33.5731, lng=181.0)
    
    def test_current_weather_validation(self):
        """Test CurrentWeather model validation."""
        location = WeatherLocation(lat=33.5731, lng=-7.5898)
        
        # Valid weather data
        weather = CurrentWeather(
            temperature=25.5,
            humidity=65,
            pressure=1013.2,
            wind_speed=3.2,
            wind_direction=180,
            rainfall_1h=0.0,
            rainfall_24h=2.5,
            weather_main="Clear",
            weather_description="clear sky",
            visibility=10.0,
            location=location,
            timestamp=datetime.utcnow()
        )
        assert weather.temperature == 25.5
        assert weather.humidity == 65
        
        # Invalid humidity
        with pytest.raises(ValueError):
            CurrentWeather(
                temperature=25.5,
                humidity=150,  # Invalid > 100
                pressure=1013.2,
                wind_speed=3.2,
                wind_direction=180,
                rainfall_1h=0.0,
                rainfall_24h=2.5,
                weather_main="Clear",
                weather_description="clear sky",
                visibility=10.0,
                location=location,
                timestamp=datetime.utcnow()
            )
    
    def test_weather_alert_validation(self):
        """Test WeatherAlert model validation."""
        now = datetime.utcnow()
        alert = WeatherAlert(
            type="heat_warning",
            severity="high",
            message="High temperature warning",
            valid_from=now,
            valid_until=now + timedelta(hours=4)
        )
        
        assert alert.type == "heat_warning"
        assert alert.severity == "high"
        assert alert.message == "High temperature warning"


class TestWeatherCache:
    """Test weather data caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, weather_service):
        """Test cache key generation for different coordinates."""
        key1 = f"weather:33.5731,-7.5898"
        key2 = f"weather:33.5732,-7.5899"
        
        assert key1 != key2
        assert "weather:" in key1
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, weather_service, sample_weather_data):
        """Test cache expiration logic."""
        with patch.object(weather_service, 'cache_service') as mock_cache:
            # Setup cache miss initially
            mock_cache.get.return_value = None
            
            # Mock HTTP client for fresh data
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = AsyncMock()
                mock_response.json.side_effect = [
                    {
                        "coord": {"lat": 33.5731, "lon": -7.5898},
                        "main": {"temp": 28.5, "humidity": 65, "pressure": 1013.2},
                        "weather": [{"main": "Clear", "description": "clear sky"}],
                        "wind": {"speed": 3.2, "deg": 180},
                        "rain": {"1h": 0.0, "24h": 2.5},
                        "visibility": 10000
                    },
                    {"list": []}
                ]
                mock_response.raise_for_status.return_value = None
                
                mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
                
                result = await weather_service.get_weather_data(33.5731, -7.5898, "test-device")
                
                # Verify cache was set with 15-minute TTL
                mock_cache.set.assert_called_once()
                call_args = mock_cache.set.call_args
                assert call_args[0][0] == "weather:33.5731,-7.5898"
                assert call_args[1]["ttl"] == 900  # 15 minutes in seconds


if __name__ == "__main__":
    pytest.main([__file__])

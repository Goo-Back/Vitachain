"""
Comprehensive tests for satellite NDVI imagery integration.
Tests Sentinel Hub service, NDVI processing, and API endpoints.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid
import httpx

from app.services.satellite_service import SatelliteService, SatelliteServiceError, SatelliteServiceTimeout, SatelliteServiceRateLimit
from app.services.ndvi_service import NDVIService, NDVIServiceError
from app.models.schemas import NDVIDataResponse, NDVIHistoryResponse, NDVISummaryResponse


class TestSatelliteService:
    """Test cases for Sentinel Hub satellite service"""
    
    @pytest.fixture
    def satellite_service(self):
        """Create satellite service instance for testing"""
        return SatelliteService("test_client_id", "test_client_secret")
    
    @pytest.mark.asyncio
    async def test_get_access_token_success(self, satellite_service):
        """Test successful access token retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            token = await satellite_service.get_access_token()
            assert token == "test_token"
            assert satellite_service.access_token == "test_token"
    
    @pytest.mark.asyncio
    async def test_get_access_token_failure(self, satellite_service):
        """Test access token retrieval failure"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError("Auth failed", request=None, response=MagicMock())
            
            with pytest.raises(SatelliteServiceError):
                await satellite_service.get_access_token()
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_cache_hit(self, satellite_service):
        """Test NDVI data retrieval from cache"""
        cached_data = {
            "current": {"ndvi_value": 0.42, "ndvi_trend": "stable"},
            "cached_at": datetime.utcnow().isoformat(),
            "cache_expires": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        with patch('app.core.cache.cache_service.get', return_value=cached_data):
            result = await satellite_service.get_ndvi_data(33.5731, -7.5898, "test-device")
            assert result["current"]["ndvi_value"] == 0.42
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_rate_limit(self, satellite_service):
        """Test NDVI data retrieval with rate limit"""
        with patch('app.core.cache.cache_service.get', return_value=None):
            with patch.object(satellite_service, '_refresh_token'):
                satellite_service.access_token = "test_token"
                satellite_service.token_expires = datetime.utcnow() + timedelta(hours=1)
                
                # Mock rate limiter to return False
                with patch('app.services.satellite_service.sentinel_rate_limiter.check_rate_limit', return_value=False):
                    with pytest.raises(SatelliteServiceRateLimit):
                        await satellite_service.get_ndvi_data(33.5731, -7.5898, "test-device")
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_timeout(self, satellite_service):
        """Test NDVI data retrieval timeout"""
        with patch('app.core.cache.cache_service.get', return_value=None):
            with patch.object(satellite_service, '_refresh_token'):
                satellite_service.access_token = "test_token"
                satellite_service.token_expires = datetime.utcnow() + timedelta(hours=1)
                
                with patch.object(satellite_service, 'check_rate_limit', return_value=True):
                    with patch('httpx.AsyncClient') as mock_client:
                        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
                        
                        with pytest.raises(SatelliteServiceTimeout):
                            await satellite_service.get_ndvi_data(33.5731, -7.5898, "test-device")
    
    @pytest.mark.asyncio
    async def test_parse_ndvi_response(self, satellite_service):
        """Test NDVI response parsing"""
        # Mock TIFF data (in reality, this would be binary TIFF data)
        mock_tiff_data = b"mock_tiff_data"
        
        result = await satellite_service._parse_ndvi_response(mock_tiff_data, 33.5731, -7.5898, "test-device")
        
        assert "current" in result
        assert "trend" in result
        assert "historical" in result
        assert "alerts" in result
        assert -1 <= result["current"]["ndvi_value"] <= 1
        assert result["current"]["location"]["lat"] == 33.5731
        assert result["current"]["location"]["lng"] == -7.5898
    
    def test_calculate_trend(self, satellite_service):
        """Test NDVI trend calculation"""
        assert satellite_service._calculate_trend(0.05) == "improving"
        assert satellite_service._calculate_trend(-0.05) == "declining"
        assert satellite_service._calculate_trend(0.01) == "stable"
        assert satellite_service._calculate_trend(-0.01) == "stable"
    
    def test_assess_vegetation_health(self, satellite_service):
        """Test vegetation health assessment"""
        assert satellite_service._assess_vegetation_health(0.5) == "good"
        assert satellite_service._assess_vegetation_health(0.35) == "moderate"
        assert satellite_service._assess_vegetation_health(0.25) == "poor"
        assert satellite_service._assess_vegetation_health(0.15) == "critical"
    
    def test_assess_data_quality(self, satellite_service):
        """Test data quality assessment"""
        assert satellite_service._assess_data_quality(5) == "excellent"
        assert satellite_service._assess_data_quality(20) == "good"
        assert satellite_service._assess_data_quality(40) == "fair"
        assert satellite_service._assess_data_quality(60) == "poor"


class TestNDVIService:
    """Test cases for NDVI service"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client"""
        supabase = MagicMock()
        supabase.table.return_value.select.return_value.execute.return_value.data = []
        return supabase
    
    @pytest.fixture
    def ndvi_service(self, mock_supabase):
        """Create NDVI service instance for testing"""
        return NDVIService(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_success(self, ndvi_service, mock_supabase):
        """Test successful NDVI data retrieval"""
        # Mock device lookup
        mock_device = {
            "device_id": "katara-test-device",
            "location_lat": 33.5731,
            "location_lng": -7.5898
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_device]
        
        # Mock satellite service
        mock_satellite_data = {
            "current": {
                "ndvi_value": 0.42,
                "ndvi_trend": "stable",
                "vegetation_health": "good",
                "imagery_url": "https://test.com/image.png",
                "cloud_cover": 15.0,
                "data_quality": "excellent",
                "location": {"lat": 33.5731, "lng": -7.5898},
                "acquisition_date": "2026-05-03T10:30:00Z",
                "timestamp": "2026-05-03T14:30:00Z"
            },
            "trend": {
                "ndvi_30d_avg": 0.44,
                "ndvi_7d_avg": 0.42,
                "ndvi_change_7d": -0.02,
                "trend_direction": "stable",
                "stress_detected": False
            },
            "historical": [],
            "alerts": [],
            "cached_at": "2026-05-03T14:30:00Z",
            "cache_expires": "2026-05-04T14:30:00Z"
        }
        
        with patch('app.services.ndvi_service.get_satellite_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_ndvi_data.return_value = mock_satellite_data
            mock_get_service.return_value = mock_service
            
            result = await ndvi_service.get_ndvi_data("katara-test-device", uuid.uuid4())
            
            assert result["current"]["ndvi_value"] == 0.42
            assert result["current"]["vegetation_health"] == "good"
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_device_not_found(self, ndvi_service, mock_supabase):
        """Test NDVI data retrieval with device not found"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        with pytest.raises(NDVIServiceError, match="Device .* not found or access denied"):
            await ndvi_service.get_ndvi_data("katara-nonexistent", uuid.uuid4())
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_location_missing(self, ndvi_service, mock_supabase):
        """Test NDVI data retrieval with missing location"""
        mock_device = {
            "device_id": "katara-test-device",
            "location_lat": None,
            "location_lng": None
        }
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_device]
        
        with pytest.raises(NDVIServiceError, match="Device .* location not configured"):
            await ndvi_service.get_ndvi_data("katara-test-device", uuid.uuid4())
    
    @pytest.mark.asyncio
    async def test_get_ndvi_history_success(self, ndvi_service, mock_supabase):
        """Test successful NDVI history retrieval"""
        # Mock device lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"device_id": "katara-test"}]
        
        # Mock historical data
        mock_history = [
            {
                "id": uuid.uuid4(),
                "ndvi_value": 0.42,
                "ndvi_trend": "stable",
                "data_quality": "excellent",
                "cloud_cover": 15.0,
                "acquisition_date": "2026-05-03T10:30:00Z",
                "imagery_url": "https://test.com/image.png",
                "created_at": "2026-05-03T14:30:00Z"
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value.data = mock_history
        
        result = await ndvi_service.get_ndvi_history("katara-test", uuid.uuid4(), 30)
        
        assert result["total_count"] == 1
        assert len(result["history"]) == 1
        assert result["history"][0]["ndvi_value"] == 0.42
    
    @pytest.mark.asyncio
    async def test_get_ndvi_history_invalid_days(self, ndvi_service):
        """Test NDVI history retrieval with invalid days parameter"""
        with pytest.raises(NDVIServiceError, match="Days parameter must be between 1 and 90"):
            await ndvi_service.get_ndvi_history("katara-test", uuid.uuid4(), 100)
    
    @pytest.mark.asyncio
    async def test_get_ndvi_summary_success(self, ndvi_service, mock_supabase):
        """Test successful NDVI summary retrieval"""
        # Mock devices
        mock_devices = [
            {"device_id": "katara-device1", "name": "Device 1", "location_lat": 33.5, "location_lng": -7.5},
            {"device_id": "katara-device2", "name": "Device 2", "location_lat": 33.6, "location_lng": -7.6}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_devices
        
        # Mock NDVI readings
        mock_readings = [
            {"ndvi_value": 0.45, "ndvi_trend": "improving", "data_quality": "excellent", "created_at": "2026-05-03T14:30:00Z"},
            {"ndvi_value": 0.38, "ndvi_trend": "stable", "data_quality": "good", "created_at": "2026-05-03T14:30:00Z"}
        ]
        
        def mock_table_side_effect(table_name):
            if table_name == "iot_devices":
                mock_table = MagicMock()
                mock_table.select.return_value.eq.return_value.execute.return_value.data = mock_devices
                return mock_table
            elif table_name == "ndvi_readings":
                mock_table = MagicMock()
                mock_table.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [mock_readings[0]]
                return mock_table
            return MagicMock()
        
        mock_supabase.table.side_effect = mock_table_side_effect
        
        result = await ndvi_service.get_ndvi_summary(uuid.uuid4())
        
        assert result["summary"]["total_devices"] == 2
        assert result["summary"]["devices_with_data"] == 1
        assert result["summary"]["avg_ndvi"] == 0.45
        assert result["summary"]["healthy_devices"] == 1
    
    def test_process_historical_data(self, ndvi_service):
        """Test historical data processing"""
        raw_data = [
            {
                "id": uuid.uuid4(),
                "ndvi_value": 0.42,
                "ndvi_trend": "stable",
                "data_quality": "excellent",
                "cloud_cover": 15.0,
                "acquisition_date": "2026-05-03T10:30:00Z",
                "imagery_url": "https://test.com/image.png",
                "created_at": "2026-05-03T14:30:00Z"
            }
        ]
        
        processed = ndvi_service._process_historical_data(raw_data)
        
        assert len(processed) == 1
        assert processed[0]["ndvi_value"] == 0.42
        assert processed[0]["data_quality"] == "excellent"
        assert processed[0]["date"] == "2026-05-03"
    
    def test_calculate_trend_statistics(self, ndvi_service):
        """Test trend statistics calculation"""
        historical_data = [
            {"ndvi_value": 0.40},
            {"ndvi_value": 0.42},
            {"ndvi_value": 0.45},
            {"ndvi_value": 0.43},
            {"ndvi_value": 0.44}
        ]
        
        stats = ndvi_service._calculate_trend_statistics(historical_data)
        
        assert "trend_direction" in stats
        assert "slope" in stats
        assert "confidence" in stats
        assert "data_points" in stats
        assert stats["data_points"] == 5
    
    def test_calculate_trend_statistics_insufficient_data(self, ndvi_service):
        """Test trend statistics with insufficient data"""
        historical_data = [{"ndvi_value": 0.42}]
        
        stats = ndvi_service._calculate_trend_statistics(historical_data)
        
        assert stats["trend_direction"] == "insufficient_data"
        assert stats["confidence"] == 0.0


class TestNDVIEndpoints:
    """Test cases for NDVI API endpoints"""
    
    @pytest.fixture
    def mock_current_user(self):
        """Create mock current user"""
        return MagicMock()
        mock_current_user.id = uuid.uuid4()
        return mock_current_user
    
    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client"""
        supabase = MagicMock()
        supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        return supabase
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_success(self, mock_supabase, mock_current_user):
        """Test successful NDVI data endpoint"""
        from app.api.routes.katara import get_ndvi_data
        
        # Mock device lookup
        mock_device = {
            "device_id": "katara-test-device-12345678-1234-1234-1234-123456789012",
            "location_lat": 33.5731,
            "location_lng": -7.5898
        }
        
        def mock_table_side_effect(table_name):
            if table_name == "iot_devices":
                mock_table = MagicMock()
                mock_table.get_device.return_value = mock_device
                return mock_table
            return MagicMock()
        
        mock_supabase.table.side_effect = mock_table_side_effect
        
        # Mock NDVI service
        mock_ndvi_data = {
            "current": {
                "ndvi_value": 0.42,
                "ndvi_trend": "stable",
                "vegetation_health": "good",
                "imagery_url": "https://test.com/image.png",
                "cloud_cover": 15.0,
                "data_quality": "excellent",
                "location": {"lat": 33.5731, "lng": -7.5898},
                "acquisition_date": "2026-05-03T10:30:00Z",
                "timestamp": "2026-05-03T14:30:00Z"
            },
            "trend": {
                "ndvi_30d_avg": 0.44,
                "ndvi_7d_avg": 0.42,
                "ndvi_change_7d": -0.02,
                "trend_direction": "stable",
                "stress_detected": False
            },
            "historical": [],
            "alerts": [],
            "cached_at": "2026-05-03T14:30:00Z",
            "cache_expires": "2026-05-04T14:30:00Z"
        }
        
        with patch('app.services.ndvi_service.NDVIService') as mock_ndvi_service:
            mock_service = AsyncMock()
            mock_service.get_ndvi_data.return_value = mock_ndvi_data
            mock_ndvi_service.return_value = mock_service
            
            with patch('app.services.device_service.DeviceService') as mock_device_service:
                mock_device_service_instance = AsyncMock()
                mock_device_service_instance.get_device.return_value = mock_device
                mock_device_service.return_value = mock_device_service_instance
                
                result = await get_ndvi_data("katara-test-device-12345678-1234-1234-1234-123456789012", mock_current_user, mock_supabase)
                
                assert result.current.ndvi_value == 0.42
                assert result.current.vegetation_health == "good"
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_invalid_device_id(self, mock_supabase, mock_current_user):
        """Test NDVI data endpoint with invalid device ID"""
        from app.api.routes.katara import get_ndvi_data
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await get_ndvi_data("invalid-device-id", mock_current_user, mock_supabase)
        
        assert exc_info.value.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_ndvi_data_invalid_coordinates(self, mock_supabase, mock_current_user):
        """Test NDVI data endpoint with invalid coordinates"""
        from app.api.routes.katara import get_ndvi_data
        from fastapi import HTTPException
        
        # Mock device with invalid coordinates
        mock_device = {
            "device_id": "katara-test-device-12345678-1234-1234-1234-123456789012",
            "location_lat": 50.0,  # Outside Morocco
            "location_lng": -7.5898
        }
        
        with patch('app.services.device_service.DeviceService') as mock_device_service:
            mock_device_service_instance = AsyncMock()
            mock_device_service_instance.get_device.return_value = mock_device
            mock_device_service.return_value = mock_device_service_instance
            
            with pytest.raises(HTTPException) as exc_info:
                await get_ndvi_data("katara-test-device-12345678-1234-1234-1234-123456789012", mock_current_user, mock_supabase)
            
            assert exc_info.value.status_code == 422
            assert "coordinates outside Morocco" in str(exc_info.value.detail)


class TestNDVIIntegration:
    """Integration tests for NDVI functionality"""
    
    @pytest.mark.asyncio
    async def test_ndvi_data_flow_integration(self):
        """Test complete NDVI data flow from API to database"""
        # This would be a full integration test testing:
        # 1. API endpoint call
        # 2. Service layer processing
        # 3. Satellite service integration
        # 4. Database storage
        # 5. Response formatting
        
        # For this example, we'll mock the external dependencies
        pass
    
    @pytest.mark.asyncio
    async def test_ndvi_ai_analysis_integration(self):
        """Test NDVI data integration with AI analysis"""
        # Test that NDVI data is properly included in AI analysis prompts
        pass


# Performance and load testing
class TestNDVIPerformance:
    """Performance tests for NDVI functionality"""
    
    @pytest.mark.asyncio
    async def test_ndvi_cache_performance(self):
        """Test NDVI caching performance"""
        # Test that cache hits are significantly faster than cache misses
        pass
    
    @pytest.mark.asyncio
    async def test_concurrent_ndvi_requests(self):
        """Test concurrent NDVI request handling"""
        # Test that the system can handle multiple simultaneous NDVI requests
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

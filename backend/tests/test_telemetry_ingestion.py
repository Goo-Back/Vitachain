"""
Comprehensive tests for telemetry data ingestion
Tests API key authentication, data validation, performance requirements, and alert triggering
"""

import pytest
import time
import uuid
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.services.telemetry_service import TelemetryService, THRESHOLDS
from app.models.schemas import (
    TelemetryCreate, TelemetryResponse,
    TelemetryUnauthorizedResponse, TelemetryForbiddenResponse
)


class TestTelemetryIngestion:
    """Test suite for telemetry data ingestion functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_api_key(self):
        """Valid API key for testing."""
        return "vc_test_api_key_123456789012345678901234567890"
    
    @pytest.fixture
    def valid_device(self):
        """Valid device data for testing."""
        return {
            "id": str(uuid.uuid4()),
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "farmer_id": str(uuid.uuid4()),
            "api_key": "vc_test_api_key_123456789012345678901234567890",
            "name": "Test Device",
            "status": "active"
        }
    
    @pytest.fixture
    def valid_telemetry_data(self):
        """Valid telemetry data for testing."""
        return {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 25.5,
            "humidity": 65.2,
            "ndvi": 0.65,
            "battery_level": 85.0,
            "timestamp": "2026-05-03T14:30:00Z"
        }
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        return mock_client, mock_table


class TestTelemetryValidation:
    """Test telemetry data validation."""
    
    def test_valid_telemetry_data(self, valid_telemetry_data):
        """Test validation of valid telemetry data."""
        telemetry = TelemetryCreate(**valid_telemetry_data)
        assert telemetry.device_id == valid_telemetry_data["device_id"]
        assert telemetry.temperature == 25.5
        assert telemetry.humidity == 65.2
        assert telemetry.ndvi == 0.65
        assert telemetry.battery_level == 85.0
    
    def test_device_id_format_validation(self):
        """Test device ID format validation."""
        # Valid device ID
        valid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 25.0,
            "humidity": 60.0,
            "ndvi": 0.5
        }
        telemetry = TelemetryCreate(**valid_data)
        assert telemetry.device_id.startswith("katara-")
        
        # Invalid device ID - wrong prefix
        with pytest.raises(ValueError, match="Device ID must start with"):
            TelemetryCreate(**{
                **valid_data,
                "device_id": "esp32-550e8400-e29b-41d4-a716-446655440000"
            })
        
        # Invalid device ID - invalid UUID
        with pytest.raises(ValueError, match="Device ID must contain a valid UUID"):
            TelemetryCreate(**{
                **valid_data,
                "device_id": "katara-invalid-uuid"
            })
    
    def test_temperature_range_validation(self):
        """Test temperature range validation."""
        valid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "humidity": 60.0,
            "ndvi": 0.5
        }
        
        # Valid temperature
        TelemetryCreate(**{**valid_data, "temperature": 25.0})
        TelemetryCreate(**{**valid_data, "temperature": -10.0})  # Min boundary
        TelemetryCreate(**{**valid_data, "temperature": 60.0})   # Max boundary
        
        # Invalid temperature
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "temperature": -10.1})  # Below min
        
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "temperature": 60.1})   # Above max
    
    def test_humidity_range_validation(self):
        """Test humidity range validation."""
        valid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 25.0,
            "ndvi": 0.5
        }
        
        # Valid humidity
        TelemetryCreate(**{**valid_data, "humidity": 50.0})
        TelemetryCreate(**{**valid_data, "humidity": 0.0})    # Min boundary
        TelemetryCreate(**{**valid_data, "humidity": 100.0})  # Max boundary
        
        # Invalid humidity
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "humidity": -0.1})  # Below min
        
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "humidity": 100.1})  # Above max
    
    def test_ndvi_range_validation(self):
        """Test NDVI range validation."""
        valid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 25.0,
            "humidity": 60.0
        }
        
        # Valid NDVI
        TelemetryCreate(**{**valid_data, "ndvi": 0.5})
        TelemetryCreate(**{**valid_data, "ndvi": -1.0})   # Min boundary
        TelemetryCreate(**{**valid_data, "ndvi": 1.0})    # Max boundary
        
        # Invalid NDVI
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "ndvi": -1.1})  # Below min
        
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "ndvi": 1.1})    # Above max
    
    def test_battery_level_validation(self):
        """Test battery level validation."""
        valid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "temperature": 25.0,
            "humidity": 60.0,
            "ndvi": 0.5
        }
        
        # Valid battery level
        TelemetryCreate(**{**valid_data, "battery_level": 50.0})
        TelemetryCreate(**{**valid_data, "battery_level": 0.0})    # Min boundary
        TelemetryCreate(**{**valid_data, "battery_level": 100.0})  # Max boundary
        
        # Invalid battery level
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "battery_level": -0.1})  # Below min
        
        with pytest.raises(ValueError):
            TelemetryCreate(**{**valid_data, "battery_level": 100.1})  # Above max


class TestTelemetryService:
    """Test telemetry service functionality."""
    
    @pytest.fixture
    def telemetry_service(self, mock_supabase):
        """Create telemetry service with mocked dependencies."""
        mock_client, mock_table = mock_supabase
        return TelemetryService(mock_client)
    
    @pytest.mark.asyncio
    async def test_validate_device_api_key_success(self, telemetry_service, valid_device):
        """Test successful API key validation."""
        # Mock successful device lookup
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
        
        result = await telemetry_service.validate_device_api_key(valid_device["api_key"])
        
        assert result["device_id"] == valid_device["device_id"]
        assert result["farmer_id"] == valid_device["farmer_id"]
    
    @pytest.mark.asyncio
    async def test_validate_device_api_key_missing(self, telemetry_service):
        """Test API key validation with missing key."""
        with pytest.raises(HTTPException) as exc_info:
            await telemetry_service.validate_device_api_key(None)
        
        assert exc_info.value.status_code == 401
        assert "UNAUTHORIZED" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_device_api_key_invalid(self, telemetry_service):
        """Test API key validation with invalid key."""
        # Mock failed device lookup
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        with pytest.raises(HTTPException) as exc_info:
            await telemetry_service.validate_device_api_key("invalid_key")
        
        assert exc_info.value.status_code == 401
        assert "UNAUTHORIZED" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_ingest_telemetry_success(self, telemetry_service, valid_device, valid_telemetry_data):
        """Test successful telemetry ingestion."""
        # Mock API key validation
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
        
        # Mock telemetry insertion
        mock_reading_id = uuid.uuid4()
        telemetry_service.supabase.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": mock_reading_id,
            "device_id": valid_telemetry_data["device_id"],
            "farmer_id": valid_device["farmer_id"]
        }]
        
        # Mock service role client
        with patch('app.services.telemetry_service.get_supabase_client') as mock_service_client:
            mock_service_client.return_value.table.return_value.insert.return_value.execute.return_value.data = [{
                "id": mock_reading_id
            }]
            
            telemetry = TelemetryCreate(**valid_telemetry_data)
            result = await telemetry_service.ingest_telemetry(telemetry, valid_device["api_key"])
        
        assert isinstance(result, TelemetryResponse)
        assert result.status == "ok"
        assert result.reading_id == mock_reading_id
        assert result.processing_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_ingest_telemetry_device_mismatch(self, telemetry_service, valid_device, valid_telemetry_data):
        """Test telemetry ingestion with device ID mismatch."""
        # Mock API key validation
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
        
        # Use different device ID in telemetry data
        mismatched_data = valid_telemetry_data.copy()
        mismatched_data["device_id"] = "katara-different-device-id"
        
        telemetry = TelemetryCreate(**mismatched_data)
        
        with pytest.raises(HTTPException) as exc_info:
            await telemetry_service.ingest_telemetry(telemetry, valid_device["api_key"])
        
        assert exc_info.value.status_code == 403
        assert "FORBIDDEN" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_check_threshold_alerts(self, telemetry_service, valid_device):
        """Test threshold alert triggering."""
        # Test data that should trigger alerts
        critical_telemetry = TelemetryCreate(
            device_id=valid_device["device_id"],
            temperature=45.0,  # Above 40°C threshold
            humidity=15.0,      # Below 20% threshold
            ndvi=0.25          # Below 0.3 threshold
        )
        
        # Mock service role client for alert insertion
        with patch('app.services.telemetry_service.get_supabase_client') as mock_service_client:
            mock_service_client.return_value.table.return_value.insert.return_value.execute.return_value.data = [{
                "id": uuid.uuid4()
            }]
            
            alerts_count = await telemetry_service.check_threshold_alerts(
                critical_telemetry, 
                valid_device["farmer_id"]
            )
        
        assert alerts_count == 3  # Should trigger all three alerts
    
    @pytest.mark.asyncio
    async def test_check_threshold_alerts_no_alerts(self, telemetry_service, valid_device):
        """Test threshold checking with normal values (no alerts)."""
        # Test data with normal values
        normal_telemetry = TelemetryCreate(
            device_id=valid_device["device_id"],
            temperature=25.0,  # Normal
            humidity=60.0,     # Normal
            ndvi=0.7          # Normal
        )
        
        alerts_count = await telemetry_service.check_threshold_alerts(
            normal_telemetry, 
            valid_device["farmer_id"]
        )
        
        assert alerts_count == 0  # Should not trigger any alerts


class TestTelemetryAPI:
    """Test telemetry API endpoints."""
    
    def test_telemetry_ingestion_success(self, client, valid_telemetry_data, valid_api_key, valid_device):
        """Test successful telemetry ingestion API call."""
        # Mock device lookup and insertion
        with patch('app.services.telemetry_service.get_supabase_client') as mock_supabase:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            # Mock device lookup
            mock_table.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
            
            # Mock telemetry insertion
            mock_table.insert.return_value.execute.return_value.data = [{
                "id": str(uuid.uuid4()),
                "device_id": valid_telemetry_data["device_id"],
                "farmer_id": valid_device["farmer_id"]
            }]
            
            mock_supabase.return_value = mock_client
            
            response = client.post(
                "/api/telemetry",
                json=valid_telemetry_data,
                headers={"X-API-Key": valid_api_key}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "reading_id" in data
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] < 100  # Should be fast
    
    def test_telemetry_ingestion_missing_api_key(self, client, valid_telemetry_data):
        """Test telemetry ingestion without API key."""
        response = client.post("/api/telemetry", json=valid_telemetry_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    def test_telemetry_ingestion_invalid_api_key(self, client, valid_telemetry_data):
        """Test telemetry ingestion with invalid API key."""
        with patch('app.services.telemetry_service.get_supabase_client') as mock_supabase:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            # Mock failed device lookup
            mock_table.select.return_value.eq.return_value.execute.return_value.data = []
            
            mock_supabase.return_value = mock_client
            
            response = client.post(
                "/api/telemetry",
                json=valid_telemetry_data,
                headers={"X-API-Key": "invalid_key"}
            )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    def test_telemetry_ingestion_validation_error(self, client, valid_api_key):
        """Test telemetry ingestion with invalid data."""
        invalid_data = {
            "device_id": "invalid-device-id",  # Invalid format
            "temperature": 100.0,              # Out of range
            "humidity": -10.0,                 # Out of range
            "ndvi": 2.0                        # Out of range
        }
        
        response = client.post(
            "/api/telemetry",
            json=invalid_data,
            headers={"X-API-Key": valid_api_key}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_telemetry_health_endpoint(self, client):
        """Test telemetry health check endpoint."""
        response = client.get("/api/telemetry/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "performance_target_ms" in data
        assert "thresholds" in data
    
    def test_get_device_telemetry_success(self, client, valid_device, valid_api_key):
        """Test getting device telemetry data."""
        # Mock device lookup and telemetry retrieval
        with patch('app.services.telemetry_service.get_supabase_client') as mock_supabase:
            mock_client = Mock()
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            
            # Mock device lookup
            mock_table.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
            
            # Mock telemetry data
            mock_table.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {
                    "id": str(uuid.uuid4()),
                    "device_id": valid_device["device_id"],
                    "farmer_id": valid_device["farmer_id"],
                    "temperature": 25.0,
                    "humidity": 60.0,
                    "ndvi": 0.5,
                    "timestamp": "2026-05-03T14:30:00Z"
                }
            ]
            
            mock_supabase.return_value = mock_client
            
            response = client.get(
                f"/api/telemetry/device/{valid_device['device_id']}",
                headers={"X-API-Key": valid_api_key},
                params={"limit": 10, "hours": 24}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == valid_device["device_id"]
        assert "readings" in data
        assert data["total"] >= 0


class TestPerformanceRequirements:
    """Test performance requirements for telemetry ingestion."""
    
    @pytest.mark.asyncio
    async def test_processing_time_requirement(self, telemetry_service, valid_device, valid_telemetry_data):
        """Test that processing time meets < 50ms requirement."""
        # Mock API key validation
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
        
        # Mock telemetry insertion
        mock_reading_id = uuid.uuid4()
        telemetry_service.supabase.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": mock_reading_id,
            "device_id": valid_telemetry_data["device_id"],
            "farmer_id": valid_device["farmer_id"]
        }]
        
        # Mock service role client
        with patch('app.services.telemetry_service.get_supabase_client') as mock_service_client:
            mock_service_client.return_value.table.return_value.insert.return_value.execute.return_value.data = [{
                "id": mock_reading_id
            }]
            
            telemetry = TelemetryCreate(**valid_telemetry_data)
            
            # Measure processing time
            start_time = time.time()
            result = await telemetry_service.ingest_telemetry(telemetry, valid_device["api_key"])
            end_time = time.time()
            
            processing_time_ms = (end_time - start_time) * 1000
            
            # Check both measured time and reported time
            assert processing_time_ms < 50, f"Processing took {processing_time_ms:.2f}ms, exceeds 50ms requirement"
            assert result.processing_time_ms < 50, f"Reported processing time {result.processing_time_ms}ms exceeds 50ms requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, telemetry_service, valid_device, valid_telemetry_data):
        """Test handling of concurrent telemetry requests."""
        import asyncio
        
        # Mock API key validation
        telemetry_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [valid_device]
        
        # Mock telemetry insertion
        mock_reading_id = uuid.uuid4()
        telemetry_service.supabase.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": mock_reading_id,
            "device_id": valid_telemetry_data["device_id"],
            "farmer_id": valid_device["farmer_id"]
        }]
        
        # Mock service role client
        with patch('app.services.telemetry_service.get_supabase_client') as mock_service_client:
            mock_service_client.return_value.table.return_value.insert.return_value.execute.return_value.data = [{
                "id": mock_reading_id
            }]
            
            telemetry = TelemetryCreate(**valid_telemetry_data)
            
            # Create 10 concurrent requests
            tasks = []
            for i in range(10):
                task = telemetry_service.ingest_telemetry(telemetry, valid_device["api_key"])
                tasks.append(task)
            
            # Execute all tasks concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify all requests succeeded
            assert len(results) == 10
            for result in results:
                assert isinstance(result, TelemetryResponse)
                assert result.status == "ok"
                assert result.processing_time_ms < 50
            
            # Total time should be much less than sequential execution
            total_time_ms = (end_time - start_time) * 1000
            assert total_time_ms < 200, f"Concurrent execution took {total_time_ms:.2f}ms, should be < 200ms for 10 requests"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

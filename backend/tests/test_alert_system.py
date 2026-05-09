"""
Comprehensive tests for KATARA Alert System
Tests alert generation, API endpoints, and real-time notifications
"""

import pytest
import uuid
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.alert_service import AlertService, get_alert_service
from app.services.threshold_service import ThresholdService, get_threshold_service
from app.services.notification_service import NotificationService, get_notification_service
from app.models.schemas import (
    AlertType, AlertSeverity, MetricType, AlertCreate,
    AlertGenerationRequest, AlertGenerationResponse, ThresholdViolation
)

# Test client setup
client = TestClient(app)

class TestThresholdService:
    """Test threshold checking logic"""
    
    def setup_method(self):
        """Setup test threshold service"""
        self.threshold_service = ThresholdService()
    
    def test_temperature_threshold_violation(self):
        """Test temperature threshold violation detection"""
        # Temperature above threshold (40°C)
        violation = self.threshold_service.check_temperature_threshold(42.5)
        
        assert violation is not None
        assert violation.metric == MetricType.TEMPERATURE
        assert violation.value == 42.5
        assert violation.threshold == 40.0
        assert violation.severity == AlertSeverity.HIGH
        assert violation.operator == ">"
        assert violation.violation_amount == 2.5
    
    def test_temperature_threshold_normal(self):
        """Test temperature within normal range"""
        violation = self.threshold_service.check_temperature_threshold(35.0)
        assert violation is None
    
    def test_humidity_threshold_violation(self):
        """Test humidity threshold violation detection"""
        # Humidity below threshold (20%)
        violation = self.threshold_service.check_humidity_threshold(15.0)
        
        assert violation is not None
        assert violation.metric == MetricType.HUMIDITY
        assert violation.value == 15.0
        assert violation.threshold == 20.0
        assert violation.severity == AlertSeverity.HIGH
        assert violation.operator == "<"
        assert violation.violation_amount == 5.0
    
    def test_humidity_threshold_normal(self):
        """Test humidity within normal range"""
        violation = self.threshold_service.check_humidity_threshold(25.0)
        assert violation is None
    
    def test_ndvi_threshold_violation(self):
        """Test NDVI threshold violation detection"""
        # NDVI below threshold (0.3)
        violation = self.threshold_service.check_ndvi_threshold(0.25)
        
        assert violation is not None
        assert violation.metric == MetricType.NDVI
        assert violation.value == 0.25
        assert violation.threshold == 0.3
        assert violation.severity == AlertSeverity.MEDIUM
        assert violation.operator == "<"
        assert abs(violation.violation_amount - 0.05) < 1e-10
    
    def test_ndvi_threshold_normal(self):
        """Test NDVI within normal range"""
        violation = self.threshold_service.check_ndvi_threshold(0.4)
        assert violation is None
    
    def test_check_all_thresholds_multiple_violations(self):
        """Test checking all thresholds with multiple violations"""
        violations = self.threshold_service.check_all_thresholds(
            temperature=42.0,  # Above threshold
            humidity=15.0,      # Below threshold
            ndvi=0.25          # Below threshold
        )
        
        assert len(violations) == 3
        assert any(v.metric == MetricType.TEMPERATURE for v in violations)
        assert any(v.metric == MetricType.HUMIDITY for v in violations)
        assert any(v.metric == MetricType.NDVI for v in violations)
    
    def test_check_all_thresholds_no_violations(self):
        """Test checking all thresholds with no violations"""
        violations = self.threshold_service.check_all_thresholds(
            temperature=35.0,  # Below threshold
            humidity=25.0,      # Above threshold
            ndvi=0.4            # Above threshold
        )
        
        assert len(violations) == 0
    
    def test_validate_metric_value(self):
        """Test metric value validation"""
        # Valid values
        assert self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, 25.0)
        assert self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 50.0)
        assert self.threshold_service.validate_metric_value(MetricType.NDVI, 0.5)
        
        # Invalid values
        assert not self.threshold_service.validate_metric_value(MetricType.TEMPERATURE, -15.0)  # Too cold
        assert not self.threshold_service.validate_metric_value(MetricType.HUMIDITY, 150.0)  # Too high
        assert not self.threshold_service.validate_metric_value(MetricType.NDVI, 2.0)  # Too high
    
    def test_performance_threshold_checking(self):
        """Test performance of threshold checking"""
        import time
        
        start_time = time.perf_counter()
        
        for _ in range(1000):
            self.threshold_service.check_all_thresholds(42.0, 15.0, 0.25)
        
        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / 1000) * 1000
        
        # Should be well under 5ms requirement
        assert avg_time_ms < 5.0, f"Threshold checking too slow: {avg_time_ms:.3f}ms average"
    
    def test_environment_variable_configuration(self):
        """Test threshold service with environment variables"""
        # This test would need to be run with environment variables set
        # For now, just verify the service loads with defaults
        config = self.threshold_service.get_threshold_config()
        assert config.temperature_high == 40.0
        assert config.humidity_low == 20.0
        assert config.ndvi_low == 0.3


class TestAlertService:
    """Test alert generation and management"""
    
    def setup_method(self):
        """Setup test alert service with mock Supabase client"""
        self.mock_supabase = AsyncMock()
        self.alert_service = AlertService(self.mock_supabase)
    
    @pytest.mark.asyncio
    async def test_create_threshold_alert_temperature(self):
        """Test creating a temperature threshold alert"""
        farmer_id = uuid.uuid4()
        device_id = "katara-test-device"
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = [{
            "id": str(uuid.uuid4()),
            "farmer_id": str(farmer_id),
            "device_id": device_id,
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Critical temperature detected: 42.5°C (threshold: 40°C). Immediate action recommended to prevent heat stress.",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        alert = await self.alert_service._create_threshold_alert(
            farmer_id=farmer_id,
            device_id=device_id,
            metric=MetricType.TEMPERATURE,
            value=42.5,
            threshold=40.0,
            severity=AlertSeverity.HIGH
        )
        
        assert alert is not None
        assert alert.farmer_id == farmer_id
        assert alert.device_id == device_id
        assert alert.type == AlertType.THRESHOLD_EXCEEDED
        assert alert.severity == AlertSeverity.HIGH
        assert "42.5°C" in alert.message
        assert alert.is_read == False
        
        # Verify Supabase was called correctly
        self.mock_supabase.table.assert_called_with("katara_alerts")
        self.mock_supabase.table.return_value.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_thresholds_and_create_alerts_multiple(self):
        """Test checking thresholds and creating multiple alerts"""
        farmer_id = uuid.uuid4()
        device_id = "katara-test-device"
        
        # Mock Supabase response for multiple alerts
        mock_result = Mock()
        alert_ids = [str(uuid.uuid4()) for _ in range(3)]
        mock_result.data = [
            {
                "id": alert_ids[0],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "high",
                "message": "Critical temperature detected: 42.5°C (threshold: 40°C). Immediate action recommended to prevent heat stress.",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            },
            {
                "id": alert_ids[1],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "high",
                "message": "Low humidity detected: 15.0% (threshold: 20%). Risk of dehydration - consider irrigation.",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            },
            {
                "id": alert_ids[2],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "medium",
                "message": "Vegetation stress detected: NDVI 0.25 (threshold: 0.3). Review irrigation and nutrient levels.",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        ]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        result = await self.alert_service.check_thresholds_and_create_alerts(
            device_id=device_id,
            farmer_id=farmer_id,
            temperature=42.5,  # Above threshold
            humidity=15.0,      # Below threshold
            ndvi=0.25           # Below threshold
        )
        
        assert isinstance(result, AlertGenerationResponse)
        assert result.alerts_created == 3
        assert len(result.alert_ids) == 3
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_get_farmer_alerts(self):
        """Test retrieving alerts for a farmer"""
        farmer_id = uuid.uuid4()
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = [
            {
                "id": str(uuid.uuid4()),
                "farmer_id": str(farmer_id),
                "device_id": "katara-device-1",
                "type": "threshold_exceeded",
                "severity": "high",
                "message": "Test alert message",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        ]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
        
        alerts = await self.alert_service.get_farmer_alerts(
            farmer_id=farmer_id,
            limit=20,
            offset=0,
            severity=AlertSeverity.HIGH,
            is_read=False
        )
        
        assert len(alerts) == 1
        assert alerts[0].farmer_id == farmer_id
        assert alerts[0].severity == AlertSeverity.HIGH
        assert alerts[0].is_read == False
    
    @pytest.mark.asyncio
    async def test_mark_alert_as_read(self):
        """Test marking an alert as read"""
        farmer_id = uuid.uuid4()
        alert_id = uuid.uuid4()
        
        # Mock Supabase responses
        # First call: check if alert exists
        mock_get_result = Mock()
        mock_get_result.data = [{
            "id": str(alert_id),
            "farmer_id": str(farmer_id),
            "device_id": "katara-device-1",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Test alert message",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }]
        
        # Second call: update alert
        mock_update_result = Mock()
        mock_update_result.data = [{
            "id": str(alert_id),
            "farmer_id": str(farmer_id),
            "device_id": "katara-device-1",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Test alert message",
            "is_read": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_get_result
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        
        updated_alert = await self.alert_service.mark_alert_as_read(alert_id, farmer_id)
        
        assert updated_alert is not None
        assert updated_alert.id == alert_id
        assert updated_alert.is_read == True
    
    @pytest.mark.asyncio
    async def test_get_unread_alerts_count(self):
        """Test getting unread alerts count"""
        farmer_id = uuid.uuid4()
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.count = 5
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
        
        count = await self.alert_service.get_unread_alerts_count(farmer_id)
        
        assert count == 5


class TestAlertAPIEndpoints:
    """Test alert API endpoints"""
    
    def test_get_farmer_alerts_success(self):
        """Test successful GET /api/katara/alerts"""
        # Mock authentication
        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = {"user_id": str(uuid.uuid4())}
            
            with patch('app.api.routes.katara.get_alert_service') as mock_service:
                mock_alert_service = AsyncMock()
                mock_alert_service.get_farmer_alerts.return_value = []
                mock_alert_service.get_unread_alerts_count.return_value = 0
                mock_service.return_value = mock_alert_service
                
                response = client.get("/api/katara/alerts")
                
                assert response.status_code == 200
                data = response.json()
                assert "alerts" in data
                assert "unread_count" in data
                assert "pagination" in data
    
    def test_get_farmer_alerts_invalid_limit(self):
        """Test GET /api/katara/alerts with invalid limit"""
        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = {"user_id": str(uuid.uuid4())}
            
            response = client.get("/api/katara/alerts?limit=0")
            
            assert response.status_code == 422
    
    def test_mark_alert_as_read_success(self):
        """Test successful PATCH /api/katara/alerts/{id}/read"""
        alert_id = uuid.uuid4()
        
        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = {"user_id": str(uuid.uuid4())}
            
            with patch('app.api.routes.katara.get_alert_service') as mock_service:
                mock_alert_service = AsyncMock()
                mock_alert = Mock()
                mock_alert.id = alert_id
                mock_alert.is_read = True
                mock_alert_service.mark_alert_as_read.return_value = mock_alert
                mock_service.return_value = mock_alert_service
                
                response = client.patch(f"/api/katara/alerts/{alert_id}/read")
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == str(alert_id)
                assert data["is_read"] == True
    
    def test_mark_alert_as_read_invalid_uuid(self):
        """Test PATCH /api/katara/alerts/{id}/read with invalid UUID"""
        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = {"user_id": str(uuid.uuid4())}
            
            response = client.patch("/api/katara/alerts/invalid-uuid/read")
            
            assert response.status_code == 422


class TestNotificationService:
    """Test real-time notification service"""
    
    def setup_method(self):
        """Setup test notification service"""
        self.mock_supabase = AsyncMock()
        self.notification_service = NotificationService(self.mock_supabase)
    
    @pytest.mark.asyncio
    async def test_subscribe_to_farmer_alerts(self):
        """Test subscribing to farmer alerts"""
        farmer_id = str(uuid.uuid4())
        callback = AsyncMock()
        
        # Mock Supabase channel
        mock_channel = AsyncMock()
        mock_channel.on_postgres_changes.return_value = mock_channel
        mock_channel.subscribe.return_value = mock_channel
        mock_channel.listen.return_value = None
        self.mock_supabase.channel.return_value = mock_channel
        
        subscription_id = await self.notification_service.subscribe_to_farmer_alerts(
            farmer_id, callback
        )
        
        assert subscription_id == f"alerts_{farmer_id}"
        assert subscription_id in self.notification_service.subscriptions
        
        # Verify Supabase channel was set up correctly
        self.mock_supabase.channel.assert_called_with(f"farmer_alerts_{farmer_id}")
        mock_channel.on_postgres_changes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_farmer_alerts(self):
        """Test unsubscribing from farmer alerts"""
        farmer_id = str(uuid.uuid4())
        callback = AsyncMock()
        
        # First subscribe
        mock_channel = AsyncMock()
        mock_channel.on_postgres_changes.return_value = mock_channel
        mock_channel.subscribe.return_value = mock_channel
        mock_channel.listen.return_value = None
        mock_channel.unsubscribe.return_value = None
        self.mock_supabase.channel.return_value = mock_channel
        
        subscription_id = await self.notification_service.subscribe_to_farmer_alerts(
            farmer_id, callback
        )
        
        # Then unsubscribe
        success = await self.notification_service.unsubscribe_from_farmer_alerts(subscription_id)
        
        assert success == True
        assert subscription_id not in self.notification_service.subscriptions
    
    @pytest.mark.asyncio
    async def test_send_manual_notification(self):
        """Test sending manual notification"""
        farmer_id = str(uuid.uuid4())
        callback = AsyncMock()
        
        # Setup subscription
        mock_channel = AsyncMock()
        mock_channel.on_postgres_changes.return_value = mock_channel
        mock_channel.subscribe.return_value = mock_channel
        mock_channel.listen.return_value = None
        self.mock_supabase.channel.return_value = mock_channel
        
        await self.notification_service.subscribe_to_farmer_alerts(farmer_id, callback)
        
        # Send manual notification
        success = await self.notification_service.send_manual_notification(
            farmer_id, "test_notification", {"message": "Test message"}
        )
        
        assert success == True
        callback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_subscriptions(self):
        """Test getting active subscriptions"""
        farmer_id = str(uuid.uuid4())
        callback = AsyncMock()
        
        # Setup subscription
        mock_channel = AsyncMock()
        mock_channel.on_postgres_changes.return_value = mock_channel
        mock_channel.subscribe.return_value = mock_channel
        mock_channel.listen.return_value = None
        self.mock_supabase.channel.return_value = mock_channel
        
        await self.notification_service.subscribe_to_farmer_alerts(farmer_id, callback)
        
        subscriptions = self.notification_service.get_active_subscriptions()
        
        assert len(subscriptions) == 1
        assert subscriptions[0]["farmer_id"] == farmer_id
        assert subscriptions[0]["status"] == "active"


class TestAlertThresholdIntegration:
    """Integration tests for alert service with threshold service"""
    
    def setup_method(self):
        """Setup test with mock Supabase client"""
        self.mock_supabase = AsyncMock()
        self.alert_service = AlertService(self.mock_supabase)
    
    @pytest.mark.asyncio
    async def test_alert_service_uses_threshold_service(self):
        """Test that alert service properly integrates with threshold service"""
        # Verify threshold service is available
        threshold_service = self.alert_service.threshold_service
        assert threshold_service is not None
        
        # Test threshold checking through alert service
        violations = threshold_service.check_all_thresholds(
            temperature=42.0,  # Above threshold
            humidity=15.0,    # Below threshold
            ndvi=0.25         # Below threshold
        )
        
        assert len(violations) == 3
    
    @pytest.mark.asyncio
    async def test_multiple_violation_alert_creation(self):
        """Test creating alerts for multiple threshold violations"""
        farmer_id = uuid.uuid4()
        device_id = "test-device"
        
        # Mock database response
        mock_result = AsyncMock()
        alert_ids = [str(uuid.uuid4()) for _ in range(3)]
        mock_result.data = [
            {
                "id": alert_ids[0],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "high",
                "message": "Critical temperature detected: 42.0°C (threshold: 40.0°C). Immediate action recommended to prevent heat stress.",
                "read_status": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            },
            {
                "id": alert_ids[1],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "high",
                "message": "Low humidity detected: 15.0% (threshold: 20%). Risk of dehydration - consider irrigation.",
                "read_status": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            },
            {
                "id": alert_ids[2],
                "farmer_id": str(farmer_id),
                "device_id": device_id,
                "type": "threshold_exceeded",
                "severity": "medium",
                "message": "Vegetation stress detected: NDVI 0.25 (threshold: 0.3). Review irrigation and nutrient levels.",
                "read_status": False,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        ]
        
        # Properly mock the async chain
        mock_table = AsyncMock()
        mock_table.insert.return_value.execute.return_value = mock_result
        self.mock_supabase.table.return_value = mock_table
        
        # Test alert generation with multiple violations
        response = await self.alert_service.check_thresholds_and_create_alerts(
            device_id=device_id,
            farmer_id=farmer_id,
            temperature=42.0,  # Above threshold
            humidity=15.0,    # Below threshold
            ndvi=0.25         # Below threshold
        )
        
        assert isinstance(response, AlertGenerationResponse)
        assert response.alerts_created == 3
        assert len(response.alert_ids) == 3
        assert response.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_no_violations_no_alerts(self):
        """Test that no alerts are created when no thresholds are violated"""
        farmer_id = uuid.uuid4()
        device_id = "test-device"
        
        # Mock empty database response (shouldn't be called)
        mock_result = AsyncMock()
        mock_result.data = []
        mock_table = AsyncMock()
        mock_table.insert.return_value.execute.return_value = mock_result
        self.mock_supabase.table.return_value = mock_table
        
        # Test with normal values (no violations)
        response = await self.alert_service.check_thresholds_and_create_alerts(
            device_id=device_id,
            farmer_id=farmer_id,
            temperature=35.0,  # Below threshold
            humidity=25.0,    # Above threshold
            ndvi=0.4         # Above threshold
        )
        
        assert response.alerts_created == 0
        assert len(response.alert_ids) == 0
        assert response.processing_time_ms > 0


class TestAlertIntegration:
    """Integration tests for complete alert flow"""
    
    @pytest.mark.asyncio
    async def test_complete_alert_flow(self):
        """Test complete flow from telemetry to alert notification"""
        # This would test the integration between telemetry ingestion,
        # alert generation, and real-time notifications
        
        # Mock the entire stack
        with patch('app.services.telemetry_service.get_alert_service') as mock_get_alert:
            mock_alert_service = AsyncMock()
            mock_alert_service.check_thresholds_and_create_alerts.return_value = AlertGenerationResponse(
                alerts_created=1,
                alert_ids=[uuid.uuid4()],
                processing_time_ms=15
            )
            mock_get_alert.return_value = mock_alert_service
            
            # Test telemetry ingestion with alert generation
            from app.services.telemetry_service import TelemetryService
            mock_supabase = AsyncMock()
            telemetry_service = TelemetryService(mock_supabase)
            
            # Mock device validation
            mock_device = {
                "device_id": "katara-test-device",
                "farmer_id": str(uuid.uuid4()),
                "api_key": "test-key"
            }
            telemetry_service.validate_device_api_key = AsyncMock(return_value=mock_device)
            
            # Mock telemetry insertion
            mock_result = Mock()
            mock_result.data = [{"id": str(uuid.uuid4())}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
            
            # Test telemetry ingestion
            from app.models.schemas import TelemetryCreate
            telemetry_data = TelemetryCreate(
                device_id="katara-test-device",
                temperature=42.5,  # Above threshold
                humidity=15.0,      # Below threshold
                ndvi=0.25           # Below threshold
            )
            
            result = await telemetry_service.ingest_telemetry(telemetry_data, "test-key")
            
            assert result.alerts_triggered == 1
            assert len(result.alert_ids) == 1
            assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_alert_generation(self):
        """Test concurrent alert generation for multiple devices"""
        # Test that the system can handle multiple devices generating alerts simultaneously
        mock_supabase = AsyncMock()
        alert_service = AlertService(mock_supabase)
        
        # Mock alert creation
        mock_result = Mock()
        mock_result.data = [{
            "id": str(uuid.uuid4()),
            "farmer_id": str(uuid.uuid4()),
            "device_id": "katara-device-1",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Test alert",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Create multiple concurrent alert generation tasks
        tasks = []
        for i in range(5):
            task = alert_service.check_thresholds_and_create_alerts(
                device_id=f"katara-device-{i}",
                farmer_id=uuid.uuid4(),
                temperature=42.0 + i,  # All above threshold
                humidity=15.0 - i,      # All below threshold
                ndvi=0.25 - i * 0.01     # All below threshold
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all alerts were created
        for result in results:
            assert isinstance(result, AlertGenerationResponse)
            assert result.alerts_created >= 1  # At least temperature alert
            assert result.processing_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__])

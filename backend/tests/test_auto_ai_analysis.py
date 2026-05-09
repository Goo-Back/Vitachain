"""
Tests for Automatic AI Analysis Service
Story: 3-10-automatic-ai-recommendation-generation
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.services.auto_analysis_service import AutoAnalysisService
from app.services.ai_service import AIAnalysisTimeout, AIAnalysisFailed
from app.models.schemas import AlertType, AlertSeverity


class TestAutoAnalysisService:
    """Test suite for AutoAnalysisService"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def auto_analysis_service(self, mock_supabase):
        """Create AutoAnalysisService instance with mocked dependencies"""
        service = AutoAnalysisService(mock_supabase)
        # Mock the dependent services
        service.ai_service = AsyncMock()
        service.alert_service = AsyncMock()
        service.weather_service = AsyncMock()
        service.ndvi_service = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_device_id(self):
        """Sample device ID"""
        return "katara-550e8400-e29b-41d4-a716"
    
    @pytest.fixture
    def sample_farmer_id(self):
        """Sample farmer ID"""
        return uuid.uuid4()
    
    @pytest.fixture
    def sample_telemetry(self):
        """Sample telemetry data"""
        return {
            "temperature": 42.5,
            "humidity": 18.2,
            "ndvi": 0.25,
            "battery_level": 78.5,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @pytest.fixture
    def critical_telemetry(self):
        """Critical telemetry data that should trigger analysis"""
        return {
            "temperature": 45.0,  # Above 40°C threshold
            "humidity": 15.0,   # Below 20% threshold
            "ndvi": 0.2,        # Below 0.3 threshold
            "battery_level": 75.0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @pytest.mark.asyncio
    async def test_handle_automatic_analysis_trigger_success(
        self, auto_analysis_service, mock_supabase, 
        sample_device_id, sample_farmer_id, critical_telemetry
    ):
        """Test successful automatic analysis trigger"""
        # Mock device settings
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "auto_analysis_enabled": True,
            "last_auto_analysis": None,
            "analysis_frequency_hours": 6
        }]
        
        # Mock rate limiting check
        mock_supabase.rpc.return_value.execute.return_value.data = True
        
        # Mock conditions change check
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
        
        # Mock telemetry data
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
            {"temperature": 40.0, "humidity": 25.0, "ndvi": 0.4, "timestamp": datetime.utcnow().isoformat()}
        ] * 10
        
        # Mock AI analysis result
        analysis_result = {"analysis_id": uuid.uuid4()}
        auto_analysis_service.ai_service.analyze_device_telemetry.return_value = analysis_result
        
        # Mock alert creation
        auto_analysis_service.alert_service.create_alert.return_value = None
        
        # Execute test
        result = await auto_analysis_service.handle_automatic_analysis_trigger(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            telemetry_reading=critical_telemetry,
            trigger_type="critical_threshold"
        )
        
        # Assertions
        assert result == analysis_result
        auto_analysis_service.ai_service.analyze_device_telemetry.assert_called_once()
        auto_analysis_service.alert_service.create_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_automatic_analysis_trigger_disabled(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id, critical_telemetry
    ):
        """Test automatic analysis trigger when disabled for device"""
        # Mock device settings with auto-analysis disabled
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "auto_analysis_enabled": False,
            "last_auto_analysis": None,
            "analysis_frequency_hours": 6
        }]
        
        # Execute test
        result = await auto_analysis_service.handle_automatic_analysis_trigger(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            telemetry_reading=critical_telemetry,
            trigger_type="critical_threshold"
        )
        
        # Assertions
        assert result is None
        auto_analysis_service.ai_service.analyze_device_telemetry.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_automatic_analysis_trigger_rate_limited(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id, critical_telemetry
    ):
        """Test automatic analysis trigger when rate limited"""
        # Mock device settings
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "auto_analysis_enabled": True,
            "last_auto_analysis": None,
            "analysis_frequency_hours": 6
        }]
        
        # Mock rate limiting check (should return False)
        mock_supabase.rpc.return_value.execute.return_value.data = False
        
        # Execute test
        result = await auto_analysis_service.handle_automatic_analysis_trigger(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            telemetry_reading=critical_telemetry,
            trigger_type="critical_threshold"
        )
        
        # Assertions
        assert result is None
        auto_analysis_service.ai_service.analyze_device_telemetry.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_automatic_analysis_trigger_conditions_unchanged(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id, critical_telemetry
    ):
        """Test automatic analysis trigger when conditions haven't changed significantly"""
        # Mock device settings
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "auto_analysis_enabled": True,
            "last_auto_analysis": None,
            "analysis_frequency_hours": 6
        }]
        
        # Mock rate limiting check
        mock_supabase.rpc.return_value.execute.return_value.data = True
        
        # Mock conditions change check (should return False - conditions unchanged)
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "trigger_conditions": {
                "current_conditions": {
                    "temperature": 42.0,  # Very close to current
                    "humidity": 18.0,      # Very close to current
                    "ndvi": 0.24            # Very close to current
                }
            }
        }]
        
        # Execute test
        result = await auto_analysis_service.handle_automatic_analysis_trigger(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            telemetry_reading=critical_telemetry,
            trigger_type="critical_threshold"
        )
        
        # Assertions
        assert result is None
        auto_analysis_service.ai_service.analyze_device_telemetry.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_automatic_analysis_trigger_ai_timeout(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id, critical_telemetry
    ):
        """Test automatic analysis trigger when AI analysis times out"""
        # Mock device settings
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "auto_analysis_enabled": True,
            "last_auto_analysis": None,
            "analysis_frequency_hours": 6
        }]
        
        # Mock rate limiting check
        mock_supabase.rpc.return_value.execute.return_value.data = True
        
        # Mock conditions change check
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
        
        # Mock telemetry data
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
            {"temperature": 40.0, "humidity": 25.0, "ndvi": 0.4, "timestamp": datetime.utcnow().isoformat()}
        ] * 10
        
        # Mock AI analysis timeout
        auto_analysis_service.ai_service.analyze_device_telemetry.side_effect = AIAnalysisTimeout()
        
        # Mock fallback alert creation
        auto_analysis_service.alert_service.create_alert.return_value = None
        
        # Execute test
        result = await auto_analysis_service.handle_automatic_analysis_trigger(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            telemetry_reading=critical_telemetry,
            trigger_type="critical_threshold"
        )
        
        # Assertions
        assert result is None
        auto_analysis_service.alert_service.create_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_devices_due_for_periodic_analysis(
        self, auto_analysis_service, mock_supabase
    ):
        """Test getting devices due for periodic analysis"""
        # Mock database function result
        mock_devices = [
            {
                "device_id": "device1",
                "farmer_id": uuid.uuid4(),
                "auto_analysis_enabled": True,
                "last_auto_analysis": None,
                "analysis_frequency_hours": 6
            },
            {
                "device_id": "device2",
                "farmer_id": uuid.uuid4(),
                "auto_analysis_enabled": True,
                "last_auto_analysis": datetime.utcnow() - timedelta(hours=8),
                "analysis_frequency_hours": 6
            }
        ]
        
        mock_supabase.rpc.return_value.execute.return_value.data = mock_devices
        
        # Execute test
        result = await auto_analysis_service.get_devices_due_for_periodic_analysis()
        
        # Assertions
        assert len(result) == 2
        assert result[0]["device_id"] == "device1"
        assert result[1]["device_id"] == "device2"
    
    @pytest.mark.asyncio
    async def test_update_device_analysis_settings(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id
    ):
        """Test updating device analysis settings"""
        # Mock update result
        updated_device = {
            "device_id": sample_device_id,
            "auto_analysis_enabled": False,
            "analysis_frequency_hours": 12,
            "last_auto_analysis": datetime.utcnow().isoformat()
        }
        
        mock_supabase.table.return_value.update.return_value.execute.return_value.data = [updated_device]
        
        # Execute test
        result = await auto_analysis_service.update_device_analysis_settings(
            device_id=sample_device_id,
            farmer_id=sample_farmer_id,
            auto_analysis_enabled=False,
            analysis_frequency_hours=12
        )
        
        # Assertions
        assert result["device_id"] == sample_device_id
        assert result["auto_analysis_enabled"] == False
        assert result["analysis_frequency_hours"] == 12
    
    @pytest.mark.asyncio
    async def test_update_device_analysis_settings_device_not_found(
        self, auto_analysis_service, mock_supabase,
        sample_device_id, sample_farmer_id
    ):
        """Test updating settings for non-existent device"""
        # Mock empty result
        mock_supabase.table.return_value.update.return_value.execute.return_value.data = []
        
        # Execute test and expect exception
        with pytest.raises(Exception):  # Should raise HTTPException
            await auto_analysis_service.update_device_analysis_settings(
                device_id=sample_device_id,
                farmer_id=sample_farmer_id,
                auto_analysis_enabled=False,
                analysis_frequency_hours=12
            )
    
    def test_determine_analysis_priority_critical(self, auto_analysis_service):
        """Test determining analysis priority for critical conditions"""
        telemetry = {
            "temperature": 45.0,  # Above 42°C critical threshold
            "humidity": 12.0,    # Below 15% critical threshold
            "ndvi": 0.15         # Below 0.2 critical threshold
        }
        
        priority = auto_analysis_service._determine_analysis_priority(
            telemetry, "critical_threshold"
        )
        
        assert priority == "critical"
    
    def test_determine_analysis_priority_high(self, auto_analysis_service):
        """Test determining analysis priority for high conditions"""
        telemetry = {
            "temperature": 41.0,  # Above 40°C but below 42°C
            "humidity": 18.0,    # Below 20% but above 15%
            "ndvi": 0.28         # Below 0.3 but above 0.2
        }
        
        priority = auto_analysis_service._determine_analysis_priority(
            telemetry, "critical_threshold"
        )
        
        assert priority == "high"
    
    def test_determine_analysis_priority_medium(self, auto_analysis_service):
        """Test determining analysis priority for medium conditions"""
        telemetry = {
            "temperature": 35.0,  # Normal temperature
            "humidity": 40.0,    # Normal humidity
            "ndvi": 0.5          # Normal NDVI
        }
        
        priority = auto_analysis_service._determine_analysis_priority(
            telemetry, "critical_threshold"
        )
        
        assert priority == "medium"
    
    def test_determine_analysis_priority_periodic(self, auto_analysis_service):
        """Test determining analysis priority for periodic analysis"""
        telemetry = {
            "temperature": 35.0,
            "humidity": 40.0,
            "ndvi": 0.5
        }
        
        priority = auto_analysis_service._determine_analysis_priority(
            telemetry, "automatic_periodic"
        )
        
        assert priority == "medium"
    
    def test_check_critical_thresholds(self, auto_analysis_service):
        """Test checking critical thresholds"""
        # Test critical temperature
        telemetry = {"temperature": 45.0, "humidity": 30.0, "ndvi": 0.4}
        exceeded = auto_analysis_service._check_critical_thresholds(telemetry)
        assert "temperature" in exceeded
        assert len(exceeded) == 1
        
        # Test critical humidity
        telemetry = {"temperature": 35.0, "humidity": 15.0, "ndvi": 0.4}
        exceeded = auto_analysis_service._check_critical_thresholds(telemetry)
        assert "humidity" in exceeded
        assert len(exceeded) == 1
        
        # Test critical NDVI
        telemetry = {"temperature": 35.0, "humidity": 30.0, "ndvi": 0.25}
        exceeded = auto_analysis_service._check_critical_thresholds(telemetry)
        assert "ndvi" in exceeded
        assert len(exceeded) == 1
        
        # Test multiple critical conditions
        telemetry = {"temperature": 45.0, "humidity": 15.0, "ndvi": 0.25}
        exceeded = auto_analysis_service._check_critical_thresholds(telemetry)
        assert "temperature" in exceeded
        assert "humidity" in exceeded
        assert "ndvi" in exceeded
        assert len(exceeded) == 3
        
        # Test normal conditions
        telemetry = {"temperature": 35.0, "humidity": 30.0, "ndvi": 0.4}
        exceeded = auto_analysis_service._check_critical_thresholds(telemetry)
        assert len(exceeded) == 0
    
    def test_map_priority_to_severity(self, auto_analysis_service):
        """Test mapping analysis priority to alert severity"""
        assert auto_analysis_service._map_priority_to_severity("critical") == AlertSeverity.CRITICAL
        assert auto_analysis_service._map_priority_to_severity("high") == AlertSeverity.HIGH
        assert auto_analysis_service._map_priority_to_severity("medium") == AlertSeverity.MEDIUM
        assert auto_analysis_service._map_priority_to_severity("low") == AlertSeverity.LOW


class TestAnalysisScheduler:
    """Test suite for AnalysisScheduler"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_auto_analysis_service(self):
        """Mock AutoAnalysisService"""
        service = AsyncMock()
        service.get_devices_due_for_periodic_analysis.return_value = []
        return service
    
    @pytest.mark.asyncio
    async def test_periodic_optimization_analysis_no_devices(
        self, mock_supabase, mock_auto_analysis_service
    ):
        """Test periodic analysis when no devices are due"""
        with patch('app.services.analysis_scheduler.get_auto_analysis_service') as mock_get_service:
            mock_get_service.return_value = mock_auto_analysis_service
            
            from app.services.analysis_scheduler import AnalysisScheduler
            scheduler = AnalysisScheduler(mock_supabase)
            
            # Execute periodic analysis
            await scheduler.periodic_optimization_analysis()
            
            # Should have checked for devices but found none
            mock_auto_analysis_service.get_devices_due_for_periodic_analysis.assert_called_once()
            mock_auto_analysis_service.handle_automatic_analysis_trigger.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_periodic_optimization_analysis_with_devices(
        self, mock_supabase, mock_auto_analysis_service
    ):
        """Test periodic analysis with devices due for analysis"""
        # Mock devices
        devices = [
            {
                "device_id": "device1",
                "farmer_id": uuid.uuid4(),
                "auto_analysis_enabled": True,
                "last_auto_analysis": None,
                "analysis_frequency_hours": 6
            }
        ]
        
        mock_auto_analysis_service.get_devices_due_for_periodic_analysis.return_value = devices
        mock_auto_analysis_service.handle_automatic_analysis_trigger.return_value = {"analysis_id": uuid.uuid4()}
        
        # Mock latest telemetry
        with patch.object(AnalysisScheduler, '_get_latest_telemetry') as mock_telemetry:
            mock_telemetry.return_value = {
                "temperature": 35.0,
                "humidity": 40.0,
                "ndvi": 0.4,
                "battery_level": 80.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with patch('app.services.analysis_scheduler.get_auto_analysis_service') as mock_get_service:
                mock_get_service.return_value = mock_auto_analysis_service
                
                from app.services.analysis_scheduler import AnalysisScheduler
                scheduler = AnalysisScheduler(mock_supabase)
                
                # Execute periodic analysis
                await scheduler.periodic_optimization_analysis()
                
                # Assertions
                mock_auto_analysis_service.get_devices_due_for_periodic_analysis.assert_called_once()
                mock_auto_analysis_service.handle_automatic_analysis_trigger.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_analysis_data(self, mock_supabase):
        """Test cleanup of old analysis data"""
        with patch('app.services.analysis_scheduler.get_auto_analysis_service'):
            from app.services.analysis_scheduler import AnalysisScheduler
            scheduler = AnalysisScheduler(mock_supabase)
            
            # Mock deletion result
            mock_supabase.table.return_value.delete.return_value.lt.return_value.execute.return_value.data = [
                {"id": uuid.uuid4()}, {"id": uuid.uuid4()}
            ]
            
            # Execute cleanup
            await scheduler.cleanup_old_analysis_data()
            
            # Assertions
            mock_supabase.table.return_value.delete.return_value.lt.assert_called_once()


# Integration Tests
class TestAutoAnalysisIntegration:
    """Integration tests for automatic analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_critical_threshold_trigger_flow(self):
        """Test complete flow from critical threshold to AI analysis"""
        # This would be an integration test that tests:
        # 1. Telemetry ingestion with critical conditions
        # 2. Automatic analysis trigger
        # 3. AI analysis execution
        # 4. Alert creation with AI recommendations
        # 5. Real-time notification
        
        # For now, this is a placeholder for the integration test structure
        pass
    
    @pytest.mark.asyncio
    async def test_periodic_analysis_flow(self):
        """Test complete flow for periodic analysis"""
        # This would test the background job execution
        pass


# Performance Tests
class TestAutoAnalysisPerformance:
    """Performance tests for automatic analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_triggers(self):
        """Test handling multiple concurrent analysis triggers"""
        # Test that the system can handle multiple devices triggering analysis simultaneously
        pass
    
    @pytest.mark.asyncio
    async def test_rate_limiting_performance(self):
        """Test rate limiting performance under high load"""
        # Test that rate limiting works efficiently under high telemetry volume
        pass


# Error Handling Tests
class TestAutoAnalysisErrorHandling:
    """Error handling tests for automatic analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_ai_service_unavailable(self):
        """Test behavior when AI service is unavailable"""
        # Test graceful degradation when Claude API is down
        pass
    
    @pytest.mark.asyncio
    async def test_database_connection_errors(self):
        """Test handling of database connection errors"""
        # Test error handling when database is unavailable
        pass
    
    @pytest.mark.asyncio
    async def test_malformed_telemetry_data(self):
        """Test handling of malformed telemetry data"""
        # Test robustness against bad telemetry data
        pass

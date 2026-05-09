"""
Tests for alert status management functionality
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.alert_service import AlertService
from app.services.realtime_service import RealtimeService
from app.models.schemas import Alert, AlertType, AlertSeverity, MetricType


class TestAlertStatusManagement:
    """Test suite for alert status management"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        supabase = MagicMock()
        supabase.table.return_value = MagicMock()
        return supabase

    @pytest.fixture
    def mock_realtime_service(self):
        """Mock realtime service"""
        realtime_service = MagicMock()
        realtime_service.broadcast_alert_status_change = AsyncMock(return_value=True)
        realtime_service.broadcast_bulk_alert_status_change = AsyncMock(return_value=True)
        return realtime_service

    @pytest.fixture
    def alert_service(self, mock_supabase, mock_realtime_service):
        """Create alert service instance with mocked dependencies"""
        with patch('app.services.alert_service.get_realtime_service', return_value=mock_realtime_service):
            service = AlertService(mock_supabase)
            service.realtime_service = mock_realtime_service
            return service

    @pytest.fixture
    def sample_alert(self):
        """Create sample alert data"""
        return {
            "id": str(uuid.uuid4()),
            "farmer_id": str(uuid.uuid4()),
            "device_id": "katara-test-device",
            "type": "threshold_exceeded",
            "severity": "high",
            "message": "Temperature threshold exceeded",
            "read_status": False,
            "read_at": None,
            "created_at": datetime.utcnow().isoformat()
        }

    @pytest.mark.asyncio
    async def test_update_alert_status_to_read(self, alert_service, sample_alert):
        """Test updating alert status to read"""
        alert_id = uuid.UUID(sample_alert["id"])
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database queries
        alert_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [sample_alert]
        
        updated_alert = {**sample_alert, "read_status": True, "read_at": datetime.utcnow().isoformat()}
        alert_service.supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [updated_alert]
        
        # Execute the method
        result = await alert_service.update_alert_status(alert_id, farmer_id, True)
        
        # Assertions
        assert result.read_status is True
        assert result.read_at is not None
        assert result.id == alert_id
        
        # Verify realtime broadcast was called
        alert_service.realtime_service.broadcast_alert_status_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_alert_status_to_unread(self, alert_service, sample_alert):
        """Test updating alert status to unread"""
        # Start with a read alert
        read_alert = {**sample_alert, "read_status": True, "read_at": datetime.utcnow().isoformat()}
        alert_id = uuid.UUID(sample_alert["id"])
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database queries
        alert_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [read_alert]
        
        updated_alert = {**read_alert, "read_status": False, "read_at": None}
        alert_service.supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [updated_alert]
        
        # Execute the method
        result = await alert_service.update_alert_status(alert_id, farmer_id, False)
        
        # Assertions
        assert result.read_status is False
        assert result.read_at is None
        assert result.id == alert_id
        
        # Verify realtime broadcast was called
        alert_service.realtime_service.broadcast_alert_status_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_alert_status_not_found(self, alert_service, sample_alert):
        """Test updating alert status when alert not found"""
        alert_id = uuid.UUID(sample_alert["id"])
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database query returning no results
        alert_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        # Execute and expect exception
        with pytest.raises(Exception, match="Alert not found or access denied"):
            await alert_service.update_alert_status(alert_id, farmer_id, True)

    @pytest.mark.asyncio
    async def test_bulk_update_alert_status(self, alert_service, sample_alert):
        """Test bulk updating alert status"""
        alert_ids = [uuid.UUID(sample_alert["id"])]
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database queries
        alert_service.supabase.table.return_value.select.return_value.in_.return_value.eq.return_value.execute.return_value.data = [sample_alert]
        
        updated_alerts = [{**sample_alert, "read_status": True, "read_at": datetime.utcnow().isoformat()}]
        alert_service.supabase.table.return_value.update.return_value.in_.return_value.eq.return_value.execute.return_value.data = updated_alerts
        
        # Execute the method
        result = await alert_service.bulk_update_alert_status(alert_ids, farmer_id, True)
        
        # Assertions
        assert result["updated_count"] == 1
        assert result["failed_updates"] == 0
        assert len(result["updated_alerts"]) == 1
        
        # Verify realtime broadcast was called
        alert_service.realtime_service.broadcast_bulk_alert_status_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_unread_alerts_count(self, alert_service, sample_alert):
        """Test getting unread alerts count"""
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database query
        alert_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.count = 5
        
        # Execute the method
        result = await alert_service.get_unread_alerts_count(farmer_id)
        
        # Assertions
        assert result == 5

    @pytest.mark.asyncio
    async def test_mark_alert_as_read_legacy(self, alert_service, sample_alert):
        """Test legacy mark_alert_as_read method"""
        alert_id = uuid.UUID(sample_alert["id"])
        farmer_id = uuid.UUID(sample_alert["farmer_id"])
        
        # Mock database queries
        alert_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [sample_alert]
        
        updated_alert = {**sample_alert, "read_status": True, "read_at": datetime.utcnow().isoformat()}
        alert_service.supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [updated_alert]
        
        # Execute the legacy method
        result = await alert_service.mark_alert_as_read(alert_id, farmer_id)
        
        # Assertions
        assert result.read_status is True
        assert result.read_at is not None


class TestRealtimeService:
    """Test suite for realtime service"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        return MagicMock()

    @pytest.fixture
    def realtime_service(self, mock_supabase):
        """Create realtime service instance"""
        return RealtimeService(mock_supabase)

    @pytest.mark.asyncio
    async def test_broadcast_alert_status_change(self, realtime_service):
        """Test broadcasting alert status change"""
        alert_id = uuid.uuid4()
        farmer_id = uuid.uuid4()
        read_status = True
        read_at = datetime.utcnow()
        
        # Execute the method
        result = await realtime_service.broadcast_alert_status_change(alert_id, farmer_id, read_status, read_at)
        
        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_broadcast_bulk_alert_status_change(self, realtime_service):
        """Test broadcasting bulk alert status change"""
        updated_alerts = [
            {
                "id": str(uuid.uuid4()),
                "read_status": True,
                "read_at": datetime.utcnow().isoformat()
            }
        ]
        farmer_id = uuid.uuid4()
        
        # Execute the method
        result = await realtime_service.broadcast_bulk_alert_status_change(updated_alerts, farmer_id)
        
        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_broadcast_unread_count_change(self, realtime_service):
        """Test broadcasting unread count change"""
        farmer_id = uuid.uuid4()
        unread_count = 3
        
        # Execute the method
        result = await realtime_service.broadcast_unread_count_change(farmer_id, unread_count)
        
        # Assertions
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])

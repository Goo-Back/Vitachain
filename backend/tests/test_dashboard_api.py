"""
Tests for KATARA Dashboard API endpoints
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import DashboardResponse, DashboardDevice, SummaryStats, AlertsInfo, TrendData


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_farmer_user():
    """Mock authenticated farmer user"""
    return {
        "user_id": str(uuid.uuid4()),
        "email": "farmer@example.com",
        "role": "FARMER",
        "user_metadata": {"role": "FARMER"}
    }


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock_client = Mock()
    return mock_client


@pytest.fixture
def sample_dashboard_data():
    """Sample dashboard data for testing"""
    farmer_id = uuid.uuid4()
    
    return DashboardResponse(
        devices=[
            DashboardDevice(
                id=uuid.uuid4(),
                device_id="katara-12345678-1234-5678-9abc-123456789def",
                name="Parcelle Nord",
                location_lat=33.5,
                location_lng=-7.6,
                status="online",
                last_seen=datetime.now(),
                current_telemetry={
                    "temperature": 25.5,
                    "humidity": 65.2,
                    "ndvi": 0.42,
                    "battery_level": 85.0,
                    "timestamp": datetime.now()
                }
            ),
            DashboardDevice(
                id=uuid.uuid4(),
                device_id="katara-87654321-4321-8765-cdef-987654321abc",
                name="Parcelle Sud",
                location_lat=33.6,
                location_lng=-7.5,
                status="offline",
                last_seen=datetime.now() - timedelta(minutes=15),
                current_telemetry=None
            )
        ],
        summary_stats=SummaryStats(
            avg_temperature=25.5,
            avg_humidity=65.2,
            avg_ndvi=0.42,
            total_devices=2,
            online_devices=1,
            offline_devices=1
        ),
        alerts=AlertsInfo(
            unread_count=2,
            recent_alerts=[
                {
                    "id": uuid.uuid4(),
                    "type": "threshold_exceeded",
                    "severity": "high",
                    "message": "Temperature critical: 42°C",
                    "created_at": datetime.now() - timedelta(minutes=30)
                }
            ]
        ),
        trend_data=TrendData(
            last_24_hours=[
                {
                    "device_id": "katara-12345678-1234-5678-9abc-123456789def",
                    "temperature": 25.5,
                    "humidity": 65.2,
                    "ndvi": 0.42,
                    "timestamp": datetime.now() - timedelta(hours=1)
                }
            ]
        )
    )


class TestDashboardAPI:
    """Test suite for Dashboard API endpoints"""

    @patch('app.api.routes.katara.get_current_user')
    @patch('app.api.routes.katara.get_supabase_client')
    def test_get_dashboard_success(self, mock_supabase_client, mock_get_user, client, mock_farmer_user, sample_dashboard_data):
        """Test successful dashboard data retrieval"""
        # Setup mocks
        mock_get_user.return_value = mock_farmer_user
        
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_dashboard_data.return_value = sample_dashboard_data
        
        mock_client_instance = Mock()
        mock_client_instance.return_value = mock_dashboard_service
        mock_supabase_client.return_value = mock_client_instance
        
        # Mock the DashboardService instantiation
        with patch('app.api.routes.katara.DashboardService', return_value=mock_dashboard_service):
            response = client.get("/api/katara/dashboard")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "devices" in data
        assert "summary_stats" in data
        assert "alerts" in data
        assert "trend_data" in data
        
        # Verify devices data
        assert len(data["devices"]) == 2
        device = data["devices"][0]
        assert device["device_id"].startswith("katara-")
        assert device["status"] in ["online", "offline", "unknown"]
        
        # Verify summary stats
        stats = data["summary_stats"]
        assert stats["total_devices"] == 2
        assert stats["online_devices"] == 1
        assert stats["offline_devices"] == 1
        
        # Verify alerts
        alerts = data["alerts"]
        assert alerts["unread_count"] == 2
        assert len(alerts["recent_alerts"]) == 1

    @patch('app.api.routes.katara.get_current_user')
    @patch('app.api.routes.katara.get_supabase_client')
    def test_get_dashboard_unauthorized(self, mock_supabase_client, mock_get_user, client):
        """Test dashboard endpoint without authentication"""
        # Setup mock to raise exception (unauthorized)
        mock_get_user.side_effect = Exception("Unauthorized")
        
        response = client.get("/api/katara/dashboard")
        
        # Should return 500 due to authentication error
        assert response.status_code == 500

    @patch('app.api.routes.katara.require_farmer')
    def test_get_dashboard_forbidden(self, mock_require_farmer, client):
        """Test dashboard endpoint with non-farmer role"""
        # Setup mock to raise forbidden exception
        mock_require_farmer.side_effect = Exception("Forbidden")
        
        response = client.get("/api/katara/dashboard")
        
        # Should return 500 due to authorization error
        assert response.status_code == 500

    @patch('app.api.routes.katara.get_current_user')
    @patch('app.api.routes.katara.get_supabase_client')
    def test_get_dashboard_empty_data(self, mock_supabase_client, mock_get_user, client, mock_farmer_user):
        """Test dashboard with no devices or data"""
        # Setup mocks
        mock_get_user.return_value = mock_farmer_user
        
        empty_dashboard_data = DashboardResponse(
            devices=[],
            summary_stats=SummaryStats(
                total_devices=0,
                online_devices=0,
                offline_devices=0
            ),
            alerts=AlertsInfo(unread_count=0, recent_alerts=[]),
            trend_data=TrendData(last_24_hours=[])
        )
        
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_dashboard_data.return_value = empty_dashboard_data
        
        mock_client_instance = Mock()
        mock_client_instance.return_value = mock_dashboard_service
        mock_supabase_client.return_value = mock_client_instance
        
        with patch('app.api.routes.katara.DashboardService', return_value=mock_dashboard_service):
            response = client.get("/api/katara/dashboard")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["devices"]) == 0
        assert data["summary_stats"]["total_devices"] == 0
        assert data["alerts"]["unread_count"] == 0
        assert len(data["trend_data"]["last_24_hours"]) == 0

    @patch('app.api.routes.katara.get_current_user')
    @patch('app.api.routes.katara.get_supabase_client')
    def test_get_device_status_success(self, mock_supabase_client, mock_get_user, client, mock_farmer_user):
        """Test device status endpoint"""
        # Setup mocks
        mock_get_user.return_value = mock_farmer_user
        
        device_id = "katara-12345678-1234-5678-9abc-123456789def"
        device_status_data = {
            "device": {
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "name": "Test Device",
                "farmer_id": mock_farmer_user["user_id"]
            },
            "latest_telemetry": {
                "temperature": 25.5,
                "humidity": 65.2,
                "timestamp": datetime.now().isoformat()
            },
            "status": "online"
        }
        
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_device_status.return_value = device_status_data
        
        mock_client_instance = Mock()
        mock_client_instance.return_value = mock_dashboard_service
        mock_supabase_client.return_value = mock_client_instance
        
        with patch('app.api.routes.katara.DashboardService', return_value=mock_dashboard_service):
            response = client.get(f"/api/katara/dashboard/device/{device_id}")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert "device" in data
        assert "latest_telemetry" in data
        assert "status" in data
        assert data["device"]["device_id"] == device_id
        assert data["status"] == "online"

    @patch('app.api.routes.katara.get_current_user')
    @patch('app.api.routes.katara.get_supabase_client')
    def test_get_device_status_not_found(self, mock_supabase_client, mock_get_user, client, mock_farmer_user):
        """Test device status endpoint with non-existent device"""
        # Setup mocks
        mock_get_user.return_value = mock_farmer_user
        
        mock_dashboard_service = AsyncMock()
        mock_dashboard_service.get_device_status.side_effect = ValueError("Device not found")
        
        mock_client_instance = Mock()
        mock_client_instance.return_value = mock_dashboard_service
        mock_supabase_client.return_value = mock_client_instance
        
        with patch('app.api.routes.katara.DashboardService', return_value=mock_dashboard_service):
            response = client.get("/api/katara/dashboard/device/non-existent-device")
        
        # Should return 404 for device not found
        assert response.status_code == 404


class TestDashboardService:
    """Test suite for DashboardService"""

    @pytest.fixture
    def dashboard_service(self, mock_supabase):
        """Dashboard service fixture"""
        from app.services.dashboard_service import DashboardService
        return DashboardService(mock_supabase)

    @pytest.fixture
    def sample_devices_data(self):
        """Sample devices data from Supabase"""
        return [
            {
                "id": str(uuid.uuid4()),
                "device_id": "katara-12345678-1234-5678-9abc-123456789def",
                "name": "Test Device 1",
                "location_lat": 33.5,
                "location_lng": -7.6,
                "farmer_id": str(uuid.uuid4()),
                "registered_at": datetime.now().isoformat()
            }
        ]

    @pytest.fixture
    def sample_telemetry_data(self):
        """Sample telemetry data from Supabase"""
        return [
            {
                "id": str(uuid.uuid4()),
                "device_id": "katara-12345678-1234-5678-9abc-123456789def",
                "temperature": 25.5,
                "humidity": 65.2,
                "ndvi": 0.42,
                "battery_level": 85.0,
                "timestamp": datetime.now().isoformat()
            }
        ]

    def test_calculate_summary_stats(self, dashboard_service):
        """Test summary statistics calculation"""
        from app.models.schemas import DashboardDevice, CurrentTelemetry, DeviceStatus
        
        devices = [
            DashboardDevice(
                id=uuid.uuid4(),
                device_id="device-1",
                status=DeviceStatus.ONLINE,
                last_seen=datetime.now(),
                current_telemetry=CurrentTelemetry(
                    temperature=25.0,
                    humidity=60.0,
                    ndvi=0.4,
                    timestamp=datetime.now()
                )
            ),
            DashboardDevice(
                id=uuid.uuid4(),
                device_id="device-2",
                status=DeviceStatus.OFFLINE,
                last_seen=datetime.now() - timedelta(minutes=15),
                current_telemetry=CurrentTelemetry(
                    temperature=27.0,
                    humidity=70.0,
                    ndvi=0.45,
                    timestamp=datetime.now() - timedelta(minutes=15)
                )
            ),
            DashboardDevice(
                id=uuid.uuid4(),
                device_id="device-3",
                status=DeviceStatus.UNKNOWN,
                last_seen=datetime.now(),
                current_telemetry=None
            )
        ]
        
        stats = dashboard_service._calculate_summary_stats(devices)
        
        assert stats.total_devices == 3
        assert stats.online_devices == 1
        assert stats.offline_devices == 1
        assert stats.avg_temperature == 26.0  # (25 + 27) / 2
        assert stats.avg_humidity == 65.0     # (60 + 70) / 2
        assert stats.avg_ndvi == 0.425       # (0.4 + 0.45) / 2

    def test_determine_device_status(self, dashboard_service):
        """Test device status determination"""
        from app.models.schemas import DeviceStatus
        
        # Test online device (recent timestamp)
        recent_telemetry = {
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
        }
        status = dashboard_service._determine_device_status(recent_telemetry)
        assert status == DeviceStatus.ONLINE
        
        # Test offline device (old timestamp)
        old_telemetry = {
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
        }
        status = dashboard_service._determine_device_status(old_telemetry)
        assert status == DeviceStatus.OFFLINE
        
        # Test unknown device (no telemetry)
        status = dashboard_service._determine_device_status(None)
        assert status == DeviceStatus.UNKNOWN

    def test_get_farmer_alerts_empty(self, dashboard_service):
        """Test alerts retrieval with no alerts"""
        farmer_id = uuid.uuid4()
        
        # Mock Supabase to return no alerts
        dashboard_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        dashboard_service.supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        
        alerts = dashboard_service._get_farmer_alerts(farmer_id)
        
        assert alerts.unread_count == 0
        assert len(alerts.recent_alerts) == 0


if __name__ == "__main__":
    pytest.main([__file__])

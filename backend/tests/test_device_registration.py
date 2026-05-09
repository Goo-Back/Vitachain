"""
Tests for KATARA device registration endpoints
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime

from app.main import app
from app.models.schemas import DeviceCreate, DeviceResponse, DeviceListResponse
from app.services.device_service import DeviceService


class TestDeviceRegistration:
    """Test device registration endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def valid_device_data(self):
        """Valid device registration data"""
        return {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "name": "Parcelle Nord",
            "location_lat": 33.5,
            "location_lng": -7.6
        }

    @pytest.fixture
    def minimal_device_data(self):
        """Minimal device registration data (only device_id)"""
        return {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440001"
        }

    @pytest.fixture
    def mock_farmer_user(self):
        """Mock authenticated farmer user"""
        return {
            "user_id": str(uuid.uuid4()),
            "email": "farmer@example.com",
            "role": "FARMER",
            "full_name": "Test Farmer"
        }

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def mock_device_service(self):
        """Mock device service"""
        with patch('app.services.device_service.DeviceService') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_register_device_success(self, client, valid_device_data, mock_farmer_user, mock_device_service):
        """Test successful device registration"""
        # Setup mock response
        expected_response = DeviceResponse(
            id=uuid.uuid4(),
            device_id=valid_device_data["device_id"],
            farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
            name=valid_device_data["name"],
            location_lat=valid_device_data["location_lat"],
            location_lng=valid_device_data["location_lng"],
            registered_at=datetime.utcnow()
        )
        mock_device_service.register_device = AsyncMock(return_value=expected_response)

        # Mock authentication
        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=valid_device_data)

        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == valid_device_data["device_id"]
        assert data["name"] == valid_device_data["name"]
        assert data["location_lat"] == valid_device_data["location_lat"]
        assert data["location_lng"] == valid_device_data["location_lng"]
        assert "farmer_id" in data
        assert "registered_at" in data

    def test_register_device_minimal_data(self, client, minimal_device_data, mock_farmer_user, mock_device_service):
        """Test device registration with minimal data"""
        expected_response = DeviceResponse(
            id=uuid.uuid4(),
            device_id=minimal_device_data["device_id"],
            farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
            name=None,
            location_lat=None,
            location_lng=None,
            registered_at=datetime.utcnow()
        )
        mock_device_service.register_device = AsyncMock(return_value=expected_response)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=minimal_device_data)

        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == minimal_device_data["device_id"]
        assert data["name"] is None
        assert data["location_lat"] is None
        assert data["location_lng"] is None

    def test_register_device_invalid_device_id_format(self, client, mock_farmer_user):
        """Test device registration with invalid device_id format"""
        invalid_data = {
            "device_id": "invalid-device-id",
            "name": "Test Device"
        }

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_register_device_invalid_coordinates(self, client, mock_farmer_user):
        """Test device registration with invalid coordinates"""
        invalid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "location_lat": 91.0,  # Invalid latitude (> 90)
            "location_lng": -181.0  # Invalid longitude (< -180)
        }

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_register_device_empty_name(self, client, mock_farmer_user):
        """Test device registration with empty name"""
        invalid_data = {
            "device_id": "katara-550e8400-e29b-41d4-a716-446655440000",
            "name": "   "  # Empty name with spaces
        }

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_register_device_duplicate_id(self, client, valid_device_data, mock_farmer_user, mock_device_service):
        """Test device registration with duplicate device ID"""
        from fastapi import HTTPException, status
        
        mock_device_service.register_device = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "DEVICE_ALREADY_EXISTS", "message": "Device with this ID already exists"}
            )
        )

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.post("/api/katara/devices", json=valid_device_data)

        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "DEVICE_ALREADY_EXISTS"

    def test_register_device_unauthorized_role(self, client, valid_device_data):
        """Test device registration by non-farmer user"""
        mock_restaurant_user = {
            "user_id": str(uuid.uuid4()),
            "email": "restaurant@example.com",
            "role": "RESTAURANT",
            "full_name": "Test Restaurant"
        }

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=403, detail="Access denied")
            
            response = client.post("/api/katara/devices", json=valid_device_data)

        assert response.status_code == 403

    def test_get_farmer_devices_success(self, client, mock_farmer_user, mock_device_service):
        """Test getting farmer's devices"""
        expected_devices = DeviceListResponse(
            devices=[
                DeviceResponse(
                    id=uuid.uuid4(),
                    device_id="katara-device-1",
                    farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
                    name="Device 1",
                    location_lat=33.5,
                    location_lng=-7.6,
                    registered_at=datetime.utcnow()
                ),
                DeviceResponse(
                    id=uuid.uuid4(),
                    device_id="katara-device-2",
                    farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
                    name="Device 2",
                    location_lat=34.0,
                    location_lng=-7.0,
                    registered_at=datetime.utcnow()
                )
            ],
            total=2
        )
        mock_device_service.get_farmer_devices = AsyncMock(return_value=expected_devices)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.get("/api/katara/devices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["devices"]) == 2
        assert data["devices"][0]["device_id"] == "katara-device-1"
        assert data["devices"][1]["device_id"] == "katara-device-2"

    def test_get_farmer_devices_empty(self, client, mock_farmer_user, mock_device_service):
        """Test getting empty device list"""
        expected_devices = DeviceListResponse(devices=[], total=0)
        mock_device_service.get_farmer_devices = AsyncMock(return_value=expected_devices)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.get("/api/katara/devices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["devices"]) == 0

    def test_get_device_by_id_success(self, client, mock_farmer_user, mock_device_service):
        """Test getting specific device by ID"""
        device_id = "katara-550e8400-e29b-41d4-a716-446655440000"
        expected_device = DeviceResponse(
            id=uuid.uuid4(),
            device_id=device_id,
            farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
            name="Test Device",
            location_lat=33.5,
            location_lng=-7.6,
            registered_at=datetime.utcnow()
        )
        mock_device_service.get_device_by_id = AsyncMock(return_value=expected_device)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.get(f"/api/katara/devices/{device_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
        assert data["name"] == "Test Device"

    def test_get_device_not_found(self, client, mock_farmer_user, mock_device_service):
        """Test getting non-existent device"""
        from fastapi import HTTPException, status
        
        device_id = "katara-nonexistent"
        mock_device_service.get_device_by_id = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
            )
        )

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.get(f"/api/katara/devices/{device_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "DEVICE_NOT_FOUND"

    def test_update_device_success(self, client, mock_farmer_user, mock_device_service):
        """Test updating device information"""
        device_id = "katara-550e8400-e29b-41d4-a716-446655440000"
        update_data = {
            "name": "Updated Device Name",
            "location_lat": 35.0,
            "location_lng": -8.0
        }
        
        expected_device = DeviceResponse(
            id=uuid.uuid4(),
            device_id=device_id,
            farmer_id=uuid.UUID(mock_farmer_user["user_id"]),
            name=update_data["name"],
            location_lat=update_data["location_lat"],
            location_lng=update_data["location_lng"],
            registered_at=datetime.utcnow()
        )
        mock_device_service.update_device = AsyncMock(return_value=expected_device)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.patch(f"/api/katara/devices/{device_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["location_lat"] == update_data["location_lat"]
        assert data["location_lng"] == update_data["location_lng"]

    def test_delete_device_success(self, client, mock_farmer_user, mock_device_service):
        """Test deleting a device"""
        device_id = "katara-550e8400-e29b-41d4-a716-446655440000"
        mock_device_service.delete_device = AsyncMock(return_value=True)

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.delete(f"/api/katara/devices/{device_id}")

        assert response.status_code == 204

    def test_delete_device_not_found(self, client, mock_farmer_user, mock_device_service):
        """Test deleting non-existent device"""
        from fastapi import HTTPException, status
        
        device_id = "katara-nonexistent"
        mock_device_service.delete_device = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DEVICE_NOT_FOUND", "message": "Device not found"}
            )
        )

        with patch('app.api.routes.katara.require_farmer') as mock_auth:
            mock_auth.return_value = mock_farmer_user
            
            response = client.delete(f"/api/katara/devices/{device_id}")

        assert response.status_code == 404


class TestDeviceService:
    """Test device service layer"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def device_service(self, mock_supabase):
        """Create device service instance"""
        return DeviceService(mock_supabase)

    @pytest.fixture
    def sample_device_data(self):
        """Sample device creation data"""
        return DeviceCreate(
            device_id="katara-550e8400-e29b-41d4-a716-446655440000",
            name="Test Device",
            location_lat=33.5,
            location_lng=-7.6
        )

    @pytest.fixture
    def farmer_id(self):
        """Sample farmer ID"""
        return uuid.uuid4()

    def test_register_device_success(self, device_service, mock_supabase, sample_device_data, farmer_id):
        """Test successful device registration in service layer"""
        # Mock Supabase responses
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": str(uuid.uuid4()),
            "device_id": sample_device_data.device_id,
            "farmer_id": str(farmer_id),
            "name": sample_device_data.name,
            "location_lat": sample_device_data.location_lat,
            "location_lng": sample_device_data.location_lng,
            "registered_at": datetime.utcnow().isoformat()
        }]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.error = None

        result = device_service.register_device(sample_device_data, farmer_id)

        assert result.device_id == sample_device_data.device_id
        assert result.farmer_id == farmer_id
        assert result.name == sample_device_data.name

    def test_register_device_duplicate_id(self, device_service, mock_supabase, sample_device_data, farmer_id):
        """Test device registration with duplicate ID"""
        from fastapi import HTTPException, status
        
        # Mock existing device
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [{
            "id": str(uuid.uuid4())
        }]

        with pytest.raises(HTTPException) as exc_info:
            device_service.register_device(sample_device_data, farmer_id)

        assert exc_info.value.status_code == 409

    def test_get_farmer_devices_success(self, device_service, mock_supabase, farmer_id):
        """Test getting farmer devices"""
        mock_devices = [
            {
                "id": str(uuid.uuid4()),
                "device_id": "katara-device-1",
                "farmer_id": str(farmer_id),
                "name": "Device 1",
                "location_lat": 33.5,
                "location_lng": -7.6,
                "registered_at": datetime.utcnow().isoformat()
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_devices
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.error = None

        result = device_service.get_farmer_devices(farmer_id)

        assert result.total == 1
        assert len(result.devices) == 1
        assert result.devices[0].device_id == "katara-device-1"


class TestDeviceValidation:
    """Test device validation schemas"""

    def test_valid_device_creation(self):
        """Test valid device creation data"""
        device_data = DeviceCreate(
            device_id="katara-550e8400-e29b-41d4-a716-446655440000",
            name="Test Device",
            location_lat=33.5,
            location_lng=-7.6
        )
        assert device_data.device_id.startswith("katara-")
        assert device_data.name == "Test Device"
        assert device_data.location_lat == 33.5
        assert device_data.location_lng == -7.6

    def test_device_id_validation(self):
        """Test device ID validation"""
        # Valid UUID
        valid_uuid = str(uuid.uuid4())
        valid_device_id = f"katara-{valid_uuid}"
        device_data = DeviceCreate(device_id=valid_device_id)
        assert device_data.device_id == valid_device_id

        # Invalid format - should raise ValidationError
        with pytest.raises(ValueError):
            DeviceCreate(device_id="invalid-format")

        # Invalid UUID - should raise ValidationError
        with pytest.raises(ValueError):
            DeviceCreate(device_id="katara-invalid-uuid")

    def test_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        device_data = DeviceCreate(
            device_id="katara-550e8400-e29b-41d4-a716-446655440000",
            location_lat=90.0,
            location_lng=180.0
        )
        assert device_data.location_lat == 90.0
        assert device_data.location_lng == 180.0

        # Invalid latitude
        with pytest.raises(ValueError):
            DeviceCreate(
                device_id="katara-550e8400-e29b-41d4-a716-446655440000",
                location_lat=91.0
            )

        # Invalid longitude
        with pytest.raises(ValueError):
            DeviceCreate(
                device_id="katara-550e8400-e29b-41d4-a716-446655440000",
                location_lng=181.0
            )

    def test_name_validation(self):
        """Test name validation"""
        # Valid name
        device_data = DeviceCreate(
            device_id="katara-550e8400-e29b-41d4-a716-446655440000",
            name="Valid Name"
        )
        assert device_data.name == "Valid Name"

        # Empty name should be stripped to None
        device_data = DeviceCreate(
            device_id="katara-550e8400-e29b-41d4-a716-446655440000",
            name="   "
        )
        assert device_data.name is None

        # Name too long
        with pytest.raises(ValueError):
            DeviceCreate(
                device_id="katara-550e8400-e29b-41d4-a716-446655440000",
                name="x" * 101  # 101 characters
            )

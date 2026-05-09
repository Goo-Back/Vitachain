"""
Integration tests for RBAC API endpoints
Tests actual FastAPI endpoints with RBAC enforcement
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from app.core.permissions import UserRole, Permission


class TestRBACIntegration:
    """Test RBAC integration with actual API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_farmer_user(self):
        """Mock farmer user"""
        return {
            "user_id": "farmer-123",
            "email": "farmer@vitachain.ma",
            "role": UserRole.FARMER,
            "full_name": "Ahmed Benali"
        }
    
    @pytest.fixture
    def mock_restaurant_user(self):
        """Mock restaurant user"""
        return {
            "user_id": "restaurant-123",
            "email": "restaurant@vitachain.ma",
            "role": UserRole.RESTAURANT,
            "full_name": "Restaurant Al Mounia"
        }
    
    @pytest.fixture
    def mock_citizen_user(self):
        """Mock citizen user"""
        return {
            "user_id": "citizen-123",
            "email": "citizen@vitachain.ma",
            "role": UserRole.CITIZEN,
            "full_name": "Mohamed Ali"
        }
    
    @pytest.fixture
    def mock_admin_user(self):
        """Mock admin user"""
        return {
            "user_id": "admin-123",
            "email": "admin@vitachain.ma",
            "role": UserRole.ADMIN,
            "full_name": "Admin User"
        }
    
    @pytest.fixture
    def mock_support_user(self):
        """Mock support user"""
        return {
            "user_id": "support-123",
            "email": "support@vitachain.ma",
            "role": UserRole.SUPPORT,
            "full_name": "Support Agent"
        }
    
    def _get_auth_headers(self, user_data):
        """Get authentication headers for user"""
        return {
            "Authorization": f"Bearer {user_data['user_id']}",
            "Cookie": "sb-access-token=test-token"
        }

    @patch('app.api.dependencies.get_current_user')
    async def test_farmer_can_access_own_endpoints(self, mock_get_current_user, client, mock_farmer_user):
        """Test farmer can access their own endpoints"""
        mock_get_current_user.return_value = mock_farmer_user
        
        # Test farmer can access telemetry
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 200
        
        # Test farmer can access devices
        response = client.get("/api/katara/devices")
        assert response.status_code == 200
        
        # Test farmer can access marketplace
        response = client.get("/api/farmarket/listings")
        assert response.status_code == 200
        
        # Test farmer cannot access admin endpoints
        response = client.get("/api/admin/users")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_restaurant_can_access_own_endpoints(self, mock_get_current_user, client, mock_restaurant_user):
        """Test restaurant can access their own endpoints"""
        mock_get_current_user.return_value = mock_restaurant_user
        
        # Test restaurant can access meals
        response = client.get("/api/secondserve/meals")
        assert response.status_code == 200
        
        # Test restaurant can access reservations
        response = client.get("/api/secondserve/reservations")
        assert response.status_code == 200
        
        # Test restaurant cannot access farmer endpoints
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_citizen_can_access_allowed_endpoints(self, mock_get_current_user, client, mock_citizen_user):
        """Test citizen can access allowed endpoints"""
        mock_get_current_user.return_value = mock_citizen_user
        
        # Test citizen can access marketplace
        response = client.get("/api/farmarket/listings")
        assert response.status_code == 200
        
        # Test citizen can make reservations
        response = client.post("/api/secondserve/reservations", json={
            "meal_id": "meal-123",
            "quantity": 2
        })
        assert response.status_code == 200
        
        # Test citizen cannot access management endpoints
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_admin_can_access_all_endpoints(self, mock_get_current_user, client, mock_admin_user):
        """Test admin can access all endpoints"""
        mock_get_current_user.return_value = mock_admin_user
        
        # Test admin can access farmer endpoints
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 200
        
        # Test admin can access restaurant endpoints
        response = client.get("/api/secondserve/meals")
        assert response.status_code == 200
        
        # Test admin can access citizen endpoints
        response = client.get("/api/farmarket/listings")
        assert response.status_code == 200
        
        # Test admin can access admin endpoints
        response = client.get("/api/admin/users")
        assert response.status_code == 200
        
        # Test admin can access support endpoints
        response = client.get("/api/support/tickets")
        assert response.status_code == 200
    
    @patch('app.api.dependencies.get_current_user')
    async def test_support_can_read_user_data(self, mock_get_current_user, client, mock_support_user):
        """Test support can read user data but not modify"""
        mock_get_current_user.return_value = mock_support_user
        
        # Test support can read user profiles
        response = client.get("/api/support/users")
        assert response.status_code == 200
        
        # Test support cannot modify user data
        response = client.patch("/api/support/users/user-123", json={
            "role": UserRole.FARMER
        })
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_unauthorized_access_denied(self, mock_get_current_user, client):
        """Test unauthorized access is denied"""
        mock_get_current_user.return_value = None
        
        # Test unauthorized access to protected endpoint
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 401
    
    @patch('app.api.dependencies.get_current_user')
    async def test_rate_limiting(self, mock_get_current_user, client, mock_farmer_user):
        """Test rate limiting on permission checks"""
        mock_get_current_user.return_value = mock_farmer_user
        
        # Simulate rapid permission checks (would trigger rate limit)
        for _ in range(150):  # Exceed rate limit of 100/min
            client.get("/api/katara/telemetry")
        
        # Should receive rate limit error
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_data_ownership_enforcement(self, mock_get_current_user, client, mock_farmer_user):
        """Test data ownership enforcement"""
        mock_get_current_user.return_value = mock_farmer_user
        
        # Test farmer can access own telemetry
        response = client.get("/api/katara/telemetry/device-123")
        assert response.status_code == 200
        
        # Test farmer cannot access other farmer's telemetry
        response = client.get("/api/katara/telemetry/device-456")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "ACCESS_DENIED"
    
    @patch('app.api.dependencies.get_current_user')
    async def test_permission_validation(self, mock_get_current_user, client):
        """Test permission validation with invalid inputs"""
        mock_get_current_user.return_value = {
            "user_id": "test-123",
            "role": "INVALID_ROLE"  # Invalid role
        }
        
        # Test invalid role raises error
        response = client.get("/api/katara/telemetry")
        assert response.status_code == 500
        assert "Invalid user_role" in response.json()["error"]["message"]


if __name__ == "__main__":
    pytest.main([__file__])

"""
Integration tests for RBAC functionality
Tests complete role-based access control workflows
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
from app.core.permissions import UserRole, Permission, rbac_manager


class TestRBACIntegration:
    """Test RBAC integration with FastAPI endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        
        # Mock user data for testing
        self.farmer_user = {
            "user_id": "farmer-123",
            "email": "farmer@vitachain.ma",
            "role": UserRole.FARMER,
            "full_name": "Ahmed Benali"
        }
        
        self.restaurant_user = {
            "user_id": "restaurant-123", 
            "email": "restaurant@vitachain.ma",
            "role": UserRole.RESTAURANT,
            "full_name": "Restaurant Al Mounia"
        }
        
        self.citizen_user = {
            "user_id": "citizen-123",
            "email": "citizen@vitachain.ma", 
            "role": UserRole.CITIZEN,
            "full_name": "Mohamed Ali"
        }
        
        self.admin_user = {
            "user_id": "admin-123",
            "email": "admin@vitachain.ma",
            "role": UserRole.ADMIN,
            "full_name": "Admin User"
        }
        
        self.support_user = {
            "user_id": "support-123",
            "email": "support@vitachain.ma",
            "role": UserRole.SUPPORT,
            "full_name": "Support Agent"
        }
    
    @patch('app.api.dependencies.get_current_user')
    def test_farmer_can_access_own_endpoints(self, mock_get_current_user):
        """Test farmer can access their own endpoints"""
        mock_get_current_user.return_value = self.farmer_user
        
        # Test farmer can access telemetry
        response = self.client.get("/api/katara/telemetry")
        assert response.status_code == 200
        
        # Test farmer can access devices
        response = self.client.get("/api/katara/devices")
        assert response.status_code == 200
        
        # Test farmer can access marketplace
        response = self.client.get("/api/farmarket/listings")
        assert response.status_code == 200
    
    @patch('app.api.dependencies.get_current_user')
    def test_farmer_cannot_access_admin_endpoints(self, mock_get_current_user):
        """Test farmer cannot access admin endpoints"""
        mock_get_current_user.return_value = self.farmer_user
        
        # Test farmer cannot access admin endpoints
        response = self.client.get("/api/admin/users")
        assert response.status_code == 403
        assert "INSUFFICIENT_PERMISSIONS" in response.json()["error"]["code"]
    
    @patch('app.api.dependencies.get_current_user')
    def test_restaurant_can_access_own_endpoints(self, mock_get_current_user):
        """Test restaurant can access their own endpoints"""
        mock_get_current_user.return_value = self.restaurant_user
        
        # Test restaurant can access meals
        response = self.client.get("/api/secondserve/meals")
        assert response.status_code == 200
        
        # Test restaurant can access reservations
        response = self.client.get("/api/secondserve/reservations")
        assert response.status_code == 200
        
        # Test restaurant can access marketplace
        response = self.client.get("/api/farmarket/listings")
        assert response.status_code == 200
    
    @patch('app.api.dependencies.get_current_user')
    def test_restaurant_cannot_access_farmer_endpoints(self, mock_get_current_user):
        """Test restaurant cannot access farmer endpoints"""
        mock_get_current_user.return_value = self.restaurant_user
        
        # Test restaurant cannot access telemetry
        response = self.client.get("/api/katara/telemetry")
        assert response.status_code == 403
        assert "INSUFFICIENT_PERMISSIONS" in response.json()["error"]["code"]
    
    @patch('app.api.dependencies.get_current_user')
    def test_citizen_can_access_allowed_endpoints(self, mock_get_current_user):
        """Test citizen can access allowed endpoints"""
        mock_get_current_user.return_value = self.citizen_user
        
        # Test citizen can access marketplace
        response = self.client.get("/api/farmarket/listings")
        assert response.status_code == 200
        
        # Test citizen can access reservations
        response = self.client.get("/api/secondserve/reservations/my")
        assert response.status_code == 200
    
    @patch('app.api.dependencies.get_current_user')
    def test_citizen_cannot_access_management_endpoints(self, mock_get_current_user):
        """Test citizen cannot access management endpoints"""
        mock_get_current_user.return_value = self.citizen_user
        
        # Test citizen cannot access meals management
        response = self.client.post("/api/secondserve/meals")
        assert response.status_code == 403
        
        # Test citizen cannot access listings management
        response = self.client.post("/api/farmarket/listings")
        assert response.status_code == 403
    
    @patch('app.api.dependencies.get_current_user')
    def test_admin_can_access_all_endpoints(self, mock_get_current_user):
        """Test admin can access all endpoints"""
        mock_get_current_user.return_value = self.admin_user
        
        # Test admin can access farmer endpoints
        response = self.client.get("/api/katara/telemetry")
        assert response.status_code == 200
        
        # Test admin can access restaurant endpoints
        response = self.client.get("/api/secondserve/meals")
        assert response.status_code == 200
        
        # Test admin can access admin endpoints
        response = self.client.get("/api/admin/users")
        assert response.status_code == 200
        
        # Test admin can access support endpoints
        response = self.client.get("/api/support/tickets")
        assert response.status_code == 200
    
    @patch('app.api.dependencies.get_current_user')
    def test_support_can_read_user_data(self, mock_get_current_user):
        """Test support can read user data but not modify"""
        mock_get_current_user.return_value = self.support_user
        
        # Test support can read user profiles
        response = self.client.get("/api/support/users")
        assert response.status_code == 200
        
        # Test support cannot modify user data
        response = self.client.patch("/api/support/users/user-123", json={"role": "FARMER"})
        assert response.status_code == 403
    
    @patch('app.api.dependencies.get_current_user')
    def test_unauthorized_access(self, mock_get_current_user):
        """Test unauthorized access without authentication"""
        mock_get_current_user.side_effect = Exception("Not authenticated")
        
        response = self.client.get("/api/katara/telemetry")
        assert response.status_code == 401
    
    def test_data_ownership_validation(self):
        """Test data ownership validation in endpoints"""
        # This would test actual data ownership logic
        # For now, we'll test the validation function directly
        
        # Admin can access any data
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, "admin-123", "farmer-456"
        )
        
        # User can access own data
        assert rbac_manager.validate_data_ownership(
            UserRole.FARMER, "farmer-123", "farmer-123"
        )
        
        # User cannot access other's data
        assert not rbac_manager.validate_data_ownership(
            UserRole.FARMER, "farmer-123", "farmer-456"
        )
        
        # Support can read any data
        assert rbac_manager.validate_data_ownership(
            UserRole.SUPPORT, "support-123", "farmer-456"
        )


class TestRBACDataAccess:
    """Test RBAC data access patterns"""
    
    def setup_method(self):
        """Setup test data"""
        self.sample_telemetry_data = {
            "device_id": "katara-device-1",
            "farmer_id": "farmer-123",
            "temperature": 25.5,
            "humidity": 65.2,
            "timestamp": "2026-05-02T10:00:00Z"
        }
        
        self.sample_meal_data = {
            "id": "meal-123",
            "restaurant_id": "restaurant-123", 
            "title": "Tajine de Poulet",
            "price": 45.0,
            "quantity_available": 10
        }
        
        self.sample_listing_data = {
            "id": "listing-123",
            "farmer_id": "farmer-123",
            "title": "Tomates cerises bio",
            "price_per_kg": 12.50,
            "quantity_kg": 100.0
        }
    
    def test_farmer_data_isolation(self):
        """Test that farmers can only access their own data"""
        farmer_id = "farmer-123"
        other_farmer_id = "farmer-456"
        
        # Farmer should access own telemetry
        assert rbac_manager.validate_data_ownership(
            UserRole.FARMER, farmer_id, farmer_id
        )
        
        # Farmer should not access other's telemetry
        assert not rbac_manager.validate_data_ownership(
            UserRole.FARMER, farmer_id, other_farmer_id
        )
    
    def test_restaurant_data_isolation(self):
        """Test that restaurants can only access their own data"""
        restaurant_id = "restaurant-123"
        other_restaurant_id = "restaurant-456"
        
        # Restaurant should access own meals
        assert rbac_manager.validate_data_ownership(
            UserRole.RESTAURANT, restaurant_id, restaurant_id
        )
        
        # Restaurant should not access other's meals
        assert not rbac_manager.validate_data_ownership(
            UserRole.RESTAURANT, restaurant_id, other_restaurant_id
        )
    
    def test_admin_data_access(self):
        """Test that admin can access all data"""
        admin_id = "admin-123"
        
        # Admin should access any user's data
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, admin_id, "farmer-123"
        )
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, admin_id, "restaurant-123"
        )
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, admin_id, "citizen-123"
        )
    
    def test_support_data_access(self):
        """Test that support can read all data but not modify"""
        support_id = "support-123"
        
        # Support should read any user's data
        assert rbac_manager.validate_data_ownership(
            UserRole.SUPPORT, support_id, "farmer-123"
        )
        assert rbac_manager.validate_data_ownership(
            UserRole.SUPPORT, support_id, "restaurant-123"
        )


class TestRBACPerformance:
    """Test RBAC performance and scalability"""
    
    def test_permission_check_performance(self):
        """Test that permission checks are fast"""
        import time
        
        # Test multiple permission checks
        start_time = time.time()
        
        for _ in range(1000):
            rbac_manager.has_permission(UserRole.FARMER, Permission.READ_OWN_TELEMETRY)
            rbac_manager.has_permission(UserRole.RESTAURANT, Permission.READ_OWN_MEALS)
            rbac_manager.has_permission(UserRole.ADMIN, Permission.READ_USERS)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 1000 checks in under 100ms
        assert total_time < 0.1, f"Permission checks too slow: {total_time}s"
    
    def test_role_validation_performance(self):
        """Test that role validation is efficient"""
        import time
        
        start_time = time.time()
        
        # Test role hierarchy checks
        for _ in range(1000):
            rbac_manager.can_access_role(UserRole.ADMIN, UserRole.FARMER)
            rbac_manager.can_access_role(UserRole.SUPPORT, UserRole.CITIZEN)
            rbac_manager.can_access_role(UserRole.FARMER, UserRole.RESTAURANT)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 1000 checks in under 50ms
        assert total_time < 0.05, f"Role validation too slow: {total_time}s"


if __name__ == "__main__":
    pytest.main([__file__])

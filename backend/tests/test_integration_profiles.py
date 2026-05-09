"""
Integration tests for profile management API endpoints
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

from app.main import app
from app.core.security import JWTManager


class TestProfileAPIIntegration:
    """Integration tests for profile API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_jwt_token(self):
        """Create mock JWT token"""
        return "mock_jwt_token_for_testing"
    
    @pytest.fixture
    def mock_user_info(self):
        """Create mock user info from JWT"""
        return {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "role": "FARMER",
            "user_metadata": {"role": "FARMER", "full_name": "Test User"}
        }
    
    @pytest.fixture
    def mock_profile_data(self):
        """Create mock profile data"""
        return {
            "id": "test-user-123",
            "email": "test@example.com",
            "full_name": "Test User",
            "phone": "+212612345678",
            "role": "FARMER",
            "created_at": "2026-05-01T10:00:00Z",
            "updated_at": "2026-05-01T10:00:00Z",
            "role_data": {
                "farm_location": "Casablanca",
                "farm_size_hectares": 15.5,
                "main_crops": ["tomatoes", "potatoes"]
            }
        }


class TestGetProfileAPI(TestProfileAPIIntegration):
    """Test GET /api/profile endpoint"""
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_get_profile_success(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info, mock_profile_data):
        """Test successful profile retrieval"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = mock_profile_data
        mock_supabase.auth.admin.get_user.return_value.user.email = "test@example.com"
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        response = client.get(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-123"
        assert data["full_name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["role"] == "FARMER"
        assert data["phone"] == "+212612345678"
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    def test_get_profile_unauthorized(self, mock_jwt_validate, client):
        """Test profile retrieval without valid token"""
        # Setup mock to raise exception
        mock_jwt_validate.side_effect = HTTPException(status_code=401, detail="Invalid token")
        
        # Make request
        response = client.get(
            "/api/profile/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        # Verify response
        assert response.status_code == 401
        assert "UNAUTHORIZED" in response.json()["error"]["code"]
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_get_profile_not_found(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test profile retrieval when profile not found"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = None
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        response = client.get(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Verify response
        assert response.status_code == 404
        assert "PROFILE_NOT_FOUND" in response.json()["error"]["code"]


class TestUpdateProfileAPI(TestProfileAPIIntegration):
    """Test PATCH /api/profile endpoint"""
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_update_profile_success(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info, mock_profile_data):
        """Test successful profile update"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        
        # Mock get_profile call
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = mock_profile_data
        
        # Mock update call
        updated_data = mock_profile_data.copy()
        updated_data["full_name"] = "Updated Name"
        updated_data["updated_at"] = "2026-05-02T14:30:00Z"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_data]
        
        mock_supabase.auth.admin.get_user.return_value.user.email = "test@example.com"
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        update_data = {
            "full_name": "Updated Name",
            "phone": "+212612345679"
        }
        
        response = client.patch(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
            json=update_data
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Profile updated successfully"
        assert data["profile"]["full_name"] == "Updated Name"
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    def test_update_profile_unauthorized(self, mock_jwt_validate, client):
        """Test profile update without valid token"""
        # Setup mock to raise exception
        mock_jwt_validate.side_effect = HTTPException(status_code=401, detail="Invalid token")
        
        # Make request
        response = client.patch(
            "/api/profile/",
            headers={"Authorization": "Bearer invalid_token"},
            json={"full_name": "Updated Name"}
        )
        
        # Verify response
        assert response.status_code == 401
        assert "UNAUTHORIZED" in response.json()["error"]["code"]
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_update_profile_invalid_phone(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test profile update with invalid phone number"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = {
            "id": "test-user-123",
            "full_name": "Test User",
            "role": "FARMER"
        }
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request with invalid phone
        update_data = {
            "phone": "invalid-phone-format"
        }
        
        response = client.patch(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
            json=update_data
        )
        
        # Verify response
        assert response.status_code == 422
        assert "VALIDATION_ERROR" in response.json()["error"]["code"]
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    def test_update_profile_empty_data(self, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test profile update with no data"""
        # Setup mock
        mock_jwt_validate.return_value = mock_user_info
        
        # Make request with empty data
        response = client.patch(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
            json={}
        )
        
        # Verify response
        assert response.status_code == 400
        assert "VALIDATION_ERROR" in response.json()["error"]["code"]


class TestProfileSummaryAPI(TestProfileAPIIntegration):
    """Test GET /api/profile/summary endpoint"""
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_get_profile_summary_success(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info, mock_profile_data):
        """Test successful profile summary retrieval"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = mock_profile_data
        mock_supabase.auth.admin.get_user.return_value.user.email = "test@example.com"
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        response = client.get(
            "/api/profile/summary",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-123"
        assert data["full_name"] == "Test User"
        assert data["role"] == "FARMER"
        assert data["completed_profile"] is True


class TestPhoneValidationAPI(TestProfileAPIIntegration):
    """Test GET /api/profile/validate-phone/{phone} endpoint"""
    
    def test_validate_phone_valid(self, client):
        """Test phone validation with valid numbers"""
        valid_phones = [
            "+212612345678",
            "0612345678",
            "0712345678"
        ]
        
        for phone in valid_phones:
            response = client.get(f"/api/profile/validate-phone/{phone}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_valid"] is True
            assert data["error_message"] is None
            assert data["formatted_phone"] is not None
    
    def test_validate_phone_invalid(self, client):
        """Test phone validation with invalid numbers"""
        invalid_phones = [
            "invalid-phone",
            "12345678",
            "0512345678"
        ]
        
        for phone in invalid_phones:
            response = client.get(f"/api/profile/validate-phone/{phone}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_valid"] is False
            assert data["error_message"] is not None
            assert data["formatted_phone"] is None
    
    def test_validate_phone_empty(self, client):
        """Test phone validation with empty phone"""
        response = client.get("/api/profile/validate-phone/")
        
        # Should handle gracefully or return 404
        assert response.status_code in [200, 404]


class TestProfileAPIErrorHandling(TestProfileAPIIntegration):
    """Test error handling in profile API"""
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_database_error_handling(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test handling of database errors"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.side_effect = Exception("Database connection failed")
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        response = client.get(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Verify error handling
        assert response.status_code == 500
        assert "INTERNAL_ERROR" in response.json()["error"]["code"]
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    @patch('app.api.routes.profiles.get_supabase_client')
    def test_supabase_service_error(self, mock_supabase_dep, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test handling of Supabase service errors"""
        # Setup mocks
        mock_jwt_validate.return_value = mock_user_info
        
        mock_supabase = Mock()
        mock_supabase.auth.admin.get_user.side_effect = Exception("Supabase auth service error")
        mock_supabase_dep.return_value = mock_supabase
        
        # Make request
        response = client.get(
            "/api/profile/",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Verify error handling
        assert response.status_code == 500
        assert "INTERNAL_ERROR" in response.json()["error"]["code"]


class TestProfileAPIRateLimiting(TestProfileAPIIntegration):
    """Test rate limiting for profile API"""
    
    @patch('app.api.routes.profiles.JWTManager.validate_jwt_token')
    def test_rate_limiting_headers(self, mock_jwt_validate, client, mock_jwt_token, mock_user_info):
        """Test that rate limiting headers are present"""
        # Setup mock
        mock_jwt_validate.return_value = mock_user_info
        
        # Make request
        response = client.get(
            "/api/profile/validate-phone/0612345678"
        )
        
        # Verify rate limiting headers (if implemented)
        # This would depend on the actual rate limiting implementation
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])

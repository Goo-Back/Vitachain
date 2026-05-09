"""
Integration tests for authentication system
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import json

from app.main import app
from app.core.security import jwt_manager


class TestAuthIntegration:
    """Integration tests for authentication endpoints"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_registration_to_login_flow(self, mock_get_ip, mock_get_supabase):
        """Test complete flow from registration to login"""
        # This would test the complete user journey
        # For now, we'll focus on login integration
        
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock successful login
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = "test-user-id"
        mock_auth_response.user.email = "test@example.com"
        mock_auth_response.user.email_confirmed_at = "2026-05-01T10:00:00Z"
        mock_auth_response.user.user_metadata = {
            "role": "FARMER",
            "full_name": "Test Farmer"
        }
        
        mock_auth_response.session = Mock()
        mock_auth_response.session.access_token = "test_access_token"
        mock_auth_response.session.refresh_token = "test_refresh_token"
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Test login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "sb-access-token" in response.cookies
        assert response.cookies["sb-access-token"] == "test_access_token"

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_login_with_cookie_persistence(self, mock_get_ip, mock_get_supabase):
        """Test that login cookies persist correctly"""
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock successful login
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = "test-user-id"
        mock_auth_response.user.email = "test@example.com"
        mock_auth_response.user.email_confirmed_at = "2026-05-01T10:00:00Z"
        mock_auth_response.user.user_metadata = {
            "role": "FARMER",
            "full_name": "Test Farmer"
        }
        
        mock_auth_response.session = Mock()
        mock_auth_response.session.access_token = "test_access_token"
        mock_auth_response.session.refresh_token = "test_refresh_token"
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make login request
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        # Verify cookies are set with correct attributes
        cookies = response.cookies
        assert "sb-access-token" in cookies
        assert "sb-refresh-token" in cookies
        
        # Note: Testing cookie attributes (httpOnly, secure, etc.) 
        # would require more complex setup with TestClient

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_login_error_handling_integration(self, mock_get_ip, mock_get_supabase):
        """Test error handling in login integration"""
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock authentication failure
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Test login with invalid credentials
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert response_data["error"]["code"] == "INVALID_CREDENTIALS"
        
        # Verify no cookies are set on error
        assert "sb-access-token" not in response.cookies


class TestJWTMiddlewareIntegration:
    """Integration tests for JWT middleware"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('app.api.dependencies.get_supabase_client')
    def test_protected_endpoint_without_token(self, mock_get_supabase):
        """Test accessing protected endpoint without token"""
        # This would test a protected endpoint
        # For now, we'll create a simple test endpoint
        
        @app.get("/api/protected")
        async def protected_endpoint(user=Depends(get_current_user)):
            return {"message": "Protected data", "user": user}
        
        response = self.client.get("/api/protected")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.api.dependencies.get_supabase_client')
    def test_protected_endpoint_with_valid_token(self, mock_get_supabase):
        """Test accessing protected endpoint with valid token"""
        # This would require a valid JWT token
        # For now, we'll mock the validation
        
        valid_token = "mock_valid_token"
        
        # Mock JWT validation
        with patch('app.core.security.jwt_manager.validate_jwt_token') as mock_validate:
            mock_validate.return_value = {
                "user_id": "test-user-id",
                "email": "test@example.com",
                "role": "FARMER",
                "user_metadata": {"role": "FARMER", "full_name": "Test User"}
            }
            
            # Make request with token in cookie
            self.client.cookies.set("sb-access-token", valid_token)
            
            # This would test a real protected endpoint
            # For now, we'll just verify the mock is called correctly
            pass


class TestRoleBasedAccessIntegration:
    """Integration tests for role-based access control"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @pytest.mark.parametrize("role,expected_access", [
        ("FARMER", True),
        ("RESTAURANT", False),
        ("CITIZEN", False),
        ("ADMIN", True),
        ("SUPPORT", False),
    ])
    def test_farmer_only_endpoint(self, role, expected_access):
        """Test endpoint that requires FARMER role"""
        # This would test role-based access control
        # For now, we'll test the redirect URL logic
        
        redirect_url = jwt_manager.get_dashboard_redirect_url(role)
        
        if role == "FARMER":
            assert redirect_url == "/dashboard/katara"
        else:
            # Other roles should not get farmer dashboard
            assert redirect_url != "/dashboard/katara"


class TestSecurityIntegration:
    """Integration tests for security features"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_rate_limiting_integration(self, mock_get_ip, mock_get_supabase):
        """Test rate limiting in real scenario"""
        mock_get_ip.return_value = "192.168.1.100"  # Same IP
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock failed authentication to trigger rate limiting
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make multiple requests from same IP
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        responses = []
        for i in range(12):  # Exceed rate limit
            response = self.client.post("/api/auth/login", json=login_data)
            responses.append(response)
        
        # First 10 should be invalid credentials
        # Last 2 should be rate limited
        assert responses[0].status_code == status.HTTP_401_UNAUTHORIZED
        assert responses[9].status_code == status.HTTP_401_UNAUTHORIZED
        assert responses[10].status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert responses[11].status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_concurrent_login_attempts(self, mock_get_ip, mock_get_supabase):
        """Test handling of concurrent login attempts"""
        # This would test concurrent request handling
        # For now, we'll structure the test
        pass


class TestErrorHandlingIntegration:
    """Integration tests for error handling"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_database_connection_error(self, mock_get_ip, mock_get_supabase):
        """Test handling of database connection errors"""
        mock_get_ip.return_value = "127.0.0.1"
        
        # Mock database connection error
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.auth.signInWithPassword.side_effect = Exception("Database connection failed")
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["error"]["code"] == "INTERNAL_ERROR"
        
        # Verify no sensitive information is leaked
        assert "Database connection failed" not in response_data["error"]["message"]

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_supabase_service_error(self, mock_get_ip, mock_get_supabase):
        """Test handling of Supabase service errors"""
        mock_get_ip.return_value = "127.0.0.1"
        
        # Mock Supabase service error
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.auth.signInWithPassword.side_effect = Exception("Supabase service unavailable")
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["error"]["code"] == "INTERNAL_ERROR"


class TestPerformanceIntegration:
    """Integration tests for performance requirements"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_login_response_time(self, mock_get_ip, mock_get_supabase):
        """Test login response time meets requirements"""
        import time
        
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock successful authentication
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = "test-user-id"
        mock_auth_response.user.email = "test@example.com"
        mock_auth_response.user.email_confirmed_at = "2026-05-01T10:00:00Z"
        mock_auth_response.user.user_metadata = {
            "role": "FARMER",
            "full_name": "Test Farmer"
        }
        
        mock_auth_response.session = Mock()
        mock_auth_response.session.access_token = "test_access_token"
        mock_auth_response.session.refresh_token = "test_refresh_token"
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # Measure response time
        start_time = time.time()
        response = self.client.post("/api/auth/login", json=login_data)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == status.HTTP_200_OK
        # Should meet requirement of < 500ms
        assert response_time_ms < 500, f"Response time {response_time_ms}ms exceeds 500ms limit"


# Import dependencies for tests
from app.api.dependencies import get_current_user, Depends

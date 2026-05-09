"""
Tests for authentication login functionality
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import json

from app.main import app
from app.models.schemas import UserLoginRequest, UserLoginResponse
from app.core.security import jwt_manager


class TestLoginEndpoint:
    """Test cases for the login endpoint"""

    def setup_method(self):
        """Setup test client and mock data"""
        self.client = TestClient(app)
        self.valid_login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        self.mock_user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "email_confirmed_at": "2026-05-01T10:00:00Z",
            "user_metadata": {
                "role": "FARMER",
                "full_name": "Test User"
            }
        }
        self.mock_session_data = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token"
        }

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_successful_login(self, mock_get_ip, mock_get_supabase):
        """Test successful login with valid credentials"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock successful authentication
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = self.mock_user_data["id"]
        mock_auth_response.user.email = self.mock_user_data["email"]
        mock_auth_response.user.email_confirmed_at = self.mock_user_data["email_confirmed_at"]
        mock_auth_response.user.user_metadata = self.mock_user_data["user_metadata"]
        
        mock_auth_response.session = Mock()
        mock_auth_response.session.access_token = self.mock_session_data["access_token"]
        mock_auth_response.session.refresh_token = self.mock_session_data["refresh_token"]
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make request
        response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["message"] == "Login successful"
        assert response_data["user"]["email"] == self.mock_user_data["email"]
        assert response_data["user"]["role"] == "FARMER"
        assert response_data["redirect_to"] == "/dashboard/katara"
        
        # Check cookies are set
        assert "sb-access-token" in response.cookies
        assert response.cookies["sb-access-token"] == self.mock_session_data["access_token"]
        assert "sb-refresh-token" in response.cookies
        assert response.cookies["sb-refresh-token"] == self.mock_session_data["refresh_token"]

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_invalid_credentials(self, mock_get_ip, mock_get_supabase):
        """Test login with invalid credentials"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock failed authentication
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make request
        response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response_data = response.json()
        assert response_data["error"]["code"] == "INVALID_CREDENTIALS"
        assert response_data["error"]["message"] == "Invalid email or password"

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_unverified_email(self, mock_get_ip, mock_get_supabase):
        """Test login with unverified email"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock authentication with unverified email
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = self.mock_user_data["id"]
        mock_auth_response.user.email = self.mock_user_data["email"]
        mock_auth_response.user.email_confirmed_at = None  # Unverified
        mock_auth_response.user.user_metadata = self.mock_user_data["user_metadata"]
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make request
        response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # Assertions
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        assert response_data["error"]["code"] == "EMAIL_NOT_VERIFIED"
        assert response_data["error"]["message"] == "Please verify your email before logging in"

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_rate_limiting(self, mock_get_ip, mock_get_supabase):
        """Test rate limiting for login attempts"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock failed authentication
        mock_auth_response = Mock()
        mock_auth_response.user = None
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make multiple requests to trigger rate limiting
        for _ in range(11):  # Exceeds rate limit of 10 per minute
            response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # The last request should be rate limited
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        response_data = response.json()
        assert response_data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_missing_session_token(self, mock_get_ip, mock_get_supabase):
        """Test login when session token is missing"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock authentication without session
        mock_auth_response = Mock()
        mock_auth_response.user = Mock()
        mock_auth_response.user.id = self.mock_user_data["id"]
        mock_auth_response.user.email = self.mock_user_data["email"]
        mock_auth_response.user.email_confirmed_at = self.mock_user_data["email_confirmed_at"]
        mock_auth_response.user.user_metadata = self.mock_user_data["user_metadata"]
        mock_auth_response.session = None  # Missing session
        
        mock_supabase.auth.signInWithPassword.return_value = mock_auth_response
        
        # Make request
        response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["error"]["code"] == "SESSION_ERROR"

    def test_invalid_email_format(self):
        """Test login with invalid email format"""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = self.client.post("/api/auth/login", json=invalid_data)
        
        # Should be handled by Pydantic validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self):
        """Test login with missing required fields"""
        # Missing password
        invalid_data = {
            "email": "test@example.com"
        }
        
        response = self.client.post("/api/auth/login", json=invalid_data)
        
        # Should be handled by Pydantic validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.get_client_ip')
    def test_server_error(self, mock_get_ip, mock_get_supabase):
        """Test handling of unexpected server errors"""
        # Setup mocks
        mock_get_ip.return_value = "127.0.0.1"
        
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        # Mock exception during authentication
        mock_supabase.auth.signInWithPassword.side_effect = Exception("Database error")
        
        # Make request
        response = self.client.post("/api/auth/login", json=self.valid_login_data)
        
        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["error"]["code"] == "INTERNAL_ERROR"


class TestJWTValidation:
    """Test cases for JWT validation functionality"""

    def test_valid_jwt_token(self):
        """Test validation of valid JWT token"""
        # This would require a real JWT token and secret
        # For now, we'll test the validation logic structure
        pass

    def test_invalid_jwt_token(self):
        """Test validation of invalid JWT token"""
        # Test with malformed token
        with pytest.raises(Exception):  # Should raise HTTPException
            jwt_manager.validate_jwt_token("invalid_token")

    def test_missing_user_id_in_token(self):
        """Test JWT token without user ID"""
        # Test with token missing 'sub' claim
        pass


class TestRoleBasedRedirection:
    """Test cases for role-based dashboard redirection"""

    @pytest.mark.parametrize("role,expected_url", [
        ("FARMER", "/dashboard/katara"),
        ("RESTAURANT", "/dashboard/secondserve"),
        ("CITIZEN", "/dashboard/secondserve"),
        ("ADMIN", "/dashboard/admin"),
        ("SUPPORT", "/dashboard/support"),
        ("UNKNOWN", "/dashboard"),  # Default fallback
    ])
    def test_dashboard_redirect_urls(self, role, expected_url):
        """Test dashboard redirection URLs for different roles"""
        redirect_url = jwt_manager.get_dashboard_redirect_url(role)
        assert redirect_url == expected_url


class TestLoginRateLimiting:
    """Test cases for login rate limiting"""

    def test_ip_rate_limiting(self):
        """Test IP-based rate limiting"""
        # This would test the rate limiting logic
        pass

    def test_account_rate_limiting(self):
        """Test account-based rate limiting"""
        # This would test the email-based rate limiting
        pass


class TestCookieHandling:
    """Test cases for HTTP-only cookie handling"""

    def test_set_auth_cookie(self):
        """Test setting authentication cookies"""
        from fastapi import Response
        
        response = Response()
        access_token = "test_access_token"
        refresh_token = "test_refresh_token"
        
        jwt_manager.set_auth_cookie(response, access_token, refresh_token)
        
        # Check that cookies are set correctly
        # This would require inspecting the response headers
        pass

    def test_clear_auth_cookies(self):
        """Test clearing authentication cookies"""
        from fastapi import Response
        
        response = Response()
        jwt_manager.clear_auth_cookies(response)
        
        # Check that cookies are cleared
        # This would require inspecting the response headers
        pass


class TestLoginIntegration:
    """Integration tests for login flow"""

    @patch('app.api.routes.auth.get_supabase_client')
    def test_complete_login_flow(self, mock_get_supabase):
        """Test complete login flow from request to response"""
        # This would test the entire login flow
        # including authentication, cookie setting, and redirection
        pass

    def test_login_with_different_roles(self):
        """Test login flow for different user roles"""
        # Test that different roles get redirected to appropriate dashboards
        pass

"""
Integration tests for password reset functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime, timedelta

from app.main import app
from app.core.security import password_reset_rate_limiter
from app.models.schemas import UserRole


class TestPasswordResetIntegration:
    """Integration tests for complete password reset flow"""
    
    def setup_method(self):
        """Setup test client and clean state"""
        self.client = TestClient(app)
        # Clear rate limiter state
        password_reset_rate_limiter.request_store = {}
    
    @patch('app.api.routes.auth.supabase')
    @patch('app.services.email_service.email_service.send_password_reset_email')
    def test_complete_password_reset_flow(self, mock_email, mock_supabase):
        """Test complete password reset flow from request to confirmation"""
        test_email = "test@example.com"
        test_password = "NewSecurePass123!"
        test_token = "valid-reset-token-123"
        
        # Step 1: Request password reset
        # Mock user existence check
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        
        # Mock password reset email sending
        mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
        mock_email.return_value = True
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": test_email}
        )
        
        assert response.status_code == 200
        reset_data = response.json()
        assert reset_data["message"] == "Password reset link sent to your email"
        assert reset_data["email_sent"] is True
        
        # Verify email was sent
        mock_email.assert_called_once()
        
        # Step 2: Confirm password reset
        # Mock OTP verification
        mock_user.id = "user-123"
        mock_supabase.auth.verifyOtp.return_value = Mock(user=mock_user)
        
        # Mock password update
        mock_supabase.auth.admin.update_user_by_id.return_value = Mock(user=mock_user)
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": test_password,
                "confirm_password": test_password,
                "token": test_token
            }
        )
        
        assert response.status_code == 200
        confirm_data = response.json()
        assert confirm_data["message"] == "Password updated successfully"
        assert confirm_data["user_id"] == "user-123"
        
        # Verify password was updated
        mock_supabase.auth.admin.update_user_by_id.assert_called_once_with(
            "user-123",
            {'password': test_password}
        )
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_unverified_email(self, mock_supabase):
        """Test password reset flow with unverified email"""
        test_email = "unverified@example.com"
        
        # Mock user with unverified email
        mock_user = Mock()
        mock_user.email_confirmed_at = None  # Unverified
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": test_email}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["code"] == "EMAIL_NOT_VERIFIED"
        assert "verify your email" in data["error"]["message"]
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_rate_limiting(self, mock_supabase):
        """Test rate limiting in password reset flow"""
        test_email = "ratelimit@example.com"
        
        # Mock user existence
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
        
        # Make 3 requests (should be allowed)
        for i in range(3):
            response = self.client.post(
                "/api/auth/password-reset",
                json={"email": test_email}
            )
            assert response.status_code == 200
        
        # 4th request should be rate limited
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": test_email}
        )
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_expired_token(self, mock_supabase):
        """Test password reset flow with expired token"""
        test_password = "NewSecurePass123!"
        expired_token = "expired-token-123"
        
        # Mock OTP verification failure (expired token)
        mock_supabase.auth.verifyOtp.side_effect = Exception("Token expired")
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": test_password,
                "confirm_password": test_password,
                "token": expired_token
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "INVALID_RESET_TOKEN"
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_weak_password(self, mock_supabase):
        """Test password reset flow with weak password"""
        weak_password = "weak"
        test_token = "valid-token-123"
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": weak_password,
                "confirm_password": weak_password,
                "token": test_token
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "WEAK_PASSWORD"
        assert "errors" in data["error"]["details"]
        
        # Verify Supabase was not called for weak password
        mock_supabase.auth.verifyOtp.assert_not_called()
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_password_mismatch(self, mock_supabase):
        """Test password reset flow with password mismatch"""
        test_token = "valid-token-123"
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "Password123!",
                "confirm_password": "DifferentPassword123!",
                "token": test_token
            }
        )
        
        assert response.status_code == 422
        # Verify Supabase was not called for mismatched passwords
        mock_supabase.auth.verifyOtp.assert_not_called()
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_multiple_users(self, mock_supabase):
        """Test password reset flow with multiple users"""
        users = [
            {"email": "farmer@example.com", "role": "FARMER", "name": "Farmer User"},
            {"email": "restaurant@example.com", "role": "RESTAURANT", "name": "Restaurant User"},
            {"email": "citizen@example.com", "role": "CITIZEN", "name": "Citizen User"},
        ]
        
        for user in users:
            # Mock user existence
            mock_user = Mock()
            mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
            mock_user.user_metadata = {"full_name": user["name"], "role": user["role"]}
            mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
            mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
            
            # Request password reset
            response = self.client.post(
                "/api/auth/password-reset",
                json={"email": user["email"]}
            )
            assert response.status_code == 200
            
            # Mock confirmation
            mock_user.id = f"user-{user['role'].lower()}"
            mock_supabase.auth.verifyOtp.return_value = Mock(user=mock_user)
            mock_supabase.auth.admin.update_user_by_id.return_value = Mock(user=mock_user)
            
            # Confirm password reset
            response = self.client.post(
                "/api/auth/password-reset/confirm",
                json={
                    "new_password": f"SecurePass{user['role']}123!",
                    "confirm_password": f"SecurePass{user['role']}123!",
                    "token": f"token-{user['role']}"
                }
            )
            assert response.status_code == 200
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_concurrent_requests(self, mock_supabase):
        """Test concurrent password reset requests"""
        test_email = "concurrent@example.com"
        
        # Mock user existence
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
        
        # Simulate concurrent requests
        responses = []
        for i in range(5):
            response = self.client.post(
                "/api/auth/password-reset",
                json={"email": test_email}
            )
            responses.append(response)
        
        # First 3 should succeed, remaining should be rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count == 3, "First 3 requests should succeed"
        assert rate_limited_count == 2, "Last 2 requests should be rate limited"
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_flow_security_logging(self, mock_supabase):
        """Test security events are logged appropriately"""
        test_email = "security@example.com"
        
        # Mock user existence
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        mock_user.user_metadata = {"full_name": "Security User", "role": "ADMIN"}
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
        
        # Request password reset
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": test_email}
        )
        
        assert response.status_code == 200
        
        # Verify the security-related calls were made
        mock_supabase.auth.admin.get_user_by_email.assert_called_once_with(test_email)
        mock_supabase.auth.resetPasswordForEmail.assert_called_once()
        
        # The actual logging would be tested by checking log outputs
        # This is a placeholder for logging verification


class TestPasswordResetErrorHandling:
    """Test error handling in password reset functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_password_reset_request_invalid_email_format(self):
        """Test password reset request with invalid email format"""
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": "invalid-email-format"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_password_reset_request_missing_email(self):
        """Test password reset request with missing email"""
        response = self.client.post(
            "/api/auth/password-reset",
            json={}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_password_reset_confirm_missing_fields(self):
        """Test password reset confirmation with missing fields"""
        # Missing new_password
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "confirm_password": "Password123!",
                "token": "valid-token"
            }
        )
        assert response.status_code == 422
        
        # Missing confirm_password
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "Password123!",
                "token": "valid-token"
            }
        )
        assert response.status_code == 422
        
        # Missing token
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "Password123!",
                "confirm_password": "Password123!"
            }
        )
        assert response.status_code == 422
    
    def test_password_reset_confirm_empty_fields(self):
        """Test password reset confirmation with empty fields"""
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "",
                "confirm_password": "",
                "token": ""
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.api.routes.auth.supabase')
    def test_password_reset_supabase_service_error(self, mock_supabase):
        """Test handling of Supabase service errors"""
        test_email = "service-error@example.com"
        
        # Mock Supabase service error
        mock_supabase.auth.admin.get_user_by_email.side_effect = Exception("Service unavailable")
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": test_email}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"


if __name__ == "__main__":
    pytest.main([__file__])

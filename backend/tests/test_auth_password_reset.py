"""
Unit tests for password reset functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.core.security import password_validator, password_reset_rate_limiter
from app.models.schemas import (
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse
)


class TestPasswordValidator:
    """Test password validation functionality"""
    
    def test_validate_password_strength_valid(self):
        """Test valid password validation"""
        valid_passwords = [
            "SecurePass123!",
            "MyStrongP@ssw0rd",
            "ComplexPassword2026#",
            "ValidPass123$",
            "Str0ng!Password"
        ]
        
        for password in valid_passwords:
            is_valid, errors = password_validator.validate_password_strength(password)
            assert is_valid, f"Password '{password}' should be valid"
            assert len(errors) == 0, f"Password '{password}' should have no errors"
    
    def test_validate_password_strength_invalid(self):
        """Test invalid password validation"""
        test_cases = [
            ("short", ["Password must be at least 8 characters long"]),
            ("nouppercase1!", ["Password must contain at least one uppercase letter"]),
            ("NOLOWERCASE1!", ["Password must contain at least one lowercase letter"]),
            ("NoNumbers!", ["Password must contain at least one number"]),
            ("NoSpecial123", ["Password should contain at least one special character"]),
            ("a", ["Password must be at least 8 characters long", 
                   "Password must contain at least one uppercase letter",
                   "Password must contain at least one lowercase letter",
                   "Password must contain at least one number",
                   "Password should contain at least one special character"])
        ]
        
        for password, expected_errors in test_cases:
            is_valid, errors = password_validator.validate_password_strength(password)
            assert not is_valid, f"Password '{password}' should be invalid"
            assert len(errors) > 0, f"Password '{password}' should have errors"
    
    def test_get_password_strength_score(self):
        """Test password strength scoring"""
        test_cases = [
            ("weak123", "weak"),  # Meets minimum requirements
            ("StrongPass123!", "strong"),  # Good password
            ("VeryStrongP@ssw0rd2026!", "very_strong"),  # Excellent password
            ("a", "very_weak"),  # Very weak password
            ("password", "very_weak"),  # Common pattern
        ]
        
        for password, expected_strength in test_cases:
            result = password_validator.get_password_strength_score(password)
            assert result["strength"] == expected_strength, f"Password '{password}' should be {expected_strength}"
            assert 0 <= result["score"] <= 100, f"Score should be between 0 and 100"
            assert isinstance(result["feedback"], list), "Feedback should be a list"


class TestPasswordResetRateLimiter:
    """Test password reset rate limiting"""
    
    def setup_method(self):
        """Setup fresh rate limiter for each test"""
        self.rate_limiter = password_reset_rate_limiter
        # Clear the request store
        self.rate_limiter.request_store = {}
    
    def test_rate_limit_within_limits(self):
        """Test requests within rate limits"""
        email = "test@example.com"
        ip = "192.168.1.1"
        
        # First request should be allowed
        allowed, reason = self.rate_limiter.check_rate_limit(email, ip)
        assert allowed, "First request should be allowed"
        assert reason == "", "No reason should be provided for allowed request"
        
        # Second request should be allowed
        allowed, reason = self.rate_limiter.check_rate_limit(email, ip)
        assert allowed, "Second request should be allowed"
        
        # Third request should be allowed
        allowed, reason = self.rate_limiter.check_rate_limit(email, ip)
        assert allowed, "Third request should be allowed"
    
    def test_email_rate_limit_exceeded(self):
        """Test email-based rate limiting"""
        email = "test@example.com"
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        
        # Make 3 requests from same email (different IPs)
        for i in range(3):
            allowed, reason = self.rate_limiter.check_rate_limit(email, f"192.168.1.{i+1}")
            assert allowed, f"Request {i+1} should be allowed"
        
        # Fourth request should be blocked
        allowed, reason = self.rate_limiter.check_rate_limit(email, ip2)
        assert not allowed, "Fourth request should be blocked"
        assert "Too many password reset requests for this email" in reason
    
    def test_ip_rate_limit_exceeded(self):
        """Test IP-based rate limiting"""
        ip = "192.168.1.1"
        
        # Make 10 requests from same IP (different emails)
        for i in range(10):
            allowed, reason = self.rate_limiter.check_rate_limit(f"test{i}@example.com", ip)
            assert allowed, f"Request {i+1} should be allowed"
        
        # Eleventh request should be blocked
        allowed, reason = self.rate_limiter.check_rate_limit("test10@example.com", ip)
        assert not allowed, "Eleventh request should be blocked"
        assert "Too many password reset requests from this IP" in reason


class TestPasswordResetEndpoints:
    """Test password reset API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('app.api.routes.auth.supabase')
    @patch('app.api.routes.auth.password_reset_rate_limiter')
    def test_request_password_reset_success(self, mock_rate_limiter, mock_supabase):
        """Test successful password reset request"""
        # Mock rate limiter to allow request
        mock_rate_limiter.check_rate_limit.return_value = (True, "")
        
        # Mock Supabase user existence check
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        
        # Mock password reset email sending
        mock_supabase.auth.resetPasswordForEmail.return_value = Mock()
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset link sent to your email"
        assert data["email_sent"] is True
        assert data["expires_in"] == 3600
    
    @patch('app.api.routes.auth.supabase')
    @patch('app.api.routes.auth.password_reset_rate_limiter')
    def test_request_password_reset_rate_limit(self, mock_rate_limiter, mock_supabase):
        """Test password reset request rate limiting"""
        # Mock rate limiter to block request
        mock_rate_limiter.check_rate_limit.return_value = (False, "Rate limit exceeded")
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    
    @patch('app.api.routes.auth.supabase')
    @patch('app.api.routes.auth.password_reset_rate_limiter')
    def test_request_password_reset_user_not_found(self, mock_rate_limiter, mock_supabase):
        """Test password reset request for non-existent user"""
        # Mock rate limiter to allow request
        mock_rate_limiter.check_rate_limit.return_value = (True, "")
        
        # Mock Supabase user not found
        mock_supabase.auth.admin.get_user_by_email.side_effect = Exception("User not found")
        
        response = self.client.post(
            "/api/auth/password-reset",
            json={"email": "nonexistent@example.com"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "USER_NOT_FOUND"
    
    @patch('app.api.routes.auth.supabase')
    def test_confirm_password_reset_success(self, mock_supabase):
        """Test successful password reset confirmation"""
        # Mock Supabase OTP verification
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_supabase.auth.verifyOtp.return_value = Mock(user=mock_user)
        
        # Mock password update
        mock_supabase.auth.admin.update_user_by_id.return_value = Mock(user=mock_user)
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "token": "valid-token-123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password updated successfully"
        assert data["user_id"] == "user-123"
    
    @patch('app.api.routes.auth.supabase')
    def test_confirm_password_reset_weak_password(self, mock_supabase):
        """Test password reset confirmation with weak password"""
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "weak",
                "confirm_password": "weak",
                "token": "valid-token-123"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "WEAK_PASSWORD"
        assert "errors" in data["error"]["details"]
    
    def test_confirm_password_reset_password_mismatch(self):
        """Test password reset confirmation with password mismatch"""
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "SecurePass123!",
                "confirm_password": "DifferentPass123!",
                "token": "valid-token-123"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "Passwords do not match" in str(data)
    
    @patch('app.api.routes.auth.supabase')
    def test_confirm_password_reset_invalid_token(self, mock_supabase):
        """Test password reset confirmation with invalid token"""
        # Mock Supabase OTP verification failure
        mock_supabase.auth.verifyOtp.side_effect = Exception("Invalid token")
        
        response = self.client.post(
            "/api/auth/password-reset/confirm",
            json={
                "new_password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "token": "invalid-token"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "INVALID_RESET_TOKEN"


class TestPasswordResetSchemas:
    """Test password reset Pydantic schemas"""
    
    def test_password_reset_request_valid(self):
        """Test valid password reset request schema"""
        request_data = {"email": "test@example.com"}
        request = PasswordResetRequest(**request_data)
        assert request.email == "test@example.com"
    
    def test_password_reset_request_invalid_email(self):
        """Test invalid email in password reset request"""
        with pytest.raises(ValueError):
            PasswordResetRequest(email="invalid-email")
    
    def test_password_reset_confirm_request_valid(self):
        """Test valid password reset confirmation request"""
        request_data = {
            "new_password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "token": "valid-token-123"
        }
        request = PasswordResetConfirmRequest(**request_data)
        assert request.new_password == "SecurePass123!"
        assert request.confirm_password == "SecurePass123!"
        assert request.token == "valid-token-123"
    
    def test_password_reset_confirm_request_password_mismatch(self):
        """Test password mismatch in confirmation request"""
        with pytest.raises(ValueError, match="Passwords do not match"):
            PasswordResetConfirmRequest(
                new_password="SecurePass123!",
                confirm_password="DifferentPass123!",
                token="valid-token-123"
            )
    
    def test_password_reset_confirm_request_short_password(self):
        """Test short password in confirmation request"""
        with pytest.raises(ValueError):
            PasswordResetConfirmRequest(
                new_password="short",
                confirm_password="short",
                token="valid-token-123"
            )


if __name__ == "__main__":
    pytest.main([__file__])

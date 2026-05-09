"""
Unit tests for magic link authentication functionality
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from app.core.security import magic_link_manager, magic_link_rate_limiter
from app.models.schemas import MagicLinkRequest, MagicLinkResponse
from app.main import app


class TestMagicLinkTokenGeneration:
    """Test magic link token generation and validation"""
    
    def test_generate_token(self):
        """Test successful token generation"""
        email = "test@example.com"
        token = magic_link_manager.generate_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify payload
        payload = jwt.decode(
            token, 
            "test_secret",  # This would be SUPABASE_JWT_SECRET in real env
            algorithms=["HS256"],
            options={"verify_signature": False}  # Skip signature verification for test
        )
        
        assert payload["email"] == email
        assert payload["type"] == "magic_link"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_token_expiry(self):
        """Test token expiry time"""
        email = "test@example.com"
        token = magic_link_manager.generate_token(email)
        
        # Decode token to check expiry
        payload = jwt.decode(
            token,
            "test_secret",
            algorithms=["HS256"],
            options={"verify_signature": False}
        )
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        expected_expiry = datetime.utcnow() + timedelta(minutes=15)
        
        # Allow 1 minute tolerance
        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        assert time_diff < 60
    
    def test_validate_valid_token(self):
        """Test successful token validation"""
        email = "test@example.com"
        token = magic_link_manager.generate_token(email)
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            payload = magic_link_manager.validate_token(token)
            
            assert payload["email"] == email
            assert payload["type"] == "magic_link"
    
    def test_validate_expired_token(self):
        """Test validation of expired token"""
        email = "test@example.com"
        
        # Create expired token by manipulating expiry
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            expired_payload = {
                'email': email,
                'exp': datetime.utcnow() - timedelta(minutes=1),  # Expired
                'iat': datetime.utcnow() - timedelta(minutes=16),
                'jti': 'test-jti',
                'type': 'magic_link'
            }
            
            expired_token = jwt.encode(expired_payload, 'test_secret', algorithm='HS256')
            
            with pytest.raises(Exception) as exc_info:
                magic_link_manager.validate_token(expired_token)
            
            assert "expired" in str(exc_info.value).lower()
    
    def test_validate_invalid_token(self):
        """Test validation of invalid token"""
        invalid_token = "invalid.token.string"
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            with pytest.raises(Exception) as exc_info:
                magic_link_manager.validate_token(invalid_token)
            
            assert "invalid" in str(exc_info.value).lower()
    
    def test_validate_wrong_token_type(self):
        """Test validation of token with wrong type"""
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            wrong_type_payload = {
                'email': 'test@example.com',
                'exp': datetime.utcnow() + timedelta(minutes=15),
                'iat': datetime.utcnow(),
                'jti': 'test-jti',
                'type': 'wrong_type'  # Wrong type
            }
            
            wrong_token = jwt.encode(wrong_type_payload, 'test_secret', algorithm='HS256')
            
            with pytest.raises(Exception) as exc_info:
                magic_link_manager.validate_token(wrong_token)
            
            assert "token type" in str(exc_info.value).lower()
    
    def test_extract_email_from_token(self):
        """Test email extraction from valid token"""
        email = "test@example.com"
        token = magic_link_manager.generate_token(email)
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            extracted_email = magic_link_manager.extract_email_from_token(token)
            assert extracted_email == email
    
    def test_is_token_expired_false(self):
        """Test token expiry check for valid token"""
        email = "test@example.com"
        token = magic_link_manager.generate_token(email)
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            is_expired = magic_link_manager.is_token_expired(token)
            assert is_expired is False
    
    def test_is_token_expired_true(self):
        """Test token expiry check for expired token"""
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            expired_payload = {
                'email': 'test@example.com',
                'exp': datetime.utcnow() - timedelta(minutes=1),
                'iat': datetime.utcnow() - timedelta(minutes=16),
                'jti': 'test-jti',
                'type': 'magic_link'
            }
            
            expired_token = jwt.encode(expired_payload, 'test_secret', algorithm='HS256')
            
            is_expired = magic_link_manager.is_token_expired(expired_token)
            assert is_expired is True


class TestMagicLinkRateLimiter:
    """Test magic link rate limiting functionality"""
    
    def setup_method(self):
        """Reset rate limiter before each test"""
        magic_link_rate_limiter.request_store = {}
    
    def test_rate_limit_allow_first_request(self):
        """Test that first request is allowed"""
        email = "test@example.com"
        ip = "192.168.1.1"
        
        allowed, reason = magic_link_rate_limiter.check_rate_limit(email, ip)
        
        assert allowed is True
        assert reason == ""
    
    def test_rate_limit_email_limit(self):
        """Test email-based rate limiting"""
        email = "test@example.com"
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        
        # Make 3 requests (should be allowed)
        for i in range(3):
            allowed, reason = magic_link_rate_limiter.check_rate_limit(email, f"192.168.1.{i+1}")
            assert allowed is True, f"Request {i+1} should be allowed"
        
        # 4th request should be blocked
        allowed, reason = magic_link_rate_limiter.check_rate_limit(email, ip2)
        assert allowed is False
        assert "email" in reason.lower()
    
    def test_rate_limit_ip_limit(self):
        """Test IP-based rate limiting"""
        ip = "192.168.1.1"
        
        # Make 10 requests from same IP (should be allowed)
        for i in range(10):
            email = f"user{i}@example.com"
            allowed, reason = magic_link_rate_limiter.check_rate_limit(email, ip)
            assert allowed is True, f"Request {i+1} should be allowed"
        
        # 11th request should be blocked
        allowed, reason = magic_link_rate_limiter.check_rate_limit("user11@example.com", ip)
        assert allowed is False
        assert "ip" in reason.lower()
    
    def test_rate_limit_cleanup_old_entries(self):
        """Test that old entries are cleaned up"""
        email = "test@example.com"
        ip = "192.168.1.1"
        
        # Add an old entry (2 hours ago)
        old_time = datetime.utcnow() - timedelta(hours=2)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = old_time
            magic_link_rate_limiter.check_rate_limit(email, ip)
        
        # Verify old entry exists
        email_key = f"magic_email_{email}"
        assert email_key in magic_link_rate_limiter.request_store
        
        # Make new request (should trigger cleanup)
        new_time = datetime.utcnow()
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = new_time
            allowed, reason = magic_link_rate_limiter.check_rate_limit("new@example.com", "192.168.1.2")
        
        # Old entry should be cleaned up
        assert email_key not in magic_link_rate_limiter.request_store
        assert allowed is True


class TestMagicLinkSchemas:
    """Test magic link Pydantic schemas"""
    
    def test_magic_link_request_valid(self):
        """Test valid magic link request schema"""
        request_data = {"email": "test@example.com"}
        request = MagicLinkRequest(**request_data)
        
        assert request.email == "test@example.com"
    
    def test_magic_link_request_invalid_email(self):
        """Test invalid email in magic link request"""
        request_data = {"email": "invalid-email"}
        
        with pytest.raises(Exception) as exc_info:
            MagicLinkRequest(**request_data)
        
        assert "email" in str(exc_info.value).lower()
    
    def test_magic_link_response_valid(self):
        """Test valid magic link response schema"""
        response_data = {
            "message": "Magic link sent",
            "email_sent": True,
            "expires_in": 900
        }
        response = MagicLinkResponse(**response_data)
        
        assert response.message == "Magic link sent"
        assert response.email_sent is True
        assert response.expires_in == 900
    
    def test_magic_link_response_invalid_expires_in(self):
        """Test invalid expires_in in magic link response"""
        response_data = {
            "message": "Magic link sent",
            "email_sent": True,
            "expires_in": -1  # Invalid negative value
        }
        
        # Pydantic should accept this but we might want to add validation
        response = MagicLinkResponse(**response_data)
        assert response.expires_in == -1


class TestMagicLinkIntegration:
    """Integration tests for magic link functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_client.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        return mock_client
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_magic_link_request_success(self, mock_email_service, mock_get_supabase, client):
        """Test successful magic link request"""
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        
        mock_email_service.send_magic_link_email = AsyncMock(return_value=True)
        
        with patch('app.core.security.settings.FRONTEND_URL', 'http://localhost:3000'):
            response = client.post(
                "/api/auth/magic-link",
                json={"email": "test@example.com"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email"
        assert data["email_sent"] is True
        assert data["expires_in"] == 900
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_request_user_not_found(self, mock_get_supabase, client):
        """Test magic link request for non-existent user"""
        mock_supabase = Mock()
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=None)
        mock_get_supabase.return_value = mock_supabase
        
        response = client.post(
            "/api/auth/magic-link",
            json={"email": "nonexistent@example.com"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "USER_NOT_FOUND"
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_request_unverified_email(self, mock_get_supabase, client):
        """Test magic link request for unverified email"""
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = None  # Unverified
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        
        response = client.post(
            "/api/auth/magic-link",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "EMAIL_NOT_VERIFIED" in data["error"]["code"]
    
    def test_magic_link_request_invalid_email(self, client):
        """Test magic link request with invalid email"""
        response = client.post(
            "/api/auth/magic-link",
            json={"email": "invalid-email"}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_magic_link_request_rate_limit(self, mock_email_service, mock_get_supabase, client):
        """Test magic link request rate limiting"""
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        
        mock_email_service.send_magic_link_email = AsyncMock(return_value=True)
        
        # Make multiple requests to trigger rate limit
        for i in range(4):  # Exceed the limit of 3 per hour
            response = client.post(
                "/api/auth/magic-link",
                json={"email": "test@example.com"},
                headers={"X-Forwarded-For": "192.168.1.1"}
            )
        
        # The last request should be rate limited
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"


if __name__ == "__main__":
    pytest.main([__file__])

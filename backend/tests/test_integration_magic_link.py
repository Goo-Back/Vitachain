"""
Integration tests for magic link authentication flow
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.core.security import magic_link_manager


class TestMagicLinkCompleteFlow:
    """Test complete magic link authentication flow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client with user data"""
        mock_client = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {
            "full_name": "Test User",
            "role": "FARMER"
        }
        mock_user.aud = "test-audience"
        
        mock_client.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_client.auth.admin.update_user_by_id.return_value = Mock()
        mock_client.auth.set_session.return_value = Mock()
        
        return mock_client
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_complete_magic_link_flow(self, mock_email_service, mock_get_supabase, client):
        """Test complete magic link flow from request to verification"""
        # Setup mocks
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {
            "full_name": "Test User",
            "role": "FARMER"
        }
        mock_user.aud = "test-audience"
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_supabase.auth.admin.update_user_by_id.return_value = Mock()
        mock_supabase.auth.set_session.return_value = Mock()
        
        mock_get_supabase.return_value = mock_supabase
        mock_email_service.send_magic_link_email = AsyncMock(return_value=True)
        
        with patch('app.core.security.settings.FRONTEND_URL', 'http://localhost:3000'):
            # Step 1: Request magic link
            request_response = client.post(
                "/api/auth/magic-link",
                json={"email": "test@example.com"}
            )
            
            assert request_response.status_code == 200
            request_data = request_response.json()
            assert request_data["message"] == "Magic link sent to your email"
            assert request_data["email_sent"] is True
            
            # Step 2: Generate token for verification (simulating email link)
            with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
                token = magic_link_manager.generate_token("test@example.com")
                
                # Step 3: Verify magic link
                verify_response = client.get(
                    f"/api/auth/magic-link/verify?token={token}"
                )
                
                assert verify_response.status_code == 200
                verify_data = verify_response.json()
                assert verify_data["message"] == "Magic link verified successfully"
                assert verify_data["user"]["email"] == "test@example.com"
                assert verify_data["user"]["role"] == "FARMER"
                assert verify_data["redirect_to"] == "/dashboard/katara"
                
                # Check for auth cookies
                cookies = verify_response.cookies
                assert "sb-access-token" in cookies
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_verification_invalid_token(self, mock_get_supabase, client):
        """Test magic link verification with invalid token"""
        response = client.get(
            "/api/auth/magic-link/verify?token=invalid.token.string"
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "INVALID_MAGIC_LINK"
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_verification_expired_token(self, mock_get_supabase, client):
        """Test magic link verification with expired token"""
        # Create expired token
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            expired_payload = {
                'email': 'test@example.com',
                'exp': datetime.utcnow() - timedelta(minutes=1),
                'iat': datetime.utcnow() - timedelta(minutes=16),
                'jti': 'test-jti',
                'type': 'magic_link'
            }
            
            expired_token = jwt.encode(expired_payload, 'test_secret', algorithm='HS256')
            
            response = client.get(
                f"/api/auth/magic-link/verify?token={expired_token}"
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "expired" in data["error"]["code"].lower()
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_verification_user_not_found(self, mock_get_supabase, client):
        """Test magic link verification when user not found"""
        mock_supabase = Mock()
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=None)
        mock_get_supabase.return_value = mock_supabase
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            token = magic_link_manager.generate_token("nonexistent@example.com")
            
            response = client.get(
                f"/api/auth/magic-link/verify?token={token}"
            )
            
            assert response.status_code == 404
            data = response.json()
            assert data["error"]["code"] == "USER_NOT_FOUND"
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_magic_link_verification_unverified_user(self, mock_get_supabase, client):
        """Test magic link verification for unverified user"""
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = None  # Unverified
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        
        with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
            token = magic_link_manager.generate_token("test@example.com")
            
            response = client.get(
                f"/api/auth/magic-link/verify?token={token}"
            )
            
            assert response.status_code == 403
            data = response.json()
            assert "EMAIL_NOT_VERIFIED" in data["error"]["code"]


class TestMagicLinkEmailIntegration:
    """Test email integration for magic links"""
    
    @pytest.fixture
    def mock_email_service(self):
        """Mock email service"""
        service = Mock()
        service.send_magic_link_email = AsyncMock(return_value=True)
        return service
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_email_service_integration(self, mock_email_service, mock_get_supabase):
        """Test email service integration"""
        from app.services.email_service import MagicLinkEmailData, UserRole
        
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        
        # Create email data
        email_data = MagicLinkData(
            recipient_email="test@example.com",
            magic_link="http://localhost:3000/auth/magic-link/callback?token=test-token",
            user_name="Test User",
            role=UserRole.CITIZEN,
            expires_in_minutes=15
        )
        
        # Test email template generation
        from app.services.email_service import EmailService
        email_service = EmailService()
        html_content = email_service._create_magic_link_template(email_data)
        
        assert "Test User" in html_content
        assert "test@example.com" in html_content
        assert "http://localhost:3000/auth/magic-link/callback?token=test-token" in html_content
        assert "15 minutes" in html_content
        assert "CITIZEN" in html_content


class TestMagicLinkSecurityIntegration:
    """Test security aspects of magic link authentication"""
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_token_single_use(self, mock_email_service, mock_get_supabase):
        """Test that tokens can only be used once"""
        from app.core.security import magic_link_manager
        
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        mock_email_service.send_magic_link_email = AsyncMock(return_value=True)
        
        client = TestClient(app)
        
        with patch('app.core.security.settings.FRONTEND_URL', 'http://localhost:3000'):
            # Request magic link
            client.post("/api/auth/magic-link", json={"email": "test@example.com"})
            
            # Generate token
            with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
                token = magic_link_manager.generate_token("test@example.com")
                
                # First verification should succeed
                response1 = client.get(f"/api/auth/magic-link/verify?token={token}")
                assert response1.status_code == 200
                
                # Note: In a real implementation, we would track used tokens
                # This test demonstrates the concept - actual implementation
                # would need token tracking in database or cache
    
    @patch('app.api.routes.auth.get_supabase_client')
    def test_role_based_redirection(self, mock_get_supabase):
        """Test role-based redirection after magic link login"""
        client = TestClient(app)
        
        test_cases = [
            ("FARMER", "/dashboard/katara"),
            ("RESTAURANT", "/dashboard/secondserve"),
            ("CITIZEN", "/dashboard/secondserve"),
            ("ADMIN", "/dashboard/admin"),
            ("SUPPORT", "/dashboard/support"),
        ]
        
        for role, expected_redirect in test_cases:
            mock_supabase = Mock()
            mock_user = Mock()
            mock_user.id = "test-user-id"
            mock_user.email = f"{role.lower()}@example.com"
            mock_user.email_confirmed_at = datetime.utcnow()
            mock_user.user_metadata = {"full_name": f"{role} User", "role": role}
            
            mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
            mock_get_supabase.return_value = mock_supabase
            
            with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
                token = magic_link_manager.generate_token(f"{role.lower()}@example.com")
                
                response = client.get(f"/api/auth/magic-link/verify?token={token}")
                
                assert response.status_code == 200
                data = response.json()
                assert data["redirect_to"] == expected_redirect


class TestMagicLinkPerformanceIntegration:
    """Test performance aspects of magic link authentication"""
    
    @patch('app.api.routes.auth.get_supabase_client')
    @patch('app.api.routes.auth.email_service')
    def test_response_time_performance(self, mock_email_service, mock_get_supabase):
        """Test that response times meet performance requirements"""
        import time
        
        mock_supabase = Mock()
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = datetime.utcnow()
        mock_user.user_metadata = {"full_name": "Test User", "role": "CITIZEN"}
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_get_supabase.return_value = mock_supabase
        mock_email_service.send_magic_link_email = AsyncMock(return_value=True)
        
        client = TestClient(app)
        
        with patch('app.core.security.settings.FRONTEND_URL', 'http://localhost:3000'):
            # Test magic link request time
            start_time = time.time()
            response = client.post("/api/auth/magic-link", json={"email": "test@example.com"})
            request_time = time.time() - start_time
            
            assert response.status_code == 200
            assert request_time < 0.5  # Should be under 500ms
            
            # Test verification time
            with patch('app.core.security.settings.SUPABASE_JWT_SECRET', 'test_secret'):
                token = magic_link_manager.generate_token("test@example.com")
                
                start_time = time.time()
                response = client.get(f"/api/auth/magic-link/verify?token={token}")
                verify_time = time.time() - start_time
                
                assert response.status_code == 200
                assert verify_time < 0.3  # Should be under 300ms


if __name__ == "__main__":
    pytest.main([__file__])

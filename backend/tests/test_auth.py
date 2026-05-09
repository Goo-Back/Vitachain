"""
Tests for authentication endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.schemas import UserRole, UserRegistrationRequest


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def valid_registration_data(self):
        """Valid registration data"""
        return {
            "email": "test@example.com",
            "role": UserRole.FARMER.value,
            "full_name": "Test User"
        }

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        mock_auth = Mock()
        mock_client.auth = mock_auth
        return mock_client

    @pytest.fixture
    def mock_email_service(self):
        """Mock email service"""
        with patch('app.services.email_service.email_service') as mock:
            mock.send_verification_email = AsyncMock(return_value=True)
            yield mock

    def test_register_user_success(self, client, valid_registration_data, mock_supabase, mock_email_service):
        """Test successful user registration"""
        # Mock Supabase responses
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = None
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = Mock()
        mock_auth_response.session.access_token = "test-token"
        
        mock_supabase.auth.sign_up.return_value = mock_auth_response
        mock_supabase.auth.admin.get_user_by_email.side_effect = Exception("User not found")
        
        # Mock email service
        mock_email_service.send_verification_email.return_value = True
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=valid_registration_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Registration successful. Please check your email for verification."
        assert data["user_id"] == "test-user-id"
        assert data["email_sent"] is True
        
        # Verify Supabase was called correctly
        mock_supabase.auth.sign_up.assert_called_once()
        call_args = mock_supabase.auth.sign_up.call_args[0][0]
        assert call_args["email"] == "test@example.com"
        assert call_args["options"]["data"]["role"] == UserRole.FARMER.value
        assert call_args["options"]["data"]["full_name"] == "Test User"
        
        # Verify email was sent
        mock_email_service.send_verification_email.assert_called_once()

    def test_register_user_invalid_email(self, client, mock_supabase, mock_email_service):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "role": UserRole.FARMER.value,
            "full_name": "Test User"
        }
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_register_user_missing_role(self, client, mock_supabase, mock_email_service):
        """Test registration with missing role"""
        invalid_data = {
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"

    def test_register_user_email_already_exists(self, client, valid_registration_data, mock_supabase, mock_email_service):
        """Test registration with existing email"""
        # Mock existing user
        mock_existing_user = Mock()
        mock_existing_user.email = "test@example.com"
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_existing_user)
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=valid_registration_data)
        
        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "EMAIL_EXISTS"

    def test_register_user_rate_limit(self, client, valid_registration_data, mock_supabase, mock_email_service):
        """Test registration rate limiting"""
        # Mock rate limit check to fail
        with patch('app.api.routes.auth.check_rate_limit', return_value=False), \
             patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=valid_registration_data)
        
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_register_user_email_service_failure(self, client, valid_registration_data, mock_supabase, mock_email_service):
        """Test registration when email service fails"""
        # Mock successful Supabase registration
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        mock_supabase.auth.sign_up.return_value = mock_auth_response
        mock_supabase.auth.admin.get_user_by_email.side_effect = Exception("User not found")
        
        # Mock email service failure
        mock_email_service.send_verification_email.return_value = False
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/register", json=valid_registration_data)
        
        assert response.status_code == 201  # Still succeeds but email_sent is False
        data = response.json()
        assert data["email_sent"] is False

    def test_verify_email_success(self, client, mock_supabase):
        """Test successful email verification"""
        # Mock user data
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = None
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        # Mock admin update
        mock_updated_user = Mock()
        mock_updated_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        
        mock_update_response = Mock()
        mock_update_response.user = mock_updated_user
        
        mock_supabase.auth.admin.get_user.return_value = mock_auth_response
        mock_supabase.auth.admin.update_user_by_id.return_value = mock_update_response
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.get("/api/auth/verify?token=test-token")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email verified successfully"
        assert data["status"] == "verified"
        assert data["user_id"] == "test-user-id"

    def test_verify_email_invalid_token(self, client, mock_supabase):
        """Test email verification with invalid token"""
        mock_supabase.auth.admin.get_user.side_effect = Exception("Invalid token")
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.get("/api/auth/verify?token=invalid-token")
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_TOKEN"

    def test_verify_email_already_verified(self, client, mock_supabase):
        """Test email verification for already verified user"""
        # Mock already verified user
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        
        mock_supabase.auth.admin.get_user.return_value = Mock(user=mock_user)
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.get("/api/auth/verify?token=test-token")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "already_verified"

    def test_resend_verification_success(self, client, mock_supabase, mock_email_service):
        """Test successful resend verification email"""
        # Mock user
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.email_confirmed_at = None
        mock_user.user_metadata = {
            "role": UserRole.FARMER.value,
            "full_name": "Test User"
        }
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        mock_email_service.send_verification_email.return_value = True
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/resend-verification", json={"email": "test@example.com"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Verification email sent successfully"
        assert data["email_sent"] is True

    def test_resend_verification_user_not_found(self, client, mock_supabase, mock_email_service):
        """Test resend verification for non-existent user"""
        mock_supabase.auth.admin.get_user_by_email.side_effect = Exception("User not found")
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/resend-verification", json={"email": "nonexistent@example.com"})
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "USER_NOT_FOUND"

    def test_resend_verification_already_verified(self, client, mock_supabase, mock_email_service):
        """Test resend verification for already verified user"""
        # Mock already verified user
        mock_user = Mock()
        mock_user.email_confirmed_at = "2023-01-01T00:00:00Z"
        
        mock_supabase.auth.admin.get_user_by_email.return_value = Mock(user=mock_user)
        
        with patch('app.api.routes.auth.get_supabase_client', return_value=mock_supabase):
            response = client.post("/api/auth/resend-verification", json={"email": "test@example.com"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "already_verified"


class TestEmailService:
    """Test email service"""

    @pytest.fixture
    def email_service(self):
        """Create email service instance"""
        from app.services.email_service import EmailService
        return EmailService()

    @pytest.fixture
    def verification_email_data(self):
        """Sample verification email data"""
        from app.models.schemas import VerificationEmailData, UserRole
        return VerificationEmailData(
            recipient_email="test@example.com",
            verification_link="https://vitachain.ma/verify?token=abc123",
            user_name="Test User",
            role=UserRole.FARMER
        )

    @pytest.mark.asyncio
    async def test_send_verification_email_success(self, email_service, verification_email_data):
        """Test successful verification email sending"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 201
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await email_service.send_verification_email(verification_email_data)
            
            assert result is True
            mock_client.post.assert_called_once()
            
            # Check the call arguments
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://api.brevo.com/v3/smtp/email"
            assert "api-key" in call_args[1]["headers"]
            
            email_data = call_args[1]["json"]
            assert email_data["to"][0]["email"] == "test@example.com"
            assert "Verify your VitaChain account" in email_data["subject"]

    @pytest.mark.asyncio
    async def test_send_verification_email_failure(self, email_service, verification_email_data):
        """Test verification email sending failure"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await email_service.send_verification_email(verification_email_data)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_send_verification_email_timeout(self, email_service, verification_email_data):
        """Test verification email sending timeout"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = Exception("Timeout")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await email_service.send_verification_email(verification_email_data)
            
            assert result is False

    def test_create_verification_template_farmer(self, email_service, verification_email_data):
        """Test email template creation for farmer role"""
        template = email_service._create_verification_template(verification_email_data)
        
        assert "Test User" in template
        assert "https://vitachain.ma/verify?token=abc123" in template
        assert "FARMER" in template
        assert "VitaChain" in template
        assert "Enregistrer vos dispositifs IoT KATARA" in template

    def test_create_verification_template_restaurant(self, email_service):
        """Test email template creation for restaurant role"""
        from app.models.schemas import VerificationEmailData, UserRole
        
        data = VerificationEmailData(
            recipient_email="restaurant@example.com",
            verification_link="https://vitachain.ma/verify",
            user_name="Restaurant Owner",
            role=UserRole.RESTAURANT
        )
        
        template = email_service._create_verification_template(data)
        
        assert "RESTAURANT" in template
        assert "Acheter des produits agricoles directement" in template

    def test_get_role_benefits(self, email_service):
        """Test role benefits extraction"""
        from app.models.schemas import UserRole
        
        farmer_benefits = email_service._get_role_benefits(UserRole.FARMER)
        assert "Enregistrer vos dispositifs IoT KATARA" in farmer_benefits
        
        restaurant_benefits = email_service._get_role_benefits(UserRole.RESTAURANT)
        assert "Acheter des produits agricoles directement" in restaurant_benefits
        
        citizen_benefits = email_service._get_role_benefits(UserRole.CITIZEN)
        assert "Découvrir des repas disponibles" in citizen_benefits


class TestValidationSchemas:
    """Test Pydantic validation schemas"""

    def test_user_registration_request_valid(self):
        """Test valid registration request"""
        data = {
            "email": "test@example.com",
            "role": UserRole.FARMER.value,
            "full_name": "Test User"
        }
        
        request = UserRegistrationRequest(**data)
        assert request.email == "test@example.com"
        assert request.role == UserRole.FARMER
        assert request.full_name == "Test User"

    def test_user_registration_request_invalid_email(self):
        """Test registration request with invalid email"""
        data = {
            "email": "invalid-email",
            "role": UserRole.FARMER.value,
            "full_name": "Test User"
        }
        
        with pytest.raises(ValueError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_invalid_role(self):
        """Test registration request with invalid role"""
        data = {
            "email": "test@example.com",
            "role": "INVALID_ROLE",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValueError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_empty_name(self):
        """Test registration request with empty name"""
        data = {
            "email": "test@example.com",
            "role": UserRole.FARMER.value,
            "full_name": "   "  # Only whitespace
        }
        
        with pytest.raises(ValueError):
            UserRegistrationRequest(**data)

    def test_user_registration_request_name_too_long(self):
        """Test registration request with name too long"""
        data = {
            "email": "test@example.com",
            "role": UserRole.FARMER.value,
            "full_name": "x" * 101  # 101 characters
        }
        
        with pytest.raises(ValueError):
            UserRegistrationRequest(**data)

    def test_user_registration_response(self):
        """Test registration response schema"""
        import uuid
        
        data = {
            "message": "Registration successful",
            "user_id": str(uuid.uuid4()),
            "email_sent": True
        }
        
        response = UserRegistrationResponse(**data)
        assert response.message == "Registration successful"
        assert response.email_sent is True
        assert isinstance(response.user_id, uuid.UUID)

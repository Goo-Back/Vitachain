"""
Unit tests for profile management functionality
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from datetime import datetime

from app.services.profile_service import ProfileService
from app.core.validation import PhoneValidator, ProfileValidator, InputSanitizer
from app.models.schemas import ProfileUpdateRequest, UserRole


class TestPhoneValidator:
    """Test phone number validation"""
    
    def test_valid_moroccan_phones(self):
        """Test valid Moroccan phone number formats"""
        valid_phones = [
            "+212612345678",
            "+212712345678",
            "0612345678",
            "0712345678"
        ]
        
        for phone in valid_phones:
            is_valid, error = PhoneValidator.validate_moroccan_phone(phone)
            assert is_valid, f"Phone {phone} should be valid"
            assert error is None, f"Phone {phone} should not have error"
    
    def test_invalid_moroccan_phones(self):
        """Test invalid Moroccan phone number formats"""
        invalid_phones = [
            "0512345678",  # Wrong prefix
            "0812345678",  # Wrong prefix
            "+212512345678",  # Wrong prefix
            "12345678",  # Too short
            "06123456789",  # Too long
            "abc123456",  # Contains letters
            "+21261234567",  # Missing digit
        ]
        
        for phone in invalid_phones:
            is_valid, error = PhoneValidator.validate_moroccan_phone(phone)
            assert not is_valid, f"Phone {phone} should be invalid"
            assert error is not None, f"Phone {phone} should have error message"
    
    def test_format_phone_number(self):
        """Test phone number formatting"""
        # Test local format to international
        formatted = PhoneValidator.format_phone_number("0612345678")
        assert formatted == "+212612345678"
        
        # Test international format stays same
        formatted = PhoneValidator.format_phone_number("+212612345678")
        assert formatted == "+212612345678"
        
        # Test empty phone
        formatted = PhoneValidator.format_phone_number("")
        assert formatted is None
        
        # Test invalid phone
        formatted = PhoneValidator.format_phone_number("invalid")
        assert formatted == "invalid"


class TestProfileValidator:
    """Test profile data validation"""
    
    def test_validate_full_name_valid(self):
        """Test valid full names"""
        valid_names = [
            "Ahmed Benali",
            "Fatima Zahra",
            "Mohammed",
            "Youssef Alami",
            "A. B.",
            "Jean-Claude",
            "O'Connor"
        ]
        
        for name in valid_names:
            is_valid, error = ProfileValidator.validate_full_name(name)
            assert is_valid, f"Name {name} should be valid"
            assert error is None, f"Name {name} should not have error"
    
    def test_validate_full_name_invalid(self):
        """Test invalid full names"""
        invalid_names = [
            "",  # Empty
            " ",  # Space only
            "A",  # Too short
            "a" * 101,  # Too long
            "123",  # Numbers only
            "John@Doe",  # Invalid character
            "<script>",  # HTML
        ]
        
        for name in invalid_names:
            is_valid, error = ProfileValidator.validate_full_name(name)
            assert not is_valid, f"Name {name} should be invalid"
            assert error is not None, f"Name {name} should have error message"
    
    def test_validate_farmer_data(self):
        """Test farmer-specific data validation"""
        # Valid farmer data
        valid_data = {
            "farm_location": "Casablanca",
            "farm_size_hectares": 15.5,
            "main_crops": ["tomatoes", "potatoes"]
        }
        is_valid, error = ProfileValidator.validate_role_data("FARMER", valid_data)
        assert is_valid
        assert error is None
        
        # Invalid farm size
        invalid_data = {
            "farm_size_hectares": -5.0
        }
        is_valid, error = ProfileValidator.validate_role_data("FARMER", invalid_data)
        assert not is_valid
        assert error is not None
        
        # Too many crops
        invalid_data = {
            "main_crops": [f"crop_{i}" for i in range(25)]
        }
        is_valid, error = ProfileValidator.validate_role_data("FARMER", invalid_data)
        assert not is_valid
        assert error is not None
    
    def test_validate_restaurant_data(self):
        """Test restaurant-specific data validation"""
        # Valid restaurant data
        valid_data = {
            "restaurant_name": "Restaurant Al Mounia",
            "address": "123 Rue Mohammed, Casablanca",
            "cuisine_type": "Moroccan"
        }
        is_valid, error = ProfileValidator.validate_role_data("RESTAURANT", valid_data)
        assert is_valid
        assert error is None
        
        # Invalid restaurant name
        invalid_data = {
            "restaurant_name": "A"  # Too short
        }
        is_valid, error = ProfileValidator.validate_role_data("RESTAURANT", invalid_data)
        assert not is_valid
        assert error is not None
    
    def test_validate_citizen_data(self):
        """Test citizen-specific data validation"""
        # Valid citizen data
        valid_data = {
            "preferred_pickup_locations": ["Casablanca", "Rabat"]
        }
        is_valid, error = ProfileValidator.validate_role_data("CITIZEN", valid_data)
        assert is_valid
        assert error is None
        
        # Too many locations
        invalid_data = {
            "preferred_pickup_locations": [f"location_{i}" for i in range(15)]
        }
        is_valid, error = ProfileValidator.validate_role_data("CITIZEN", invalid_data)
        assert not is_valid
        assert error is not None


class TestInputSanitizer:
    """Test input sanitization"""
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        # Test HTML removal
        dirty = "<script>alert('xss')</script>Hello"
        clean = InputSanitizer.sanitize_string(dirty)
        assert "&lt;script&gt;" in clean
        assert "Hello" in clean
        
        # Test quotes
        dirty = "John's \"test\""
        clean = InputSanitizer.sanitize_string(dirty)
        assert "&#x27;" in clean
        assert "&quot;" in clean
        
        # Test non-string input
        clean = InputSanitizer.sanitize_string(123)
        assert clean == "123"
    
    def test_sanitize_profile_data(self):
        """Test profile data sanitization"""
        dirty_data = {
            "full_name": "<script>alert('xss')</script>John",
            "phone": "0612345678",
            "role_data": {
                "farm_location": "Casablanca <test>",
                "main_crops": ["tomato", "<script>alert('xss')</script>potato"]
            }
        }
        
        clean_data = InputSanitizer.sanitize_profile_data(dirty_data)
        
        assert "&lt;script&gt;" in clean_data["full_name"]
        assert clean_data["phone"] == "0612345678"
        assert "&lt;test&gt;" in clean_data["role_data"]["farm_location"]
        assert "&lt;script&gt;" in clean_data["role_data"]["main_crops"][1]


class TestProfileService:
    """Test profile service business logic"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client"""
        mock_client = Mock()
        return mock_client
    
    @pytest.fixture
    def profile_service(self, mock_supabase):
        """Create profile service with mock client"""
        return ProfileService(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, profile_service, mock_supabase):
        """Test successful profile retrieval"""
        # Mock profile data
        mock_profile_data = {
            "id": "user-123",
            "full_name": "Ahmed Benali",
            "phone": "+212612345678",
            "role": "FARMER",
            "created_at": "2026-05-01T10:00:00Z",
            "updated_at": "2026-05-01T10:00:00Z"
        }
        
        # Mock Supabase responses
        mock_result = Mock()
        mock_result.data = mock_profile_data
        mock_result.error = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value = mock_result
        mock_supabase.auth.admin.get_user.return_value.user.email = "ahmed@example.com"
        
        # Test profile retrieval
        result = await profile_service.get_profile("user-123")
        
        assert result["id"] == "user-123"
        assert result["full_name"] == "Ahmed Benali"
        assert result["email"] == "ahmed@example.com"
        assert result["role"] == "FARMER"
    
    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, profile_service, mock_supabase):
        """Test profile not found error"""
        # Mock empty response
        mock_result = Mock()
        mock_result.data = None
        mock_result.error = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value = mock_result
        
        # Test should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await profile_service.get_profile("user-123")
        
        assert exc_info.value.status_code == 404
        assert "PROFILE_NOT_FOUND" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, profile_service, mock_supabase):
        """Test successful profile update"""
        # Mock current profile
        mock_current_profile = {
            "id": "user-123",
            "full_name": "Ahmed Benali",
            "phone": "+212612345678",
            "role": "FARMER",
            "created_at": "2026-05-01T10:00:00Z",
            "updated_at": "2026-05-01T10:00:00Z"
        }
        
        # Mock update response
        mock_updated_profile = {
            "id": "user-123",
            "full_name": "Ahmed Benali Updated",
            "phone": "+212612345678",
            "role": "FARMER",
            "created_at": "2026-05-01T10:00:00Z",
            "updated_at": "2026-05-02T14:30:00Z"
        }
        
        # Mock Supabase responses
        mock_select_result = Mock()
        mock_select_result.data = mock_current_profile
        mock_select_result.error = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value = mock_select_result
        
        mock_update_result = Mock()
        mock_update_result.data = [mock_updated_profile]
        mock_update_result.error = None
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Mock get_profile call
        profile_service.get_profile = AsyncMock(return_value=mock_updated_profile)
        
        # Test profile update
        update_data = {
            "full_name": "Ahmed Benali Updated"
        }
        
        result = await profile_service.update_profile("user-123", update_data)
        
        assert result["message"] == "Profile updated successfully"
        assert result["profile"]["full_name"] == "Ahmed Benali Updated"
    
    @pytest.mark.asyncio
    async def test_update_profile_invalid_phone(self, profile_service, mock_supabase):
        """Test profile update with invalid phone number"""
        # Mock current profile
        mock_current_profile = {
            "id": "user-123",
            "full_name": "Ahmed Benali",
            "role": "FARMER"
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.data = mock_current_profile
        
        # Test with invalid phone
        update_data = {
            "phone": "invalid-phone"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await profile_service.update_profile("user-123", update_data)
        
        assert exc_info.value.status_code == 422
        assert "VALIDATION_ERROR" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_validate_profile_access(self, profile_service):
        """Test profile access validation"""
        # Same user should have access
        assert await profile_service.validate_profile_access("user-123", "user-123") is True
        
        # Different user should not have access
        assert await profile_service.validate_profile_access("user-123", "user-456") is False
    
    @pytest.mark.asyncio
    async def test_get_profile_summary(self, profile_service):
        """Test profile summary generation"""
        # Mock profile data
        mock_profile = {
            "id": "user-123",
            "full_name": "Ahmed Benali",
            "role": "FARMER",
            "phone": "+212612345678",
            "updated_at": "2026-05-02T14:30:00Z",
            "role_data": {
                "farm_location": "Casablanca"
            }
        }
        
        profile_service.get_profile = AsyncMock(return_value=mock_profile)
        
        result = await profile_service.get_profile_summary("user-123")
        
        assert result["id"] == "user-123"
        assert result["full_name"] == "Ahmed Benali"
        assert result["role"] == "FARMER"
        assert result["completed_profile"] is True
    
    def test_is_profile_complete(self, profile_service):
        """Test profile completion check"""
        # Complete farmer profile
        complete_profile = {
            "full_name": "Ahmed Benali",
            "phone": "+212612345678",
            "role": "FARMER",
            "role_data": {
                "farm_location": "Casablanca"
            }
        }
        assert profile_service._is_profile_complete(complete_profile) is True
        
        # Incomplete farmer profile (no phone)
        incomplete_profile = {
            "full_name": "Ahmed Benali",
            "role": "FARMER",
            "role_data": {
                "farm_location": "Casablanca"
            }
        }
        assert profile_service._is_profile_complete(incomplete_profile) is False
        
        # Complete citizen profile
        complete_citizen = {
            "full_name": "Fatima Zahra",
            "phone": "+212612345678",
            "role": "CITIZEN"
        }
        assert profile_service._is_profile_complete(complete_citizen) is True


if __name__ == "__main__":
    pytest.main([__file__])

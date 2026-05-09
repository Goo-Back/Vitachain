# Security Tests for VitaChain
# Comprehensive security testing suite

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import hashlib
import secrets

from app.core.security import APIKeyManager, SecurityValidator, SecurityHeaders
from app.core.security_monitoring import SecurityMonitor
from app.services.api_key_rotation_service import APIKeyRotationService
from app.core.middleware.security import SecurityMiddleware


class TestAPIKeyManager:
    """Test API key management functionality"""
    
    def setup_method(self):
        self.api_key_manager = APIKeyManager()
    
    def test_generate_api_key(self):
        """Test API key generation"""
        api_key = self.api_key_manager.generate_api_key()
        
        assert api_key.startswith("vitachain-")
        assert len(api_key) > 40
        assert "-" in api_key
        
        # Test uniqueness
        api_key2 = self.api_key_manager.generate_api_key()
        assert api_key != api_key2
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        api_key = "vitachain-test-key-12345"
        hashed = self.api_key_manager.hash_api_key(api_key)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA256 hex length
        
        # Test consistency
        hashed2 = self.api_key_manager.hash_api_key(api_key)
        assert hashed == hashed2
    
    def test_validate_api_key(self):
        """Test API key validation"""
        api_key = "vitachain-test-key-12345"
        hashed = self.api_key_manager.hash_api_key(api_key)
        
        # Valid key
        assert self.api_key_manager.validate_api_key(api_key, hashed) is True
        
        # Invalid key
        assert self.api_key_manager.validate_api_key("wrong-key", hashed) is False
    
    def test_should_rotate_key(self):
        """Test key rotation timing"""
        old_date = datetime.utcnow() - timedelta(days=100)
        recent_date = datetime.utcnow() - timedelta(days=30)
        
        # Should rotate old key
        assert self.api_key_manager.should_rotate_key(old_date) is True
        
        # Should not rotate recent key
        assert self.api_key_manager.should_rotate_key(recent_date) is False
    
    def test_extract_device_id_from_key(self):
        """Test device ID extraction from API key"""
        api_key = "vitachain-device123-abcde"
        device_id = self.api_key_manager.extract_device_id_from_key(api_key)
        
        assert device_id == "device123"
        
        # Test invalid format
        assert self.api_key_manager.extract_device_id_from_key("invalid-key") is None


class TestSecurityValidator:
    """Test security validation functionality"""
    
    def setup_method(self):
        self.validator = SecurityValidator()
        self.api_key_manager = APIKeyManager()
    
    def test_validate_api_request_valid(self):
        """Test valid API request validation"""
        api_key = "vitachain-device123-abcde"
        device_id = "device123"
        
        result = self.validator.validate_api_request(api_key, device_id, self.api_key_manager)
        assert result is True
    
    def test_validate_api_request_invalid_format(self):
        """Test invalid API request format"""
        api_key = "invalid-format"
        device_id = "device123"
        
        result = self.validator.validate_api_request(api_key, device_id, self.api_key_manager)
        assert result is False
    
    def test_validate_api_request_missing_data(self):
        """Test API request with missing data"""
        result = self.validator.validate_api_request("", "", self.api_key_manager)
        assert result is False
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        data = {
            "name": "<script>alert('xss')</script>",
            "description": "Normal text",
            "number": 42
        }
        
        sanitized = self.validator.sanitize_input(data)
        
        assert sanitized["name"] == "&lt;script&gt;alert('xss')&lt;/script&gt;"
        assert sanitized["description"] == "Normal text"
        assert sanitized["number"] == 42
    
    def test_validate_telemetry_data_valid(self):
        """Test valid telemetry data validation"""
        data = {
            "device_id": "device123",
            "temperature": 25.5,
            "humidity": 60.0,
            "ndvi": 0.75
        }
        
        result = self.validator.validate_telemetry_data(data)
        assert result is True
    
    def test_validate_telemetry_data_invalid_temperature(self):
        """Test telemetry data with invalid temperature"""
        data = {
            "device_id": "device123",
            "temperature": 100.0,  # Out of range
            "humidity": 60.0
        }
        
        result = self.validator.validate_telemetry_data(data)
        assert result is False
    
    def test_validate_telemetry_data_missing_fields(self):
        """Test telemetry data with missing required fields"""
        data = {
            "temperature": 25.5,
            "humidity": 60.0
            # Missing device_id
        }
        
        result = self.validator.validate_telemetry_data(data)
        assert result is False


class TestSecurityHeaders:
    """Test security headers functionality"""
    
    def setup_method(self):
        self.headers = SecurityHeaders()
    
    def test_get_security_headers(self):
        """Test security headers generation"""
        headers = self.headers.get_security_headers()
        
        assert isinstance(headers, dict)
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers
        
        # Check specific values
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"


class TestSecurityMonitor:
    """Test security monitoring functionality"""
    
    def setup_method(self):
        self.monitor = SecurityMonitor()
    
    def test_log_failed_authentication(self):
        """Test failed authentication logging"""
        ip = "192.168.1.100"
        user_agent = "TestBot/1.0"
        
        # Log failed attempts
        for i in range(6):  # Exceed threshold
            self.monitor.log_failed_authentication(ip, user_agent, "/auth/login")
        
        # Check if suspicious activity was detected
        assert len(self.monitor.failed_auth_attempts) > 0
    
    def test_log_api_abuse(self):
        """Test API abuse logging"""
        ip = "192.168.1.101"
        endpoint = "/api/telemetry"
        
        # Log rate violations
        for i in range(105):  # Exceed threshold
            self.monitor.log_api_abuse(ip, endpoint, rate_violation=True)
        
        # Check if violations were recorded
        assert len(self.monitor.api_rate_violations) > 0
    
    def test_log_suspicious_request(self):
        """Test suspicious request logging"""
        ip = "192.168.1.102"
        user_agent = "SuspiciousBot/1.0"
        request_path = "/admin/../../etc/passwd"
        pattern = "path_traversal"
        
        self.monitor.log_suspicious_request(ip, user_agent, request_path, pattern)
        
        # Check if pattern was recorded
        assert pattern in self.monitor.suspicious_patterns
        assert self.monitor.suspicious_patterns[pattern] > 0
    
    def test_get_security_metrics(self):
        """Test security metrics retrieval"""
        # Add some events
        self.monitor.log_security_event("test_event", "low", test_data="test")
        
        metrics = self.monitor.get_security_metrics()
        
        assert isinstance(metrics, dict)
        assert "failed_auth_attempts_24h" in metrics
        assert "rate_violations_24h" in metrics
        assert "suspicious_patterns_24h" in metrics
        assert "currently_blocked_ips" in metrics
    
    def test_get_ip_reputation(self):
        """Test IP reputation calculation"""
        ip = "192.168.1.103"
        
        # Add some failed attempts
        for i in range(3):
            self.monitor.log_failed_authentication(ip, "TestBot/1.0")
        
        reputation = self.monitor.get_ip_reputation(ip)
        
        assert isinstance(reputation, dict)
        assert "ip" in reputation
        assert "reputation_score" in reputation
        assert "reputation" in reputation
        assert "failed_auth_attempts" in reputation
        assert "rate_violations" in reputation
        assert "is_blocked" in reputation
    
    def test_block_ip_temporarily(self):
        """Test temporary IP blocking"""
        ip = "192.168.1.104"
        
        self.monitor.block_ip_temporarily(ip, hours=1)
        
        assert self.monitor.is_ip_blocked(ip) is True


class TestAPIKeyRotationService:
    """Test API key rotation service"""
    
    def setup_method(self):
        self.mock_supabase = Mock()
        self.service = APIKeyRotationService(self.mock_supabase, rotation_enabled=True)
    
    @pytest.mark.asyncio
    async def test_force_rotate_key(self):
        """Test manual key rotation"""
        device_id = "device123"
        
        # Mock current key
        current_key = {
            "id": "key123",
            "device_id": device_id,
            "active": True,
            "created_at": (datetime.utcnow() - timedelta(days=100)).isoformat()
        }
        
        # Mock Supabase responses
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [current_key]
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "key123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "new_key123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "audit123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "notification123"}]
        
        # Test rotation
        result = await self.service.force_rotate_key(device_id, "test_rotation")
        
        assert result is True
        
        # Verify Supabase calls
        assert self.mock_supabase.table.call_count >= 4  # Select, update, insert, audit log
    
    @pytest.mark.asyncio
    async def test_get_rotation_status(self):
        """Test rotation status retrieval"""
        # Mock Supabase responses
        self.mock_supabase.table.return_value.select.return_value.lt.return_value.eq.return_value.execute.return_value.data = [
            {"id": "key1"}, {"id": "key2"}
        ]
        
        status = await self.service.get_rotation_status()
        
        assert isinstance(status, dict)
        assert "service_running" in status
        assert "rotation_enabled" in status
        assert "upcoming_rotations_30d" in status
        assert "expired_keys_pending" in status
    
    @pytest.mark.asyncio
    async def test_get_device_key_history(self):
        """Test device key history retrieval"""
        device_id = "device123"
        
        # Mock Supabase response
        mock_keys = [
            {"id": "key1", "device_id": device_id, "created_at": "2026-01-01T00:00:00Z"},
            {"id": "key2", "device_id": device_id, "created_at": "2026-02-01T00:00:00Z"}
        ]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_keys
        
        history = await self.service.get_device_key_history(device_id)
        
        assert isinstance(history, list)
        assert len(history) == 2
        assert history[0]["device_id"] == device_id


class TestSecurityMiddleware:
    """Test security middleware functionality"""
    
    def setup_method(self):
        self.mock_app = Mock()
        self.middleware = SecurityMiddleware(self.mock_app, api_key_required=False)
    
    def test_get_client_ip(self):
        """Test client IP extraction"""
        # Mock request with forwarded header
        mock_request = Mock()
        mock_request.headers = {"x-forwarded-for": "192.168.1.100"}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.100"
        
        # Mock request without forwarded header
        mock_request.headers = {}
        ip = self.middleware._get_client_ip(mock_request)
        assert ip == "127.0.0.1"
    
    def test_generate_request_id(self):
        """Test request ID generation"""
        request_id1 = self.middleware._generate_request_id()
        request_id2 = self.middleware._generate_request_id()
        
        assert isinstance(request_id1, str)
        assert len(request_id1) == 16
        assert request_id1 != request_id2
    
    @pytest.mark.asyncio
    async def test_check_suspicious_patterns(self):
        """Test suspicious pattern detection"""
        # Mock request with path traversal
        mock_request = Mock()
        mock_request.url.path = "/admin/../../etc/passwd"
        mock_request.query_params = Mock()
        mock_request.query_params.__str__ = Mock(return_value="normal=query")
        
        ip = "192.168.1.100"
        user_agent = "TestBot/1.0"
        
        # This should raise an exception due to suspicious pattern
        with pytest.raises(Exception):  # HTTPException will be raised
            self.middleware._check_suspicious_patterns(mock_request, ip, user_agent)


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def setup_method(self):
        self.api_key_manager = APIKeyManager()
        self.security_validator = SecurityValidator()
        self.security_monitor = SecurityMonitor()
    
    def test_end_to_end_api_key_workflow(self):
        """Test complete API key workflow"""
        # Generate key
        api_key = self.api_key_manager.generate_api_key()
        device_id = self.api_key_manager.extract_device_id_from_key(api_key)
        
        # Validate request
        is_valid = self.security_validator.validate_api_request(api_key, device_id, self.api_key_manager)
        assert is_valid is True
        
        # Test with wrong device ID
        is_invalid = self.security_validator.validate_api_request(api_key, "wrong_device", self.api_key_manager)
        assert is_invalid is False
    
    def test_security_monitoring_integration(self):
        """Test security monitoring integration"""
        ip = "192.168.1.200"
        user_agent = "MaliciousBot/1.0"
        
        # Simulate attack sequence
        for i in range(6):
            self.security_monitor.log_failed_authentication(ip, user_agent)
        
        # Check IP reputation
        reputation = self.security_monitor.get_ip_reputation(ip)
        assert reputation["reputation_score"] < 100
        assert reputation["failed_auth_attempts"] >= 5
        
        # Check if IP was blocked
        if self.security_monitor.is_ip_blocked(ip):
            assert reputation["is_blocked"] is True


# Performance tests
class TestSecurityPerformance:
    """Performance tests for security components"""
    
    def test_api_key_generation_performance(self):
        """Test API key generation performance"""
        api_key_manager = APIKeyManager()
        
        start_time = time.time()
        
        # Generate 1000 keys
        for _ in range(1000):
            api_key_manager.generate_api_key()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        assert duration < 1.0
        assert len(api_key_manager.generate_api_key()) > 40
    
    def test_security_validation_performance(self):
        """Test security validation performance"""
        validator = SecurityValidator()
        api_key_manager = APIKeyManager()
        
        api_key = api_key_manager.generate_api_key()
        device_id = api_key_manager.extract_device_id_from_key(api_key)
        
        start_time = time.time()
        
        # Validate 1000 requests
        for _ in range(1000):
            validator.validate_api_request(api_key, device_id, api_key_manager)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 0.5 seconds)
        assert duration < 0.5


# Test fixtures and utilities
@pytest.fixture
def sample_api_key():
    """Generate sample API key for testing"""
    api_key_manager = APIKeyManager()
    return api_key_manager.generate_api_key()


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    client = Mock()
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test"}]
    client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test"}]
    return client

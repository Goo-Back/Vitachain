# Security Monitoring Tests for VitaChain
# Test suspicious login detection functionality

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.core.security_monitoring import SecurityMonitor
from app.core.geo_ip_service import GeoIPService
from app.models.security_schemas import LoginAnalysisRequest, SecurityEventType

class TestSecurityMonitoring:
    """Test security monitoring and suspicious login detection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.security_monitor = SecurityMonitor()
        self.geo_service = GeoIPService()
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_success_normal(self):
        """Test normal successful login analysis"""
        request = LoginAnalysisRequest(
            user_id="test_user_123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            success=True,
            location_data={
                "country_code": "US",
                "city": "New York",
                "isp": "Comcast Cable"
            }
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success,
            location_data=request.location_data
        )
        
        assert result["risk_score"] == 0
        assert result["anomalies"] == []
        assert result["recommendations"] == []
        assert result["should_block"] == False
        assert result["should_notify"] == False
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_failed_multiple_attempts(self):
        """Test failed login attempts from same IP"""
        # Simulate multiple failed attempts
        ip = "192.168.1.200"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Log 5 failed attempts (threshold)
        for i in range(5):
            self.security_monitor.log_failed_authentication(
                ip=ip,
                user_agent=user_agent,
                endpoint="/api/auth/login",
                error_type="invalid_credentials"
            )
        
        request = LoginAnalysisRequest(
            user_id="test_user_456",
            ip_address=ip,
            user_agent=user_agent,
            success=False
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success
        )
        
        assert result["risk_score"] >= 30  # Should detect multiple failed attempts
        assert len(result["anomalies"]) > 0
        assert "multiple_failed_auth" in [anomaly.get("type") for anomaly in result["anomalies"]]
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_new_country(self):
        """Test login from unusual geographic location"""
        # Set up user with typical US location
        self.security_monitor.update_user_login_pattern(
            user_id="test_user_geo",
            ip="192.168.1.100",
            user_agent="Mozilla/5.0",
            location_data={"country_code": "US", "city": "New York"},
            success=True
        )
        
        # Test login from different country
        request = LoginAnalysisRequest(
            user_id="test_user_geo",
            ip_address="192.168.1.150",
            user_agent="Mozilla/5.0",
            success=True,
            location_data={
                "country_code": "CN",  # China - different from US
                "city": "Beijing"
            }
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success,
            location_data=request.location_data
        )
        
        assert result["risk_score"] >= 30  # Should detect new country
        assert any(anomaly.get("type") == "new_country" for anomaly in result["anomalies"])
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_new_device(self):
        """Test login from new device"""
        # Set up user with typical device
        self.security_monitor.update_user_login_pattern(
            user_id="test_user_device",
            ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            success=True
        )
        
        # Test login from different device
        request = LoginAnalysisRequest(
            user_id="test_user_device",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
            success=True
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success
        )
        
        assert result["risk_score"] >= 20  # Should detect new device
        assert any(anomaly.get("type") == "new_device" for anomaly in result["anomalies"])
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_credential_stuffing(self):
        """Test credential stuffing detection"""
        ip = "192.168.1.250"
        
        # Simulate logins for many different accounts from same IP
        for i in range(10):
            self.security_monitor.log_security_event(
                event_type="login_attempt",
                severity="info",
                user_id=f"test_user_{i}",
                ip_address=ip,
                metadata={"success": True}
            )
        
        request = LoginAnalysisRequest(
            user_id="test_user_new",
            ip_address=ip,
            user_agent="Mozilla/5.0",
            success=False
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success
        )
        
        assert result["risk_score"] >= 40  # Should detect credential stuffing
        assert result["should_block"] == True
        assert any(anomaly.get("type") == "credential_stuffing" for anomaly in result["anomalies"])
    
    @pytest.mark.asyncio
    async def test_analyze_login_attempt_high_velocity(self):
        """Test high login velocity detection"""
        user_id = "test_user_velocity"
        ip = "192.168.1.175"
        
        # Simulate rapid logins
        base_time = datetime.utcnow()
        for i in range(12):  # 12 logins in short time
            self.security_monitor.update_user_login_pattern(
                user_id=user_id,
                ip=ip,
                user_agent="Mozilla/5.0",
                success=True
            )
        
        request = LoginAnalysisRequest(
            user_id=user_id,
            ip_address=ip,
            user_agent="Mozilla/5.0",
            success=True
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success
        )
        
        assert result["risk_score"] >= 25  # Should detect high velocity
        assert any(anomaly.get("type") == "high_velocity" for anomaly in result["anomalies"])
    
    def test_device_fingerprinting(self):
        """Test device fingerprint generation"""
        # Test Chrome on Windows
        ua_chrome_windows = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        fp_chrome_windows = self.security_monitor._generate_device_fingerprint(ua_chrome_windows)
        assert fp_chrome_windows is not None
        assert len(fp_chrome_windows) == 16  # MD5 hash length
        
        # Test Safari on iPhone
        ua_safari_iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
        fp_safari_iphone = self.security_monitor._generate_device_fingerprint(ua_safari_iphone)
        assert fp_safari_iphone is not None
        assert len(fp_safari_iphone) == 16
        
        # Test unknown user agent
        fp_unknown = self.security_monitor._generate_device_fingerprint("")
        assert fp_unknown == "unknown"
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        ip = "192.168.1.999"
        
        # Initially not blocked
        assert not self.security_monitor.is_ip_blocked(ip)
        
        # Block IP
        self.security_monitor.block_ip_temporarily(ip, hours=1)
        
        # Should now be blocked
        assert self.security_monitor.is_ip_blocked(ip)
        
        # Test with blocked IP
        request = LoginAnalysisRequest(
            user_id="test_user",
            ip_address=ip,
            user_agent="Mozilla/5.0",
            success=True
        )
        
        result = self.security_monitor.analyze_login_attempt(
            user_id=request.user_id,
            ip=request.ip_address,
            user_agent=request.user_agent,
            success=request.success
        )
        
        assert result["risk_score"] == 100  # Maximum risk for blocked IP
        assert result["should_block"] == True
        assert "blocked_ip_attempt" in [anomaly.get("type") for anomaly in result["anomalies"]]
    
    def test_geographic_anomaly_detection(self):
        """Test geographic anomaly detection"""
        user_id = "test_user_geo"
        
        # Set up typical US locations
        self.security_monitor.user_login_patterns[user_id] = {
            "countries": ["US", "CA"],
            "cities": ["New York", "Toronto"],
            "last_location": {"country_code": "US", "city": "New York"}
        }
        
        # Test new country anomaly
        location_data = {"country_code": "FR", "city": "Paris"}
        anomaly = self.security_monitor._detect_geographic_anomaly(user_id, "192.168.1.100", location_data)
        
        assert anomaly is not None
        assert anomaly["type"] == "new_country"
        assert anomaly["country"] == "FR"
        
        # Test same country (no anomaly)
        location_data_same = {"country_code": "US", "city": "Los Angeles"}
        anomaly_none = self.security_monitor._detect_geographic_anomaly(user_id, "192.168.1.100", location_data_same)
        
        assert anomaly_none is None
    
    def test_ip_reputation_calculation(self):
        """Test IP reputation scoring"""
        ip = "192.168.1.100"
        
        # Good IP reputation
        reputation_good = self.security_monitor.get_ip_reputation(ip)
        assert reputation_good["reputation_score"] >= 70
        assert reputation_good["reputation"] == "good"
        
        # Add failed attempts to lower reputation
        for i in range(5):
            self.security_monitor.log_failed_authentication(
                ip=ip,
                user_agent="Mozilla/5.0",
                error_type="invalid_credentials"
            )
        
        reputation_poor = self.security_monitor.get_ip_reputation(ip)
        assert reputation_poor["reputation_score"] < 70
        assert reputation_poor["reputation"] in ["suspicious", "poor"]
        assert reputation_poor["failed_attempts"] >= 5

class TestGeoIPService:
    """Test IP geolocation service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.geo_service = GeoIPService()
    
    @pytest.mark.asyncio
    async def test_get_ip_location_success(self):
        """Test successful IP geolocation lookup"""
        ip = "8.8.8.8"
        
        # Mock successful API response
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "countryCode": "US",
                "countryName": "United States",
                "city": "Mountain View",
                "lat": 37.4056,
                "lon": -122.0775,
                "isp": "Google LLC"
            }
            mock_get.return_value = mock_response
            
            result = await self.geo_service.get_ip_location(ip)
            
            assert result is not None
            assert result["ip_address"] == ip
            assert result["country_code"] == "US"
            assert result["city"] == "Mountain View"
            assert result["country_name"] == "United States"
    
    @pytest.mark.asyncio
    async def test_get_ip_location_cache_hit(self):
        """Test IP geolocation cache functionality"""
        ip = "8.8.8.8"
        
        # First call
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "countryCode": "US",
                "countryName": "United States",
                "city": "Mountain View"
            }
            mock_get.return_value = mock_response
            
            # First call should hit API
            result1 = await self.geo_service.get_ip_location(ip)
            assert result1 is not None
            
            # Second call should hit cache
            result2 = await self.geo_service.get_ip_location(ip)
            assert result2 is not None
            assert result2["country_code"] == "US"
            
            # Verify mock was called only once
            mock_get.assert_called_once()
    
    def test_high_risk_country_detection(self):
        """Test high-risk country detection"""
        geo_service = GeoIPService()
        
        # Test high-risk countries
        assert geo_service.is_high_risk_country("CN") == True
        assert geo_service.is_high_risk_country("RU") == True
        assert geo_service.is_high_risk_country("IR") == True
        
        # Test safe countries
        assert geo_service.is_high_risk_country("US") == False
        assert geo_service.is_high_risk_country("CA") == False
        assert geo_service.is_high_risk_country("FR") == False
    
    def test_location_risk_scoring(self):
        """Test location-based risk scoring"""
        geo_service = GeoIPService()
        
        # High risk location
        high_risk_location = {
            "country_code": "CN",
            "is_proxy": False,
            "isp": "China Telecom"
        }
        high_risk_score = geo_service.get_risk_score_for_location(high_risk_location)
        assert high_risk_score >= 30  # Base score for high-risk country
        
        # Proxy/VPN location
        proxy_location = {
            "country_code": "US",
            "is_proxy": True,
            "isp": "VPN Provider"
        }
        proxy_score = geo_service.get_risk_score_for_location(proxy_location)
        assert proxy_score >= 20  # Additional score for proxy
        
        # Missing location data
        missing_location = {}
        missing_score = geo_service.get_risk_score_for_location(missing_location)
        assert missing_score >= 10  # Score for missing data
        
        # Safe location
        safe_location = {
            "country_code": "CA",
            "is_proxy": False,
            "isp": "Rogers Communications"
        }
        safe_score = geo_service.get_risk_score_for_location(safe_location)
        assert safe_score == 0  # No risk factors

if __name__ == "__main__":
    pytest.main([__file__])

# Security API Tests for VitaChain
# Test security monitoring endpoints

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.core.security_monitoring import security_monitor
from app.core.geo_ip_service import geo_ip_service
from app.models.security_schemas import SecurityEventType, SecuritySeverity

class TestSecurityAPI:
    """Test security API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.security_monitor = security_monitor
    
    @pytest.mark.asyncio
    async def test_analyze_login_endpoint_success(self):
        """Test login analysis endpoint with normal data"""
        # Mock dependencies
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "test_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            
            # Test request data
            request_data = {
                "user_id": "test_user_123",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "success": True,
                "location_data": {
                    "country_code": "US",
                    "city": "New York"
                }
            }
            
            response = self.client.post("/api/security/analyze-login", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test_user_123"
            assert data["ip_address"] == "192.168.1.100"
            assert data["success"] == True
            assert data["risk_score"] == 0
            assert data["anomalies"] == []
            assert data["should_block"] == False
            assert data["should_notify"] == False
    
    @pytest.mark.asyncio
    async def test_analyze_login_endpoint_suspicious(self):
        """Test login analysis endpoint with suspicious data"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase, \
             patch('app.api.routes.security.geo_ip_service') as mock_geo:
            
            mock_user.return_value = {"id": "test_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_geo.get_ip_location.return_value = {
                "country_code": "CN",  # High-risk country
                "city": "Beijing"
            }
            
            # Test request data with suspicious patterns
            request_data = {
                "user_id": "test_user_456",
                "ip_address": "192.168.1.200",
                "user_agent": "Mozilla/5.0",
                "success": True,
                "location_data": {
                    "country_code": "CN",
                    "city": "Beijing"
                }
            }
            
            response = self.client.post("/api/security/analyze-login", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["risk_score"] >= 30  # Should detect high-risk country
            assert len(data["anomalies"]) > 0
            assert data["should_notify"] == True
    
    @pytest.mark.asyncio
    async def test_security_metrics_endpoint_admin(self):
        """Test security metrics endpoint for admin"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value.data = []
            
            response = self.client.get("/api/security/dashboard/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert "failed_auth_attempts_24h" in data
            assert "currently_blocked_ips" in data
            assert "recent_alerts" in data
    
    @pytest.mark.asyncio
    async def test_security_metrics_endpoint_unauthorized(self):
        """Test security metrics endpoint without admin role"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "regular_user", "role": "USER"}  # Not admin
            
            response = self.client.get("/api/security/dashboard/metrics")
            
            assert response.status_code == 403
            data = response.json()
            assert data["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @pytest.mark.asyncio
    async def test_security_alerts_endpoint(self):
        """Test security alerts endpoint"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value.data = [
                {
                    "id": "alert_1",
                    "alert_type": "suspicious_login",
                    "severity": "high",
                    "title": "Suspicious Login Detected",
                    "description": "Login from unusual location",
                    "user_id": "test_user",
                    "ip_address": "192.168.1.100",
                    "requires_action": True,
                    "is_read": False,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            response = self.client.get("/api/security/alerts")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["alert_type"] == "suspicious_login"
            assert data[0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_block_ip_endpoint(self):
        """Test IP blocking endpoint"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = {
                "id": "ip_rep_1",
                "ip_address": "192.168.1.250",
                "is_blocked": True,
                "blocked_until": datetime.utcnow().isoformat(),
                "block_reason": "Suspicious activity"
            }
            
            request_data = {
                "duration_hours": 2,
                "reason": "Test blocking"
            }
            
            response = self.client.post(f"/api/security/ip/192.168.1.250/block", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["ip_address"] == "192.168.1.250"
            assert data["blocked"] == True
            assert data["reason"] == "Test blocking"
    
    @pytest.mark.asyncio
    async def test_block_ip_endpoint_unauthorized(self):
        """Test IP blocking endpoint without admin role"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "regular_user", "role": "USER"}  # Not admin
            
            request_data = {
                "duration_hours": 1,
                "reason": "Test blocking"
            }
            
            response = self.client.post(f"/api/security/ip/192.168.1.250/block", json=request_data)
            
            assert response.status_code == 403
            data = response.json()
            assert data["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @pytest.mark.asyncio
    async def test_ip_reputation_endpoint(self):
        """Test IP reputation endpoint"""
        with patch('app.api.routes.security.get_current_user') as mock_user, \
             patch('app.api.routes.security.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
                {
                    "id": "ip_rep_1",
                    "ip_address": "192.168.1.100",
                    "reputation_score": 25,
                    "failed_attempts": 8,
                    "successful_logins": 2,
                    "is_blocked": False,
                    "last_activity": datetime.utcnow().isoformat()
                }
            ]
            
            response = self.client.get(f"/api/security/ip/192.168.1.100/reputation")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ip_address"] == "192.168.1.100"
            assert data["reputation_score"] == 25
            assert data["reputation"] == "suspicious"
            assert data["failed_attempts"] == 8

class TestAdminDashboardAPI:
    """Test admin dashboard endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    @pytest.mark.asyncio
    async def test_security_overview_endpoint(self):
        """Test security overview endpoint"""
        with patch('app.api.routes.admin_dashboard.get_current_user') as mock_user, \
             patch('app.api.routes.admin_dashboard.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            
            # Mock security monitor metrics
            with patch('app.core.security_monitoring.security_monitor.get_security_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "failed_auth_attempts_24h": 15,
                    "rate_violations_24h": 3,
                    "suspicious_patterns_24h": 7,
                    "currently_blocked_ips": 2,
                    "active_failed_auth_sessions": 5,
                    "active_rate_violations": 1,
                    "top_suspicious_patterns": {"credential_stuffing": 3, "new_device": 2}
                }
                
                response = self.client.get("/api/admin/dashboard/security/overview")
                
                assert response.status_code == 200
                data = response.json()
                assert data["failed_auth_attempts_24h"] == 15
                assert data["currently_blocked_ips"] == 2
                assert data["top_suspicious_patterns"]["credential_stuffing"] == 3
    
    @pytest.mark.asyncio
    async def test_security_overview_endpoint_unauthorized(self):
        """Test security overview endpoint without admin role"""
        with patch('app.api.routes.admin_dashboard.get_current_user') as mock_user, \
             patch('app.api.routes.admin_dashboard.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "regular_user", "role": "USER"}  # Not admin
            
            response = self.client.get("/api/admin/dashboard/security/overview")
            
            assert response.status_code == 403
            data = response.json()
            assert data["code"] == "INSUFFICIENT_PERMISSIONS"
    
    @pytest.mark.asyncio
    async def test_dashboard_alerts_endpoint(self):
        """Test dashboard alerts endpoint"""
        with patch('app.api.routes.admin_dashboard.get_current_user') as mock_user, \
             patch('app.api.routes.admin_dashboard.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.offset.return_value.execute.return_value.data = [
                {
                    "id": "alert_1",
                    "alert_type": "suspicious_login",
                    "severity": "high",
                    "title": "New Device Login",
                    "description": "Login from unrecognized device",
                    "user_id": "test_user",
                    "ip_address": "192.168.1.100",
                    "requires_action": True,
                    "is_read": False,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            response = self.client.get("/api/admin/dashboard/security/alerts")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["alert_type"] == "suspicious_login"
            assert data[0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_ip_reputation_overview_endpoint(self):
        """Test IP reputation overview endpoint"""
        with patch('app.api.routes.admin_dashboard.get_current_user') as mock_user, \
             patch('app.api.routes.admin_dashboard.get_supabase_client') as mock_supabase:
            
            mock_user.return_value = {"id": "admin_user", "role": "ADMIN"}
            mock_supabase.return_value = AsyncMock()
            mock_supabase.table.return_value.select.return_value.or_.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {
                    "id": "ip_rep_1",
                    "ip_address": "192.168.1.100",
                    "reputation_score": 15,  # Below threshold
                    "failed_attempts": 2,
                    "successful_logins": 10,
                    "is_blocked": False,
                    "last_activity": datetime.utcnow().isoformat()
                }
            ]
            
            response = self.client.get("/api/admin/dashboard/security/ip-reputation?risk_threshold=50&limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 1
            assert data["risk_threshold"] == 50
            assert len(data["ips"]) == 1
            assert data["ips"][0]["reputation_score"] == 15

if __name__ == "__main__":
    pytest.main([__file__])

"""
Tests for Account Blocking functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.core.account_blocking import AccountBlockingService
from app.core.notification_service import NotificationService
from app.models.account_models import (
    AccountBlockRequest,
    AccountUnblockRequest,
    BlockExtensionRequest
)

client = TestClient(app)

class TestAccountBlockingService:
    """Test cases for AccountBlockingService"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        return mock_client
    
    @pytest.fixture
    def mock_notification_service(self):
        """Mock notification service"""
        mock_service = AsyncMock(spec=NotificationService)
        return mock_service
    
    @pytest.fixture
    def blocking_service(self, mock_supabase, mock_notification_service):
        """Create AccountBlockingService instance with mocked dependencies"""
        return AccountBlockingService(mock_supabase, mock_notification_service)
    
    @pytest.mark.asyncio
    async def test_block_user_success(self, blocking_service, mock_supabase, mock_notification_service):
        """Test successful user blocking"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"account_status": "active", "blocked_until": None}
        ]
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "block-123", "user_id": "user-123"}
        ]
        
        # Execute
        result = await blocking_service.block_user(
            user_id="user-123",
            blocked_by="admin-123",
            block_reason="Suspicious activity",
            duration_hours=24
        )
        
        # Assertions
        assert result["block_id"] == "block-123"
        assert result["user_id"] == "user-123"
        assert result["block_reason"] == "Suspicious activity"
        assert result["auto_block"] is False
        
        # Verify notification was sent
        mock_notification_service.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_block_user_already_blocked(self, blocking_service, mock_supabase):
        """Test blocking already blocked user"""
        # Setup mocks
        future_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"account_status": "blocked", "blocked_until": future_time}
        ]
        
        # Execute and assert
        with pytest.raises(Exception, match="already blocked"):
            await blocking_service.block_user(
                user_id="user-123",
                blocked_by="admin-123",
                block_reason="Test",
                duration_hours=24
            )
    
    @pytest.mark.asyncio
    async def test_unblock_user_success(self, blocking_service, mock_supabase, mock_notification_service):
        """Test successful user unblocking"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            # First call: check user status
            Mock(data=[{"account_status": "blocked", "blocked_until": None}]),
            # Second call: get active block
            Mock(data=[{"id": "block-123", "blocked_at": "2024-01-01T00:00:00Z", "block_reason": "Test"}])
        ]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "block-123"}
        ]
        
        # Execute
        result = await blocking_service.unblock_user(
            user_id="user-123",
            unblocked_by="admin-123",
            unblock_reason="Appeal approved"
        )
        
        # Assertions
        assert result["user_id"] == "user-123"
        assert result["unblock_reason"] == "Appeal approved"
        assert result["previous_block_id"] == "block-123"
        
        # Verify notification was sent
        mock_notification_service.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unblock_user_not_blocked(self, blocking_service, mock_supabase):
        """Test unblocking user that is not blocked"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"account_status": "active", "blocked_until": None}
        ]
        
        # Execute and assert
        with pytest.raises(Exception, match="not currently blocked"):
            await blocking_service.unblock_user(
                user_id="user-123",
                unblocked_by="admin-123",
                unblock_reason="Test"
            )
    
    @pytest.mark.asyncio
    async def test_extend_block_success(self, blocking_service, mock_supabase):
        """Test successful block extension"""
        # Setup mocks
        future_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "block-123",
                "blocked_until": future_time,
                "block_duration_hours": 24,
                "block_reason": "Original reason",
                "metadata": {}
            }
        ]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "block-123"}
        ]
        
        # Execute
        result = await blocking_service.extend_block(
            user_id="user-123",
            extended_by="admin-123",
            additional_hours=12,
            extension_reason="Extended for review"
        )
        
        # Assertions
        assert result["block_id"] == "block-123"
        assert result["user_id"] == "user-123"
        assert result["additional_hours"] == 12
        assert result["total_duration_hours"] == 36
    
    @pytest.mark.asyncio
    async def test_get_blocked_users(self, blocking_service, mock_supabase):
        """Test getting blocked users list"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [
            {
                "id": "block-123",
                "user_id": "user-123",
                "block_reason": "Test",
                "block_duration_hours": 24,
                "blocked_at": "2024-01-01T00:00:00Z",
                "blocked_until": "2024-01-02T00:00:00Z",
                "auto_block": False,
                "profiles": {
                    "id": "user-123",
                    "full_name": "Test User",
                    "email": "test@example.com",
                    "role": "CITIZEN"
                }
            }
        ]
        
        # Execute
        result = await blocking_service.get_blocked_users(limit=10, offset=0)
        
        # Assertions
        assert len(result["blocks"]) == 1
        assert result["total"] == 1
        assert result["blocks"][0]["user_id"] == "user-123"
        assert "time_remaining_hours" in result["blocks"][0]
    
    @pytest.mark.asyncio
    async def test_check_user_block_status_blocked(self, blocking_service, mock_supabase):
        """Test checking block status for blocked user"""
        # Setup mocks
        future_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "account_status": "blocked",
                "block_reason": "Test",
                "blocked_at": "2024-01-01T00:00:00Z",
                "blocked_until": future_time,
                "auto_block": False
            }
        ]
        
        # Execute
        result = await blocking_service.check_user_block_status("user-123")
        
        # Assertions
        assert result["is_blocked"] is True
        assert result["block_reason"] == "Test"
        assert result["auto_block"] is False
    
    @pytest.mark.asyncio
    async def test_check_user_block_status_not_blocked(self, blocking_service, mock_supabase):
        """Test checking block status for active user"""
        # Setup mocks
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"account_status": "active", "blocked_until": None}
        ]
        
        # Execute
        result = await blocking_service.check_user_block_status("user-123")
        
        # Assertions
        assert result["is_blocked"] is False


class TestAccountBlockingAPI:
    """Test cases for Account Blocking API endpoints"""
    
    @pytest.fixture
    def mock_admin_token(self):
        """Mock admin JWT token"""
        return "Bearer mock_admin_token"
    
    @pytest.fixture
    def mock_jwt_validation(self, monkeypatch):
        """Mock JWT validation"""
        mock_validate = Mock(return_value={"user_id": "admin-123", "role": "ADMIN"})
        monkeypatch.setattr("app.core.security.JWTManager.validate_jwt_token", mock_validate)
    
    @pytest.fixture
    def mock_supabase_client(self, monkeypatch):
        """Mock Supabase client"""
        mock_client = Mock()
        monkeypatch.setattr("app.core.database.get_supabase_client", lambda: mock_client)
        return mock_client
    
    def test_block_user_endpoint_success(self, mock_admin_token, mock_jwt_validation, mock_supabase_client):
        """Test successful block user endpoint"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"role": "ADMIN"}
        ]
        
        with patch('app.api.routes.admin_blocking.AccountBlockingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.block_user.return_value = {
                "block_id": "block-123",
                "user_id": "user-123",
                "blocked_until": "2024-01-02T00:00:00Z",
                "block_reason": "Test",
                "auto_block": False
            }
            mock_service_class.return_value = mock_service
            
            # Execute
            response = client.post(
                "/api/admin/users/user-123/block",
                json={
                    "block_reason": "Test",
                    "duration_hours": 24,
                    "auto_block": False
                },
                headers={"Authorization": mock_admin_token}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["block_id"] == "block-123"
            assert data["user_id"] == "user-123"
    
    def test_block_user_endpoint_unauthorized(self):
        """Test block user endpoint without authorization"""
        response = client.post(
            "/api/admin/users/user-123/block",
            json={"block_reason": "Test", "duration_hours": 24}
        )
        
        assert response.status_code == 401
    
    def test_unblock_user_endpoint_success(self, mock_admin_token, mock_jwt_validation, mock_supabase_client):
        """Test successful unblock user endpoint"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"role": "ADMIN"}
        ]
        
        with patch('app.api.routes.admin_blocking.AccountBlockingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.unblock_user.return_value = {
                "user_id": "user-123",
                "unblocked_at": "2024-01-01T12:00:00Z",
                "unblock_reason": "Appeal approved",
                "previous_block_id": "block-123"
            }
            mock_service_class.return_value = mock_service
            
            # Execute
            response = client.post(
                "/api/admin/users/user-123/unblock",
                json={"unblock_reason": "Appeal approved"},
                headers={"Authorization": mock_admin_token}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "user-123"
            assert data["unblock_reason"] == "Appeal approved"
    
    def test_get_blocked_users_endpoint(self, mock_admin_token, mock_jwt_validation, mock_supabase_client):
        """Test get blocked users endpoint"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"role": "ADMIN"}
        ]
        
        with patch('app.api.routes.admin_blocking.AccountBlockingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_blocked_users.return_value = {
                "blocks": [],
                "total": 0,
                "limit": 50,
                "offset": 0
            }
            mock_service_class.return_value = mock_service
            
            # Execute
            response = client.get(
                "/api/admin/users/blocked",
                headers={"Authorization": mock_admin_token}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
    
    def test_extend_block_endpoint(self, mock_admin_token, mock_jwt_validation, mock_supabase_client):
        """Test extend block endpoint"""
        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"role": "ADMIN"}
        ]
        
        with patch('app.api.routes.admin_blocking.AccountBlockingService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.extend_block.return_value = {
                "block_id": "block-123",
                "user_id": "user-123",
                "new_blocked_until": "2024-01-03T00:00:00Z",
                "additional_hours": 12,
                "total_duration_hours": 36
            }
            mock_service_class.return_value = mock_service
            
            # Execute
            response = client.post(
                "/api/admin/users/user-123/block/extend",
                json={
                    "additional_hours": 12,
                    "extension_reason": "Extended for review"
                },
                headers={"Authorization": mock_admin_token}
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["additional_hours"] == 12
            assert data["total_duration_hours"] == 36


class TestAccountBlockingIntegration:
    """Integration tests for account blocking"""
    
    def test_login_blocked_user(self):
        """Test that blocked users cannot login"""
        with patch('app.core.database.get_supabase_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            # Mock successful auth but blocked user
            mock_client.auth.signInWithPassword.return_value = Mock(
                user=Mock(
                    id="user-123",
                    email="test@example.com",
                    email_confirmed_at=datetime.utcnow().isoformat(),
                    user_metadata={"role": "CITIZEN", "full_name": "Test User"}
                ),
                session=Mock(access_token="token", refresh_token="refresh")
            )
            
            with patch('app.api.routes.auth.AccountBlockingService') as mock_service_class:
                mock_service = AsyncMock()
                mock_service.check_user_block_status.return_value = {
                    "is_blocked": True,
                    "block_reason": "Suspicious activity",
                    "blocked_until": "2024-01-02T00:00:00Z",
                    "auto_block": False
                }
                mock_service_class.return_value = mock_service
                
                # Execute
                response = client.post(
                    "/api/auth/login",
                    json={"email": "test@example.com", "password": "password"}
                )
                
                # Assertions
                assert response.status_code == 403
                data = response.json()
                assert data["code"] == "ACCOUNT_BLOCKED"
                assert "blocked_until" in data
    
    def test_login_active_user_success(self):
        """Test that active users can login normally"""
        with patch('app.core.database.get_supabase_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            # Mock successful auth and active user
            mock_client.auth.signInWithPassword.return_value = Mock(
                user=Mock(
                    id="user-123",
                    email="test@example.com",
                    email_confirmed_at=datetime.utcnow().isoformat(),
                    user_metadata={"role": "CITIZEN", "full_name": "Test User"}
                ),
                session=Mock(access_token="token", refresh_token="refresh")
            )
            
            with patch('app.api.routes.auth.AccountBlockingService') as mock_service_class:
                mock_service = AsyncMock()
                mock_service.check_user_block_status.return_value = {"is_blocked": False}
                mock_service_class.return_value = mock_service
                
                # Execute
                response = client.post(
                    "/api/auth/login",
                    json={"email": "test@example.com", "password": "password"}
                )
                
                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Login successful"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

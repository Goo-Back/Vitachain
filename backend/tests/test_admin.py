"""
Tests for Admin User Management functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status
import uuid
from datetime import datetime

from app.main import app
from app.services.admin_service import AdminUserService
from app.models.schemas import (
    UserStatus,
    UserRole,
    UserStatusUpdateRequest,
    UserRoleUpdateRequest,
    BulkUserUpdateRequest
)


class TestAdminEndpoints:
    """Test suite for admin user management endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def admin_token(self):
        """Mock admin JWT token"""
        return "mock_admin_jwt_token"
    
    @pytest.fixture
    def user_token(self):
        """Mock regular user JWT token"""
        return "mock_user_jwt_token"
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        return Mock()
    
    @pytest.fixture
    def admin_service(self, mock_supabase):
        """Create admin service with mock Supabase"""
        return AdminUserService(mock_supabase)

    def test_get_users_admin_only(self, client, user_token):
        """Test that get users endpoint requires admin role"""
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "ADMIN_ACCESS_DENIED" in response.json()["error"]["code"]

    def test_get_users_success(self, client, admin_token, mock_supabase):
        """Test successful users retrieval"""
        # Mock database response
        mock_users = [
            {
                "id": str(uuid.uuid4()),
                "email": "admin@example.com",
                "full_name": "Admin User",
                "role": "ADMIN",
                "account_status": "active",
                "created_at": "2026-05-01T10:00:00Z",
                "updated_at": "2026-05-01T10:00:00Z",
                "last_login": "2026-05-02T14:30:00Z",
                "devices_count": 0,
                "listings_count": 0,
                "reservations_count": 0,
                "orders_count": 0
            }
        ]
        
        mock_stats = {
            "total_users": 1,
            "active_users": 1,
            "blocked_users": 0,
            "pending_users": 0,
            "users_by_role": {"ADMIN": 1},
            "registrations_today": 0,
            "registrations_this_week": 1,
            "registrations_this_month": 1
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value = Mock(
            data=mock_users
        )
        
        # Mock stats query
        mock_supabase.table.return_value.select.return_value.execute.side_effect = [
            Mock(data=[{"account_status": "active"}]),
            Mock(data=[{"role": "ADMIN"}]),
            Mock(data=[{"id": str(uuid.uuid4())}]),
            Mock(data=[{"id": str(uuid.uuid4())}]),
            Mock(data=[{"id": str(uuid.uuid4())}]),
            Mock(data=[{"id": str(uuid.uuid4())}])
        ]
        
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "pagination" in data
        assert "stats" in data
        assert len(data["users"]) == 1
        assert data["users"][0]["email"] == "admin@example.com"

    def test_get_user_details_success(self, client, admin_token, mock_supabase):
        """Test successful user details retrieval"""
        user_id = str(uuid.uuid4())
        mock_user = {
            "id": user_id,
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "FARMER",
            "account_status": "active",
            "created_at": "2026-05-01T10:00:00Z",
            "updated_at": "2026-05-01T10:00:00Z",
            "last_login": "2026-05-02T14:30:00Z"
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[mock_user]
        )
        
        response = client.get(
            f"/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "FARMER"

    def test_get_user_details_not_found(self, client, admin_token, mock_supabase):
        """Test user details retrieval for non-existent user"""
        user_id = str(uuid.uuid4())
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        response = client.get(
            f"/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "USER_NOT_FOUND" in response.json()["error"]["code"]

    def test_update_user_status_success(self, client, admin_token, mock_supabase):
        """Test successful user status update"""
        user_id = str(uuid.uuid4())
        update_data = {
            "new_status": "blocked",
            "reason": "Violation of platform policies"
        }
        
        # Mock current user data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "account_status": "active",
                "email": "test@example.com"
            }]
        )
        
        # Mock update
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        
        # Mock audit log
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()
        
        response = client.patch(
            f"/api/admin/users/{user_id}/status",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User status updated successfully"
        assert data["new_status"] == "blocked"

    def test_update_user_role_success(self, client, admin_token, mock_supabase):
        """Test successful user role update"""
        user_id = str(uuid.uuid4())
        update_data = {
            "new_role": "SUPPORT",
            "reason": "Promoted to support role"
        }
        
        # Mock current user data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "role": "FARMER",
                "email": "test@example.com"
            }]
        )
        
        # Mock update
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        
        # Mock audit log
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()
        
        response = client.patch(
            f"/api/admin/users/{user_id}/role",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "User role updated successfully"
        assert data["new_role"] == "SUPPORT"

    def test_bulk_update_users_success(self, client, admin_token, mock_supabase):
        """Test successful bulk user update"""
        user_ids = [str(uuid.uuid4()) for _ in range(3)]
        bulk_data = {
            "user_ids": user_ids,
            "action": "update_role",
            "data": {
                "new_role": "SUPPORT",
                "reason": "Bulk role assignment"
            }
        }
        
        # Mock individual user updates
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{"role": "FARMER", "email": f"test{i}@example.com"} for i in range(3)]
        )
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()
        
        response = client.post(
            "/api/admin/users/bulk-update",
            json=bulk_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated_count"] == 3
        assert data["failed_count"] == 0

    def test_export_users_csv_success(self, client, admin_token, mock_supabase):
        """Test successful CSV export"""
        # Mock users data
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": str(uuid.uuid4()),
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "role": "FARMER",
                    "account_status": "active"
                }
            ]
        )
        
        response = client.post(
            "/api/admin/users/export",
            params={"format": "csv"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert data["format"] == "csv"
        assert "test@example.com" in data["data"]


class TestAdminService:
    """Test suite for admin service business logic"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        return Mock()
    
    @pytest.fixture
    def admin_service(self, mock_supabase):
        """Create admin service with mock Supabase"""
        return AdminUserService(mock_supabase)

    @pytest.mark.asyncio
    async def test_get_users_with_filters(self, admin_service, mock_supabase):
        """Test user retrieval with filters"""
        # Mock database response
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": str(uuid.uuid4()),
                    "email": "farmer@example.com",
                    "full_name": "Farmer User",
                    "role": "FARMER",
                    "account_status": "active"
                }
            ]
        )
        
        # Mock stats queries
        mock_supabase.table.return_value.select.return_value.execute.side_effect = [
            Mock(data=[{"account_status": "active"}]),
            Mock(data=[{"role": "FARMER"}]),
            Mock(data=[{"id": str(uuid.uuid4())}])
        ]
        
        result = await admin_service.get_users(
            page=1,
            limit=20,
            search="farmer",
            role=UserRole.FARMER,
            status=UserStatus.ACTIVE
        )
        
        assert len(result.users) == 1
        assert result.users[0]["email"] == "farmer@example.com"
        assert result.stats.total_users == 1
        assert result.stats.active_users == 1

    @pytest.mark.asyncio
    async def test_update_user_status_invalid_transition(self, admin_service, mock_supabase):
        """Test user status update with invalid transition"""
        user_id = str(uuid.uuid4())
        
        # Mock current user data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{"account_status": "active", "email": "test@example.com"}]
        )
        
        # Mock status validation to return False
        admin_service._is_valid_status_transition = Mock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            await admin_service.update_user_status(
                user_id=user_id,
                new_status=UserStatus.BLOCKED,
                reason="Test reason",
                admin_id=str(uuid.uuid4())
            )
        
        assert "INVALID_STATUS_TRANSITION" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_bulk_update_users_partial_failure(self, admin_service, mock_supabase):
        """Test bulk user update with some failures"""
        user_ids = [str(uuid.uuid4()) for _ in range(3)]
        bulk_request = BulkUserUpdateRequest(
            user_ids=user_ids,
            action="update_role",
            data={"new_role": "SUPPORT", "reason": "Bulk update"}
        )
        
        # Mock first user update to succeed, others to fail
        call_count = 0
        def mock_update(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return Mock()
            else:
                raise Exception("Update failed")
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = mock_update
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock()
        
        result = await admin_service.bulk_update_users(
            bulk_request=bulk_request,
            admin_id=str(uuid.uuid4())
        )
        
        assert result.updated_count == 1
        assert result.failed_count == 2
        assert len(result.results) == 3

    @pytest.mark.asyncio
    async def test_export_users_csv_generation(self, admin_service, mock_supabase):
        """Test CSV export data generation"""
        from app.models.schemas import AdminUserView
        
        mock_users = [
            AdminUserView(
                id=uuid.uuid4(),
                email="test@example.com",
                full_name="Test User",
                role=UserRole.FARMER,
                account_status=UserStatus.ACTIVE,
                created_at="2026-05-01T10:00:00Z",
                updated_at="2026-05-01T10:00:00Z",
                last_login="2026-05-02T14:30:00Z",
                devices_count=2,
                listings_count=5,
                reservations_count=3,
                orders_count=1
            )
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value = Mock(
            data=mock_users
        )
        
        csv_data = await admin_service.export_users(
            export_request=Mock(format="csv"),
            admin_id=str(uuid.uuid4())
        )
        
        assert "test@example.com" in csv_data
        assert "Test User" in csv_data
        assert "FARMER" in csv_data
        assert "2" in csv_data  # devices_count

    @pytest.mark.asyncio
    async def test_audit_logging(self, admin_service, mock_supabase):
        """Test that admin actions are logged properly"""
        user_id = str(uuid.uuid4())
        admin_id = str(uuid.uuid4())
        
        # Mock admin lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{"email": "admin@example.com"}]
        )
        
        # Mock audit log insertion
        mock_insert = Mock()
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert
        
        await admin_service._log_admin_action(
            admin_id=admin_id,
            action="test_action",
            target_user_id=user_id,
            target_user_email="test@example.com",
            details={"test": "data"}
        )
        
        # Verify audit log was created
        mock_insert.assert_called_once()
        call_args = mock_insert.call_args[0][0][0]
        assert call_args["admin_id"] == admin_id
        assert call_args["action"] == "test_action"
        assert call_args["target_user_id"] == user_id
        assert call_args["details"]["test"] == "data"


class TestAdminSecurity:
    """Test suite for admin security and access control"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_unauthorized_access(self, client):
        """Test that admin endpoints require authentication"""
        response = client.get("/api/admin/users")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "UNAUTHORIZED" in response.json()["error"]["code"]

    def test_non_admin_access_denied(self, client, mock_supabase):
        """Test that non-admin users are denied access"""
        # Mock JWT validation to return non-admin user
        with patch('app.api.routes.admin.JWTManager.validate_jwt_token') as mock_jwt:
            mock_jwt.return_value = {
                "user_id": str(uuid.uuid4()),
                "role": "FARMER"  # Non-admin role
            }
            
            response = client.get(
                "/api/admin/users",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "ADMIN_ACCESS_DENIED" in response.json()["error"]["code"]

    def test_admin_access_granted(self, client, mock_supabase):
        """Test that admin users are granted access"""
        # Mock JWT validation to return admin user
        with patch('app.api.routes.admin.JWTManager.validate_jwt_token') as mock_jwt:
            mock_jwt.return_value = {
                "user_id": str(uuid.uuid4()),
                "role": "ADMIN"
            }
            
            response = client.get(
                "/api/admin/users",
                headers={"Authorization": "Bearer valid_token"}
            )
            
            # Should not raise access denied error
            assert response.status_code != status.HTTP_403_FORBIDDEN


if __name__ == "__main__":
    pytest.main([__file__])

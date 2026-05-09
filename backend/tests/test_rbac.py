"""
Comprehensive RBAC tests for VitaChain platform
Tests role-based access control, permissions, and data ownership
"""

import pytest
import asyncio
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, AsyncMock
from app.core.permissions import (
    UserRole, Permission, RBACManager,
    rbac_manager, require_telemetry_access,
    require_device_management, require_marketplace_access,
    require_listing_management, require_meal_management,
    require_reservation_access, require_user_management,
    require_system_access, require_admin_access
)


class TestRBACManager:
    """Test RBAC Manager functionality"""
    
    def test_admin_has_all_permissions(self):
        """Admin should have all permissions"""
        for permission in Permission:
            assert rbac_manager.has_permission(UserRole.ADMIN, permission)
    
    def test_farmer_permissions(self):
        """Farmer should have specific permissions"""
        farmer_permissions = [
            Permission.READ_OWN_TELEMETRY,
            Permission.WRITE_OWN_DEVICES,
            Permission.READ_OWN_ALERTS,
            Permission.WRITE_OWN_ALERTS,
            Permission.READ_OWN_LISTINGS,
            Permission.WRITE_OWN_LISTINGS,
            Permission.READ_MARKETPLACE,
            Permission.WRITE_OWN_ORDERS,
            Permission.READ_OWN_ORDERS,
            Permission.READ_PROFILES,
            Permission.WRITE_PROFILES,
        ]
        
        for permission in farmer_permissions:
            assert rbac_manager.has_permission(UserRole.FARMER, permission)
        
        # Farmer should not have restaurant-specific permissions
        assert not rbac_manager.has_permission(UserRole.FARMER, Permission.READ_OWN_MEALS)
        assert not rbac_manager.has_permission(UserRole.FARMER, Permission.WRITE_OWN_MEALS)
    
    def test_restaurant_permissions(self):
        """Restaurant should have specific permissions"""
        restaurant_permissions = [
            Permission.READ_OWN_MEALS,
            Permission.WRITE_OWN_MEALS,
            Permission.READ_OWN_RESERVATIONS,
            Permission.WRITE_OWN_RESERVATIONS,
            Permission.READ_MARKETPLACE,
            Permission.READ_PROFILES,
            Permission.WRITE_PROFILES,
        ]
        
        for permission in restaurant_permissions:
            assert rbac_manager.has_permission(UserRole.RESTAURANT, permission)
        
        # Restaurant should not have farmer-specific permissions
        assert not rbac_manager.has_permission(UserRole.RESTAURANT, Permission.READ_OWN_TELEMETRY)
        assert not rbac_manager.has_permission(UserRole.RESTAURANT, Permission.WRITE_OWN_DEVICES)
    
    def test_citizen_permissions(self):
        """Citizen should have limited permissions"""
        citizen_permissions = [
            Permission.READ_MARKETPLACE,
            Permission.WRITE_OWN_RESERVATIONS,
            Permission.READ_OWN_RESERVATIONS,
            Permission.READ_PROFILES,
            Permission.WRITE_PROFILES,
        ]
        
        for permission in citizen_permissions:
            assert rbac_manager.has_permission(UserRole.CITIZEN, permission)
        
        # Citizen should not have management permissions
        assert not rbac_manager.has_permission(UserRole.CITIZEN, Permission.READ_OWN_TELEMETRY)
        assert not rbac_manager.has_permission(UserRole.CITIZEN, Permission.WRITE_OWN_DEVICES)
        assert not rbac_manager.has_permission(UserRole.CITIZEN, Permission.READ_USERS)
    
    def test_support_permissions(self):
        """Support should have read-only permissions"""
        support_permissions = [
            Permission.READ_USERS,
            Permission.READ_PROFILES,
            Permission.WRITE_RESET_CODES,
            Permission.WRITE_UNBLOCK_ACCOUNTS,
            Permission.READ_AUDIT_LOGS,
        ]
        
        for permission in support_permissions:
            assert rbac_manager.has_permission(UserRole.SUPPORT, permission)
        
        # Support should not have write permissions for user data
        assert not rbac_manager.has_permission(UserRole.SUPPORT, Permission.WRITE_USERS)
        assert not rbac_manager.has_permission(UserRole.SUPPORT, Permission.READ_OWN_TELEMETRY)
    
    def test_has_any_permission(self):
        """Test any permission checking"""
        # Should return True if user has any of the permissions
        assert rbac_manager.has_any_permission(
            UserRole.FARMER, 
            [Permission.READ_OWN_TELEMETRY, Permission.READ_OWN_MEALS]
        )
        
        # Should return False if user has none of the permissions
        assert not rbac_manager.has_any_permission(
            UserRole.CITIZEN,
            [Permission.READ_OWN_TELEMETRY, Permission.WRITE_OWN_DEVICES]
        )
    
    def test_has_all_permissions(self):
        """Test all permission checking"""
        # Should return True if user has all permissions
        assert rbac_manager.has_all_permissions(
            UserRole.FARMER,
            [Permission.READ_OWN_TELEMETRY, Permission.WRITE_OWN_DEVICES]
        )
        
        # Should return False if user missing any permission
        assert not rbac_manager.has_all_permissions(
            UserRole.FARMER,
            [Permission.READ_OWN_TELEMETRY, Permission.READ_OWN_MEALS]
        )
    
    def test_can_access_role(self):
        """Test role-based access control"""
        # Admin can access all roles
        assert rbac_manager.can_access_role(UserRole.ADMIN, UserRole.FARMER)
        assert rbac_manager.can_access_role(UserRole.ADMIN, UserRole.SUPPORT)
        
        # Support can access non-admin roles
        assert rbac_manager.can_access_role(UserRole.SUPPORT, UserRole.FARMER)
        assert rbac_manager.can_access_role(UserRole.SUPPORT, UserRole.RESTAURANT)
        assert rbac_manager.can_access_role(UserRole.SUPPORT, UserRole.CITIZEN)
        
        # Support cannot access admin
        assert not rbac_manager.can_access_role(UserRole.SUPPORT, UserRole.ADMIN)
        
        # Users can only access their own role
        assert rbac_manager.can_access_role(UserRole.FARMER, UserRole.FARMER)
        assert not rbac_manager.can_access_role(UserRole.FARMER, UserRole.RESTAURANT)
    
    def test_validate_data_ownership(self):
        """Test data ownership validation"""
        user_id = "user-123"
        resource_user_id = "user-123"
        other_user_id = "user-456"
        
        # Admin can access all resources
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, user_id, resource_user_id
        )
        assert rbac_manager.validate_data_ownership(
            UserRole.ADMIN, user_id, other_user_id
        )
        
        # Support can read all resources
        assert rbac_manager.validate_data_ownership(
            UserRole.SUPPORT, user_id, resource_user_id
        )
        assert rbac_manager.validate_data_ownership(
            UserRole.SUPPORT, user_id, other_user_id
        )
        
        # Users can only access their own resources
        assert rbac_manager.validate_data_ownership(
            UserRole.FARMER, user_id, resource_user_id
        )
        assert not rbac_manager.validate_data_ownership(
            UserRole.FARMER, user_id, other_user_id
        )


class TestPermissionCheckingFunctions:
    """Test permission checking functions"""
    
    @pytest.mark.asyncio
    async def test_require_telemetry_access_success(self):
        """Should allow access with correct permission"""
        await require_telemetry_access(UserRole.FARMER, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_telemetry_access_denied(self):
        """Should deny access without permission"""
        with pytest.raises(HTTPException) as exc_info:
            await require_telemetry_access(UserRole.CITIZEN, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "INSUFFICIENT_PERMISSIONS" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_require_device_management_success(self):
        """Should allow device management for farmer"""
        await require_device_management(UserRole.FARMER, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_device_management_denied(self):
        """Should deny device management for citizen"""
        with pytest.raises(HTTPException) as exc_info:
            await require_device_management(UserRole.CITIZEN, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_marketplace_access_success(self):
        """Should allow marketplace access for all user roles"""
        await require_marketplace_access(UserRole.FARMER, "user-123")
        await require_marketplace_access(UserRole.RESTAURANT, "user-123")
        await require_marketplace_access(UserRole.CITIZEN, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_meal_management_success(self):
        """Should allow meal management for restaurant"""
        await require_meal_management(UserRole.RESTAURANT, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_meal_management_denied(self):
        """Should deny meal management for farmer"""
        with pytest.raises(HTTPException) as exc_info:
            await require_meal_management(UserRole.FARMER, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_user_management_success(self):
        """Should allow user management for support"""
        await require_user_management(UserRole.SUPPORT, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_user_management_denied(self):
        """Should deny user management for citizen"""
        with pytest.raises(HTTPException) as exc_info:
            await require_user_management(UserRole.CITIZEN, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_system_access_success(self):
        """Should allow system access for admin"""
        await require_system_access(UserRole.ADMIN, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_system_access_denied(self):
        """Should deny system access for farmer"""
        with pytest.raises(HTTPException) as exc_info:
            await require_system_access(UserRole.FARMER, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_require_admin_access_success(self):
        """Should allow admin access for admin"""
        await require_admin_access(UserRole.ADMIN, "user-123")
    
    @pytest.mark.asyncio
    async def test_require_admin_access_denied(self):
        """Should deny admin access for non-admin roles"""
        with pytest.raises(HTTPException) as exc_info:
            await require_admin_access(UserRole.FARMER, "user-123")
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "ADMIN_ACCESS_REQUIRED" in str(exc_info.value.detail)


class TestRBACDataOwnership:
    """Test RBAC data ownership validation"""
    
    @pytest.mark.asyncio
    async def test_check_data_ownership_success(self):
        """Should allow access to own resources"""
        await rbac_manager.check_data_ownership(
            UserRole.FARMER, "user-123", "user-123", "telemetry"
        )
    
    @pytest.mark.asyncio
    async def test_check_data_ownership_denied(self):
        """Should deny access to other's resources"""
        with pytest.raises(HTTPException) as exc_info:
            await rbac_manager.check_data_ownership(
                UserRole.FARMER, "user-123", "user-456", "telemetry"
            )
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "ACCESS_DENIED" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_check_data_ownership_admin_override(self):
        """Admin should access all resources regardless of ownership"""
        await rbac_manager.check_data_ownership(
            UserRole.ADMIN, "admin-123", "user-456", "telemetry"
        )
    
    @pytest.mark.asyncio
    async def test_check_data_ownership_support_readonly(self):
        """Support should access all resources for readonly operations"""
        await rbac_manager.check_data_ownership(
            UserRole.SUPPORT, "support-123", "user-456", "user_profile"
        )


class TestRBACIntegration:
    """Test RBAC integration with dependencies"""
    
    @pytest.mark.asyncio
    async def test_rbac_dependency_integration(self):
        """Test RBAC integration with FastAPI dependencies"""
        from app.api.dependencies import (
            require_permission, require_any_permission,
            require_telemetry_permission, require_device_permission,
            require_listing_permission, require_meal_permission,
            require_reservation_permission, require_user_read_permission,
            require_system_permission, require_admin_with_audit
        )
        
        # Test that dependency factories return callable functions
        telemetry_dep = require_permission(Permission.READ_OWN_TELEMETRY)
        assert callable(telemetry_dep)
        
        any_perm_dep = require_any_permission(
            Permission.READ_OWN_TELEMETRY, Permission.READ_MARKETPLACE
        )
        assert callable(any_perm_dep)
        
        # Test that predefined dependencies are callable
        assert callable(require_telemetry_permission)
        assert callable(require_device_permission)
        assert callable(require_listing_permission)
        assert callable(require_meal_permission)
        assert callable(require_reservation_permission)
        assert callable(require_user_read_permission)
        assert callable(require_system_permission)
        assert callable(require_admin_with_audit)


if __name__ == "__main__":
    pytest.main([__file__])

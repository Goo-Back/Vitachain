"""
Role-Based Access Control (RBAC) Permission System for VitaChain
Handles granular permissions, role hierarchy, and access control
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
import structlog
from fastapi import HTTPException, status
from functools import wraps
import time
from collections import defaultdict

logger = structlog.get_logger("rbac")

class UserRole(str, Enum):
    """User roles for VitaChain platform"""
    FARMER = "FARMER"
    RESTAURANT = "RESTAURANT"
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"

class Permission(str, Enum):
    """Granular permissions for VitaChain platform"""
    # Telemetry permissions (KATARA)
    READ_OWN_TELEMETRY = "read:own_telemetry"
    WRITE_OWN_DEVICES = "write:own_devices"
    READ_OWN_ALERTS = "read:own_alerts"
    WRITE_OWN_ALERTS = "write:own_alerts"
    
    # Marketplace permissions (FARMARKET)
    READ_OWN_LISTINGS = "read:own_listings"
    WRITE_OWN_LISTINGS = "write:own_listings"
    READ_MARKETPLACE = "read:marketplace"
    WRITE_OWN_ORDERS = "write:own_orders"
    READ_OWN_ORDERS = "read:own_orders"
    
    # Restaurant permissions (SECONDSERVE)
    READ_OWN_MEALS = "read:own_meals"
    WRITE_OWN_MEALS = "write:own_meals"
    READ_OWN_RESERVATIONS = "read:own_reservations"
    WRITE_OWN_RESERVATIONS = "write:own_reservations"
    
    # User management permissions
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    READ_PROFILES = "read:profiles"
    WRITE_PROFILES = "write:profiles"
    
    # Support permissions
    WRITE_RESET_CODES = "write:reset_codes"
    WRITE_UNBLOCK_ACCOUNTS = "write:unblock_accounts"
    
    # Account blocking permissions
    BLOCK_ACCOUNTS = "block:accounts"
    UNBLOCK_ACCOUNTS = "unblock:accounts"
    EXTEND_BLOCKS = "extend:blocks"
    VIEW_BLOCKED_USERS = "view:blocked_users"
    
    # Admin permissions
    READ_SYSTEM = "read:system"
    WRITE_SYSTEM = "write:system"
    READ_AUDIT_LOGS = "read:audit_logs"
    WRITE_AUDIT_LOGS = "write:audit_logs"

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self._role_permissions: Dict[UserRole, Set[Permission]] = {
            UserRole.FARMER: {
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
            },
            UserRole.RESTAURANT: {
                Permission.READ_OWN_MEALS,
                Permission.WRITE_OWN_MEALS,
                Permission.READ_OWN_RESERVATIONS,
                Permission.WRITE_OWN_RESERVATIONS,
                Permission.READ_MARKETPLACE,
                Permission.READ_PROFILES,
                Permission.WRITE_PROFILES,
            },
            UserRole.CITIZEN: {
                Permission.READ_MARKETPLACE,
                Permission.WRITE_OWN_RESERVATIONS,
                Permission.READ_OWN_RESERVATIONS,
                Permission.READ_PROFILES,
                Permission.WRITE_PROFILES,
            },
            UserRole.SUPPORT: {
                Permission.READ_USERS,
                Permission.READ_PROFILES,
                Permission.WRITE_RESET_CODES,
                Permission.WRITE_UNBLOCK_ACCOUNTS,
                Permission.UNBLOCK_ACCOUNTS,
                Permission.VIEW_BLOCKED_USERS,
                Permission.READ_AUDIT_LOGS,
            },
            UserRole.ADMIN: {
                # Admin has all permissions
                Permission.READ_OWN_TELEMETRY,
                Permission.WRITE_OWN_DEVICES,
                Permission.READ_OWN_ALERTS,
                Permission.WRITE_OWN_ALERTS,
                Permission.READ_OWN_LISTINGS,
                Permission.WRITE_OWN_LISTINGS,
                Permission.READ_MARKETPLACE,
                Permission.WRITE_OWN_ORDERS,
                Permission.READ_OWN_ORDERS,
                Permission.READ_OWN_MEALS,
                Permission.WRITE_OWN_MEALS,
                Permission.READ_OWN_RESERVATIONS,
                Permission.WRITE_OWN_RESERVATIONS,
                Permission.READ_USERS,
                Permission.WRITE_USERS,
                Permission.READ_PROFILES,
                Permission.WRITE_PROFILES,
                Permission.WRITE_RESET_CODES,
                Permission.WRITE_UNBLOCK_ACCOUNTS,
                Permission.BLOCK_ACCOUNTS,
                Permission.UNBLOCK_ACCOUNTS,
                Permission.EXTEND_BLOCKS,
                Permission.VIEW_BLOCKED_USERS,
                Permission.READ_SYSTEM,
                Permission.WRITE_SYSTEM,
                Permission.READ_AUDIT_LOGS,
                Permission.WRITE_AUDIT_LOGS,
            }
        }
        
        # Role hierarchy for inheritance
        self._role_hierarchy: Dict[UserRole, List[UserRole]] = {
            UserRole.ADMIN: [UserRole.SUPPORT, UserRole.FARMER, UserRole.RESTAURANT, UserRole.CITIZEN],
            UserRole.SUPPORT: [UserRole.FARMER, UserRole.RESTAURANT, UserRole.CITIZEN],
            UserRole.FARMER: [],
            UserRole.RESTAURANT: [],
            UserRole.CITIZEN: [],
        }
        
        # Rate limiting for permission checks
        self._rate_limits = defaultdict(list)
        self._permission_cache = {}
        
        # Pre-compute permission sets for faster lookup
        self._role_permission_sets = {
            role: frozenset(permissions) 
            for role, permissions in self._role_permissions.items()
        }
    
    def _check_rate_limit(self, user_id: str, operation: str) -> bool:
        """
        Check if user has exceeded rate limit for permission checks
        
        Args:
            user_id: User ID for rate limiting
            operation: Operation type (e.g., 'permission_check')
            
        Returns:
            True if within rate limit, False otherwise
        """
        now = time.time()
        if user_id in self._rate_limits[operation]:
            recent_checks = [t for t in self._rate_limits[operation] if now - t < 60]
            if len(recent_checks) >= 100:  # 100 checks per minute
                return False
            self._rate_limits[operation] = [t for t in self._rate_limits[operation] if now - t < 60]
        self._rate_limits[operation].append(now)
        return True

    def has_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """
        Check if user role has specific permission with optimized caching and rate limiting
        
        Args:
            user_role: User's role
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admin has all permissions
        if user_role == UserRole.ADMIN:
            return True
        
        # Check cache first
        cache_key = f"{user_role}:{permission}"
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        # Use pre-computed frozenset for faster lookup
        role_permissions = self._role_permission_sets.get(user_role, frozenset())
        has_perm = permission in role_permissions
        
        # Cache result
        self._permission_cache[cache_key] = has_perm
        
        return has_perm
    
    def has_any_permission(self, user_role: UserRole, permissions: List[Permission]) -> bool:
        """
        Check if user role has any of the specified permissions
        
        Args:
            user_role: User's role
            permissions: List of permissions to check
            
        Returns:
            True if user has any of the permissions, False otherwise
        """
        return any(self.has_permission(user_role, perm) for perm in permissions)
    
    def has_all_permissions(self, user_role: UserRole, permissions: List[Permission]) -> bool:
        """
        Check if user role has all of the specified permissions
        
        Args:
            user_role: User's role
            permissions: List of permissions to check
            
        Returns:
            True if user has all permissions, False otherwise
        """
        return all(self.has_permission(user_role, perm) for perm in permissions)
    
    def can_access_role(self, user_role: UserRole, target_role: UserRole) -> bool:
        """
        Check if user can access resources belonging to target role
        Based on role hierarchy
        
        Args:
            user_role: User's role
            target_role: Target role to access
            
        Returns:
            True if user can access target role resources, False otherwise
        """
        # Admin can access all roles
        if user_role == UserRole.ADMIN:
            return True
        
        # Support can access all user roles for support purposes
        if user_role == UserRole.SUPPORT and target_role != UserRole.ADMIN:
            return True
        
        # Users can only access their own role resources
        return user_role == target_role
    
    def get_user_permissions(self, user_role: UserRole) -> Set[Permission]:
        """
        Get all permissions for a user role
        
        Args:
            user_role: User's role
            
        Returns:
            Set of permissions for the role
        """
        return self._role_permissions.get(user_role, set()).copy()
    
    def validate_data_ownership(self, user_role: UserRole, user_id: str, resource_user_id: str) -> bool:
        """
        Validate if user can access specific resource based on ownership
        
        Args:
            user_role: User's role
            user_id: Current user's ID
            resource_user_id: Owner ID of the resource
            
        Returns:
            True if user can access resource, False otherwise
        """
        # Admin can access all resources
        if user_role == UserRole.ADMIN:
            return True
        
        # Support can read all resources for support purposes
        if user_role == UserRole.SUPPORT:
            return True
        
        # Users can only access their own resources
        return user_id == resource_user_id
    
    async def check_permission(self, user_role: UserRole, permission: Permission, user_id: str = None):
        """
        Check permission and raise exception if not authorized
        
        Args:
            user_role: User's role
            permission: Permission to check
            user_id: User ID for logging purposes
            
        Raises:
            HTTPException: If user doesn't have permission
            ValueError: If invalid parameters provided
        """
        # Input validation
        if user_role is None:
            raise ValueError("user_role cannot be None")
        
        if permission is None:
            raise ValueError("permission cannot be None")
        
        if user_role not in UserRole:
            raise ValueError(f"Invalid user_role: {user_role}")
        
        if permission not in Permission:
            raise ValueError(f"Invalid permission: {permission}")
        
        # Rate limiting check
        if user_id and not self._check_rate_limit(user_id, "permission_check"):
            logger.warning(
                "rate_limit_exceeded",
                user_id=user_id,
                operation="permission_check",
                severity="warning"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many permission checks. Please try again later."
                }
            )
        
        if not self.has_permission(user_role, permission):
            logger.warning(
                "access_denied_insufficient_permissions",
                user_id=user_id,
                user_role=user_role,
                required_permission=permission,
                severity="warning"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Access denied. Required permission: {permission.value}"
                }
            )
        
        logger.debug(
            "permission_granted",
            user_id=user_id,
            user_role=user_role,
            permission=permission,
            severity="debug"
        )
    
    async def check_data_ownership(self, user_role: UserRole, user_id: str, resource_user_id: str, resource_type: str = None):
        """
        Check data ownership and raise exception if not authorized
        
        Args:
            user_role: User's role
            user_id: Current user's ID
            resource_user_id: Owner ID of the resource
            resource_type: Type of resource for logging
            
        Raises:
            HTTPException: If user doesn't have access to resource
        """
        if not self.validate_data_ownership(user_role, user_id, resource_user_id):
            logger.warning(
                "access_denied_data_ownership",
                user_id=user_id,
                user_role=user_role,
                resource_user_id=resource_user_id,
                resource_type=resource_type,
                severity="warning"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCESS_DENIED",
                    "message": "You can only access your own resources"
                }
            )
        
        logger.debug(
            "data_access_granted",
            user_id=user_id,
            user_role=user_role,
            resource_user_id=resource_user_id,
            resource_type=resource_type,
            severity="debug"
        )

# Global RBAC manager instance
rbac_manager = RBACManager()

# Permission checking functions for common use cases
async def require_telemetry_access(user_role: UserRole, user_id: str):
    """Require telemetry access permission"""
    await rbac_manager.check_permission(user_role, Permission.READ_OWN_TELEMETRY, user_id)

async def require_device_management(user_role: UserRole, user_id: str):
    """Require device management permission"""
    await rbac_manager.check_permission(user_role, Permission.WRITE_OWN_DEVICES, user_id)

async def require_marketplace_access(user_role: UserRole, user_id: str):
    """Require marketplace access permission"""
    await rbac_manager.check_permission(user_role, Permission.READ_MARKETPLACE, user_id)

async def require_listing_management(user_role: UserRole, user_id: str):
    """Require listing management permission"""
    await rbac_manager.check_permission(user_role, Permission.WRITE_OWN_LISTINGS, user_id)

async def require_meal_management(user_role: UserRole, user_id: str):
    """Require meal management permission"""
    await rbac_manager.check_permission(user_role, Permission.WRITE_OWN_MEALS, user_id)

async def require_reservation_access(user_role: UserRole, user_id: str):
    """Require reservation access permission"""
    await rbac_manager.check_permission(user_role, Permission.READ_OWN_RESERVATIONS, user_id)

async def require_user_management(user_role: UserRole, user_id: str):
    """Require user management permission"""
    await rbac_manager.check_permission(user_role, Permission.READ_USERS, user_id)

async def require_system_access(user_role: UserRole, user_id: str):
    """Require system access permission"""
    await rbac_manager.check_permission(user_role, Permission.READ_SYSTEM, user_id)

async def require_admin_access(user_role: UserRole, user_id: str):
    """Require admin access permission"""
    if user_role != UserRole.ADMIN:
        logger.warning(
            "admin_access_denied",
            user_id=user_id,
            user_role=user_role,
            severity="warning"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ADMIN_ACCESS_REQUIRED",
                "message": "This endpoint requires ADMIN role"
            }
        )

async def require_account_blocking(user_role: UserRole, user_id: str):
    """Require account blocking permission"""
    await rbac_manager.check_permission(user_role, Permission.BLOCK_ACCOUNTS, user_id)

async def require_account_unblocking(user_role: UserRole, user_id: str):
    """Require account unblocking permission"""
    await rbac_manager.check_permission(user_role, Permission.UNBLOCK_ACCOUNTS, user_id)

async def require_block_extension(user_role: UserRole, user_id: str):
    """Require block extension permission"""
    await rbac_manager.check_permission(user_role, Permission.EXTEND_BLOCKS, user_id)

async def require_view_blocked_users(user_role: UserRole, user_id: str):
    """Require view blocked users permission"""
    await rbac_manager.check_permission(user_role, Permission.VIEW_BLOCKED_USERS, user_id)

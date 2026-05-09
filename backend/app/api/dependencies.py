"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Request, Depends
from supabase import Client

from app.core.security import jwt_manager
from app.core.database import get_supabase_client
from app.core.logging import logger
from app.core.permissions import (
    UserRole, Permission, rbac_manager,
    require_telemetry_access, require_device_management,
    require_marketplace_access, require_listing_management,
    require_meal_management, require_reservation_access,
    require_user_management, require_system_access,
    require_admin_access
)


async def get_current_user(
    request: Request,
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        request: FastAPI request object
        supabase: Supabase client
        
    Returns:
        User information from JWT token
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # Extract token from httpOnly cookie
    token = request.cookies.get("sb-access-token")
    
    if not token:
        logger.warning(
            "Authentication attempt without token",
            path=request.url.path,
            method=request.method
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "NOT_AUTHENTICATED",
                "message": "Authentication required"
            }
        )
    
    try:
        # Validate JWT token and extract user info
        user_info = jwt_manager.validate_jwt_token(token)
        
        logger.debug(
            "User authentication successful",
            user_id=user_info["user_id"],
            role=user_info["role"],
            path=request.url.path
        )
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user authentication",
            error=str(e),
            path=request.url.path
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_ERROR",
                "message": "Failed to authenticate user"
            }
        )


async def get_current_user_optional(
    request: Request,
    supabase: Client = Depends(get_supabase_client)
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user if authenticated
    
    Returns:
        User information if authenticated, None otherwise
    """
    try:
        return await get_current_user(request, supabase)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Dependency factory to require specific user role
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        if user_role != required_role:
            logger.warning(
                "Access denied: insufficient role",
                user_id=current_user["user_id"],
                user_role=user_role,
                required_role=required_role
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Access denied. Required role: {required_role}"
                }
            )
        
        return current_user
    
    return role_checker


def require_any_role(*allowed_roles: str):
    """
    Dependency factory to require any of the specified roles
    
    Args:
        allowed_roles: List of allowed user roles
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
            logger.warning(
                "Access denied: role not allowed",
                user_id=current_user["user_id"],
                user_role=user_role,
                allowed_roles=allowed_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
                }
            )
        
        return current_user
    
    return role_checker


# Enhanced RBAC dependencies with permission checking
def require_permission(permission: Permission):
    """
    Dependency factory to require specific permission
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function that checks user permission
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = UserRole(current_user.get("role"))
        user_id = current_user.get("user_id")
        
        await rbac_manager.check_permission(user_role, permission, user_id)
        return current_user
    
    return permission_checker

def require_any_permission(*permissions: Permission):
    """
    Dependency factory to require any of specified permissions
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Dependency function that checks user permissions
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = UserRole(current_user.get("role"))
        user_id = current_user.get("user_id")
        
        if not rbac_manager.has_any_permission(user_role, list(permissions)):
            logger.warning(
                "access_denied_insufficient_permissions",
                user_id=user_id,
                user_role=user_role,
                required_permissions=[p.value for p in permissions],
                severity="warning"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": f"Access denied. Required one of: {', '.join([p.value for p in permissions])}"
                }
            )
        
        return current_user
    
    return permission_checker

def require_data_ownership(resource_user_id_param: str = "resource_user_id"):
    """
    Dependency factory to require data ownership validation
    
    Args:
        resource_user_id_param: Parameter name containing resource owner ID
        
    Returns:
        Dependency function that checks data ownership
    """
    async def ownership_checker(
        request: Request,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = UserRole(current_user.get("role"))
        user_id = current_user.get("user_id")
        
        # Extract resource user ID from path params or query params
        resource_user_id = None
        if hasattr(request, 'path_params') and resource_user_id_param in request.path_params:
            resource_user_id = request.path_params[resource_user_id_param]
        elif hasattr(request, 'query_params') and resource_user_id_param in request.query_params:
            resource_user_id = request.query_params[resource_user_id_param]
        
        if resource_user_id:
            await rbac_manager.check_data_ownership(user_role, user_id, resource_user_id)
        
        return current_user
    
    return ownership_checker

# Permission-based dependencies
require_telemetry_permission = require_permission(Permission.READ_OWN_TELEMETRY)
require_device_permission = require_permission(Permission.WRITE_OWN_DEVICES)
require_alert_permission = require_permission(Permission.READ_OWN_ALERTS)
require_listing_permission = require_permission(Permission.WRITE_OWN_LISTINGS)
require_meal_permission = require_permission(Permission.WRITE_OWN_MEALS)
require_reservation_permission = require_permission(Permission.READ_OWN_RESERVATIONS)
require_user_read_permission = require_permission(Permission.READ_USERS)
require_user_write_permission = require_permission(Permission.WRITE_USERS)
require_system_permission = require_permission(Permission.READ_SYSTEM)

# Common role dependencies (backward compatibility)
require_farmer = require_role("FARMER")
require_restaurant = require_role("RESTAURANT")
require_citizen = require_role("CITIZEN")
require_admin = require_role("ADMIN")
require_support = require_role("SUPPORT")

# Multi-role dependencies
require_farmer_or_restaurant = require_any_role("FARMER", "RESTAURANT")
require_restaurant_or_citizen = require_any_role("RESTAURANT", "CITIZEN")
require_admin_or_support = require_any_role("ADMIN", "SUPPORT")
require_any_user_role = require_any_role("FARMER", "RESTAURANT", "CITIZEN", "ADMIN", "SUPPORT")

# Admin-only dependency with enhanced logging
async def require_admin_with_audit(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require admin role with audit logging"""
    user_role = UserRole(current_user.get("role"))
    user_id = current_user.get("user_id")
    
    await require_admin_access(user_role, user_id)
    
    # Log admin access for audit
    logger.info(
        "admin_access_granted",
        user_id=user_id,
        user_role=user_role,
        severity="info"
    )
    
    return current_user

# Support user dependency with read-only restrictions
async def require_support_readonly(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require support role with read-only access validation"""
    user_role = UserRole(current_user.get("role"))
    user_id = current_user.get("user_id")
    
    if user_role != UserRole.SUPPORT:
        logger.warning(
            "support_access_denied",
            user_id=user_id,
            user_role=user_role,
            severity="warning"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SUPPORT_ACCESS_REQUIRED",
                "message": "This endpoint requires SUPPORT role"
            }
        )
    
    logger.info(
        "support_access_granted",
        user_id=user_id,
        user_role=user_role,
        severity="info"
    )
    
    return current_user

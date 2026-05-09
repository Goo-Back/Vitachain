"""
Admin User Management API Routes
Handles all admin user management operations including search, filtering, status updates, and bulk operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import structlog
from datetime import datetime
from jose import JWTError

from app.core.config import settings
from app.core.database import get_supabase_client
from supabase import Client
from app.core.security import JWTManager
from app.middleware.rate_limiter import rate_limit
from app.models.schemas import (
    UserListResponse,
    UserStatus,
    AdminUserView,
    UserFilters,
    UserStatusUpdateRequest,
    UserRoleUpdateRequest,
    BulkUserUpdateRequest,
    BulkUserUpdateResponse,
    UserExportRequest,
    AdminAccessDeniedResponse,
    UserNotFoundAdminResponse,
    InvalidStatusTransitionResponse,
    BulkOperationFailedResponse,
    UserRole
)
from app.models.account_models import (
    AccountBlockRequest,
    AccountUnblockRequest,
    BlockExtensionRequest,
    BlockResponse,
    UnblockResponse,
    BlockExtensionResponse,
    BlockedUsersListResponse,
    BlockCleanupResponse
)
from app.services.admin_service import AdminUserService

logger = structlog.get_logger("admin_routes")

# Initialize router
router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate user ID from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User ID from JWT token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        user_info = JWTManager.validate_jwt_token(token)
        return user_info["user_id"]
    except JWTError as e:
        logger.warning("Invalid JWT token in admin request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AdminAccessDeniedResponse().error
        )
    except Exception as e:
        logger.error("Unexpected error during JWT validation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Extract complete user information from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Complete user information from JWT token
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        user_info = JWTManager.validate_jwt_token(token)
        return user_info
    except JWTError as e:
        logger.warning("Invalid JWT token in admin request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AdminAccessDeniedResponse().error
        )
    except Exception as e:
        logger.error("Unexpected error during JWT validation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


async def require_admin_role(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Validate that user has ADMIN role
    
    Args:
        current_user: Current user information from JWT
        
    Returns:
        Current user information if ADMIN role
        
    Raises:
        HTTPException: If user doesn't have ADMIN role
    """
    if current_user.get("role") != "ADMIN":
        logger.warning(
            "Non-admin user attempted admin access",
            user_id=current_user.get("user_id"),
            role=current_user.get("role")
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AdminAccessDeniedResponse().error
        )
    return current_user


@router.get("/users", response_model=UserListResponse)
@rate_limit(max_requests=50, window_seconds=60)
async def get_users(
    request: Request,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id),
    supabase_client = Depends(get_supabase_client)
) -> UserListResponse:
    """
    Get paginated list of users with search and filters
    
    Args:
        request: FastAPI request object
        page: Page number for pagination
        limit: Number of users per page
        search: Search term for email or name
        role: Filter by user role
        status: Filter by account status
        date_from: Filter users from date
        date_to: Filter users to date
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        UserListResponse with users, pagination, and stats
    """
    try:
        logger.info(
            "Admin user list request",
            admin_id=current_user["user_id"],
            page=page,
            limit=limit,
            search=search,
            role=role,
            status=status,
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Convert status string to enum if provided
        status_enum = None
        if status:
            from app.models.schemas import UserStatus
            try:
                status_enum = UserStatus(status)
            except ValueError:
                logger.warning("Invalid status filter", status=status)
                status_enum = None
        
        # Get users with filters
        result = await admin_service.get_users(
            page=page,
            limit=limit,
            search=search,
            role=role,
            status=status_enum,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info(
            "Admin user list retrieved successfully",
            admin_id=current_user["user_id"],
            user_count=len(result.users)
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in get_users",
            admin_id=current_user["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve users"
            }
        )


@router.get("/users/{user_id}", response_model=AdminUserView)
@rate_limit(max_requests=50, window_seconds=60)
async def get_user_details(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_admin_role),
    supabase_client: Client = Depends(get_supabase_client)
) -> AdminUserView:
    """
    Get detailed information about a specific user
    
    Args:
        user_id: UUID of the user
        request: FastAPI request object
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        AdminUserView with detailed user information
    """
    try:
        logger.info(
            "Admin user details request",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Get user details
        user_details = await admin_service.get_user_details(user_id)
        
        logger.info(
            "Admin user details retrieved successfully",
            admin_id=current_user["user_id"],
            target_user_id=user_id
        )
        
        return user_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in get_user_details",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve user details"
            }
        )


@router.patch("/users/{user_id}/status", response_model=dict)
@rate_limit(max_requests=50, window_seconds=60)
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role),
    supabase_client: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Update user account status
    
    Args:
        user_id: UUID of the user to update
        status_update: Status update request with new status and reason
        request: FastAPI request object
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success response with updated status
    """
    try:
        logger.info(
            "Admin user status update request",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            new_status=status_update.new_status,
            reason=status_update.reason,
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Update user status
        result = await admin_service.update_user_status(
            user_id=user_id,
            new_status=status_update.new_status,
            reason=status_update.reason,
            admin_id=current_user["user_id"]
        )
        
        logger.info(
            "Admin user status updated successfully",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            new_status=status_update.new_status
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in update_user_status",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to update user status"
            }
        )


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdateRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_admin_role),
    supabase_client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Update user role
    
    Args:
        user_id: UUID of the user to update
        role_update: Role update request with new role and reason
        request: FastAPI request object
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Success response with updated role
    """
    try:
        logger.info(
            "Admin user role update request",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            new_role=role_update.new_role,
            reason=role_update.reason,
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Update user role
        result = await admin_service.update_user_role(
            user_id=user_id,
            new_role=role_update.new_role,
            reason=role_update.reason,
            admin_id=current_user["user_id"]
        )
        
        logger.info(
            "Admin user role updated successfully",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            new_role=role_update.new_role
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in update_user_role",
            admin_id=current_user["user_id"],
            target_user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to update user role"
            }
        )


@router.post("/users/bulk-update", response_model=BulkUserUpdateResponse)
async def bulk_update_users(
    bulk_request: BulkUserUpdateRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_admin_role),
    supabase_client = Depends(get_supabase_client)
) -> BulkUserUpdateResponse:
    """
    Perform bulk operations on multiple users
    
    Args:
        bulk_request: Bulk update request with user IDs and action
        request: FastAPI request object
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        BulkUserUpdateResponse with operation results
    """
    try:
        logger.info(
            "Admin bulk user update request",
            admin_id=current_user["user_id"],
            action=bulk_request.action,
            user_count=len(bulk_request.user_ids),
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Perform bulk update
        result = await admin_service.bulk_update_users(
            bulk_request=bulk_request,
            admin_id=current_user["user_id"]
        )
        
        logger.info(
            "Admin bulk user update completed",
            admin_id=current_user["user_id"],
            action=bulk_request.action,
            updated_count=result.updated_count,
            failed_count=result.failed_count
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in bulk_update_users",
            admin_id=current_user["user_id"],
            action=bulk_request.action,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to perform bulk operation"
            }
        )


@router.post("/users/export", response_model=dict)
@rate_limit(max_requests=20, window_seconds=60)
async def export_users(
    export_request: UserExportRequest,
    current_user: Dict[str, Any] = Depends(require_admin_role),
    supabase_client: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Export user data in specified format
    
    Args:
        export_request: Export request with filters and format
        request: FastAPI request object
        current_user: Current admin user from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Export data or file information
    """
    try:
        logger.info(
            "Admin user export request",
            admin_id=current_user["user_id"],
            format=export_request.format,
            ip=request.client.host
        )
        
        # Initialize admin service
        admin_service = AdminUserService(supabase_client)
        
        # Export user data
        export_data = await admin_service.export_users(
            export_request=export_request,
            admin_id=current_user["user_id"]
        )
        
        logger.info(
            "Admin user export completed successfully",
            admin_id=current_user["user_id"],
            format=export_request.format
        )
        
        return {
            "message": "User data exported successfully",
            "format": export_request.format,
            "data": export_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error in export_users",
            admin_id=current_user["user_id"],
            format=export_request.format,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to export user data"
            }
        )


# Error handlers are handled at the main FastAPI app level







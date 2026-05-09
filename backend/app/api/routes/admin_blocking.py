"""
Admin Account Blocking API Routes
Handles all admin account blocking operations including block, unblock, extend, and cleanup
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import structlog
from datetime import datetime

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.security import JWTManager
from app.core.permissions import (
    require_account_blocking, require_account_unblocking, 
    require_block_extension, require_view_blocked_users,
    UserRole
)
from app.middleware.rate_limiter import rate_limit
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
from app.core.account_blocking import AccountBlockingService
from app.core.notification_service import NotificationService
from app.core.account_blocking_exceptions import (
    AccountBlockingError, UserNotFoundError, UserAlreadyBlockedError,
    UserNotBlockedError, InvalidBlockDurationError, InvalidBlockReasonError
)

logger = structlog.get_logger("admin_blocking_routes")

# Initialize router
router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()


async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                                 supabase_client = Depends(get_supabase_client)) -> Dict[str, Any]:
    """
    Get current admin user with role validation
    
    Args:
        credentials: HTTP Bearer credentials
        supabase_client: Supabase client
        
    Returns:
        Current user information with role
        
    Raises:
        HTTPException: If user is not found or doesn't have required role
    """
    try:
        token = credentials.credentials
        user_info = JWTManager.validate_jwt_token(token)
        user_id = user_info["user_id"]
        
        # Get user role from database
        result = supabase_client.table("profiles").select("role").eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "USER_NOT_FOUND", "message": "User not found"}
            )
        
        user_role_str = result.data[0].get("role")
        user_role = UserRole(user_role_str) if user_role_str else None
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "INVALID_ROLE", "message": "Invalid user role"}
            )
        
        return {
            "user_id": user_id,
            "role": user_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Invalid JWT token in admin request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid authentication token"}
        )


@router.post("/users/{user_id}/block", response_model=BlockResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def block_user_account(
    user_id: str,
    block_request: AccountBlockRequest,
    current_user: Dict[str, Any] = Depends(get_current_admin_user),
    supabase_client = Depends(get_supabase_client)
) -> BlockResponse:
    """
    Block a user account temporarily
    
    Args:
        user_id: ID of user to block
        block_request: Block details including reason and duration
        current_user: Current admin user
        supabase_client: Supabase client
        
    Returns:
        Block details
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Check permissions
        await require_account_blocking(current_user["role"], current_user["user_id"])
        
        # Initialize services
        notification_service = NotificationService(supabase_client)
        blocking_service = AccountBlockingService(supabase_client, notification_service)
        
        # Block the user
        result = await blocking_service.block_user(
            user_id=user_id,
            blocked_by=current_user["user_id"],
            block_reason=block_request.block_reason,
            duration_hours=block_request.duration_hours,
            auto_block=block_request.auto_block
        )
        
        logger.info(
            "admin_blocked_user",
            admin_id=current_user["user_id"],
            user_id=user_id,
            block_reason=block_request.block_reason,
            duration_hours=block_request.duration_hours
        )
        
        return BlockResponse(**result)
        
    except (UserNotFoundError, UserAlreadyBlockedError, InvalidBlockDurationError, InvalidBlockReasonError) as e:
        logger.warning(
            "block_user_validation_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": e.error_code,
                "message": str(e),
                "details": e.details
            }
        )
    except AccountBlockingError as e:
        logger.error(
            "block_user_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": e.error_code,
                "message": "Failed to block user account"
            }
        )
    except Exception as e:
        logger.error(
            "block_user_unexpected_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


@router.post("/users/{user_id}/unblock", response_model=UnblockResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def unblock_user_account(
    user_id: str,
    unblock_request: AccountUnblockRequest,
    current_user: Dict[str, Any] = Depends(get_current_admin_user),
    supabase_client = Depends(get_supabase_client)
) -> UnblockResponse:
    """
    Unblock a user account
    
    Args:
        user_id: ID of user to unblock
        unblock_request: Unblock reason
        current_user: Current admin user
        supabase_client: Supabase client
        
    Returns:
        Unblock details
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Check permissions
        await require_account_unblocking(current_user["role"], current_user["user_id"])
        
        # Initialize services
        notification_service = NotificationService(supabase_client)
        blocking_service = AccountBlockingService(supabase_client, notification_service)
        
        # Unblock user
        result = await blocking_service.unblock_user(
            user_id=user_id,
            unblocked_by=current_user["user_id"],
            unblock_reason=unblock_request.unblock_reason
        )
        
        logger.info(
            "user_unblocked_successfully",
            user_id=user_id,
            unblocked_by=current_user["user_id"],
            previous_block_id=result["previous_block_id"]
        )
        
        return UnblockResponse(**result)
        
    except (UserNotFoundError, UserNotBlockedError) as e:
        logger.warning(
            "unblock_user_validation_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": e.error_code,
                "message": str(e),
                "details": e.details
            }
        )
    except AccountBlockingError as e:
        logger.error(
            "unblock_user_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": e.error_code,
                "message": "Failed to unblock user account"
            }
        )
    except Exception as e:
        logger.error(
            "unblock_user_unexpected_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


@router.get("/users/blocked", response_model=BlockedUsersListResponse)
@rate_limit(max_requests=20, window_seconds=60)
async def get_blocked_users(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_admin_user),
    supabase_client = Depends(get_supabase_client)
) -> BlockedUsersListResponse:
    """
    Get list of blocked users
    
    Args:
        limit: Maximum number of results to return
        offset: Number of results to skip
        current_user: Current admin user
        supabase_client: Supabase client
        
    Returns:
        List of blocked users with pagination
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Check permissions
        await require_view_blocked_users(current_user["role"], current_user["user_id"])
        
        # Initialize services
        notification_service = NotificationService(supabase_client)
        blocking_service = AccountBlockingService(supabase_client, notification_service)
        
        # Get blocked users
        result = await blocking_service.get_blocked_users(limit=limit, offset=offset)
        
        logger.info(
            "blocked_users_listed",
            admin_id=current_user["user_id"],
            total=result["total"],
            limit=limit,
            offset=offset
        )
        
        return BlockedUsersListResponse(**result)
        
    except AccountBlockingError as e:
        logger.error(
            "get_blocked_users_error",
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": e.error_code,
                "message": "Failed to retrieve blocked users"
            }
        )
    except Exception as e:
        logger.error(
            "get_blocked_users_unexpected_error",
            admin_id=current_user["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


@router.post("/users/{user_id}/block/extend", response_model=BlockExtensionResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def extend_user_block(
    user_id: str,
    extend_request: BlockExtensionRequest,
    current_user: Dict[str, Any] = Depends(get_current_admin_user),
    supabase_client = Depends(get_supabase_client)
) -> BlockExtensionResponse:
    """
    Extend a user's block duration
    
    Args:
        user_id: ID of user whose block to extend
        extend_request: Extension details
        current_user: Current admin user
        supabase_client: Supabase client
        
    Returns:
        Extension details
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Check permissions
        await require_block_extension(current_user["role"], current_user["user_id"])
        
        # Initialize services
        notification_service = NotificationService(supabase_client)
        blocking_service = AccountBlockingService(supabase_client, notification_service)
        
        # Extend block
        result = await blocking_service.extend_block(
            user_id=user_id,
            extended_by=current_user["user_id"],
            additional_hours=extend_request.additional_hours,
            extension_reason=extend_request.extension_reason
        )
        
        logger.info(
            "user_block_extended",
            admin_id=current_user["user_id"],
            user_id=user_id,
            additional_hours=extend_request.additional_hours,
            extension_reason=extend_request.extension_reason
        )
        
        return BlockExtensionResponse(**result)
        
    except (UserNotFoundError, UserNotBlockedError, InvalidBlockDurationError) as e:
        logger.warning(
            "extend_block_validation_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": e.error_code,
                "message": str(e),
                "details": e.details
            }
        )
    except AccountBlockingError as e:
        logger.error(
            "extend_block_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error_code=e.error_code,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": e.error_code,
                "message": "Failed to extend user block"
            }
        )
    except Exception as e:
        logger.error(
            "extend_block_unexpected_error",
            user_id=user_id,
            admin_id=current_user["user_id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


@router.post("/internal/blocks/cleanup", response_model=BlockCleanupResponse)
@rate_limit(max_requests=5, window_seconds=60)
async def cleanup_expired_blocks(
    supabase_client = Depends(get_supabase_client)
) -> BlockCleanupResponse:
    """
    Internal endpoint to process expired blocks
    Called by background scheduler
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        Cleanup results
        
    Raises:
        HTTPException: If operation fails
    """
    try:
        # Initialize blocking service
        notification_service = NotificationService(supabase_client)
        blocking_service = AccountBlockingService(supabase_client, notification_service)
        
        # Clean up expired blocks
        cleaned_count = await blocking_service.cleanup_expired_blocks()
        
        logger.info(
            "block_cleanup_completed",
            cleaned_blocks=cleaned_count
        )
        
        return BlockCleanupResponse(
            cleaned_blocks=cleaned_count,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(
            "cleanup_expired_blocks_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "CLEANUP_FAILED", "message": str(e)}
        )

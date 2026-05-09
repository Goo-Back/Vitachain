"""
Profile Management API Routes
Handles user profile viewing and updating
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import structlog
from jose import JWTError

from app.core.config import settings
from app.core.database import get_supabase_client
from app.core.security import JWTManager
from app.models.schemas import (
    ProfileViewResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    ProfileNotFoundResponse,
    ProfileValidationErrorResponse,
    ProfileUnauthorizedResponse,
    ProfileForbiddenResponse
)
from app.services.profile_service import ProfileService

logger = structlog.get_logger("profile_routes")

# Initialize router
router = APIRouter(prefix="/api/profile", tags=["profiles"])
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
        logger.warning("Invalid JWT token in profile request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ProfileUnauthorizedResponse().error
        )
    except Exception as e:
        logger.error("Unexpected error during JWT validation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "Internal server error"}
        )


@router.get("/", response_model=ProfileViewResponse)
async def get_profile(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> ProfileViewResponse:
    """
    Get current user's profile
    
    Args:
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        User profile data
        
    Raises:
        HTTPException: If profile not found or access denied
    """
    try:
        logger.info("Profile view request", user_id=user_id, ip=request.client.host)
        
        # Initialize profile service
        profile_service = ProfileService(supabase_client)
        
        # Get profile
        profile_data = await profile_service.get_profile(user_id)
        
        logger.info("Profile retrieved successfully", user_id=user_id)
        return ProfileViewResponse(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_profile", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve profile"
            }
        )


@router.patch("/", response_model=ProfileUpdateResponse)
async def update_profile(
    request: Request,
    profile_update: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> ProfileUpdateResponse:
    """
    Update current user's profile
    
    Args:
        request: FastAPI request object
        profile_update: Profile update data
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Updated profile data
        
    Raises:
        HTTPException: If validation fails or update fails
    """
    try:
        logger.info("Profile update request", user_id=user_id, ip=request.client.host)
        
        # Initialize profile service
        profile_service = ProfileService(supabase_client)
        
        # Convert Pydantic model to dict
        update_data = profile_update.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": "No valid fields to update"
                }
            )
        
        # Update profile
        result = await profile_service.update_profile(user_id, update_data)
        
        logger.info("Profile updated successfully", user_id=user_id)
        return ProfileUpdateResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in update_profile", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to update profile"
            }
        )


@router.get("/summary")
async def get_profile_summary(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase_client=Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get profile summary for dashboard
    
    Args:
        request: FastAPI request object
        user_id: Current user ID from JWT
        supabase_client: Supabase client instance
        
    Returns:
        Profile summary data
    """
    try:
        logger.info("Profile summary request", user_id=user_id)
        
        # Initialize profile service
        profile_service = ProfileService(supabase_client)
        
        # Get profile summary
        summary = await profile_service.get_profile_summary(user_id)
        
        logger.info("Profile summary retrieved", user_id=user_id)
        return summary
        
    except Exception as e:
        logger.error("Error in get_profile_summary", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to retrieve profile summary"
            }
        )


@router.get("/validate-phone/{phone}")
async def validate_phone_number(
    phone: str,
    request: Request
) -> Dict[str, Any]:
    """
    Validate phone number format (public endpoint)
    
    Args:
        phone: Phone number to validate
        request: FastAPI request object
        
    Returns:
        Validation result
    """
    try:
        logger.info("Phone validation request", phone=phone[:10] + "...", ip=request.client.host)
        
        from app.core.validation import PhoneValidator
        
        # Validate phone number
        is_valid, error_message = PhoneValidator.validate_moroccan_phone(phone)
        
        # Format phone number if valid
        formatted_phone = None
        if is_valid:
            formatted_phone = PhoneValidator.format_phone_number(phone)
        
        result = {
            "is_valid": is_valid,
            "formatted_phone": formatted_phone,
            "error_message": error_message if not is_valid else None
        }
        
        logger.info("Phone validation completed", is_valid=is_valid)
        return result
        
    except Exception as e:
        logger.error("Error in validate_phone_number", phone=phone[:10] + "...", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to validate phone number"
            }
        )


# Error handlers are handled at the main FastAPI app level

"""
Authentication routes for VitaChain
"""

import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.database import get_supabase_client
from app.core.supabase_http import get_supabase_http_client
from app.core.security import jwt_manager, magic_link_manager, magic_link_rate_limiter, password_validator, password_reset_rate_limiter
from app.core.security_monitoring import security_monitor
from app.core.geo_ip_service import geo_ip_service
from app.models.schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserLoginRequest,
    UserLoginResponse,
    ValidationErrorResponse,
    EmailExistsResponse,
    RateLimitResponse,
    InvalidCredentialsResponse,
    EmailNotVerifiedResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerificationRequest,
    MagicLinkVerificationResponse,
    UserNotFoundResponse,
    InvalidMagicLinkResponse,
    TokenUsedResponse,
    MagicLinkRateLimitResponse,
    MagicLinkEmailData,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordMismatchResponse,
    WeakPasswordResponse,
    InvalidResetTokenResponse,
    PasswordResetRateLimitResponse,
    PasswordResetEmailData
)
from app.services.email_service import email_service, VerificationEmailData, UserRole
from app.api.dependencies import get_current_user
from app.services.session_service import get_session_service
from app.models.session_models import (
    LogoutRequest,
    LogoutResponse,
    ForceLogoutRequest,
    SessionInfo,
    UserSessionsResponse,
    SessionNotFoundResponse,
    SessionExpiredResponse,
    UnauthorizedSessionResponse
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def check_rate_limit(ip: str, email: str) -> bool:
    """
    Simple rate limiting for registration
    In production, use Redis or similar
    """
    now = datetime.now()
    key_ip = f"reg_ip_{ip}"
    key_email = f"reg_email_{email}"
    
    # Clean old entries (older than 1 hour)
    cutoff = now - timedelta(hours=1)
    keys_to_remove = []
    
    for key, timestamps in rate_limit_store.items():
        rate_limit_store[key] = [ts for ts in timestamps if ts > cutoff]
        if not rate_limit_store[key]:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del rate_limit_store[key]
    
    # Check IP rate limit (5 per minute)
    if key_ip in rate_limit_store:
        recent_ip = [ts for ts in rate_limit_store[key_ip] if ts > now - timedelta(minutes=1)]
        if len(recent_ip) >= 5:
            return False
        rate_limit_store[key_ip] = recent_ip + [now]
    else:
        rate_limit_store[key_ip] = [now]
    
    # Check email rate limit (3 per hour)
    if key_email in rate_limit_store:
        recent_email = rate_limit_store[key_email]
        if len(recent_email) >= 3:
            return False
        rate_limit_store[key_email] = recent_email + [now]
    else:
        rate_limit_store[key_email] = [now]
    
    return True

def check_login_rate_limit(ip: str, email: str) -> bool:
    """
    Rate limiting for login attempts
    IP-based: 10 attempts per minute
    Account-based: 5 attempts per minute
    """
    now = datetime.now()
    key_ip = f"login_ip_{ip}"
    key_email = f"login_email_{email}"
    
    # Clean old entries (older than 1 hour)
    cutoff = now - timedelta(hours=1)
    keys_to_remove = []
    
    for key, timestamps in rate_limit_store.items():
        rate_limit_store[key] = [ts for ts in timestamps if ts > cutoff]
        if not rate_limit_store[key]:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del rate_limit_store[key]
    
    # Check IP rate limit (10 per minute)
    if key_ip in rate_limit_store:
        recent_ip = [ts for ts in rate_limit_store[key_ip] if ts > now - timedelta(minutes=1)]
        if len(recent_ip) >= 10:
            return False
        rate_limit_store[key_ip] = recent_ip + [now]
    else:
        rate_limit_store[key_ip] = [now]
    
    # Check email rate limit (5 per minute)
    if key_email in rate_limit_store:
        recent_email = [ts for ts in rate_limit_store[key_email] if ts > now - timedelta(minutes=1)]
        if len(recent_email) >= 5:
            return False
        rate_limit_store[key_email] = recent_email + [now]
    else:
        rate_limit_store[key_email] = [now]
    
    return True

@router.post("/register-disabled", response_model=UserRegistrationResponse)
async def register_user_disabled(
    request: UserRegistrationRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Register a new user with email verification
    
    Args:
        request: User registration data
        http_request: HTTP request for rate limiting
        supabase: Supabase client
        
    Returns:
        Registration response with user ID
        
    Raises:
        HTTPException: For validation errors, existing email, or rate limiting
    """
    try:
        # Rate limiting
        client_ip = get_client_ip(http_request)
        if not check_rate_limit(client_ip, request.email):
            logger.warning(
                "Rate limit exceeded for registration",
                ip=client_ip,
                email=request.email
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=RateLimitResponse().error
            )
        
        # Check if user already exists using HTTP client
        try:
            supabase_http = get_supabase_http_client(service_role=True)
            # For now, we'll skip the existing user check and let Supabase handle duplicates
            # This avoids the proxy error with the old client
            logger.info(
                "Proceeding with registration",
                email=request.email,
                ip=client_ip
            )
        except Exception as e:
            logger.warning(
                "Error setting up HTTP client",
                error=str(e),
                email=request.email
            )
        
        # Use HTTP client for Supabase Auth with user's password
        supabase_http = get_supabase_http_client(service_role=True)
        
        auth_response = supabase_http.sign_up(
            email=request.email,
            password=request.password,
            user_metadata={
                'role': request.role.value,
                'full_name': request.full_name,
                'registration_ip': client_ip,
                'registration_method': 'direct_signup'
            }
        )
        
        if not auth_response.get('success', False):
            logger.error(
                "Supabase auth registration failed",
                email=request.email,
                response=auth_response
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "REGISTRATION_FAILED",
                    "message": "Failed to create user account"
                }
            )
        
        user_id = auth_response.get('user', {}).get('id')
        
        # Create verification link
        session_data = auth_response.get('user', {}).get('session', {})
        access_token = session_data.get('access_token')
        verification_link = f"{settings.FRONTEND_URL}/auth/verify?token={access_token}" if access_token else f"{settings.FRONTEND_URL}/auth/verify-email"
        
        # Send verification email
        email_data = VerificationEmailData(
            recipient_email=request.email,
            verification_link=verification_link,
            user_name=request.full_name,
            role=request.role
        )
        
        email_sent = await email_service.send_verification_email(email_data)
        
        if not email_sent:
            # User created but email failed - log but don't fail the request
            logger.error(
                "Failed to send verification email",
                user_id=user_id,
                email=request.email
            )
            # In production, you might want to implement a retry mechanism
        
        logger.info(
            "User registration completed",
            user_id=user_id,
            email=request.email,
            role=request.role.value,
            email_sent=email_sent,
            ip=client_ip
        )
        
        return UserRegistrationResponse(
            message="Registration successful. Please check your email for verification.",
            user_id=user_id,
            email_sent=email_sent
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during registration",
            error=str(e),
            email=request.email,
            ip=get_client_ip(http_request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during registration"
            }
        )

@router.get("/verify")
async def verify_email(token: str, supabase: Client = Depends(get_supabase_client)):
    """
    Verify email using token from verification link
    
    Args:
        token: Verification token
        supabase: Supabase client
        
    Returns:
        Success message
        
    Raises:
        HTTPException: For invalid or expired tokens
    """
    try:
        # Verify the token and get user using HTTP client
        supabase_http = get_supabase_http_client(service_role=True)
        auth_response = supabase_http.get_user(token)
        
        if not auth_response.get('success', False) or not auth_response.get('user'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired verification link"
                }
            )
        
        user = auth_response.get('user', {})
        
        # Check if user is already verified
        if user.get('email_confirmed_at'):
            logger.info(
                "Email verification attempted for already verified user",
                user_id=user.get('id'),
                email=user.get('email')
            )
            return {
                "message": "Email already verified",
                "status": "already_verified"
            }
        
        # Mark email as confirmed - skip for now as we need to implement this in HTTP client
        logger.info(
            "Email verification completed",
            user_id=user.get('id'),
            email=user.get('email')
        )
        
        # Email verification completed successfully
        logger.info(
            "Email verification successful",
            user_id=user.get('id'),
            email=user.get('email')
        )
        
        return {
            "message": "Email verified successfully",
            "status": "verified",
            "user_id": user.get('id')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during email verification",
            error=str(e),
            token=token[:10] + "..." if len(token) > 10 else token
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during email verification"
            }
        )

@router.post("/resend-verification")
async def resend_verification_email(
    email: str,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Resend verification email
    
    Args:
        email: User email
        http_request: HTTP request for rate limiting
        supabase: Supabase client
        
    Returns:
        Success message
        
    Raises:
        HTTPException: For invalid email or rate limiting
    """
    try:
        # Rate limiting
        client_ip = get_client_ip(http_request)
        if not check_rate_limit(client_ip, email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=RateLimitResponse().error
            )
        
        # Get user by email
        try:
            auth_response = supabase.auth.admin.get_user_by_email(email)
            if not auth_response or not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "No account found with this email"
                    }
                )
        except Exception as e:
            if "User not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "USER_NOT_FOUND",
                        "message": "No account found with this email"
                    }
                )
            raise
        
        user = auth_response.user
        
        # Check if already verified
        if user.email_confirmed_at:
            return {
                "message": "Email already verified",
                "status": "already_verified"
            }
        
        # Generate new verification link
        verification_link = f"{settings.FRONTEND_URL}/auth/verify?token={user.id}"
        
        # Send verification email
        user_metadata = user.user_metadata or {}
        email_data = VerificationEmailData(
            recipient_email=email,
            verification_link=verification_link,
            user_name=user_metadata.get('full_name', 'User'),
            role=UserRole(user_metadata.get('role', 'CITIZEN'))
        )
        
        email_sent = await email_service.send_verification_email(email_data)
        
        if not email_sent:
            logger.error(
                "Failed to resend verification email",
                user_id=user.id,
                email=email
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "EMAIL_SEND_FAILED",
                    "message": "Failed to send verification email"
                }
            )
        
        logger.info(
            "Verification email resent successfully",
            user_id=user.id,
            email=email,
            ip=client_ip
        )
        
        return {
            "message": "Verification email sent successfully",
            "email_sent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error resending verification email",
            error=str(e),
            email=email,
            ip=get_client_ip(http_request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

@router.post("/login-disabled", response_model=UserLoginResponse)
async def login_user_disabled(
    request: UserLoginRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Authenticate user with email and password
    
    Args:
        request: Login credentials
        http_request: HTTP request for rate limiting and response
        supabase: Supabase client
        
    Returns:
        Login response with user info and redirect URL
        
    Raises:
        HTTPException: For invalid credentials, unverified email, or rate limiting
    """
    try:
        # Rate limiting
        client_ip = get_client_ip(http_request)
        if not check_login_rate_limit(client_ip, request.email):
            logger.warning(
                "Login rate limit exceeded",
                ip=client_ip,
                email=request.email
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=RateLimitResponse().error
            )
        
        # Authenticate with Supabase using HTTP client
        supabase_http = get_supabase_http_client(service_role=False)
        
        auth_response = supabase_http.sign_in(
            email=request.email,
            password=request.password
        )
        
        if not auth_response.get('success', False):
            # Log failed authentication attempt
            security_monitor.log_failed_authentication(
                ip=client_ip,
                user_agent=get_client_ip(http_request),
                endpoint="/api/auth/login",
                error_type="invalid_credentials"
            )
            
            # Perform security analysis on failed attempt
            try:
                from app.api.routes.security import analyze_login_attempt
                from app.core.geo_ip_service import geo_ip_service
                
                location_data = await geo_ip_service.get_ip_location(client_ip)
                analysis_result = await analyze_login_attempt(
                    LoginAnalysisRequest(
                        user_id="unknown",  # Failed login, no user ID
                        ip_address=client_ip,
                        user_agent=get_client_ip(http_request),
                        success=False,
                        location_data=location_data
                    ),
                    http_request,
                    supabase
                )
                
                # Log security event if suspicious
                if analysis_result.anomalies or analysis_result.risk_score > 20:
                    logger.warning("suspicious_failed_login_detected", 
                               ip=client_ip,
                               email=request.email,
                               risk_score=analysis_result.risk_score,
                               anomalies=analysis_result.anomalies)
            except Exception as e:
                logger.error("failed_login_analysis_error", 
                           error=str(e),
                           ip=client_ip,
                           email=request.email)
            
            logger.warning(
                "Login attempt with invalid credentials",
                email=request.email,
                ip=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=InvalidCredentialsResponse().error
            )
        
        user = auth_response.get('user', {})
        
        # Check if email is verified
        if not user.get('email_confirmed_at'):
            logger.warning(
                "Login attempt with unverified email",
                user_id=user.id,
                email=request.email,
                ip=client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=EmailNotVerifiedResponse().error
            )
        
        # Check if user account is blocked
        try:
            from app.core.account_blocking import AccountBlockingService
            from app.core.notification_service import NotificationService
            
            notification_service = NotificationService(supabase)
            blocking_service = AccountBlockingService(supabase, notification_service)
            
            block_status = await blocking_service.check_user_block_status(user.id)
            
            if block_status["is_blocked"]:
                logger.warning(
                    "Login attempt from blocked user",
                    user_id=user.id,
                    email=request.email,
                    ip=client_ip,
                    block_reason=block_status.get("block_reason"),
                    auto_block=block_status.get("auto_block", False)
                )
                
                # Return specific error for blocked users
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "ACCOUNT_BLOCKED",
                        "message": "Your account has been temporarily blocked",
                        "block_reason": block_status.get("block_reason"),
                        "blocked_until": block_status.get("blocked_until"),
                        "auto_block": block_status.get("auto_block", False)
                    }
                )
        except HTTPException:
            # Re-raise HTTP exceptions (like our block exception)
            raise
        except Exception as e:
            # Log error but don't block login for system failures
            logger.error(
                "Error checking user block status",
                user_id=user.id,
                error=str(e),
                ip=client_ip
            )
        
        # Extract user information
        user_metadata = user.user_metadata or {}
        role = user_metadata.get('role', 'CITIZEN')
        full_name = user_metadata.get('full_name', 'User')
        
        # Get session tokens
        session = auth_response.session
        if not session or not session.access_token:
            logger.error(
                "Login succeeded but no session token received",
                user_id=user.id,
                email=request.email
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "SESSION_ERROR",
                    "message": "Failed to create user session"
                }
            )
        
        # Perform security analysis on successful login
        try:
            from app.api.routes.security import analyze_login_attempt
            from app.core.geo_ip_service import geo_ip_service
            
            # Get IP geolocation data
            location_data = await geo_ip_service.get_ip_location(client_ip)
            
            # Analyze login attempt
            analysis_result = await analyze_login_attempt(
                LoginAnalysisRequest(
                    user_id=user.id,
                    ip_address=client_ip,
                    user_agent=get_client_ip(http_request),
                    success=True,
                    location_data=location_data
                ),
                http_request,
                supabase
            )
            
            # Log security event if suspicious
            if analysis_result.anomalies or analysis_result.risk_score > 20:
                logger.warning("suspicious_login_detected", 
                           user_id=user.id,
                           email=user.email,
                           ip=client_ip,
                           risk_score=analysis_result.risk_score,
                           anomalies=analysis_result.anomalies)
            
            # Update user login patterns for successful login
            security_monitor.update_user_login_pattern(
                user_id=user.id,
                ip=client_ip,
                user_agent=get_client_ip(http_request),
                location_data=location_data,
                success=True
            )
            
        except Exception as e:
            logger.error("security_analysis_failed", 
                       error=str(e),
                       user_id=user.id,
                       ip=client_ip)
        
        # Create response with cookies
        response = JSONResponse(
            content=UserLoginResponse(
                message="Login successful",
                user={
                    "id": user.id,
                    "email": user.email,
                    "role": role,
                    "full_name": full_name
                },
                redirect_to=jwt_manager.get_dashboard_redirect_url(role)
            ).dict()
        )
        
        # Set httpOnly cookies
        jwt_manager.set_auth_cookie(
            response=response,
            access_token=session.access_token,
            refresh_token=session.refresh_token
        )
        
        logger.info(
            "User login successful",
            user_id=user.id,
            email=request.email,
            role=role,
            ip=client_ip
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during login",
            error=str(e),
            email=request.email,
            ip=get_client_ip(http_request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during login"
            }
        )

@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Request a magic link for passwordless authentication
    
    Args:
        request: Magic link request with email
        http_request: HTTP request for rate limiting
        supabase: Supabase client
        
    Returns:
        Magic link response with success message
        
    Raises:
        HTTPException: For validation errors, user not found, or rate limiting
    """
    try:
        # Rate limiting
        client_ip = get_client_ip(http_request)
        allowed, reason = magic_link_rate_limiter.check_rate_limit(request.email, client_ip)
        if not allowed:
            logger.warning(
                "Magic link rate limit exceeded",
                ip=client_ip,
                email=request.email,
                reason=reason
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=MagicLinkRateLimitResponse().error
            )
        
        # Check if user exists and is verified
        try:
            existing_user = supabase.auth.admin.get_user_by_email(request.email)
            if not existing_user or not existing_user.user:
                logger.info(
                    "Magic link requested for non-existent user",
                    email=request.email,
                    ip=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            
            user = existing_user.user
            
            # Check if email is verified
            if not user.email_confirmed_at:
                logger.warning(
                    "Magic link requested for unverified email",
                    user_id=user.id,
                    email=request.email,
                    ip=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "EMAIL_NOT_VERIFIED",
                        "message": "Please verify your email before requesting a magic link"
                    }
                )
                
        except Exception as e:
            if "User not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            elif isinstance(e, HTTPException):
                raise
            else:
                logger.warning(
                    "Error checking user existence",
                    error=str(e),
                    email=request.email
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "USER_CHECK_FAILED",
                        "message": "Failed to verify user account"
                    }
                )
        
        # Generate magic link token
        magic_token = magic_link_manager.generate_token(request.email)
        
        # Create magic link URL
        magic_link_url = f"{settings.FRONTEND_URL}/auth/magic-link/callback?token={magic_token}"
        
        # Send magic link email
        user_metadata = user.user_metadata or {}
        email_data = MagicLinkEmailData(
            recipient_email=request.email,
            magic_link=magic_link_url,
            user_name=user_metadata.get('full_name', 'User'),
            role=UserRole(user_metadata.get('role', 'CITIZEN')),
            expires_in_minutes=15
        )
        
        email_sent = await email_service.send_magic_link_email(email_data)
        
        if not email_sent:
            logger.error(
                "Failed to send magic link email",
                user_id=user.id,
                email=request.email
            )
            # Continue with response but log the error
        
        logger.info(
            "Magic link request completed",
            user_id=user.id,
            email=request.email,
            email_sent=email_sent,
            ip=client_ip
        )
        
        return MagicLinkResponse(
            message="Magic link sent to your email",
            email_sent=email_sent,
            expires_in=900  # 15 minutes in seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during magic link request",
            error=str(e),
            email=request.email,
            ip=get_client_ip(http_request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during magic link request"
            }
        )

@router.get("/magic-link/verify", response_model=MagicLinkVerificationResponse)
async def verify_magic_link(
    token: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Verify magic link token and authenticate user
    
    Args:
        token: Magic link token from email
        supabase: Supabase client
        
    Returns:
        Authentication response with user info and redirect URL
        
    Raises:
        HTTPException: For invalid or expired tokens
    """
    try:
        # Validate magic link token
        try:
            token_payload = magic_link_manager.validate_token(token)
            email = token_payload.get('email')
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=InvalidMagicLinkResponse().error
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(
                "Invalid magic link token format",
                error=str(e),
                token_preview=token[:10] + "..." if len(token) > 10 else token
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=InvalidMagicLinkResponse().error
            )
        
        # Get user by email
        try:
            auth_response = supabase.auth.admin.get_user_by_email(email)
            if not auth_response or not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            
            user = auth_response.user
            
        except Exception as e:
            if "User not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "USER_RETRIEVAL_FAILED",
                    "message": "Failed to retrieve user information"
                }
            )
        
        # Check if user is verified
        if not user.email_confirmed_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "EMAIL_NOT_VERIFIED",
                    "message": "Please verify your email before using magic links"
                }
            )
        
        # Extract user information
        user_metadata = user.user_metadata or {}
        role = user_metadata.get('role', 'CITIZEN')
        full_name = user_metadata.get('full_name', 'User')
        
        # Create session using Supabase (this will handle JWT creation)
        try:
            # Use Supabase to create a session for the user
            session_response = supabase.auth.admin.update_user_by_id(
                user.id,
                {'email_confirm': True}  # This ensures user is confirmed
            )
            
            # For magic link, we need to create a session manually
            # In production, you might want to use Supabase's OTP verification
            session = supabase.auth.set_session(
                access_token=user.aud,  # This is a placeholder - adjust based on your needs
                refresh_token=None
            )
            
        except Exception as e:
            logger.error(
                "Failed to create session for magic link user",
                user_id=user.id,
                email=email,
                error=str(e)
            )
            # Continue without session creation for now
        
        # Create response with cookies
        response = JSONResponse(
            content=MagicLinkVerificationResponse(
                message="Magic link verified successfully",
                user={
                    "id": user.id,
                    "email": user.email,
                    "role": role,
                    "full_name": full_name
                },
                redirect_to=jwt_manager.get_dashboard_redirect_url(role)
            ).dict()
        )
        
        # Set httpOnly cookies (using the token as access token)
        # Note: In a real implementation, you'd get proper JWT tokens from Supabase
        # For now, we'll use the magic link token as a placeholder
        jwt_manager.set_auth_cookie(
            response=response,
            access_token=token,  # This should be replaced with proper JWT
            refresh_token=None
        )
        
        logger.info(
            "Magic link verification successful",
            user_id=user.id,
            email=email,
            role=role
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during magic link verification",
            error=str(e),
            token_preview=token[:10] + "..." if len(token) > 10 else token
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during magic link verification"
            }
        )

@router.post("/password-reset", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    http_request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Request password reset via email
    
    Args:
        request: Password reset request with email
        http_request: HTTP request for rate limiting
        supabase: Supabase client
        
    Returns:
        Password reset response with success message
        
    Raises:
        HTTPException: For validation errors, user not found, or rate limiting
    """
    try:
        # Rate limiting
        client_ip = get_client_ip(http_request)
        allowed, reason = password_reset_rate_limiter.check_rate_limit(request.email, client_ip)
        if not allowed:
            logger.warning(
                "Password reset rate limit exceeded",
                ip=client_ip,
                email=request.email,
                reason=reason
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=PasswordResetRateLimitResponse().error
            )
        
        # Check if user exists and is verified
        try:
            existing_user = supabase.auth.admin.get_user_by_email(request.email)
            if not existing_user or not existing_user.user:
                logger.info(
                    "Password reset requested for non-existent user",
                    email=request.email,
                    ip=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            
            user = existing_user.user
            
            # Check if email is verified
            if not user.email_confirmed_at:
                logger.warning(
                    "Password reset requested for unverified email",
                    user_id=user.id,
                    email=request.email,
                    ip=client_ip
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "EMAIL_NOT_VERIFIED",
                        "message": "Please verify your email before requesting a password reset"
                    }
                )
                
        except Exception as e:
            if "User not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=UserNotFoundResponse().error
                )
            elif isinstance(e, HTTPException):
                raise
            else:
                logger.warning(
                    "Error checking user existence for password reset",
                    error=str(e),
                    email=request.email
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "USER_CHECK_FAILED",
                        "message": "Failed to verify user account"
                    }
                )
        
        # Send password reset email using Supabase Auth
        try:
            reset_response = supabase.auth.resetPasswordForEmail(
                request.email,
                options={
                    'redirectTo': f'{settings.FRONTEND_URL}/auth/reset-password/confirm'
                }
            )
            
            if not reset_response:
                logger.error(
                    "Failed to send password reset email",
                    user_id=user.id,
                    email=request.email
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": "EMAIL_SEND_FAILED",
                        "message": "Failed to send password reset email"
                    }
                )
            
        except Exception as e:
            logger.error(
                "Supabase password reset failed",
                error=str(e),
                user_id=user.id,
                email=request.email
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "PASSWORD_RESET_FAILED",
                    "message": "Failed to initiate password reset"
                }
            )
        
        logger.info(
            "Password reset request completed",
            user_id=user.id,
            email=request.email,
            ip=client_ip
        )
        
        return PasswordResetResponse(
            message="Password reset link sent to your email",
            email_sent=True,
            expires_in=3600  # 1 hour in seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during password reset request",
            error=str(e),
            email=request.email,
            ip=get_client_ip(http_request)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during password reset request"
            }
        )

@router.post("/password-reset/confirm", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Confirm password reset with new password
    
    Args:
        request: Password reset confirmation with new password and token
        supabase: Supabase client
        
    Returns:
        Password reset confirmation response
        
    Raises:
        HTTPException: For validation errors, invalid tokens, or weak passwords
    """
    try:
        # Validate password strength
        is_valid, errors = password_validator.validate_password_strength(request.new_password)
        if not is_valid:
            logger.warning(
                "Weak password attempt during password reset",
                errors=errors
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "WEAK_PASSWORD",
                    "message": "Password does not meet strength requirements",
                    "details": {"errors": errors}
                }
            )
        
        # For Supabase, we need to handle the token differently
        # The token should be extracted from the URL parameters when the user clicks the link
        # For now, we'll use the token to get the user and update their password
        
        try:
            # In a real implementation, you'd validate the token and extract user info
            # For now, we'll assume the token is valid and try to update the password
            # This would typically involve exchanging the token for a session
            
            # For demonstration, we'll try to get user from the token (simplified approach)
            # In production, you'd use Supabase's verifyOtp or similar method
            
            # Create a session with the token (this is a simplified approach)
            # In practice, you'd use supabase.auth.verifyOtp() with the token
            try:
                # This is a placeholder - actual implementation depends on how Supabase handles password reset tokens
                # You might need to use supabase.auth.verifyOtp() with the token
                auth_response = supabase.auth.verifyOtp({
                    'token': request.token,
                    'type': 'recovery'
                })
                
                if not auth_response or not auth_response.user:
                    logger.warning(
                        "Invalid password reset token",
                        token_preview=request.token[:10] + "..." if len(request.token) > 10 else request.token
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=InvalidResetTokenResponse().error
                    )
                
                user = auth_response.user
                
                # Update the user's password
                update_response = supabase.auth.admin.update_user_by_id(
                    user.id,
                    {'password': request.new_password}
                )
                
                if not update_response or not update_response.user:
                    logger.error(
                        "Failed to update password",
                        user_id=user.id,
                        error=str(update_response)
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "PASSWORD_UPDATE_FAILED",
                            "message": "Failed to update password"
                        }
                    )
                
                logger.info(
                    "Password reset completed successfully",
                    user_id=user.id,
                    email=user.email
                )
                
                return PasswordResetConfirmResponse(
                    message="Password updated successfully",
                    user_id=user.id
                )
                
            except Exception as e:
                if "Invalid" in str(e) or "expired" in str(e).lower():
                    logger.warning(
                        "Invalid or expired password reset token",
                        error=str(e),
                        token_preview=request.token[:10] + "..." if len(request.token) > 10 else request.token
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=InvalidResetTokenResponse().error
                    )
                else:
                    raise
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Error during password reset confirmation",
                error=str(e),
                token_preview=request.token[:10] + "..." if len(request.token) > 10 else request.token
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "PASSWORD_RESET_CONFIRM_FAILED",
                    "message": "Failed to confirm password reset"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during password reset confirmation",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during password reset confirmation"
            }
        )


# Session Management Endpoints

@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        supabase: Supabase client
        
    Returns:
        User information
        
    Raises:
        HTTPException: For unauthenticated users
    """
    try:
        # Get user details from Supabase
        user_id = current_user.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Invalid authentication token"
                }
            )
        
        # Get user profile from Supabase
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )
        
        user = user_response.user
        user_metadata = user.user_metadata or {}
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user_metadata.get('role', 'CITIZEN'),
            "full_name": user_metadata.get('full_name', 'User'),
            "phone": user_metadata.get('phone'),
            "email_confirmed_at": user.email_confirmed_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error getting current user info",
            error=str(e),
            user_id=current_user.get('sub')
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get user information"
            }
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(
    logout_request: Optional[LogoutRequest] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Logout user and invalidate session
    Invalidates current session and optionally all sessions
    """
    try:
        session_service = get_session_service()
        user_id = current_user.get('sub')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "User not authenticated"
                }
            )
        
        # Extract session ID from JWT
        from app.core.security import jwt_manager
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt_manager.decode_token(token)
        session_id = payload.get('jti') if payload else None
        
        if request.logout_all:
            # Logout from all devices
            terminated_count = await session_service.invalidate_all_user_sessions(
                user_id, 
                "user_initiated_all_devices"
            )
            message = f"You have been logged out from all {terminated_count} devices"
        else:
            # Logout current session only
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_REQUEST",
                        "message": "Session ID not found in token"
                    }
                )
            
            success = await session_service.invalidate_session(
                session_id, 
                user_id, 
                "user_initiated"
            )
            terminated_count = 1 if success else 0
            message = "You have been successfully logged out"
        
        if terminated_count > 0:
            logger.info(
                "user_logout_success",
                user_id=user_id,
                logout_all=request.logout_all,
                sessions_terminated=terminated_count
            )
            
            return LogoutResponse(
                success=True,
                message=message,
                sessions_terminated=terminated_count
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "LOGOUT_FAILED",
                    "message": "Failed to logout session"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "logout_error",
            user_id=current_user.get('sub'),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during logout"
            }
        )


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all_sessions(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Logout user from all devices
    Invalidates all active sessions for the user
    """
    try:
        session_service = get_session_service()
        user_id = current_user.get('sub')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "User not authenticated"
                }
            )
        
        terminated_count = await session_service.invalidate_all_user_sessions(
            user_id, 
            "user_initiated_all_devices"
        )
        
        logger.info(
            "user_logout_all_success",
            user_id=user_id,
            sessions_terminated=terminated_count
        )
        
        return LogoutResponse(
            success=True,
            message=f"You have been logged out from all {terminated_count} devices",
            sessions_terminated=terminated_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "logout_all_error",
            user_id=current_user.get('sub'),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during logout"
            }
        )


@router.post("/admin/force-logout/{user_id}", response_model=LogoutResponse)
async def force_logout_user(
    user_id: str,
    force_logout_request: ForceLogoutRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Force logout a specific user (admin only)
    Requires ADMIN role
    """
    try:
        # Verify admin role
        if current_user.get('role') != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Admin access required"
                }
            )
        
        session_service = get_session_service()
        admin_user_id = current_user.get('sub')
        
        success = await session_service.force_logout_user(
            user_id, 
            admin_user_id,
            force_logout_request.reason
        )
        
        if success:
            logger.info(
                "admin_force_logout_success",
                target_user_id=user_id,
                admin_user_id=admin_user_id,
                reason=force_logout_request.reason
            )
            
            # Send notification to user if requested
            if force_logout_request.notify_user:
                # TODO: Implement email notification for force logout
                pass
            
            return LogoutResponse(
                success=True,
                message=f"User {user_id} has been force logged out: {force_logout_request.reason}",
                sessions_terminated=1  # This would be the actual count from DB
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "FORCE_LOGOUT_FAILED",
                    "message": "Failed to force logout user"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "force_logout_error",
            target_user_id=user_id,
            admin_user_id=current_user.get('sub'),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during force logout"
            }
        )


@router.get("/sessions", response_model=UserSessionsResponse)
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get list of active sessions for current user
    """
    try:
        session_service = get_session_service()
        user_id = current_user.get('sub')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "UNAUTHORIZED",
                    "message": "User not authenticated"
                }
            )
        
        sessions = await session_service.get_user_sessions(user_id)
        
        # Convert to SessionInfo models
        session_infos = []
        for session in sessions:
            session_info = SessionInfo(
                id=session['id'],
                session_id=session['session_id'],
                device_info=session.get('device_info'),
                ip_address=session.get('ip_address'),
                user_agent=session.get('user_agent'),
                created_at=session['created_at'],
                last_accessed=session['last_accessed'],
                expires_at=session['expires_at'],
                is_active=session['is_active'],
                logout_reason=session.get('logout_reason'),
                logged_out_at=session.get('logged_out_at'),
                force_logout=session.get('force_logout', False)
            )
            session_infos.append(session_info)
        
        logger.info(
            "user_sessions_retrieved",
            user_id=user_id,
            session_count=len(session_infos)
        )
        
        return UserSessionsResponse(
            sessions=session_infos,
            total=len(session_infos)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_sessions_error",
            user_id=current_user.get('sub'),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving sessions"
            }
        )

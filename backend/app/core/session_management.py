"""
Session management middleware for VitaChain
Handles JWT validation with database session tracking
"""

import time
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logging import get_logger
from app.services.session_service import get_session_service

logger = get_logger(__name__)


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for session validation and management"""
    
    def __init__(self, app, session_timeout_hours: int = 24):
        super().__init__(app)
        self.session_timeout_hours = session_timeout_hours
        self.session_service = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request with session validation"""
        
        # Skip session validation for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract JWT token
        token = self._extract_token(request)
        
        if not token:
            # No token provided - continue to auth middleware
            return await call_next(request)
        
        try:
            # Decode JWT to get session info
            payload = self._decode_jwt(token)
            if not payload:
                return await call_next(request)
            
            session_id = payload.get('jti')
            user_id = payload.get('sub')
            
            if not session_id or not user_id:
                logger.warning(
                    "invalid_jwt_payload",
                    token_preview=token[:20] + "..."
                )
                return await call_next(request)
            
            # Initialize session service if needed
            if not self.session_service:
                self.session_service = get_session_service()
            
            # Validate session in database
            session_valid = await self.session_service.validate_session(session_id, user_id)
            
            if session_valid:
                # Session is valid - add to request state
                request.state.session_id = session_id
                request.state.user_id = user_id
                request.state.session_valid = True
                
                # Add session info to headers for debugging
                response = await call_next(request)
                if hasattr(response, 'headers'):
                    response.headers["X-Session-Valid"] = "true"
                    response.headers["X-Session-ID"] = session_id
                
                return response
            else:
                # Session is invalid or expired
                logger.info(
                    "session_validation_failed",
                    session_id=session_id,
                    user_id=user_id
                )
                
                # Return 401 for invalid session
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": "SESSION_INVALID",
                            "message": "Your session has expired or is invalid. Please log in again."
                        }
                    },
                    headers={
                        "X-Session-Valid": "false",
                        "X-Logout-Reason": "session_expired"
                    }
                )
        
        except Exception as e:
            logger.error(
                "session_middleware_error",
                error=str(e),
                path=request.url.path
            )
            # Continue to next middleware on error
            return await call_next(request)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # Extract Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    def _decode_jwt(self, token: str) -> Optional[dict]:
        """Decode JWT token and extract payload"""
        try:
            from app.core.security import jwt_manager
            payload = jwt_manager.decode_token(token)
            return payload
        except Exception as e:
            logger.warning(
                "jwt_decode_error",
                error=str(e),
                token_preview=token[:20] + "..."
            )
            return None
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)"""
        public_paths = {
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/magic-link",
            "/api/auth/verify-magic-link",
            "/api/auth/reset-password",
            "/api/auth/confirm-reset-password",
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json"
        }
        
        # Check if path starts with any public path
        return any(path.startswith(public_path) for public_path in public_paths)


class SessionCleanupMiddleware:
    """Middleware to handle session cleanup tasks"""
    
    def __init__(self, app, cleanup_interval_minutes: int = 30):
        super().__init__(app)
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.session_service = None
        self._last_cleanup = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request with periodic cleanup"""
        
        # Check if cleanup is needed (every 30 minutes)
        current_time = time.time()
        if current_time - self._last_cleanup > (self.cleanup_interval_minutes * 60):
            await self._perform_cleanup()
            self._last_cleanup = current_time
        
        return await call_next(request)
    
    async def _perform_cleanup(self):
        """Perform session cleanup in background"""
        try:
            if not self.session_service:
                self.session_service = get_session_service()
            
            cleaned_count = await self.session_service.cleanup_expired_sessions()
            
            if cleaned_count > 0:
                logger.info(
                    "session_cleanup_completed",
                    cleaned_sessions=cleaned_count
                )
        
        except Exception as e:
            logger.error(
                "session_cleanup_error",
                error=str(e)
            )

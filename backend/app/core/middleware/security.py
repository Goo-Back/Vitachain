# Security Middleware for VitaChain
# Provides security checks, rate limiting, and monitoring for FastAPI applications

import time
import hashlib
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import structlog

from ..security import APIKeyManager, SecurityValidator, security_headers
from ..security_monitoring import security_monitor

logger = structlog.get_logger("security_middleware")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for FastAPI applications"""
    
    def __init__(self, app, api_key_required: bool = False):
        super().__init__(app)
        self.api_key_required = api_key_required
        self.api_key_manager = APIKeyManager()
        self.security_validator = SecurityValidator()
        
        # Rate limiting per IP
        self.rate_limits = {}
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_requests = 100  # per window
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security checks"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        try:
            # Security checks
            await self._perform_security_checks(request, client_ip, user_agent)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log request
            self._log_request(request, response, start_time)
            
            return response
            
        except HTTPException as e:
            # Log security violation
            security_monitor.log_security_event(
                "http_exception",
                "medium",
                status_code=e.status_code,
                detail=e.detail,
                ip=client_ip,
                user_agent=user_agent,
                path=request.url.path
            )
            raise
            
        except Exception as e:
            # Log unexpected error
            logger.error("security_middleware_error",
                        error=str(e),
                        ip=client_ip,
                        path=request.url.path,
                        severity="high")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _perform_security_checks(self, request: Request, client_ip: str, user_agent: str):
        """Perform comprehensive security checks"""
        
        # Check if IP is blocked
        if security_monitor.is_ip_blocked(client_ip):
            logger.warning("blocked_ip_attempt",
                          ip=client_ip,
                          path=request.url.path,
                          severity="high")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Rate limiting check
        await self._check_rate_limit(request, client_ip)
        
        # Suspicious pattern detection
        self._check_suspicious_patterns(request, client_ip, user_agent)
        
        # API key validation for telemetry endpoints
        if request.url.path.startswith("/api/telemetry") or self.api_key_required:
            await self._validate_api_key(request)
        
        # Input validation
        await self._validate_request_input(request)
    
    async def _check_rate_limit(self, request: Request, client_ip: str):
        """Check rate limiting for client IP"""
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Initialize rate limit tracking for new IP
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Clean old requests
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limits[client_ip]) >= self.rate_limit_max_requests:
            security_monitor.log_api_abuse(
                client_ip,
                str(request.url.path),
                rate_violation=True,
                request_count=len(self.rate_limits[client_ip])
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        self.rate_limits[client_ip].append(now)
    
    def _check_suspicious_patterns(self, request: Request, client_ip: str, user_agent: str):
        """Check for suspicious request patterns"""
        path = request.url.path
        query_string = str(request.query_params)
        
        # Check for suspicious patterns in path
        suspicious_patterns = [
            "../", "..\\", "%2e%2e",  # Path traversal
            "<script", "javascript:",  # XSS attempts
            "union select", "drop table",  # SQL injection
            "exec(", "system(",  # Code execution
            "/etc/passwd", "/etc/shadow",  # File access
        ]
        
        for pattern in suspicious_patterns:
            if pattern.lower() in path.lower() or pattern.lower() in query_string.lower():
                security_monitor.log_suspicious_request(
                    client_ip,
                    user_agent,
                    path,
                    f"pattern_{pattern.replace(' ', '_')}"
                )
                
                # Block malicious requests
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request"
                )
        
        # Check for missing user agent (bot-like behavior)
        if not user_agent or user_agent.strip() == "":
            security_monitor.log_suspicious_request(
                client_ip,
                "empty",
                path,
                "missing_user_agent"
            )
    
    async def _validate_api_key(self, request: Request):
        """Validate API key for protected endpoints"""
        api_key = request.headers.get("x-api-key")
        device_id = request.headers.get("x-device-id")
        
        if not api_key:
            security_monitor.log_security_event(
                "missing_api_key",
                "medium",
                ip=self._get_client_ip(request),
                path=request.url.path
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        # Validate API key format and device ID
        if not self.security_validator.validate_api_request(api_key, device_id, self.api_key_manager):
            security_monitor.log_security_event(
                "invalid_api_key",
                "high",
                ip=self._get_client_ip(request),
                path=request.url.path,
                device_id=device_id
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    
    async def _validate_request_input(self, request: Request):
        """Validate request input data"""
        # For telemetry endpoints, validate data format
        if request.url.path.startswith("/api/telemetry"):
            if request.method == "POST":
                try:
                    # Get request body (would need to be implemented based on FastAPI request handling)
                    # For now, this is a placeholder
                    pass
                except Exception as e:
                    logger.warning("telemetry_data_validation_failed",
                                error=str(e),
                                severity="medium")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid telemetry data format"
                    )
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        headers = security_headers.get_security_headers()
        
        for header, value in headers.items():
            response.headers[header] = value
        
        # Add custom security headers
        response.headers["X-Security-Middleware"] = "VitaChain"
        response.headers["X-Request-ID"] = self._generate_request_id()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking"""
        timestamp = str(time.time())
        random_data = str(time.time()).encode()
        return hashlib.sha256(random_data).hexdigest()[:16]
    
    def _log_request(self, request: Request, response: Response, start_time: float):
        """Log request for security monitoring"""
        process_time = (time.time() - start_time) * 1000
        
        # Log structured request
        logger.info("api_request",
                   method=request.method,
                   url=str(request.url),
                   status_code=response.status_code,
                   process_time_ms=round(process_time, 2),
                   ip=self._get_client_ip(request),
                   user_agent=request.headers.get("user-agent", ""),
                   path=request.url.path)
        
        # Log suspicious status codes
        if response.status_code >= 400:
            security_monitor.log_security_event(
                "http_error_response",
                "medium" if response.status_code < 500 else "high",
                status_code=response.status_code,
                path=request.url.path,
                ip=self._get_client_ip(request)
            )

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process authentication"""
        
        # Skip authentication for health checks and public endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Skip authentication for static files
        if request.url.path.startswith("/static/") or request.url.path.startswith("/favicon"):
            return await call_next(request)
        
        # Check for JWT token in Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In production, validate JWT token here
            # For now, we'll just log it
            logger.info("jwt_token_present",
                        path=request.url.path,
                        severity="info")
        
        # Continue with request
        return await call_next(request)

class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware for API endpoints"""
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or [
            "https://vitachain.ma",
            "https://www.vitachain.ma",
            "https://api.vitachain.ma"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process CORS"""
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            self._add_cors_headers(response, origin)
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        self._add_cors_headers(response, origin)
        
        return response
    
    def _add_cors_headers(self, response: Response, origin: str):
        """Add CORS headers to response"""
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With, X-API-Key, X-Device-ID"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"

# Factory functions for easy middleware creation
def create_security_middleware(app, api_key_required: bool = False):
    """Create security middleware instance"""
    return SecurityMiddleware(app, api_key_required)

def create_authentication_middleware(app):
    """Create authentication middleware instance"""
    return AuthenticationMiddleware(app)

def create_cors_middleware(app, allowed_origins: list = None):
    """Create CORS middleware instance"""
    return CORSMiddleware(app, allowed_origins)

"""
Rate Limiting Middleware for Admin Endpoints
Protects admin endpoints from abuse and ensures fair usage
"""

import time
import asyncio
from typing import Dict, Any, Optional
from functools import wraps
import structlog
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = structlog.get_logger("rate_limiter")

class RateLimiter:
    """Simple in-memory rate limiter for development"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]
        
        return len(self.requests[key]) < self.max_requests
    
    def add_request(self, key: str):
        """Add a request to the limiter"""
        self.requests[key] = self.requests.get(key, [])
        self.requests[key].append(time.time())

# Global rate limiters for different endpoint types
admin_limiter = RateLimiter(max_requests=50, window_seconds=60)  # 50 requests per minute for admin endpoints
export_limiter = RateLimiter(max_requests=20, window_seconds=60)  # 20 requests per minute for export endpoints

def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_func: Optional[callable] = None
):
    """Rate limiting decorator for endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get rate limiter based on function
            limiter = admin_limiter if 'admin' in func.__name__ else export_limiter
            
            # Get client identifier (IP address or user ID)
            request: Request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            # Try to get user ID from JWT token for user-specific limits
            client_key = request.client.host
            try:
                # Extract user ID from JWT if available
                auth_header = request.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    # In production, decode JWT to get user ID
                    # For now, use IP-based limiting
                    pass
            except Exception as e:
                logger.warning(f"Error extracting client identifier for rate limiting: {e}")
            
            if not limiter.is_allowed(client_key):
                logger.warning(
                    f"Rate limit exceeded for {client_key}",
                    client_ip=request.client.host,
                    endpoint=func.__name__
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds",
                        "retry_after": window_seconds
                    }
                )
            
            # Add request to limiter
            limiter.add_request(client_key)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app):
        super().__init__(app)
        self.admin_limiter = RateLimiter(max_requests=50, window_seconds=60)
        self.export_limiter = RateLimiter(max_requests=20, window_seconds=60)
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_key = request.client.host
        
        # Check rate limits based on path
        path = request.url.path
        
        if '/api/admin/' in path:
            if not self.admin_limiter.is_allowed(client_key):
                logger.warning(
                    f"Admin rate limit exceeded for {client_key}",
                    client_ip=request.client.host,
                    path=path
                )
                return Response(
                    content='{"error": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please try again later."}',
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            self.admin_limiter.add_request(client_key)
        
        elif '/api/admin/users/export' in path:
            if not self.export_limiter.is_allowed(client_key):
                logger.warning(
                    f"Export rate limit exceeded for {client_key}",
                    client_ip=request.client.host,
                    path=path
                )
                return Response(
                    content='{"error": "RATE_LIMIT_EXCEEDED", "message": "Too many export requests. Please try again later."}',
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            self.export_limiter.add_request(client_key)
        
        # Continue with the request
        response = await call_next(request)
        return response

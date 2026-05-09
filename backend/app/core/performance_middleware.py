"""Performance monitoring middleware for FastAPI applications."""

import time
import asyncio
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import uuid
import psutil

from app.core.logging import get_logger
from app.core.performance import performance_monitor, PerformanceMetrics, get_current_system_metrics
from app.core.cache import cache_service
from app.core.database import get_database_optimizer

logger = get_logger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance and collecting metrics."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self._request_start_times: Dict[str, float] = {}
        
        # Performance thresholds from settings
        settings = get_settings()
        self.response_time_threshold = getattr(settings, 'api_response_time_threshold', 200.0)  # ms
        self.memory_threshold = getattr(settings, 'memory_usage_threshold', 80.0)  # percent
        self.cpu_threshold = getattr(settings, 'cpu_usage_threshold', 80.0)  # percent
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and collect performance metrics."""
        if not self.enabled:
            return await call_next(request)
        
        # Generate unique request ID for correlation
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time and initial system state
        start_time = time.time()
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process = None
            initial_memory = 0.0
        
        # Get cache stats before request
        cache_stats_before = None
        try:
            if cache_service._redis:
                cache_stats_before = await cache_service.get_stats()
        except Exception:
            pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate performance metrics
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Get final system state
        if process:
            try:
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage_mb = final_memory
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                memory_usage_mb = initial_memory
        else:
            memory_usage_mb = initial_memory
        cpu_usage_percent = psutil.cpu_percent()
        
        # Get cache stats after request
        cache_stats_after = None
        cache_hits = 0
        cache_misses = 0
        try:
            if cache_service._redis:
                cache_stats_after = await cache_service.get_stats()
                if cache_stats_before and cache_stats_after:
                    cache_hits = cache_stats_after['hits'] - cache_stats_before['hits']
                    cache_misses = cache_stats_after['misses'] - cache_stats_before['misses']
        except Exception:
            pass
        
        # Create performance metric
        metric = PerformanceMetrics(
            endpoint=self._get_endpoint_name(request),
            method=request.method,
            response_time_ms=response_time_ms,
            status_code=response.status_code,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            timestamp=end_time,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            database_queries=getattr(request.state, 'db_queries', 0)
        )
        
        # Record metric
        performance_monitor.record_metric(metric)
        
        # Add performance headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-MS"] = str(round(response_time_ms, 2))
        response.headers["X-Memory-Usage-MB"] = str(round(memory_usage_mb, 2))
        
        # Log performance warnings
        self._log_performance_warnings(request, metric)
        
        # Log request completion
        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            endpoint=self._get_endpoint_name(request),
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            memory_usage_mb=memory_usage_mb,
            cache_hits=cache_hits,
            cache_misses=cache_misses
        )
        
        return response
    
    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request."""
        # Try to get route pattern from FastAPI
        if hasattr(request, 'scope') and 'route' in request.scope:
            route = request.scope['route']
            if hasattr(route, 'path'):
                return route.path
        
        # Fallback to URL path
        return request.url.path
    
    def _log_performance_warnings(self, request: Request, metric: PerformanceMetrics) -> None:
        """Log performance warnings for slow requests."""
        if metric.response_time_ms > self.response_time_threshold:
            logger.warning(
                "slow_api_request",
                endpoint=metric.endpoint,
                method=metric.method,
                response_time_ms=metric.response_time_ms,
                threshold_ms=self.response_time_threshold,
                status_code=metric.status_code
            )
        
        if metric.memory_usage_mb > (self.memory_threshold * psutil.virtual_memory().total / 100 / 1024 / 1024):
            logger.warning(
                "high_memory_api_request",
                endpoint=metric.endpoint,
                memory_usage_mb=metric.memory_usage_mb,
                threshold_percent=self.memory_threshold
            )


class DatabaseQueryMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring database query performance."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and monitor database queries."""
        if not self.enabled:
            return await call_next(request)
        
        # Initialize query counter for this request
        request.state.db_queries = 0
        request.state.db_query_time = 0.0
        
        # Process request
        response = await call_next(request)
        
        # Add database metrics to response headers
        response.headers["X-DB-Queries"] = str(getattr(request.state, 'db_queries', 0))
        response.headers["X-DB-Query-Time-MS"] = str(round(getattr(request.state, 'db_query_time', 0.0), 2))
        
        return response


class CacheOptimizationMiddleware(BaseHTTPMiddleware):
    """Middleware for cache optimization and HTTP caching headers."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        
        # Cache header configurations by endpoint type
        self.cache_configs = {
            # Static assets - long cache
            "/static/": {"max-age": "31536000", "immutable": True},
            "/assets/": {"max-age": "31536000", "immutable": True},
            "/images/": {"max-age": "2592000"},  # 30 days
            
            # API endpoints - short cache for GET requests
            "/api/health": {"max-age": "30"},
            "/api/farmarket/listings": {"max-age": "300"},  # 5 minutes
            "/api/secondserve/meals": {"max-age": "300"},   # 5 minutes
            
            # No cache for sensitive endpoints
            "/auth/": {"no-cache": True},
            "/api/profile": {"no-cache": True},
            "/api/admin/": {"no-cache": True},
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and add cache headers."""
        if not self.enabled:
            return await call_next(request)
        
        response = await call_next(request)
        
        # Add cache headers based on endpoint
        self._add_cache_headers(request, response)
        
        # Add compression indication
        if self._should_compress(request, response):
            response.headers["X-Should-Compress"] = "true"
        
        return response
    
    def _add_cache_headers(self, request: Request, response: Response) -> None:
        """Add appropriate cache headers based on endpoint."""
        path = request.url.path
        
        # Find matching cache configuration
        cache_config = None
        for pattern, config in self.cache_configs.items():
            if path.startswith(pattern):
                cache_config = config
                break
        
        if cache_config:
            if cache_config.get("no-cache"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            else:
                cache_control_parts = [f"max-age={cache_config['max-age']}"]
                if cache_config.get("immutable"):
                    cache_control_parts.append("immutable")
                response.headers["Cache-Control"] = ", ".join(cache_control_parts)
        
        # Add ETag for GET requests if not already present
        if request.method == "GET" and "ETag" not in response.headers:
            # Simple ETag based on response content hash
            import hashlib
            content = getattr(response, 'body', b'')
            if content:
                etag = f'"{hashlib.md5(content).hexdigest()}"'
                response.headers["ETag"] = etag
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed."""
        # Don't compress already compressed content
        if "Content-Encoding" in response.headers:
            return False
        
        # Don't compress very small responses
        content_length = len(getattr(response, 'body', b''))
        if content_length < 1024:  # Less than 1KB
            return False
        
        # Check if client accepts compression
        accept_encoding = request.headers.get("Accept-Encoding", "")
        return "gzip" in accept_encoding.lower() or "deflate" in accept_encoding.lower()


class SecurityPerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware that combines security headers with performance monitoring."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and add security headers with performance considerations."""
        if not self.enabled:
            return await call_next(request)
        
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Add security headers (lightweight ones)
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        # Add performance timing header
        processing_time = (time.time() - start_time) * 1000
        response.headers["X-Processing-Time-MS"] = str(round(processing_time, 2))
        
        return response


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware for request correlation and tracing."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and add correlation ID."""
        if not self.enabled:
            return await call_next(request)
        
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


# Performance monitoring utilities
async def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    # Get endpoint statistics
    endpoint_stats = {}
    common_endpoints = [
        "/api/health",
        "/api/katara/dashboard", 
        "/api/farmarket/listings",
        "/api/secondserve/meals"
    ]
    
    for endpoint in common_endpoints:
        stats = performance_monitor.get_endpoint_stats(endpoint, minutes=60)
        if stats:
            endpoint_stats[endpoint] = stats
    
    # Get system statistics
    system_stats = performance_monitor.get_system_stats(minutes=60)
    
    # Get cache statistics
    cache_stats = {}
    try:
        if cache_service._redis:
            cache_stats = await cache_service.get_stats()
            cache_stats["memory_info"] = await cache_service.get_memory_info()
    except Exception as e:
        cache_stats["error"] = str(e)
    
    # Get database statistics
    db_stats = {}
    try:
        db_optimizer = get_database_optimizer()
        if db_optimizer:
            db_stats_obj = await db_optimizer.get_database_stats(minutes=60)
            db_stats = asdict(db_stats_obj)
    except Exception as e:
        db_stats["error"] = str(e)
    
    # Get top slow endpoints
    slow_endpoints = performance_monitor.get_top_slow_endpoints(limit=5, minutes=60)
    
    # Get current system metrics
    current_metrics = get_current_system_metrics()
    
    return {
        "timestamp": time.time(),
        "endpoint_stats": endpoint_stats,
        "system_stats": system_stats,
        "cache_stats": cache_stats,
        "database_stats": db_stats,
        "slow_endpoints": slow_endpoints,
        "current_system_metrics": asdict(current_metrics),
        "performance_health": await performance_monitor.performance_health_check()
    }


# Middleware factory function
def create_performance_middleware_stack(app, enabled: bool = True) -> None:
    """Create and add performance monitoring middleware stack to FastAPI app."""
    if not enabled:
        return
    
    # Add middleware in order (outermost first)
    app.add_middleware(RequestCorrelationMiddleware, enabled=enabled)
    app.add_middleware(SecurityPerformanceMiddleware, enabled=enabled)
    app.add_middleware(CacheOptimizationMiddleware, enabled=enabled)
    app.add_middleware(DatabaseQueryMiddleware, enabled=enabled)
    app.add_middleware(PerformanceMonitoringMiddleware, enabled=enabled)
    
    logger.info("performance_middleware_stack_initialized")


# Performance monitoring endpoint
async def performance_metrics_endpoint() -> Dict[str, Any]:
    """Endpoint to expose performance metrics."""
    return await get_performance_summary()


# Health check with performance metrics
async def health_with_performance() -> Dict[str, Any]:
    """Enhanced health check with performance metrics."""
    current_metrics = get_current_system_metrics()
    performance_health = await performance_monitor.performance_health_check()
    
    # Determine overall health status
    health_status = "healthy"
    if performance_health["health_score"] < 70:
        health_status = "degraded"
    if performance_health["health_score"] < 50:
        health_status = "unhealthy"
    
    return {
        "status": health_status,
        "timestamp": time.time(),
        "performance": performance_health,
        "system": asdict(current_metrics),
        "checks": {
            "memory_ok": current_metrics.memory_percent < 80,
            "cpu_ok": current_metrics.cpu_percent < 80,
            "disk_ok": current_metrics.disk_usage_percent < 85,
            "performance_score_ok": performance_health["health_score"] >= 70
        }
    }

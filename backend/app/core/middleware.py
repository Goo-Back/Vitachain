"""Performance monitoring and logging middleware."""

import time
import psutil
import asyncio
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and request logging."""
    
    def __init__(self, app, thresholds: dict = None):
        super().__init__(app)
        self.settings = get_settings()
        self.thresholds = thresholds or {
            "api_response_time": self.settings.api_response_time_threshold,
            "memory_usage": self.settings.memory_usage_threshold,
            "cpu_usage": self.settings.cpu_usage_threshold,
            "disk_usage": self.settings.disk_usage_threshold,
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance monitoring."""
        start_time = time.time()
        
        # Get initial system metrics
        initial_memory = psutil.virtual_memory().percent
        initial_cpu = psutil.cpu_percent(interval=None)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Get final system metrics
        final_memory = psutil.virtual_memory().percent
        final_cpu = psutil.cpu_percent(interval=None)
        
        # Log request with performance metrics
        logger.info(
            "api_request",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
            user_agent=request.headers.get("user-agent", ""),
            memory_usage_percent=final_memory,
            cpu_usage_percent=final_cpu,
            correlation_id=request.state.correlation_id if hasattr(request.state, 'correlation_id') else None,
        )
        
        # Check performance thresholds
        await self._check_thresholds(process_time, final_memory, final_cpu, request)
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Memory-Usage"] = f"{final_memory:.1f}%"
        
        return response
    
    async def _check_thresholds(self, process_time: float, memory: float, cpu: float, request: Request):
        """Check performance thresholds and log warnings."""
        warnings = []
        
        if process_time > self.thresholds["api_response_time"]:
            warnings.append(f"Response time {process_time:.2f}ms exceeds threshold {self.thresholds['api_response_time']}ms")
        
        if memory > self.thresholds["memory_usage"]:
            warnings.append(f"Memory usage {memory:.1f}% exceeds threshold {self.thresholds['memory_usage']}%")
        
        if cpu > self.thresholds["cpu_usage"]:
            warnings.append(f"CPU usage {cpu:.1f}% exceeds threshold {self.thresholds['cpu_usage']}%")
        
        if warnings:
            logger.warning(
                "performance_threshold_exceeded",
                url=str(request.url),
                method=request.method,
                warnings=warnings,
                process_time_ms=process_time,
                memory_usage_percent=memory,
                cpu_usage_percent=cpu,
            )


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request state."""
        import uuid
        
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting based on client IP."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                url=str(request.url),
                method=request.method,
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove requests older than 1 minute."""
        cutoff_time = current_time - 60
        self.request_counts = {
            ip: times for ip, times in self.request_counts.items()
            if any(t > cutoff_time for t in times)
        }
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit."""
        if client_ip not in self.request_counts:
            return False
        
        # Count requests in last minute
        cutoff_time = current_time - 60
        recent_requests = [
            t for t in self.request_counts[client_ip]
            if t > cutoff_time
        ]
        
        return len(recent_requests) >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request from client."""
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        self.request_counts[client_ip].append(current_time)


class SystemMetricsCollector:
    """Background system metrics collector."""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self._running = False
    
    async def start(self):
        """Start background metrics collection."""
        if not self.settings.enable_metrics:
            return
        
        self._running = True
        asyncio.create_task(self._collect_loop())
        self.logger.info("system_metrics_started", interval=self.interval)
    
    async def stop(self):
        """Stop background metrics collection."""
        self._running = False
        self.logger.info("system_metrics_stopped")
    
    async def _collect_loop(self):
        """Background loop for collecting metrics."""
        while self._running:
            try:
                await self._collect_and_log_metrics()
                await asyncio.sleep(self.interval)
            except Exception as e:
                self.logger.error("metrics_collection_error", error=str(e))
                await asyncio.sleep(10)  # Short delay on error
    
    async def _collect_and_log_metrics(self):
        """Collect and log system metrics."""
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        metrics = {
            "timestamp": time.time(),
            "system": {
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "cpu_percent": cpu,
            },
            "process": {
                "memory_rss_mb": process_memory.rss / (1024**2),
                "memory_vms_mb": process_memory.vms / (1024**2),
                "cpu_percent": process_cpu,
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0,
            }
        }
        
        self.logger.info("system_metrics", **metrics)
        
        # Check thresholds
        await self._check_system_thresholds(metrics)
    
    async def _check_system_thresholds(self, metrics: dict):
        """Check system metrics against thresholds."""
        warnings = []
        
        if metrics["system"]["memory_percent"] > self.thresholds["memory_usage"]:
            warnings.append(f"System memory {metrics['system']['memory_percent']:.1f}% exceeds threshold")
        
        if metrics["system"]["disk_percent"] > self.thresholds["disk_usage"]:
            warnings.append(f"Disk usage {metrics['system']['disk_percent']:.1f}% exceeds threshold")
        
        if metrics["system"]["cpu_percent"] > self.thresholds["cpu_usage"]:
            warnings.append(f"CPU usage {metrics['system']['cpu_percent']:.1f}% exceeds threshold")
        
        if warnings:
            self.logger.warning(
                "system_threshold_exceeded",
                warnings=warnings,
                metrics=metrics
            )


# Global metrics collector
metrics_collector = SystemMetricsCollector(
    interval=get_settings().metrics_interval
)

"""Performance monitoring and optimization utilities."""

import time
import asyncio
import psutil
import gc
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from functools import wraps
import threading

from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: float
    cache_hits: int = 0
    cache_misses: int = 0
    database_queries: int = 0


@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_connections: int
    timestamp: float


class PerformanceMonitor:
    """Main performance monitoring class."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self._lock = threading.Lock()
        self._max_metrics = get_settings().performance_metrics_limit or 10000
        
        # Performance thresholds
        self.response_time_threshold = get_settings().api_response_time_threshold or 200
        self.memory_threshold = get_settings().memory_usage_threshold or 80
        self.cpu_threshold = get_settings().cpu_usage_threshold or 80
        self.disk_threshold = get_settings().disk_usage_threshold or 85
    
    def record_metric(self, metric: PerformanceMetrics) -> None:
        """Record a performance metric."""
        with self._lock:
            self.metrics.append(metric)
            
            # Keep only recent metrics
            if len(self.metrics) > self._max_metrics:
                self.metrics = self.metrics[-self._max_metrics:]
            
            # Check for performance alerts
            self._check_performance_alerts(metric)
    
    def record_system_metric(self, metric: SystemMetrics) -> None:
        """Record system metrics."""
        with self._lock:
            self.system_metrics.append(metric)
            
            # Keep only recent metrics
            if len(self.system_metrics) > self._max_metrics:
                self.system_metrics = self.system_metrics[-self._max_metrics:]
            
            # Check for system alerts
            self._check_system_alerts(metric)
    
    def _check_performance_alerts(self, metric: PerformanceMetrics) -> None:
        """Check for performance alerts and log warnings."""
        if metric.response_time_ms > self.response_time_threshold:
            logger.warning(
                "slow_response_time",
                endpoint=metric.endpoint,
                response_time_ms=metric.response_time_ms,
                threshold_ms=self.response_time_threshold
            )
        
        if metric.memory_usage_mb > (self.memory_threshold * psutil.virtual_memory().total / 100 / 1024 / 1024):
            logger.warning(
                "high_memory_usage",
                endpoint=metric.endpoint,
                memory_usage_mb=metric.memory_usage_mb,
                threshold_percent=self.memory_threshold
            )
    
    def _check_system_alerts(self, metric: SystemMetrics) -> None:
        """Check for system resource alerts."""
        if metric.cpu_percent > self.cpu_threshold:
            logger.warning(
                "high_cpu_usage",
                cpu_percent=metric.cpu_percent,
                threshold_percent=self.cpu_threshold
            )
        
        if metric.memory_percent > self.memory_threshold:
            logger.warning(
                "high_memory_usage_system",
                memory_percent=metric.memory_percent,
                threshold_percent=self.memory_threshold
            )
        
        if metric.disk_usage_percent > self.disk_threshold:
            logger.warning(
                "high_disk_usage",
                disk_usage_percent=metric.disk_usage_percent,
                threshold_percent=self.disk_threshold
            )
    
    def get_endpoint_stats(self, endpoint: str, minutes: int = 60) -> Dict[str, Any]:
        """Get performance statistics for a specific endpoint."""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics 
                if m.endpoint == endpoint and m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {}
        
        response_times = [m.response_time_ms for m in recent_metrics]
        return {
            "endpoint": endpoint,
            "request_count": len(recent_metrics),
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "p99_response_time_ms": self._percentile(response_times, 99),
            "success_rate": len([m for m in recent_metrics if m.status_code < 400]) / len(recent_metrics) if recent_metrics else 0.0,
            "cache_hit_rate": self._calculate_cache_hit_rate(recent_metrics),
            "period_minutes": minutes
        }
    
    def get_system_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get system performance statistics."""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            recent_metrics = [
                m for m in self.system_metrics 
                if m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {}
        
        return {
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "max_cpu_percent": max(m.cpu_percent for m in recent_metrics),
            "avg_memory_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            "max_memory_percent": max(m.memory_percent for m in recent_metrics),
            "avg_disk_usage_percent": sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            "current_memory_used_mb": recent_metrics[-1].memory_used_mb if recent_metrics else 0,
            "current_memory_available_mb": recent_metrics[-1].memory_available_mb if recent_metrics else 0,
            "period_minutes": minutes
        }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_cache_hit_rate(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate cache hit rate from metrics."""
        total_requests = len(metrics)
        if total_requests == 0:
            return 0.0
        
        total_hits = sum(m.cache_hits for m in metrics)
        total_cache_operations = sum(m.cache_hits + m.cache_misses for m in metrics)
        
        if total_cache_operations == 0:
            return 0.0
        
        return (total_hits / total_cache_operations) * 100
    
    def clear_old_metrics(self, hours: int = 24) -> None:
        """Clear metrics older than specified hours."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            self.system_metrics = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
    
    def get_top_slow_endpoints(self, limit: int = 10, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get top slowest endpoints."""
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        # Group by endpoint and calculate average response time
        endpoint_stats = {}
        for metric in recent_metrics:
            if metric.endpoint not in endpoint_stats:
                endpoint_stats[metric.endpoint] = []
            endpoint_stats[metric.endpoint].append(metric.response_time_ms)
        
        # Calculate averages and sort
        endpoint_averages = []
        for endpoint, times in endpoint_stats.items():
            avg_time = sum(times) / len(times)
            endpoint_averages.append({
                "endpoint": endpoint,
                "avg_response_time_ms": avg_time,
                "request_count": len(times)
            })
        
        return sorted(endpoint_averages, key=lambda x: x["avg_response_time_ms"], reverse=True)[:limit]


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_current_system_metrics() -> SystemMetrics:
    """Get current system metrics."""
    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory metrics
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_used_mb = memory.used / 1024 / 1024
    memory_available_mb = memory.available / 1024 / 1024
    
    # Disk metrics
    disk = psutil.disk_usage('/')
    disk_usage_percent = (disk.used / disk.total) * 100
    
    # Network connections
    try:
        active_connections = len(psutil.net_connections())
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        active_connections = 0
    
    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        memory_used_mb=memory_used_mb,
        memory_available_mb=memory_available_mb,
        disk_usage_percent=disk_usage_percent,
        active_connections=active_connections,
        timestamp=time.time()
    )


@asynccontextmanager
async def performance_context(endpoint: str, method: str = "GET"):
    """Context manager for measuring performance."""
    start_time = time.time()
    
    # Get initial system metrics
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        yield
    finally:
        # Calculate performance metrics
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Get final system metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage_mb = final_memory
        cpu_usage_percent = psutil.cpu_percent()
        
        # Create and record metric
        metric = PerformanceMetrics(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            status_code=200,  # Will be updated by middleware
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            timestamp=end_time
        )
        
        performance_monitor.record_metric(metric)


def monitor_performance(endpoint: str, method: str = "GET"):
    """Decorator for monitoring function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with performance_context(endpoint, method):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def collect_system_metrics() -> None:
    """Collect and record system metrics."""
    metrics = get_current_system_metrics()
    performance_monitor.record_system_metric(metrics)


def optimize_memory() -> Dict[str, Any]:
    """Perform memory optimization."""
    # Force garbage collection
    collected = gc.collect()
    
    # Get memory before and after
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Additional cleanup
    gc.collect()
    
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_freed = memory_before - memory_after
    
    logger.info(
        "memory_optimization",
        memory_before_mb=memory_before,
        memory_after_mb=memory_after,
        memory_freed_mb=memory_freed,
        objects_collected=collected
    )
    
    return {
        "memory_before_mb": memory_before,
        "memory_after_mb": memory_after,
        "memory_freed_mb": memory_freed,
        "objects_collected": collected
    }


# Performance monitoring task
async def performance_monitoring_task() -> None:
    """Background task for continuous performance monitoring."""
    while True:
        try:
            await collect_system_metrics()
            
            # Clean up old metrics periodically
            performance_monitor.clear_old_metrics(hours=24)
            
            # Sleep for configured interval
            interval = get_settings().metrics_interval or 60
            await asyncio.sleep(interval)
            
        except Exception as e:
            logger.error("performance_monitoring_error", error=str(e))
            await asyncio.sleep(60)  # Wait before retrying


# Performance health check
async def performance_health_check() -> Dict[str, Any]:
    """Perform comprehensive performance health check."""
    current_metrics = get_current_system_metrics()
    
    # Get recent endpoint performance
    slow_endpoints = performance_monitor.get_top_slow_endpoints(limit=5, minutes=15)
    
    # Calculate health score
    health_issues = []
    
    if current_metrics.cpu_percent > 80:
        health_issues.append("High CPU usage")
    
    if current_metrics.memory_percent > 80:
        health_issues.append("High memory usage")
    
    if current_metrics.disk_usage_percent > 85:
        health_issues.append("High disk usage")
    
    if slow_endpoints and slow_endpoints[0]["avg_response_time_ms"] > 500:
        health_issues.append("Slow API responses")
    
    health_score = max(0, 100 - len(health_issues) * 25)
    
    return {
        "health_score": health_score,
        "health_issues": health_issues,
        "current_metrics": asdict(current_metrics),
        "slow_endpoints": slow_endpoints[:3],
        "timestamp": time.time()
    }
